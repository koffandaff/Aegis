import Auth from '../auth.js';
import Api from '../api.js';
import Components from '../components.js';

class DashboardView {
    constructor() {
        this.intervals = [];
    }

    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('dashboard')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in" style="font-size: 2.5rem; margin-bottom: 2rem;">System Overview</h1>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
                        <div class="card glass fade-in" style="animation-delay: 0.1s;">
                            <h3 style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase;">Total Scans</h3>
                            <p id="stat-total-scans" style="font-size: 2.5rem; color: var(--primary); font-family: 'JetBrains Mono'; margin-top: 0.5rem; font-weight: bold;">-</p>
                        </div>
                        <div class="card glass fade-in" style="animation-delay: 0.2s;">
                            <h3 style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase;">Chat Sessions</h3>
                            <p id="stat-chat-sessions" style="font-size: 2.5rem; color: #a55eea; font-family: 'JetBrains Mono'; margin-top: 0.5rem; font-weight: bold;">-</p>
                        </div>
                        <div class="card glass fade-in" style="animation-delay: 0.3s;">
                            <h3 style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase;">Total Messages</h3>
                            <p id="stat-chat-messages" style="font-size: 2.5rem; color: #fd9644; font-family: 'JetBrains Mono'; margin-top: 0.5rem; font-weight: bold;">-</p>
                        </div>
                        <div class="card glass fade-in" style="animation-delay: 0.4s;">
                            <h3 style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase;">CPU Usage</h3>
                            <p id="stat-cpu" style="font-size: 2.5rem; color: var(--secondary); font-family: 'JetBrains Mono'; margin-top: 0.5rem; font-weight: bold;">-</p>
                        </div>
                        <div class="card glass fade-in" style="animation-delay: 0.5s;">
                            <h3 style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase;">Memory Usage</h3>
                            <p id="stat-memory" style="font-size: 2.5rem; color: #00e5ff; font-family: 'JetBrains Mono'; margin-top: 0.5rem; font-weight: bold;">-</p>
                        </div>
                    </div>

                    <div class="card glass fade-in" style="animation-delay: 0.6s;">
                        <h3 style="margin-bottom: 1.5rem;">System Status</h3>
                        <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">All core modules are functional. Operation "FS" is active.</p>
                        
                        <div style="border: 1px dashed var(--primary); border-radius: 8px; padding: 1.5rem; background: rgba(0, 255, 157, 0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <span style="color: var(--primary); font-family: 'JetBrains Mono';">[ OS / PLATFORM ]</span>
                                <span id="stat-os" style="color: var(--text-main);">-</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                <span style="color: var(--primary); font-family: 'JetBrains Mono';">[ DISK USAGE ]</span>
                                <span id="stat-disk" style="color: var(--text-main);">-</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: var(--primary); font-family: 'JetBrains Mono';">[ UPTIME ]</span>
                                <span id="stat-uptime" style="color: var(--text-main);">-</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());

        // Initial load
        await this.loadStats();
        await this.loadSystemStatus();

        // Start live updates
        this.startLiveUpdates();
    }

    async loadStats() {
        try {
            const [history, sessions] = await Promise.all([
                Api.get('/scans/user/history'),
                Api.get('/chat/sessions')
            ]);

            // Scans
            const statEl = document.getElementById('stat-total-scans');
            if (statEl) statEl.textContent = history?.total || 0;

            // Chat Stats
            const sessionsCount = sessions?.length || 0;
            const messagesCount = sessions?.reduce((acc, s) => acc + (s.message_count || 0), 0) || 0;

            const sessionEl = document.getElementById('stat-chat-sessions');
            const msgEl = document.getElementById('stat-chat-messages');

            if (sessionEl) sessionEl.textContent = sessionsCount;
            if (msgEl) msgEl.textContent = messagesCount;

        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    async loadSystemStatus() {
        try {
            // Use Api.baseUrl to derive root URL (remove /api suffix)
            const rootUrl = Api.baseUrl.replace(/\/api$/, '');
            const response = await fetch(`${rootUrl}/status`);
            const statusData = await response.json();

            if (statusData && statusData.system) {
                const cpuEl = document.getElementById('stat-cpu');
                const memEl = document.getElementById('stat-memory');
                const diskEl = document.getElementById('stat-disk');
                const osEl = document.getElementById('stat-os');
                const uptimeEl = document.getElementById('stat-uptime');

                if (cpuEl) cpuEl.textContent = statusData.system.cpu_usage || 'N/A';
                if (memEl) memEl.textContent = statusData.system.memory_usage || 'N/A';
                if (diskEl) diskEl.textContent = statusData.system.disk_usage || 'N/A';
                if (osEl) osEl.textContent = statusData.system.platform || 'N/A';
                if (uptimeEl) uptimeEl.textContent = statusData.system.uptime || 'N/A';
            }
        } catch (error) {
            console.error('Failed to load system status:', error);
        }
    }

    startLiveUpdates() {
        // Clear any existing intervals
        this.stopLiveUpdates();

        // System status - refresh every 5 seconds
        this.intervals.push(setInterval(() => {
            this.loadSystemStatus();
        }, 5000));

        // Stats - refresh every 60 seconds
        this.intervals.push(setInterval(() => {
            this.loadStats();
        }, 60000));

        // Cleanup on navigation
        window.addEventListener('hashchange', () => this.stopLiveUpdates(), { once: true });
    }

    stopLiveUpdates() {
        this.intervals.forEach(interval => clearInterval(interval));
        this.intervals = [];
    }
}

export default new DashboardView();
