class TermsView {
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
                    <h1 style="font-size: 2.5rem; margin-bottom: 2rem; color: var(--primary);">Terms of Service</h1>
                    
                    <div class="card glass" style="padding: 2rem; margin-bottom: 2rem;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; padding: 1rem; background: rgba(255, 189, 46, 0.1); border: 1px solid #ffbd2e; border-radius: 8px;">
                            <span class="material-symbols-outlined" style="color: #ffbd2e; font-size: 2rem;">gavel</span>
                            <div>
                                <h3 style="color: #ffbd2e; margin: 0;">Legal Agreement</h3>
                                <p style="margin: 0; font-size: 0.9rem; color: #ffeaa7;">By accessing Aegis, you agree to these binding terms.</p>
                            </div>
                        </div>

                        <h2 style="font-size: 1.5rem; margin: 1.5rem 0 1rem; color: #fff;">1. Acceptance of Terms</h2>
                        <p style="margin-bottom: 1rem; line-height: 1.6;">
                            Aegis provides security tools for authorized use only. Illegal activities performed using our tools will not be tolerated and may be reported to authorities.
                        </p>

                        <h2 style="font-size: 1.5rem; margin: 1.5rem 0 1rem; color: #fff;">2. Use Safely</h2>
                        <p style="margin-bottom: 1rem; line-height: 1.6;">
                            <strong>Use It Safely.</strong> You agree to take full responsibility for your actions. Aegis is not liable for any damage caused by misuse of our scanning or reconnaissance tools.
                        </p>

                        <h2 style="font-size: 1.5rem; margin: 1.5rem 0 1rem; color: #fff;">3. Account Termination</h2>
                        <p style="margin-bottom: 1rem; line-height: 1.6;">
                            We reserve the right to terminate accounts found to be engaging in malicious activities, including but not limited to unauthorized testing, DoS attacks, or data theft.
                        </p>

                        <h2 style="font-size: 1.5rem; margin: 1.5rem 0 1rem; color: #fff;">4. Disclaimer of Warranties</h2>
                        <p style="margin-bottom: 1rem; line-height: 1.6;">
                            The service is provided "as is". We make no warranties regarding the accuracy or completeness of scan results.
                        </p>
                    </div>

                    <p style="text-align: center; color: var(--text-muted);">Effective Date: 2026-02-02</p>
                </div>
            </div>
        `;
    }

    async afterRender() { }
}

export default new TermsView();
