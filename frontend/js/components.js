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
            <div class="glass" style="width: 250px; height: 100%; padding: 2rem 1rem; flex-shrink: 0; display: flex; flex-direction: column; gap: 0.5rem;">
                ${links.map(link => `
                    <a href="#/${link.path}" class="${activePath.includes(link.path) ? 'btn' : 'btn-outline'}" 
                       style="text-align: left; ${activePath.includes(link.path) ? '' : 'border: none; color: var(--text-muted);'} display: flex; align-items: center;">
                       <span class="material-symbols-outlined" style="margin-right: 0.75rem; font-size: 1.25rem;">${link.icon}</span> ${link.label}
                    </a>
                `).join('')}
            </div>
        `;
    }

    static renderNavbar() {
        const user = JSON.parse(localStorage.getItem('user')) || { username: 'Guest' };
        return `
            <div class="glass" style="position: fixed; top: 0; left: 0; width: 100%; height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 2rem; z-index: 100;">
                <a href="#/dashboard" style="text-decoration: none; display: flex; align-items: center; gap: 0rem;">
                    <span class="material-symbols-outlined" style="color: #fff; font-size: 1.8rem; margin-right: 0.5rem; text-shadow: 0 0 15px rgba(255,255,255,0.4);">security</span>
                    <span style="font-size: 1.4rem; font-weight: 800; color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.3); font-family: 'JetBrains Mono', monospace; letter-spacing: 1px;">Fsociety</span>
                    <span style="color: #fff; animation: blink 1s step-end infinite; font-weight: 300; text-shadow: 0 0 10px rgba(255,255,255,0.5);">_</span>
                </a>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <a href="#/profile" class="btn-outline" style="padding: 0.25rem 0.5rem; display: flex; align-items: center; gap: 0.5rem; border: none; color: var(--text-muted);">
                        <span class="material-symbols-outlined">account_circle</span>
                        <span style="font-size: 0.9rem;">${user.username}</span>
                    </a>
                    ${user.role === 'admin' ? '<span class="badge" style="background: var(--secondary); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; color: #fff;">ADMIN</span>' : ''}
                    <button id="logout-btn" class="btn-outline" style="padding: 0.25rem 0.75rem; font-size: 0.8rem; border-color: rgba(255,255,255,0.2);">LOGOUT</button>
                </div>
            </div>
        `;
    }

    static renderFloatingChat() {
        // Don't show on the chat page itself
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
}

export default Components;


