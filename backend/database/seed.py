"""
Database Seeding - Initial data for the application

Creates default admin user and demo users with sample activities and stats.
"""
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from database.models import User, UserStats, ActivityLog, VPNServer
from database.repositories.user_repository import UserRepository
from database.repositories.activity_repository import ActivityRepository


def seed_database(db: Session):
    """
    Seed the database with initial data.
    
    Includes:
    - Default admin user
    - Demo users
    - Sample activities
    - Sample statistics
    - VPN servers
    """
    user_repo = UserRepository(db)
    activity_repo = ActivityRepository(db)
    
    print("[SEED] Starting database seeding...")
    
    # ==================== ADMIN USERS ====================
    admin_users = [
        {
            "email": "admin@fsociety.com",
            "username": "admin",
            "password": "Admin123!",
            "full_name": "System Administrator",
            "bio": "Root access authorized."
        },
        {
            "email": "dhruvil@fsociety.com",
            "username": "dhruvil",
            "password": "Fsociety2026!",
            "full_name": "Dhruvil Admin",
            "bio": "Lead Developer & Admin."
        }
    ]



    for admin_data in admin_users:
        existing_user = user_repo.get_by_email(admin_data["email"])
        
        import bcrypt
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(admin_data["password"].encode('utf-8'), salt).decode('utf-8')

        if not existing_user:
            user_repo.create({
                "email": admin_data["email"],
                "username": admin_data["username"],
                "password_hash": password_hash,
                "full_name": admin_data["full_name"],
                "bio": admin_data["bio"],
                "role": "admin",
            })
            print(f"[SEED] Created admin: {admin_data['email']}")
        else:
            # Update password for existing user
            user_repo.update(existing_user.id, {"password_hash": password_hash})
            print(f"[SEED] Updated admin password: {admin_data['email']}")
    
    # ==================== DEMO USERS ====================
    # 1. Mr. Robot (Main Demo User)
    mrrobot_email = "mrrobot@fsociety.com"
    existing_robot = user_repo.get_by_email(mrrobot_email)
    
    import bcrypt
    salt = bcrypt.gensalt()
    mrrobot_pass = bcrypt.hashpw("Elliot123!".encode('utf-8'), salt).decode('utf-8')
    
    if not existing_robot:
        user_repo.create({
            "email": mrrobot_email,
            "username": "mrrobot",
            "password_hash": mrrobot_pass,
            "full_name": "Elliot Alderson",
            "company": "Allsafe Cybersecurity",
            "bio": "I am a cyber security engineer by day...",
            "role": "user",
        })
        print(f"[SEED] Created demo user: {mrrobot_email}")
    else:
        user_repo.update(existing_robot.id, {"password_hash": mrrobot_pass})
        print(f"[SEED] Updated demo user password: {mrrobot_email}")

    # 2. Other Demo Users
    demo_users_data = [
        {"email": "alice@example.com", "username": "alice_sec", "full_name": "Alice Security", "company": "CyberCorp"},
        {"email": "bob@example.com", "username": "bob_hack", "full_name": "Bob Hacker", "company": "SecureNet"},
    ]
    
    # Hash for other demo users
    import bcrypt
    salt = bcrypt.gensalt()
    demo_password_hash = bcrypt.hashpw("Demo123!".encode('utf-8'), salt).decode('utf-8')
    
    created_users = []
    for user_data in demo_users_data:
        if not user_repo.get_by_email(user_data["email"]):
            user = user_repo.create({
                **user_data,
                "password_hash": demo_password_hash,
                "role": "user",
            })
            created_users.append(user)
            print(f"[SEED] Created demo user: {user_data['email']}")
    
    # ==================== SAMPLE STATS & ACTIVITIES ====================
    # Only seed if no activities exist (prevents duplicates on restart)
    existing_activities = db.query(ActivityLog).limit(1).first()
    if not existing_activities:
        actions = ["scan", "chat", "ssl_scan", "phishing_check", "vpn_generate", "login", "footprint", "hash_check"]
        
        all_users = user_repo.get_all()
        for user in all_users:
            # Add random stats
            user_repo.update_stats(user.id, {
                "total_scans": random.randint(5, 50),
                "phishing_checks": random.randint(2, 20),
                "security_scans": random.randint(1, 15),
                "vpn_configs": random.randint(0, 5),
                "reports_generated": random.randint(1, 10),
                "file_analysis": random.randint(0, 10),
                "malware_detected": random.randint(0, 3),
                "last_active": datetime.now(timezone.utc),
            })
            
            # Add random activities
            for _ in range(random.randint(3, 10)):
                action = random.choice(actions)
                activity_time = datetime.now(timezone.utc) - timedelta(
                    hours=random.randint(0, 72),
                    minutes=random.randint(0, 59)
                )
                
                activity_repo.create({
                    "user_id": user.id,
                    "action": action,
                    "details": {"target": f"example-{random.randint(1, 100)}.com"},
                    "ip_address": f"192.168.1.{random.randint(1, 254)}",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "timestamp": activity_time,
                })
        
        print(f"[SEED] Added stats and activities for {len(all_users)} users")
    else:
        print("[SEED] Skipping stats/activities (already exist)")
    
    # ==================== VPN SERVERS ====================
    vpn_servers = [
        {"id": "us-east", "name": "USA - New York", "address": "vpn-us.fsociety.com", "region": "Americas", "current_load": "42%"},
        {"id": "eu-central", "name": "Germany - Frankfurt", "address": "vpn-eu.fsociety.com", "region": "Europe", "current_load": "18%"},
        {"id": "asia-east", "name": "Japan - Tokyo", "address": "vpn-asia.fsociety.com", "region": "Asia", "current_load": "65%"},
        {"id": "in-west", "name": "India - Mumbai", "address": "vpn-in.fsociety.com", "region": "Asia", "current_load": "20%"},
    ]
    
    for server_data in vpn_servers:
        existing = db.query(VPNServer).filter(VPNServer.id == server_data["id"]).first()
        if not existing:
            server = VPNServer(**server_data)
            db.add(server)
    
    db.commit()
    print(f"[SEED] Added {len(vpn_servers)} VPN servers")
    
    print("[SEED] Database seeding complete!")
