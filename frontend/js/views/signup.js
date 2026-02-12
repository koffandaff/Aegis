import Auth from '../auth.js';
import Utils from '../utils.js';
import Router from '../router.js';

class SignupView {
    async render() {
        return `
            <div style="min-height: 100vh; display: flex; flex-direction: column; position: relative; overflow: hidden;">
                <!-- Animated Background -->
                <div class="hero-gradient" style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; animation: rotateGradient 20s linear infinite;"></div>
                <div style="position: absolute; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(5px);"></div>

                <div class="container" style="display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 2rem 0; position: relative; z-index: 1;">
                    <div class="card glass fade-in" style="width: 100%; max-width: 450px; padding: 3rem 2rem;">
                        <a href="#/" style="display: flex; align-items: center; gap: 0.5rem; text-decoration: none; color: var(--text-muted); font-size: 0.8rem; margin-bottom: 2rem; width: fit-content; transition: color 0.2s;" onmouseover="this.style.color='var(--primary)'" onmouseout="this.style.color='var(--text-muted)'">
                            <span class="material-symbols-outlined" style="font-size: 1rem;">arrow_back</span>
                            Back to Home
                        </a>

                        <!-- Cold Start Warning -->
                        <div id="cold-start-banner" style="background: linear-gradient(135deg, rgba(255,165,0,0.15), rgba(255,165,0,0.05)); border: 1px solid rgba(255,165,0,0.3); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.75rem;">
                            <span class="material-symbols-outlined" style="color: #ffa502; font-size: 1.2rem; flex-shrink: 0;">cloud_sync</span>
                            <span style="font-size: 0.78rem; color: #ccc; line-height: 1.4;">Server may be in <strong style="color: #ffa502;">cold start</strong> mode. First request might take 30–60s. Please be patient.</span>
                        </div>

                        <h2 class="page-title" style="text-align: center; margin-bottom: 0.5rem;">Join Fsociety</h2>
                        <p style="text-align: center; color: var(--text-muted); margin-bottom: 2.5rem; font-size: 0.9rem;">Initialize anonymous connection.</p>
                        
                        <form id="signup-form">
                            <div style="margin-bottom: 1rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">USERNAME</label>
                                <input type="text" id="username" required placeholder="elliot_alderson" style="background: rgba(0,0,0,0.3);">
                            </div>

                            <div style="margin-bottom: 1rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">EMAIL ADDRESS</label>
                                <input type="email" id="email" required placeholder="fsociety@protonmail.com" style="background: rgba(0,0,0,0.3);">
                            </div>

                            <div style="margin-bottom: 1.5rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">FULL NAME (FOR IDENTITY)</label>
                                <input type="text" id="full_name" placeholder="Optional" style="background: rgba(0,0,0,0.3);">
                            </div>

                            <div style="margin-bottom: 1rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">SECURITY TOKEN (PASSWORD)</label>
                                <div style="position: relative; display: flex; align-items: center;">
                                    <input type="password" id="password" required placeholder="••••••••" style="width: 100%; padding-right: 40px; background: rgba(0,0,0,0.3);">
                                    <span class="material-symbols-outlined toggle-password" style="position: absolute; right: 10px; cursor: pointer; color: var(--text-muted); user-select: none; z-index: 10;">visibility</span>
                                </div>
                                
                                <div style="margin-top: 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.75rem; color: var(--text-muted);">
                                    <div id="req-len" class="req-item"><span class="icon">○</span> 8+ Chars</div>
                                    <div id="req-num" class="req-item"><span class="icon">○</span> Number</div>
                                    <div id="req-cap" class="req-item"><span class="icon">○</span> Uppercase</div>
                                    <div id="req-sym" class="req-item"><span class="icon">○</span> Symbol</div>
                                </div>
                            </div>

                            <div style="margin-bottom: 2.5rem;">
                                <label style="display: block; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">VERIFY TOKEN</label>
                                <input type="password" id="confirm-password" required placeholder="••••••••" style="background: rgba(0,0,0,0.3);">
                            </div>
                            
                            <div style="margin-bottom: 2rem; display: flex; gap: 0.5rem; align-items: start;">
                                <input type="checkbox" id="privacy-check" style="margin-top: 5px;">
                                <label for="privacy-check" style="font-size: 0.85rem; color: var(--text-muted); cursor: pointer;">
                                    I agree to the <a href="#/privacy" target="_blank" style="color: var(--primary);">Privacy Policy</a> and acknowledge that this tool is for educational purposes only.
                                </label>
                            </div>
                            
                            <button type="submit" class="btn" id="signup-btn" style="width: 100%; padding: 1rem; font-weight: bold; letter-spacing: 2px; display: flex; align-items: center; justify-content: center; gap: 0.75rem;">
                                INITIALIZE IDENTITY
                            </button>
                        </form>

                        <div style="margin-top: 2rem; text-align: center; font-size: 0.9rem;">
                            <span style="color: var(--text-muted);">Already initialized? </span>
                            <a href="#/login" style="color: var(--primary); text-decoration: none; border-bottom: 1px dashed var(--primary);">Login to Terminal</a>
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
                .signup-spinner {
                    width: 18px; height: 18px;
                    border: 2px solid rgba(0,0,0,0.2);
                    border-top-color: #000;
                    border-radius: 50%;
                    animation: spinLoader 0.6s linear infinite;
                }
                .req-item { display: flex; align-items: center; gap: 0.4rem; transition: all 0.3s; opacity: 0.6; }
                .req-item.valid { color: var(--primary); opacity: 1; }
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

        // Strength checker
        passwordInput.addEventListener('keyup', () => {
            const password = passwordInput.value;
            const updateReq = (id, valid) => {
                const el = document.getElementById(id);
                if (valid) {
                    el.classList.add('valid');
                    el.querySelector('.icon').textContent = '✓';
                } else {
                    el.classList.remove('valid');
                    el.querySelector('.icon').textContent = '○';
                }
            };

            updateReq('req-len', password.length >= 8);
            updateReq('req-num', /[0-9]/.test(password));
            updateReq('req-cap', /[A-Z]/.test(password));
            updateReq('req-sym', /[^a-zA-Z0-9]/.test(password));
        });

        const form = document.getElementById('signup-form');
        const signupBtn = document.getElementById('signup-btn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const privacyCheck = document.getElementById('privacy-check');

            if (!privacyCheck.checked) {
                Utils.showToast('Please agree to the Privacy Policy', 'warning');
                return;
            }

            if (password !== confirmPassword) {
                Utils.showToast('Passwords do not match', 'warning');
                return;
            }

            const userData = {
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                full_name: document.getElementById('full_name').value,
                password: password
            };

            // Show loading state
            signupBtn.disabled = true;
            signupBtn.innerHTML = '<div class="signup-spinner"></div> CREATING IDENTITY...';

            try {
                await Auth.signup(userData);
                Utils.showToast('Account Created. Please Login.', 'success');
                Router.navigate('/login');
            } catch (error) {
                signupBtn.disabled = false;
                signupBtn.textContent = 'INITIALIZE IDENTITY';
                Utils.showToast(error.message, 'error');
            }
        });
    }
}

export default new SignupView();
