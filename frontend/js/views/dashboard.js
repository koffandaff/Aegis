import Components from '../components.js';

class DashboardView {
    async render() {
        const user = JSON.parse(localStorage.getItem('user')) || { username: 'Guest' };

        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('dashboard')}
                
                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <div class="fade-in">
                        <header style="margin-bottom: 2rem;">
                            <h1 style="font-size: 2rem; margin-bottom: 0.5rem;">Welcome back, <span style="color: var(--primary);">${user.username}</span></h1>
                            <p style="color: var(--text-muted);">System status: <span style="color: var(--success);">ONLINE</span> - Secure Connection Established</p>
                        </header>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
                            <!-- AI Assistant Card -->
                            <div class="card glass" style="padding: 1.5rem; display: flex; flex-direction: column; height: 100%;">
                                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                    <span class="material-symbols-outlined" style="font-size: 2rem; color: var(--primary);">smart_toy</span>
                                    <h3 style="margin: 0;">AI Assistant</h3>
                                </div>
                                <p style="color: var(--text-muted); font-size: 0.9rem; flex: 1; margin-bottom: 1.5rem;">
                                    Interact with Cybiz, your advanced cybersecurity AI companion. Get help with scanning, analysis, and security concepts.
                                </p>
                                <a href="#/chat" class="btn" style="text-align: center;">Launch Chat</a>
                            </div>

                            <!-- Network Scan Card -->
                            <div class="card glass" style="padding: 1.5rem; display: flex; flex-direction: column; height: 100%;">
                                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                    <span class="material-symbols-outlined" style="font-size: 2rem; color: #3498db;">radar</span>
                                    <h3 style="margin: 0;">Network Scanner</h3>
                                </div>
                                <p style="color: var(--text-muted); font-size: 0.9rem; flex: 1; margin-bottom: 1.5rem;">
                                    Perform comprehensive network reconnaissance using Nmap, DNS enumeration, and Whois lookups.
                                </p>
                                <a href="#/scan" class="btn" style="text-align: center;">Start Scan</a>
                            </div>

                            <!-- Digital Footprint Card -->
                            <div class="card glass" style="padding: 1.5rem; display: flex; flex-direction: column; height: 100%;">
                                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                    <span class="material-symbols-outlined" style="font-size: 2rem; color: #f39c12;">fingerprint</span>
                                    <h3 style="margin: 0;">Digital Footprint</h3>
                                </div>
                                <p style="color: var(--text-muted); font-size: 0.9rem; flex: 1; margin-bottom: 1.5rem;">
                                    Analyze public exposure and OSINT data for domains and usernames. Check for data leaks.
                                </p>
                                <a href="#/footprint" class="btn" style="text-align: center;">Analyze Footprint</a>
                            </div>
                            
                            <!-- Phishing Detector -->
                             <div class="card glass" style="padding: 1.5rem; display: flex; flex-direction: column; height: 100%;">
                                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                    <span class="material-symbols-outlined" style="font-size: 2rem; color: #e74c3c;">phishing</span>
                                    <h3 style="margin: 0;">Phishing Detector</h3>
                                </div>
                                <p style="color: var(--text-muted); font-size: 0.9rem; flex: 1; margin-bottom: 1.5rem;">
                                    Verify suspicious URLs and emails using advanced heuristics and threat intelligence.
                                </p>
                                <a href="#/phishing" class="btn" style="text-align: center;">Check URL</a>
                            </div>
                        </div>

                        <!-- System Stats / Quick Info -->
                        <div class="card glass" style="padding: 1.5rem; margin-bottom: 2rem;">
                            <h3 style="margin-bottom: 1rem;">System Metrics</h3>
                            <div class="system-metrics" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
                                <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                                    <div style="font-size: 2rem; font-weight: bold; color: var(--primary);">ACTIVE</div>
                                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">Protection Status</div>
                                </div>
                                <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                                    <div style="font-size: 2rem; font-weight: bold; color: #3498db;">AES-256</div>
                                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">Encryption Level</div>
                                </div>
                                <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                                    <div style="font-size: 2rem; font-weight: bold; color: #9b59b6;">0</div>
                                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">Threats Detected</div>
                                </div>
                                <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                                    <div style="font-size: 2rem; font-weight: bold; color: var(--success);">100%</div>
                                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">Uptime</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        // No special logic needed for dashboard yet
    }
}

export default new DashboardView();
