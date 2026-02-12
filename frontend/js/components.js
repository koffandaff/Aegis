class Components {
    static renderSidebar(activePath = '') {
        const user = JSON.parse(localStorage.getItem('user')) || { role: 'user' };
        const links = [
            { path: 'dashboard', label: 'Dashboard', icon: 'grid_view' },
            { path: 'chat', label: 'AI Assistant', icon: 'smart_toy' },
            { path: 'footprint', label: 'Digital Footprint', icon: 'fingerprint' },
            { path: 'scan', label: 'Network Scan', icon: 'radar' },
            { path: 'security', label: 'Security Audit', icon: 'security' },
            { path: 'phishing', label: 'Phishing Detector', icon: 'phishing' },
            { path: 'files', label: 'File Analysis', icon: 'folder_open' },
            { path: 'vpn', label: 'VPN Configs', icon: 'vpn_lock' },
            { path: 'history', label: 'Operation History', icon: 'history' },
        ];

        if (user.role === 'admin') {
            links.push({ path: 'admin', label: 'Admin Panel', icon: 'admin_panel_settings' });
        }

        return `
            <div id="sidebar-overlay" class="sidebar-overlay" onclick="toggleSidebar()"></div>
            <div id="app-sidebar" class="glass app-sidebar">
                <div class="sidebar-close-row">
                    <button class="sidebar-close-btn" onclick="toggleSidebar()">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                </div>
                ${links.map(link => `
                    <a href="#/${link.path}" class="${activePath.includes(link.path) ? 'btn' : 'btn-outline'}" 
                       style="text-align: left; ${activePath.includes(link.path) ? '' : 'border: none; color: var(--text-muted);'} display: flex; align-items: center;"
                       onclick="if(window.innerWidth <= 768) toggleSidebar()">
                       <span class="material-symbols-outlined" style="margin-right: 0.75rem; font-size: 1.25rem;">${link.icon}</span> ${link.label}
                    </a>
                `).join('')}
                
                <!-- Mobile Only: Profile & Logout -->
                <div class="mobile-only" style="margin-top: auto; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); flex-direction: column; gap: 0.5rem;">
                    ${user.username !== 'Guest' ? `
                        <div onclick="window.location.hash='#/profile'; toggleSidebar()" style="display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem; color: var(--text-muted); cursor: pointer;">
                            <span class="material-symbols-outlined">account_circle</span>
                            <span>${user.username} <span style="font-size: 0.7rem; opacity: 0.7;">(${user.role})</span></span>
                        </div>
                        <button onclick="localStorage.removeItem('access_token'); localStorage.removeItem('user'); window.location.reload();" class="btn-outline" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 0.5rem; border-color: var(--danger); color: var(--danger);">
                            <span class="material-symbols-outlined">logout</span> LOGOUT
                        </button>
                    ` : `
                        <button onclick="window.location.hash='#/login'; toggleSidebar()" class="btn" style="width: 100%; text-align: center;">LOGIN</button>
                        <button onclick="window.location.hash='#/signup'; toggleSidebar()" class="btn-outline" style="width: 100%; text-align: center;">SIGN UP</button>
                    `}
                </div>
            </div>
        `;
    }

    static renderNavbar() {
        const user = JSON.parse(localStorage.getItem('user')) || { username: 'Guest' };
        return `
            <div class="glass app-navbar">
                <div style="display: flex; align-items: center; gap: 0; white-space: nowrap;">
                    ${user.username !== 'Guest' ? `
                        <button id="hamburger-btn" class="hamburger-btn" onclick="toggleSidebar()">
                            <span class="material-symbols-outlined">menu</span>
                        </button>
                    ` : ''}
                    <a href="#/" style="text-decoration: none; display: flex; align-items: center; gap: 0;">
                        <span class="material-symbols-outlined" style="color: #fff; font-size: 1.8rem; margin-right: 0.2rem; text-shadow: 0 0 15px rgba(255,255,255,0.4);">security</span>
                        <span class="navbar-brand-text" style="font-size: 1.2rem; font-weight: 800; color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.3); font-family: 'JetBrains Mono', monospace; letter-spacing: 1px;">Aegis</span>
                        <span style="color: #fff; animation: blink 1s step-end infinite; font-weight: 300; text-shadow: 0 0 10px rgba(255,255,255,0.5);">_</span>
                    </a>
                </div>
                <!-- Navbar Actions (Desktop Only for Guest) -->
                <div class="${user.username !== 'Guest' ? 'navbar-actions' : 'navbar-actions desktop-only'}">
                    ${user.username !== 'Guest' ? `
                        <a href="#/profile" class="btn-outline navbar-profile-link" style="padding: 0.25rem 0.5rem; display: flex; align-items: center; gap: 0.5rem; border: none; color: var(--text-muted);">
                            <span class="material-symbols-outlined">account_circle</span>
                            <span class="navbar-username">${user.username}</span>
                        </a>
                        ${user.role === 'admin' ? '<span class="badge" style="background: var(--secondary); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; color: #fff;">ADMIN</span>' : ''}
                        <button id="logout-btn" class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.8rem; border-color: rgba(255,255,255,0.2);">LOGOUT</button>
                    ` : `
                        <a href="#/login" class="btn" style="padding: 0.4rem 1.2rem; font-size: 0.85rem;">LOGIN</a>
                        <a href="#/signup" class="btn-outline" style="padding: 0.4rem 1.2rem; font-size: 0.85rem;">SIGN UP</a>
                    `}
                </div>
            </div>
        `;
    }

    static renderFloatingChat() {
        if (window.location.hash.includes('#/chat')) return '';

        return `
            <a href="#/chat" id="floating-chat-link" style="position: fixed; bottom: 2rem; right: 2rem; z-index: 1000; text-decoration: none;">
                <button style="width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); border: none; cursor: pointer; box-shadow: 0 4px 20px rgba(0, 255, 157, 0.4); display: flex; align-items: center; justify-content: center; transition: transform 0.3s, box-shadow 0.3s;"
                        onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                    <span class="material-symbols-outlined" style="font-size: 1.8rem; color: #000;">smart_toy</span>
                </button>
            </a>
        `;
    }

    static renderProgressBar(id = 'global-progress') {
        return `
            <div id="${id}-container" class="fs-progress-container">
                <div id="${id}-bar" class="fs-progress-bar"></div>
            </div>
            <div id="${id}-text" style="text-align: center; margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-muted); display: none;">Initializing...</div>
        `;
    }

    static renderModal(id, title, content, actions) {
        return `
            <div id="${id}" class="modal-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); z-index: 1000; align-items: center; justify-content: center;">
                <div class="card glass modal-content" style="max-width: 500px; width: 90%; animation: slideIn 0.3s ease;">
                    <h3 style="margin-bottom: 1rem; color: var(--primary); display: flex; align-items: center; gap: 0.5rem;">
                        ${title}
                    </h3>
                    <div style="margin-bottom: 1.5rem; color: var(--text-main); line-height: 1.6;">
                        ${content}
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 1rem;">
                        ${actions}
                    </div>
                </div>
            </div>
        `;
    }

    static showModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    static hideModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.style.display = 'none';
        }
    }
}

// Global sidebar toggle function
window.toggleSidebar = function () {
    const sidebar = document.getElementById('app-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }
};

export default Components;
