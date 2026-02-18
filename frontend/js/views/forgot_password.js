import Auth from '../auth.js';
import Utils from '../utils.js';
import Router from '../router.js';

class ForgotPasswordView {
    async render() {
        return `
            <div style="min-height: 100vh; display: flex; flex-direction: column; position: relative; overflow: hidden;">
                <!-- Animated Background -->
                <div class="hero-gradient" style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; animation: rotateGradient 20s linear infinite;"></div>
                <div style="position: absolute; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(5px);"></div>

                <div class="container" style="display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 2rem 0; position: relative; z-index: 1;">
                    <div class="card glass fade-in" style="width: 100%; max-width: 400px; padding: 3rem 2rem;">
                        <h2 class="page-title" style="text-align: center; margin-bottom: 0.5rem; font-size: 1.8rem;">Recovery</h2>
                        <p style="text-align: center; color: var(--text-muted); margin-bottom: 2.5rem; font-size: 0.9rem;">Enter email to receive OTP code.</p>
                        
                        <form id="forgot-form">
                            <div style="margin-bottom: 2rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">EMAIL ADDRESS</label>
                                <input type="email" id="email" required placeholder="aegis@protonmail.com" style="background: rgba(0,0,0,0.3);">
                            </div>
                            
                            <button type="submit" class="btn" style="width: 100%; padding: 1rem; font-weight: bold; letter-spacing: 2px;">SEND OTP CODE</button>
                        </form>

                        <div style="margin-top: 2rem; text-align: center; font-size: 0.9rem;">
                            <a href="#/login" style="color: var(--text-muted); text-decoration: none; transition: color 0.3s;">
                                <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 1rem;">arrow_back</span>
                                Return to Login
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

    async afterRender() {
        const form = document.getElementById('forgot-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const btn = form.querySelector('button');

            try {
                btn.disabled = true;
                btn.innerHTML = '<span class="material-symbols-outlined spin">sync</span> SENDING...';

                await Auth.forgotPassword(email);

                Utils.showToast('OTP sent to your email.', 'success');
                // Navigate to reset page with email
                setTimeout(() => Router.navigate(`/reset-password?email=${encodeURIComponent(email)}`), 1500);
            } catch (error) {
                Utils.showToast(error.message || 'Failed to send OTP', 'error');
                btn.disabled = false;
                btn.textContent = 'SEND OTP CODE';
            }
        });
    }
}

export default new ForgotPasswordView();
