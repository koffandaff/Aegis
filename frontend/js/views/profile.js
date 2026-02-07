import Auth from '../auth.js';
import Api from '../api.js';
import Utils from '../utils.js';
import Components from '../components.js';

class ProfileView {
    async render() {
        const user = JSON.parse(localStorage.getItem('user')) || {};
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar()}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">User Profile</h1>
                    
                    <div style="display: grid; gap: 2rem; max-width: 700px;">
                        <!-- Profile Information Card -->
                        <div class="card glass fade-in">
                            <h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="color: var(--primary);">person</span>
                                Profile Information
                            </h3>
                            <form id="profile-form">
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                                    <div>
                                        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.85rem;">Username</label>
                                        <input type="text" id="username" value="${user.username || ''}" disabled style="opacity: 0.7;">
                                    </div>
                                    <div>
                                        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.85rem;">Email</label>
                                        <input type="email" id="email" value="${user.email || ''}" disabled style="opacity: 0.7;">
                                    </div>
                                </div>
                                <div style="margin-top: 1.5rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.85rem;">Full Name</label>
                                    <input type="text" id="full_name" value="${user.full_name || ''}" placeholder="Your full name">
                                </div>
                                <div style="margin-top: 1.5rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.85rem;">Bio</label>
                                    <textarea id="bio" rows="3" placeholder="Tell us about yourself...">${user.bio || ''}</textarea>
                                </div>
                                <button type="submit" class="btn" style="margin-top: 1.5rem;">
                                    <span class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem;">save</span>
                                    UPDATE PROFILE
                                </button>
                            </form>
                        </div>

                        <!-- Change Password Card -->
                        <div class="card glass fade-in" style="animation-delay: 0.1s;">
                            <h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="color: var(--secondary);">lock</span>
                                Change Password
                            </h3>
                            <form id="password-form">
                                <div style="margin-bottom: 1.5rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.85rem;">Current Password</label>
                                    <div style="position: relative;">
                                        <input type="password" id="current_password" required placeholder="Enter current password">
                                        <button type="button" class="toggle-password" data-target="current_password" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-muted); cursor: pointer;">
                                            <span class="material-symbols-outlined" style="font-size: 1.2rem;">visibility</span>
                                        </button>
                                    </div>
                                </div>
                                <div style="margin-bottom: 1.5rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.85rem;">New Password</label>
                                    <div style="position: relative;">
                                        <input type="password" id="new_password" required minlength="8" placeholder="Enter new password (min 8 characters)">
                                        <button type="button" class="toggle-password" data-target="new_password" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-muted); cursor: pointer;">
                                            <span class="material-symbols-outlined" style="font-size: 1.2rem;">visibility</span>
                                        </button>
                                    </div>
                                </div>
                                <div style="margin-bottom: 1.5rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.85rem;">Confirm New Password</label>
                                    <div style="position: relative;">
                                        <input type="password" id="confirm_password" required placeholder="Confirm new password">
                                        <button type="button" class="toggle-password" data-target="confirm_password" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-muted); cursor: pointer;">
                                            <span class="material-symbols-outlined" style="font-size: 1.2rem;">visibility</span>
                                        </button>
                                    </div>
                                </div>
                                <div id="password-strength" style="margin-bottom: 1rem; display: none;">
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <div style="flex: 1; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden;">
                                            <div id="strength-bar" style="height: 100%; width: 0%; transition: all 0.3s;"></div>
                                        </div>
                                        <span id="strength-text" style="font-size: 0.75rem; color: var(--text-muted);"></span>
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-secondary" style="margin-top: 0.5rem;">
                                    <span class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem;">key</span>
                                    CHANGE PASSWORD
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            ${Components.renderFloatingChat()}
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());

        // Profile form handler
        const profileForm = document.getElementById('profile-form');
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fullName = document.getElementById('full_name').value;
            const bio = document.getElementById('bio').value;

            try {
                // Try API first
                await Api.put('/user/profile', { full_name: fullName, bio });

                // Update local storage
                const user = JSON.parse(localStorage.getItem('user'));
                user.full_name = fullName;
                user.bio = bio;
                localStorage.setItem('user', JSON.stringify(user));

                Utils.showToast('Profile Updated', 'success');
            } catch (error) {
                // Fallback to local storage if API fails
                const user = JSON.parse(localStorage.getItem('user'));
                user.full_name = fullName;
                user.bio = bio;
                localStorage.setItem('user', JSON.stringify(user));

                Utils.showToast('Profile Updated (Local)', 'success');
            }
        });

        // Password form handler
        const passwordForm = document.getElementById('password-form');
        passwordForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const currentPassword = document.getElementById('current_password').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            // Validate passwords match
            if (newPassword !== confirmPassword) {
                Utils.showToast('New passwords do not match', 'error');
                return;
            }

            // Validate password length
            if (newPassword.length < 8) {
                Utils.showToast('Password must be at least 8 characters', 'error');
                return;
            }

            try {
                await Api.put('/user/password', {
                    current_password: currentPassword,
                    new_password: newPassword
                });

                Utils.showToast('Password changed successfully', 'success');

                // Clear form
                document.getElementById('current_password').value = '';
                document.getElementById('new_password').value = '';
                document.getElementById('confirm_password').value = '';
                document.getElementById('password-strength').style.display = 'none';
            } catch (error) {
                Utils.showToast(error.message || 'Failed to change password', 'error');
            }
        });

        // Toggle password visibility
        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.dataset.target;
                const input = document.getElementById(targetId);
                const icon = btn.querySelector('.material-symbols-outlined');

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.textContent = 'visibility_off';
                } else {
                    input.type = 'password';
                    icon.textContent = 'visibility';
                }
            });
        });

        // Password strength indicator
        const newPasswordInput = document.getElementById('new_password');
        newPasswordInput.addEventListener('input', (e) => {
            const password = e.target.value;
            const strengthContainer = document.getElementById('password-strength');
            const strengthBar = document.getElementById('strength-bar');
            const strengthText = document.getElementById('strength-text');

            if (password.length === 0) {
                strengthContainer.style.display = 'none';
                return;
            }

            strengthContainer.style.display = 'block';

            // Calculate strength
            let strength = 0;
            if (password.length >= 8) strength += 25;
            if (password.length >= 12) strength += 15;
            if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 20;
            if (/\d/.test(password)) strength += 20;
            if (/[^a-zA-Z0-9]/.test(password)) strength += 20;

            // Set bar and text
            strengthBar.style.width = `${strength}%`;

            if (strength < 40) {
                strengthBar.style.backgroundColor = '#e74c3c';
                strengthText.textContent = 'Weak';
                strengthText.style.color = '#e74c3c';
            } else if (strength < 70) {
                strengthBar.style.backgroundColor = '#ffa502';
                strengthText.textContent = 'Medium';
                strengthText.style.color = '#ffa502';
            } else {
                strengthBar.style.backgroundColor = '#2ed573';
                strengthText.textContent = 'Strong';
                strengthText.style.color = '#2ed573';
            }
        });
    }
}

export default new ProfileView();
