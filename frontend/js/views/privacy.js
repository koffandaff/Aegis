class PrivacyView {
    async render() {
        return `
            <div style="min-height: 100vh; background: #000; padding: 6rem 2rem;">
                <!-- Navigation -->
                <nav class="glass" style="position: fixed; top: 0; width: 100%; z-index: 100; display: flex; justify-content: space-between; align-items: center; padding: 1rem 3rem; left: 0;">
                    <a href="#/" style="text-decoration: none; display: flex; align-items: center;">
                        <span class="material-symbols-outlined" style="color: #fff; font-size: 1.8rem; margin-right: 0.5rem;">security</span>
                        <span style="font-size: 1.5rem; font-weight: 800; color: #fff; font-family: 'JetBrains Mono', monospace;">Aegis</span>
                    </a>
                    <a href="#/" class="btn-outline" style="padding: 0.5rem 1.5rem;">Back to Home</a>
                </nav>

                <div class="container" style="max-width: 800px; margin: 0 auto; color: #e0e0e0;">
                    <h1 style="font-size: 2.5rem; margin-bottom: 2rem; color: var(--primary);">Privacy Policy</h1>
                    
                    <div class="card glass" style="padding: 2rem; margin-bottom: 2rem;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; padding: 1rem; background: rgba(255, 71, 87, 0.1); border: 1px solid #ff4757; border-radius: 8px;">
                            <span class="material-symbols-outlined" style="color: #ff4757; font-size: 2rem;">warning</span>
                            <div>
                                <h3 style="color: #ff4757; margin: 0;">Disclaimer: Use Responsibly</h3>
                                <p style="margin: 0; font-size: 0.9rem; color: #ffcccc;">This platform is for educational and authorized security testing purposes only.</p>
                            </div>
                        </div>

                        <h2 style="font-size: 1.5rem; margin: 1.5rem 0 1rem; color: #fff;">1. Information Collection</h2>
                        <p style="margin-bottom: 1rem; line-height: 1.6;">
                            We collect information necessary to provide our security services, including account credentials (hashed), activity logs, and scan configurations.
                        </p>

                        <h2 style="font-size: 1.5rem; margin: 1.5rem 0 1rem; color: #fff;">2. Usage of Data</h2>
                        <p style="margin-bottom: 1rem; line-height: 1.6;">
                            Data collected is used securely to generating reports, analyze vulnerabilities, and improve our threat detection engine. We do not sell your data to third parties.
                        </p>

                        <h2 style="font-size: 1.5rem; margin: 1.5rem 0 1rem; color: #fff;">3. Security</h2>
                        <p style="margin-bottom: 1rem; line-height: 1.6;">
                            We employ enterprise-grade encryption for all sensitive data. However, as a security platform, you acknowledge the inherent risks associated with storing security-sensitive information.
                        </p>

                        <h2 style="font-size: 1.5rem; margin: 1.5rem 0 1rem; color: #fff;">4. Ethical Use</h2>
                        <p style="margin-bottom: 1rem; line-height: 1.6;">
                            By using Aegis, you agree to only scan networks and systems you own or have explicit permission to test. Unauthorized access is strictly prohibited.
                        </p>
                    </div>

                    <p style="text-align: center; color: var(--text-muted);">Last Updated: 2026-02-02</p>
                </div>
            </div>
        `;
    }

    async afterRender() { }
}

export default new PrivacyView();
