import Auth from '../auth.js';
import Utils from '../utils.js';
import Router from '../router.js';

class LoginView {
    async render() {
        return `
            <div style="min-height: 100vh; display: flex; flex-direction: column; position: relative; overflow: hidden;">
                <!-- Animated Background -->
                <div class="hero-gradient" style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; animation: rotateGradient 20s linear infinite;"></div>
                <div style="position: absolute; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(5px);"></div>

                <div class="container" style="display: flex; justify-content: center; align-items: center; min-height: 100vh; position: relative; z-index: 1;">
                    <div class="card glass fade-in" style="width: 100%; max-width: 400px; padding: 3rem 2rem;">
                        <a href="#/" style="display: flex; align-items: center; gap: 0.5rem; text-decoration: none; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 2rem; width: fit-content; transition: color 0.2s;" onmouseover="this.style.color='var(--primary)'" onmouseout="this.style.color='var(--text-muted)'">
                            <span class="material-symbols-outlined" style="font-size: 1rem;">arrow_back</span>
                            Back to Home
                        </a>

                        <!-- Cold Start Warning -->
                        <div id="cold-start-banner" style="background: linear-gradient(135deg, rgba(255,165,0,0.15), rgba(255,165,0,0.05)); border: 1px solid rgba(255,165,0,0.3); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.75rem;">
                            <span class="material-symbols-outlined" style="color: #ffa502; font-size: 1.2rem; flex-shrink: 0;">cloud_sync</span>
                            <span style="font-size: 0.78rem; color: #ccc; line-height: 1.4;">Server may be in <strong style="color: #ffa502;">cold start</strong> mode. First request might take 30–60s. Please be patient.</span>
                        </div>

                        <h2 class="page-title" style="text-align: center; margin-bottom: 0.5rem;">Access System</h2>
                        <p style="text-align: center; color: var(--text-muted); margin-bottom: 2.5rem; font-size: 0.9rem;">Fsociety Terminal Login</p>
                        
                        <form id="login-form">
                             <div style="margin-bottom: 1.5rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">EMAIL ADDRESS</label>
                                <input type="email" id="email" required placeholder="name@protocol.com" style="background: rgba(0,0,0,0.3);">
                            </div>
                            
                            <div style="margin-bottom: 2rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <label style="font-size: 0.85rem; color: var(--text-muted); letter-spacing: 1px;">PASSWORD</label>
                                    <a href="#/forgot-password" style="font-size: 0.8rem; color: var(--primary); text-decoration: none;">Forgot Password?</a>
                                </div>
                                <div style="position: relative; display: flex; align-items: center;">
                                    <input type="password" id="password" required placeholder="••••••••" style="width: 100%; padding-right: 40px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #fff;">
                                    <span class="material-symbols-outlined toggle-password" style="position: absolute; right: 10px; cursor: pointer; color: var(--text-muted); user-select: none; z-index: 10;">visibility</span>
                                </div>
                            </div>
                            
                            <button type="submit" class="btn" id="login-btn" style="width: 100%; padding: 1rem; font-weight: bold; letter-spacing: 2px; display: flex; align-items: center; justify-content: center; gap: 0.75rem;">
                                ACCESS SYSTEM
                            </button>
                        </form>

                        <div style="margin-top: 2rem; text-align: center; font-size: 0.9rem;">
                            <span style="color: var(--text-muted);">New agent? </span>
                            <a href="#/signup" style="color: var(--primary); text-decoration: none; border-bottom: 1px dashed var(--primary);">Initialize Identity</a>
                        </div>
                    </div>
                </div>
            </div>
            <style>
                @keyframes rotateGradient {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                @keyframes spinLoader {
                    to { transform: rotate(360deg); }
                }
                .login-spinner {
                    width: 18px; height: 18px;
                    border: 2px solid rgba(0,0,0,0.2);
                    border-top-color: #000;
                    border-radius: 50%;
                    animation: spinLoader 0.6s linear infinite;
                }
            </style>
        `;
    }

    async afterRender() {
        const passwordInput = document.getElementById('password');
        const toggleBtn = document.querySelector('.toggle-password');

        if (toggleBtn && passwordInput) {
            toggleBtn.onclick = () => {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    toggleBtn.textContent = 'visibility_off';
                } else {
                    passwordInput.type = 'password';
                    toggleBtn.textContent = 'visibility';
                }
            };
        }

        const form = document.getElementById('login-form');
        const loginBtn = document.getElementById('login-btn');

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const emailInput = document.getElementById('email');
                const passwordInput = document.getElementById('password');

                if (!emailInput || !passwordInput) return;

                const email = emailInput.value;
                const password = passwordInput.value;

                // Show loading state
                loginBtn.disabled = true;
                loginBtn.innerHTML = '<div class="login-spinner"></div> CONNECTING TO SERVER...';

                try {
                    const result = await Auth.login(email, password);
                    // If null, the disabled modal is already showing
                    if (result === null) {
                        loginBtn.disabled = false;
                        loginBtn.textContent = 'ACCESS SYSTEM';
                        return;
                    }

                    Utils.showToast('Access Granted', 'success');
                    Router.navigate('/dashboard');
                } catch (error) {
                    loginBtn.disabled = false;
                    loginBtn.textContent = 'ACCESS SYSTEM';
                    Utils.showToast(error.message, 'error');
                }
            });
        }
    }
}

export default new LoginView();
