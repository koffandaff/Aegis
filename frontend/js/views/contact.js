class ContactView {
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

                <div class="container" style="max-width: 600px; margin: 0 auto; color: #e0e0e0; display: flex; flex-direction: column; align-items: center; text-align: center;">
                    <h1 style="font-size: 3rem; margin-bottom: 1rem; color: var(--primary);">Contact Us</h1>
                    <p style="font-size: 1.1rem; color: var(--text-muted); margin-bottom: 3rem;">
                        Have questions about our security platform?
                    </p>
                    
                    <div class="card glass" style="padding: 3rem; width: 100%; position: relative; overflow: hidden;">
                        <div class="hero-gradient" style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; opacity: 0.1; animation: rotateGradient 10s linear infinite;"></div>
                        
                        <div style="position: relative; z-index: 1;">
                            <span class="material-symbols-outlined" style="font-size: 4rem; color: var(--primary); margin-bottom: 1.5rem;">mark_email_unread</span>
                            
                            <h2 style="margin-bottom: 1rem;">Get in Touch</h2>
                            <p style="color: var(--text-muted); margin-bottom: 2rem;">
                                For support, security reports, or business inquiries, please reach out to our team directly.
                            </p>
                            
                            <a href="mailto:reconauto@gmail.com" style="display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(255,255,255,0.1); padding: 1rem 2rem; border-radius: 50px; text-decoration: none; color: #fff; border: 1px solid rgba(255,255,255,0.2); transition: all 0.3s;">
                                <span class="material-symbols-outlined">email</span>
                                <span style="font-size: 1.1rem; font-weight: 500;">reconauto@gmail.com</span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            <style>
                @keyframes rotateGradient {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            </style>
        `;
    }

    async afterRender() { }
}

export default new ContactView();
