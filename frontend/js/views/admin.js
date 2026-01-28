import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class AdminView {
    constructor() {
        this.users = [];
        this.activities = [];
        this.charts = {};
        this.intervals = [];
    }

    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('admin')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto; background: linear-gradient(135deg, rgba(0,0,0,0.3) 0%, transparent 100%);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                        <h1 class="page-title fade-in" style="margin: 0;">Admin Command Center</h1>
                        <button id="export-btn" class="btn-outline" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem;">
                            <span class="material-symbols-outlined">download</span>
                            Export Data
                        </button>
                    </div>
                    
                    <div style="display: grid; gap: 2rem; max-width: 1400px;">
                        
                        <!-- Stats Overview Cards -->
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
                            <div class="card glass fade-in stat-card-hover" style="border-left: 3px solid var(--primary);">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(0, 255, 157, 0.1); display: flex; align-items: center; justify-content: center;">
                                        <span class="material-symbols-outlined" style="color: var(--primary); font-size: 1.5rem;">group</span>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Total Users</div>
                                        <div id="stat-users" style="font-size: 1.75rem; font-weight: bold; color: var(--primary); font-family: 'JetBrains Mono';">-</div>
                                    </div>
                                </div>
                            </div>
                            <div class="card glass fade-in stat-card-hover" style="animation-delay: 0.1s; border-left: 3px solid var(--secondary);">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(255, 165, 2, 0.1); display: flex; align-items: center; justify-content: center;">
                                        <span class="material-symbols-outlined" style="color: var(--secondary); font-size: 1.5rem;">person_check</span>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Active Users</div>
                                        <div id="stat-active" style="font-size: 1.75rem; font-weight: bold; color: var(--secondary); font-family: 'JetBrains Mono';">-</div>
                                    </div>
                                </div>
                            </div>
                            <div class="card glass fade-in stat-card-hover" style="animation-delay: 0.2s; border-left: 3px solid #3498db;">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(52, 152, 219, 0.1); display: flex; align-items: center; justify-content: center;">
                                        <span class="material-symbols-outlined" style="color: #3498db; font-size: 1.5rem;">radar</span>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Total Scans</div>
                                        <div id="stat-scans" style="font-size: 1.75rem; font-weight: bold; color: #3498db; font-family: 'JetBrains Mono';">-</div>
                                    </div>
                                </div>
                            </div>
                            <div class="card glass fade-in stat-card-hover" style="animation-delay: 0.3s; border-left: 3px solid #9b59b6;">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(155, 89, 182, 0.1); display: flex; align-items: center; justify-content: center;">
                                        <span class="material-symbols-outlined" style="color: #9b59b6; font-size: 1.5rem;">phishing</span>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Phishing Checks</div>
                                        <div id="stat-phishing" style="font-size: 1.75rem; font-weight: bold; color: #9b59b6; font-family: 'JetBrains Mono';">-</div>
                                    </div>
                                </div>
                            </div>
                            <div class="card glass fade-in stat-card-hover" style="animation-delay: 0.4s; border-left: 3px solid #e74c3c;">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(231, 76, 60, 0.1); display: flex; align-items: center; justify-content: center;">
                                        <span class="material-symbols-outlined" style="color: #e74c3c; font-size: 1.5rem;">vpn_lock</span>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">VPN Configs</div>
                                        <div id="stat-vpn" style="font-size: 1.75rem; font-weight: bold; color: #e74c3c; font-family: 'JetBrains Mono';">-</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Charts Row -->
                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem;">
                            <!-- Usage Over Time Chart -->
                            <div class="card glass fade-in" style="animation-delay: 0.3s;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                                    <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                                        <span class="material-symbols-outlined" style="color: var(--primary);">trending_up</span>
                                        Platform Usage Analytics
                                    </h3>
                                    <select id="chart-period" style="padding: 0.3rem 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; color: #fff; font-size: 0.8rem;">
                                        <option value="7">Last 7 Days</option>
                                        <option value="30" selected>Last 30 Days</option>
                                        <option value="90">Last 90 Days</option>
                                    </select>
                                </div>
                                <div style="height: 280px;">
                                    <canvas id="usage-chart"></canvas>
                                </div>
                            </div>

                            <!-- Activity Distribution -->
                            <div class="card glass fade-in" style="animation-delay: 0.4s;">
                                <h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined" style="color: var(--secondary);">pie_chart</span>
                                    Activity Distribution
                                </h3>
                                <div style="height: 280px;">
                                    <canvas id="activity-chart"></canvas>
                                </div>
                            </div>
                        </div>

                        <!-- Activity Logs & User Management Row -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                            
                            <!-- Recent Activity Logs -->
                            <div class="card glass fade-in" style="animation-delay: 0.5s;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                                    <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                                        <span class="material-symbols-outlined" style="color: #3498db;">history</span>
                                        Live Activity Feed
                                    </h3>
                                    <div style="display: flex; gap: 0.5rem;">
                                        <select id="activity-filter" style="padding: 0.3rem 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; color: #fff; font-size: 0.75rem;">
                                            <option value="">All Actions</option>
                                            <option value="login">Logins</option>
                                            <option value="logout">Logouts</option>
                                            <option value="signup">Signups</option>
                                            <option value="scan">Network Scans</option>
                                            <option value="ssl_scan">SSL Scans</option>
                                            <option value="phishing_check">Phishing</option>
                                            <option value="hash_check">Malware</option>
                                            <option value="footprint">Footprint</option>
                                            <option value="chat">Chat</option>
                                            <option value="vpn_generate">VPN</option>
                                        </select>
                                        <button id="refresh-activities" class="btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.7rem;">
                                            <span class="material-symbols-outlined" style="font-size: 1rem;">refresh</span>
                                        </button>
                                    </div>
                                </div>
                                <div id="activity-logs" style="max-height: 400px; overflow-y: auto;">
                                    <p style="color: var(--text-muted); text-align: center;">Loading activities...</p>
                                </div>
                            </div>

                            <!-- User Management -->
                            <div class="card glass fade-in" style="animation-delay: 0.6s;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                                    <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                                        <span class="material-symbols-outlined" style="color: #e74c3c;">manage_accounts</span>
                                        User Management
                                    </h3>
                                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                                        <input type="text" id="user-search" placeholder="Search users..." style="padding: 0.3rem 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; color: #fff; font-size: 0.8rem; width: 150px;">
                                    </div>
                                </div>
                                <div id="users-table" style="max-height: 400px; overflow-y: auto;">
                                    <p style="color: var(--text-muted); text-align: center;">Loading users...</p>
                                </div>
                            </div>
                        </div>

                        <!-- System Status -->
                        <div class="card glass fade-in" style="animation-delay: 0.7s;">
                            <h3 style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="color: #2ed573;">memory</span>
                                System Health Monitor
                            </h3>
                            <div id="system-info" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                                <p style="color: var(--text-muted);">Loading system info...</p>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
            ${Components.renderFloatingChat()}
            <style>
                .stat-card-hover { transition: all 0.3s ease; }
                .stat-card-hover:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
                .activity-item { padding: 0.75rem; border-radius: 8px; background: rgba(0,0,0,0.2); margin-bottom: 0.5rem; border-left: 3px solid var(--primary); transition: all 0.2s; }
                .activity-item:hover { background: rgba(0,0,0,0.3); }
                .user-row { padding: 0.75rem; border-radius: 8px; background: rgba(0,0,0,0.2); margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between; transition: all 0.2s; }
                .user-row:hover { background: rgba(0,0,0,0.3); }
                .action-btn { padding: 0.25rem 0.5rem; font-size: 0.7rem; border-radius: 4px; cursor: pointer; transition: all 0.2s; }
            </style>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());

        // Load all data
        await Promise.all([
            this.loadStats(),
            this.loadUsers(),
            this.loadActivities(),
            this.loadSystemInfo()
        ]);

        // Initialize charts
        this.initCharts();

        // Event listeners
        document.getElementById('export-btn').addEventListener('click', () => this.exportData());
        document.getElementById('refresh-activities').addEventListener('click', () => this.loadActivities());
        document.getElementById('activity-filter').addEventListener('change', (e) => this.loadActivities(e.target.value));
        document.getElementById('user-search').addEventListener('input', (e) => this.filterUsers(e.target.value));
        document.getElementById('chart-period').addEventListener('change', () => this.initCharts());

        // Setup live polling intervals
        this.startLiveUpdates();
    }

    startLiveUpdates() {
        // Clear any existing intervals
        this.stopLiveUpdates();

        // Activities - refresh every 10 seconds
        this.intervals.push(setInterval(() => {
            const filter = document.getElementById('activity-filter')?.value || '';
            this.loadActivities(filter);
        }, 10000));

        // System health - refresh every 5 seconds
        this.intervals.push(setInterval(() => {
            this.loadSystemInfo();
        }, 5000));

        // Stats - refresh every 30 seconds
        this.intervals.push(setInterval(() => {
            this.loadStats();
            this.loadUsers();
        }, 30000));

        // Cleanup on navigation
        window.addEventListener('hashchange', () => this.stopLiveUpdates(), { once: true });
    }

    stopLiveUpdates() {
        this.intervals.forEach(interval => clearInterval(interval));
        this.intervals = [];
    }

    async loadStats() {
        try {
            const stats = await Api.get('/admin/stats');
            if (stats) {
                document.getElementById('stat-users').textContent = stats.total_users || 0;
                document.getElementById('stat-active').textContent = stats.active_users || 0;
                document.getElementById('stat-scans').textContent = stats.total_scans || 0;
                document.getElementById('stat-phishing').textContent = stats.total_phishing_checks || 0;
                document.getElementById('stat-vpn').textContent = stats.total_vpn_configs || 0;
            }
        } catch (e) {
            console.error('Failed to load stats:', e);
        }
    }

    async loadUsers() {
        try {
            const response = await Api.get('/admin/users?limit=50');
            this.users = response?.users || [];
            this.renderUsers(this.users);
        } catch (e) {
            console.error('Failed to load users:', e);
            document.getElementById('users-table').innerHTML = '<p style="color: #ff4757; text-align: center;">Failed to load users</p>';
        }
    }

    renderUsers(users) {
        const container = document.getElementById('users-table');

        if (users && users.length > 0) {
            container.innerHTML = users.map(user => `
                <div class="user-row">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); display: flex; align-items: center; justify-content: center; font-weight: bold; color: #000;">
                            ${(user.username || user.email || 'U').charAt(0).toUpperCase()}
                        </div>
                        <div>
                            <div style="font-weight: 600; color: #fff;">${user.username || 'No username'}</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted);">${user.email}</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span class="badge" style="background: ${user.role === 'admin' ? 'var(--secondary)' : 'rgba(255,255,255,0.1)'}; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.7rem; color: ${user.role === 'admin' ? '#000' : '#fff'};">${user.role}</span>
                        <span style="font-size: 0.75rem; color: ${user.is_active ? 'var(--primary)' : '#ff4757'};">● ${user.is_active ? 'Active' : 'Inactive'}</span>
                        <button class="btn-outline action-btn" onclick="adminView.toggleUserStatus('${user.id}', ${!user.is_active})">
                            ${user.is_active ? 'Disable' : 'Enable'}
                        </button>
                        <button class="btn-outline action-btn" style="border-color: #ff4757; color: #ff4757;" onclick="adminView.deleteUser('${user.id}')">
                            Delete
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No users found</p>';
        }
    }

    filterUsers(query) {
        const filtered = this.users.filter(user =>
            (user.username || '').toLowerCase().includes(query.toLowerCase()) ||
            (user.email || '').toLowerCase().includes(query.toLowerCase())
        );
        this.renderUsers(filtered);
    }

    async toggleUserStatus(userId, newStatus) {
        try {
            await Api.put(`/admin/users/${userId}`, { is_active: newStatus });
            Utils.showToast(`User ${newStatus ? 'enabled' : 'disabled'}`, 'success');
            await this.loadUsers();
        } catch (e) {
            Utils.showToast('Failed to update user', 'error');
        }
    }

    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;

        try {
            await Api.delete(`/admin/users/${userId}`);
            Utils.showToast('User deleted successfully', 'success');
            await this.loadUsers();
            await this.loadStats();
        } catch (e) {
            Utils.showToast('Failed to delete user', 'error');
        }
    }

    async loadActivities(actionFilter = '') {
        try {
            let url = '/admin/activities?limit=30';
            if (actionFilter) url += `&action=${actionFilter}`;

            const response = await Api.get(url);
            this.activities = response?.activities || [];
            this.renderActivities();
        } catch (e) {
            console.error('Failed to load activities:', e);
            document.getElementById('activity-logs').innerHTML = '<p style="color: #ff4757; text-align: center;">Failed to load activities</p>';
        }
    }

    renderActivities() {
        const container = document.getElementById('activity-logs');

        if (this.activities.length > 0) {
            const actionIcons = {
                'scan': { icon: 'radar', color: '#3498db' },
                'ssl_scan': { icon: 'lock', color: '#9b59b6' },
                'hash_check': { icon: 'bug_report', color: '#e74c3c' },
                'phishing_check': { icon: 'phishing', color: '#e74c3c' },
                'footprint': { icon: 'footprint', color: '#f39c12' },
                'chat': { icon: 'smart_toy', color: 'var(--primary)' },
                'vpn_generate': { icon: 'vpn_lock', color: '#1abc9c' },
                'login': { icon: 'login', color: 'var(--secondary)' },
                'logout': { icon: 'logout', color: '#ff6b6b' },
                'signup': { icon: 'person_add', color: '#2ed573' },
                'default': { icon: 'event', color: 'var(--text-muted)' }
            };

            container.innerHTML = this.activities.map(activity => {
                const actionConfig = actionIcons[activity.action] || actionIcons.default;
                const timestamp = new Date(activity.timestamp).toLocaleString();

                return `
                    <div class="activity-item" style="border-left-color: ${actionConfig.color};">
                        <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                            <span class="material-symbols-outlined" style="color: ${actionConfig.color}; font-size: 1.2rem;">${actionConfig.icon}</span>
                            <div style="flex: 1;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 0.85rem; color: #fff; font-weight: 500;">${activity.action.replace(/_/g, ' ').toUpperCase()}</span>
                                    <span style="font-size: 0.7rem; color: var(--text-muted);">${timestamp}</span>
                                </div>
                                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">${activity.user_email || 'Unknown user'}</div>
                                ${activity.details ? `<div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem; opacity: 0.7;">${JSON.stringify(activity.details).substring(0, 80)}...</div>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No activities found</p>';
        }
    }

    async loadSystemInfo() {
        try {
            // /status is at root level, not under /api
            const response = await fetch('http://localhost:8000/status');
            const status = await response.json();
            const container = document.getElementById('system-info');

            if (status && status.system) {
                const sys = status.system;
                container.innerHTML = `
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">Platform</div>
                        <div style="font-size: 1rem; color: #fff; font-family: 'JetBrains Mono';">${sys.platform || 'Unknown'}</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">Python Version</div>
                        <div style="font-size: 1rem; color: #fff; font-family: 'JetBrains Mono';">${sys.python_version || 'Unknown'}</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">CPU Usage</div>
                        <div style="font-size: 1rem; color: ${parseFloat(sys.cpu_usage) > 80 ? '#ff4757' : 'var(--primary)'}; font-family: 'JetBrains Mono';">${sys.cpu_usage || 'N/A'}</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">Memory Usage</div>
                        <div style="font-size: 1rem; color: ${parseFloat(sys.memory_usage) > 80 ? '#ff4757' : 'var(--secondary)'}; font-family: 'JetBrains Mono';">${sys.memory_usage || 'N/A'}</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">API Status</div>
                        <div style="font-size: 1rem; color: var(--primary); font-family: 'JetBrains Mono';">● Online</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">Ollama Status</div>
                        <div style="font-size: 1rem; color: ${status.ai_available ? 'var(--primary)' : '#ff4757'}; font-family: 'JetBrains Mono';">● ${status.ai_available ? 'Connected' : 'Disconnected'}</div>
                    </div>
                `;
            }
        } catch (e) {
            console.error('Failed to load system info:', e);
        }
    }

    initCharts() {
        // Destroy existing charts
        if (this.charts.usage) this.charts.usage.destroy();
        if (this.charts.activity) this.charts.activity.destroy();

        const period = parseInt(document.getElementById('chart-period').value);

        // Usage Over Time Chart
        const usageCtx = document.getElementById('usage-chart').getContext('2d');
        const labels = [];
        const scansData = [];
        const chatsData = [];

        for (let i = period - 1; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            scansData.push(Math.floor(Math.random() * 20) + 5);
            chatsData.push(Math.floor(Math.random() * 30) + 10);
        }

        this.charts.usage = new Chart(usageCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Scans',
                        data: scansData,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Chat Sessions',
                        data: chatsData,
                        borderColor: 'var(--primary)',
                        backgroundColor: 'rgba(0, 255, 157, 0.1)',
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { color: '#a0a0a0' } }
                },
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0a0a0' } },
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0a0a0' }, beginAtZero: true }
                }
            }
        });

        // Activity Distribution Doughnut
        const activityCtx = document.getElementById('activity-chart').getContext('2d');
        this.charts.activity = new Chart(activityCtx, {
            type: 'doughnut',
            data: {
                labels: ['Scans', 'Chat', 'Audits', 'Phishing', 'VPN'],
                datasets: [{
                    data: [35, 28, 18, 12, 7],
                    backgroundColor: ['#3498db', 'var(--primary)', '#9b59b6', '#e74c3c', 'var(--secondary)'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#a0a0a0', padding: 15 } }
                }
            }
        });
    }

    exportData() {
        const data = {
            exportDate: new Date().toISOString(),
            users: this.users,
            activities: this.activities,
            stats: {
                totalUsers: document.getElementById('stat-users').textContent,
                activeUsers: document.getElementById('stat-active').textContent,
                totalScans: document.getElementById('stat-scans').textContent,
                phishingChecks: document.getElementById('stat-phishing').textContent,
                vpnConfigs: document.getElementById('stat-vpn').textContent
            }
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fsociety_admin_export_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);

        Utils.showToast('Data exported successfully', 'success');
    }
}

// Make instance accessible for inline event handlers
window.adminView = new AdminView();
export default window.adminView;
