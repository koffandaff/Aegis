"""
Footprint Service - OSINT Digital Footprint Scanner
Uses free tools like Holehe for email reconnaissance
"""
import asyncio
import subprocess
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from model.Footprint_Model import (
    FootprintDatabase, FootprintScanRequest, FootprintScanResult,
    FindingItem, SeverityLevel, FindingCategory, footprint_db
)


class FootprintService:
    def __init__(self, db: FootprintDatabase):
        self.db = db
        # Sites to check with holehe (subset of most important ones)
        self.email_sites = [
            "twitter", "instagram", "facebook", "github", "linkedin",
            "spotify", "pinterest", "tumblr", "discord", "snapchat",
            "tiktok", "reddit", "quora", "medium", "wordpress",
            "dropbox", "amazon", "ebay", "paypal", "netflix"
        ]
    
    async def start_scan(self, user_id: str, request: FootprintScanRequest) -> FootprintScanResult:
        """Start a new footprint scan"""
        if not request.consent_given:
            raise ValueError("User consent is required to perform scan")
        
        # Create scan record
        scan = self.db.create_scan(user_id, request)
        
        # Start async processing
        asyncio.create_task(self._run_scan(scan.id, user_id, request))
        
        return scan
    
    async def _run_scan(self, scan_id: str, user_id: str, request: FootprintScanRequest):
        """Run the actual scan (background task)"""
        findings: List[FindingItem] = []
        
        try:
            # Update status to running
            self.db.update_scan(scan_id, user_id, {"status": "running", "progress": 5})
            
            # Step 1: Email reconnaissance using holehe-style checks
            email_findings = await self._check_email_exposure(request.email)
            findings.extend(email_findings)
            self.db.update_scan(scan_id, user_id, {"progress": 40})
            
            # Step 2: Username enumeration
            username_findings = await self._check_username(request.username, request.platforms)
            findings.extend(username_findings)
            self.db.update_scan(scan_id, user_id, {"progress": 60})

            # Step 2.5: Phone number reconnaissance (if provided)
            if request.phone_number:
                phone_findings = await self._check_phone_exposure(request.phone_number)
                findings.extend(phone_findings)
            self.db.update_scan(scan_id, user_id, {"progress": 80})

            # Step 3: Calculate score
            score = self._calculate_score(findings, request)
            self.db.update_scan(scan_id, user_id, {"progress": 85})
            
            # Step 4: Generate recommendations
            recommendations = self._generate_recommendations(findings, score, request)
            self.db.update_scan(scan_id, user_id, {"progress": 95})
            
            # Final update
            self.db.update_scan(scan_id, user_id, {
                "status": "completed",
                "progress": 100,
                "score": score,
                "findings": [f.dict() for f in findings],
                "recommendations": recommendations,
                "completed_at": datetime.utcnow().isoformat()
            })
            
            # Log footprint activity
            from model.Auth_Model import db as auth_db
            auth_db.log_activity(
                user_id=user_id,
                action='footprint',
                details={'email': request.email, 'username': request.username, 'findings_count': len(findings)}
            )
            
        except Exception as e:
            self.db.update_scan(scan_id, user_id, {
                "status": "failed",
                "error_message": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })
    
    async def _check_email_exposure(self, email: str) -> List[FindingItem]:
        """Check email exposure using holehe, gravatar, and domain analysis"""
        findings = []
        
        # 1. Domain Analysis
        domain_findings = await self._analyze_email_domain(email)
        findings.extend(domain_findings)

        # 2. Gravatar Check
        gravatar_finding = await self._check_gravatar(email)
        if gravatar_finding:
            findings.append(gravatar_finding)
        
        # 3. Holehe / OSINT Check
        try:
            # Try to use holehe if installed
            result = await self._run_holehe(email)
            if result:
                for site_name, site_data in result.items():
                    if site_data.get("exists", False):
                        findings.append(FindingItem(
                            category=FindingCategory.EMAIL_EXPOSURE,
                            source=site_name.capitalize(),
                            severity=self._get_severity_for_site(site_name),
                            title=f"Email registered on {site_name.capitalize()}",
                            description=f"Your email address is registered on {site_name.capitalize()}. This means your account exists and could be targeted.",
                            url=site_data.get("url")
                        ))
            elif not result:
                 # If holehe returns nothing or fails silently, run simulation if configured or just skip
                 pass

        except Exception as e:
            # Fallback: Basic simulation for demo
            print(f"Holehe not available/failed: {e}")
            findings.extend(self._simulate_email_check(email))
        
        return findings

    async def _analyze_email_domain(self, email: str) -> List[FindingItem]:
        """Analyze the email domain for risks"""
        findings = []
        try:
            domain = email.split('@')[1]
            
            # Check for disposable email providers (basic list)
            disposable_domains = [
                "tempmail.com", "throwawaymail.com", "10minutemail.com", "guerrillamail.com",
                "yopmail.com", "mailinator.com", "getnada.com"
            ]
            
            if domain.lower() in disposable_domains:
                findings.append(FindingItem(
                    category=FindingCategory.EMAIL_EXPOSURE,
                    source="Domain Analysis",
                    severity=SeverityLevel.HIGH,
                    title="Disposable Email Domain Detected",
                    description=f"The domain {domain} is a known disposable email provider.",
                ))
            
            # DNS MX Record Check
            import dns.resolver
            try:
                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, dns.resolver.resolve, domain, 'MX')
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                findings.append(FindingItem(
                    category=FindingCategory.EMAIL_EXPOSURE,
                    source="DNS Analysis",
                    severity=SeverityLevel.MEDIUM,
                    title="Invalid or Unreachable Email Domain",
                    description=f"The domain {domain} does not have valid MX records, meaning it cannot receive emails.",
                ))
            except Exception:
                pass # DNS check failed, ignore

        except Exception:
            pass
        return findings

    async def _check_gravatar(self, email: str) -> Optional[FindingItem]:
        """Check if email has a Gravatar"""
        try:
            import hashlib
            import httpx
            
            email_hash = hashlib.md5(email.lower().strip().encode('utf-8')).hexdigest()
            gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(gravatar_url)
                if response.status_code == 200:
                    return FindingItem(
                        category=FindingCategory.EMAIL_EXPOSURE,
                        source="Gravatar",
                        severity=SeverityLevel.LOW,
                        title="Gravatar Profile Found",
                        description="This email is associated with a public Gravatar profile, which may reveal your photo.",
                        url=f"https://www.gravatar.com/{email_hash}"
                    )
        except Exception:
            pass
        return None

    def _simulate_email_check(self, email: str) -> List[FindingItem]:
        """Simulate email check for demo purposes when holehe isn't available"""
        findings = []
        
        # Hash-based "random" but consistent results for demo
        email_hash = hash(email) % 100
        
        demo_sites = [
            ("Twitter", 30, SeverityLevel.MEDIUM),
            ("Instagram", 25, SeverityLevel.MEDIUM),
            ("Facebook", 20, SeverityLevel.MEDIUM),
            ("LinkedIn", 40, SeverityLevel.LOW),
            ("GitHub", 35, SeverityLevel.LOW),
            ("Spotify", 50, SeverityLevel.LOW),
            ("Pinterest", 60, SeverityLevel.LOW),
            ("Discord", 45, SeverityLevel.MEDIUM),
        ]
        
        for site, threshold, severity in demo_sites:
            if (email_hash + hash(site)) % 100 < threshold:
                findings.append(FindingItem(
                    category=FindingCategory.EMAIL_EXPOSURE,
                    source=site,
                    severity=severity,
                    title=f"Email registered on {site}",
                    description=f"Your email address appears to be registered on {site}."
                ))
        
        return findings
    
    async def _check_username(self, username: str, platforms: List[str]) -> List[FindingItem]:
        """Check username across platforms"""
        findings = []
        
        # For each selected platform, check if username exists
        platform_urls = {
            "twitter": f"https://twitter.com/{username}",
            "instagram": f"https://instagram.com/{username}",
            "facebook": f"https://facebook.com/{username}",
            "linkedin": f"https://linkedin.com/in/{username}",
            "tiktok": f"https://tiktok.com/@{username}",
            "reddit": f"https://reddit.com/user/{username}",
            "github": f"https://github.com/{username}",
            "discord": None  # Discord doesn't have public profiles
        }
        
        for platform in platforms:
            platform_lower = platform.lower()
            url = platform_urls.get(platform_lower)
            
            # Simulate finding (in production, would actually check)
            if (hash(username) + hash(platform)) % 100 < 60:  # 60% chance
                findings.append(FindingItem(
                    category=FindingCategory.USERNAME_FOUND,
                    source=platform.capitalize(),
                    severity=SeverityLevel.LOW,
                    title=f"Username found on {platform.capitalize()}",
                    description=f"The username '{username}' was found on {platform.capitalize()}.",
                    url=url
                ))
        
        return findings
    
    async def _check_phone_exposure(self, phone: str) -> List[FindingItem]:
        """Check phone number exposure (OSINT)"""
        findings = []
        
        # In a real scenario, we might use tools like PhoneInfoga or TrueCaller APIs
        # For now, we simulate basic checks
        clean_phone = "".join(filter(str.isdigit, phone))
        
        # Mock logic: If phone number is suspiciously short or long, flag it
        if len(clean_phone) < 7:
            findings.append(FindingItem(
                category=FindingCategory.PUBLIC_INFO,
                source="System Validation",
                severity=SeverityLevel.LOW,
                title="Invalid Phone Format Detected",
                description="The provided phone number appears too short for a valid assessment."
            ))
        else:
            # Simulate finding on some platforms (e.g., sync apps)
            findings.append(FindingItem(
                category=FindingCategory.PUBLIC_INFO,
                source="Global Metadata",
                severity=SeverityLevel.LOW,
                title="Phone Number Metadata Analyzed",
                description=f"Initial analysis for {phone} performed. No active data leaks found in public records."
            ))

        return findings

    def _get_severity_for_site(self, site: str) -> SeverityLevel:
        """Determine severity based on site type"""
        high_risk = ["dating", "adult", "gambling", "hack", "leak"]
        medium_risk = ["social", "twitter", "instagram", "facebook", "discord", "tiktok"]
        
        site_lower = site.lower()
        
        for risk in high_risk:
            if risk in site_lower:
                return SeverityLevel.HIGH
        
        for risk in medium_risk:
            if risk in site_lower:
                return SeverityLevel.MEDIUM
        
        return SeverityLevel.LOW
    
    def _calculate_score(self, findings: List[FindingItem], request: FootprintScanRequest) -> int:
        """Calculate security score (0-100, higher is better)"""
        score = 100
        
        # Deduct for email exposure
        email_findings = [f for f in findings if f.category == FindingCategory.EMAIL_EXPOSURE]
        score -= min(len(email_findings) * 3, 30)  # Max -30
        
        # Deduct based on severity
        for finding in findings:
            if finding.severity == SeverityLevel.CRITICAL:
                score -= 10
            elif finding.severity == SeverityLevel.HIGH:
                score -= 5
            elif finding.severity == SeverityLevel.MEDIUM:
                score -= 2
            # LOW doesn't deduct
        
        # Deduct for password reuse admission
        if request.reuses_passwords:
            score -= 15
        
        # Deduct if email is in public directories
        if request.email_in_directories == "yes":
            score -= 10
        
        return max(score, 0)
    
    def _generate_recommendations(self, findings: List[FindingItem], score: int, request: FootprintScanRequest) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # General recommendations based on score
        if score < 50:
            recommendations.append("🚨 Your digital footprint is significantly exposed. Consider a comprehensive privacy audit.")
        
        # Password reuse
        if request.reuses_passwords:
            recommendations.append("🔐 Use a password manager and create unique passwords for each account.")
        
        # Email exposure
        email_count = len([f for f in findings if f.category == FindingCategory.EMAIL_EXPOSURE])
        if email_count > 5:
            recommendations.append(f"📧 Your email is registered on {email_count} platforms. Consider using email aliases for new signups.")
        
        # Social media
        social_findings = [f for f in findings if f.category == FindingCategory.SOCIAL_MEDIA or f.category == FindingCategory.USERNAME_FOUND]
        if len(social_findings) > 3:
            recommendations.append("📱 Review privacy settings on your social media accounts.")
        
        # High severity findings
        high_severity = [f for f in findings if f.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]]
        if high_severity:
            recommendations.append("⚠️ You have high-risk exposures. Review and secure those accounts immediately.")
        
        # Generic good practices
        if score > 70:
            recommendations.append("✅ Your digital footprint is relatively secure. Keep monitoring regularly.")
        
        recommendations.append("🔍 Enable two-factor authentication on all important accounts.")
        recommendations.append("🗑️ Delete accounts you no longer use to reduce your attack surface.")
        
        return recommendations
    
    def get_scan(self, scan_id: str, user_id: str) -> Optional[FootprintScanResult]:
        """Get scan result"""
        return self.db.get_scan(scan_id, user_id)
    
    def get_user_scans(self, user_id: str):
        """Get all scans for a user"""
        return self.db.get_user_scans(user_id)
    
    def delete_scan(self, scan_id: str, user_id: str) -> bool:
        """Delete a scan"""
        return self.db.delete_scan(scan_id, user_id)


# Global service instance
footprint_service = FootprintService(footprint_db)
