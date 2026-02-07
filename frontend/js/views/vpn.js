import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class VpnView {
    constructor() {
        this.selectedServer = null;
        this.currentUser = null;
    }

    async render() {
        // Get current user for filename
        this.currentUser = Auth.getCurrentUser();
        const username = this.currentUser?.username || 'user';

        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('vpn')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">Fsociety Secure Tunnel</h1>
                    
                    <!-- Disclaimer Banner -->
                    <div class="fade-in" style="background: rgba(231, 76, 60, 0.1); border-left: 4px solid #e74c3c; padding: 1rem; margin-bottom: 2rem; border-radius: 4px;">
                        <strong style="color: #e74c3c; display: flex; align-items: center; gap: 0.5rem;">
                            <span class="material-symbols-outlined">warning</span> DISCLAIMER: DEMO MODE
                        </strong>
                        <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.5rem; margin-bottom: 0;">
                            This VPN service is currently running in <strong>simulation mode</strong> with dummy configurations. 
                            In a real production environment, properly hosting these VPN servers would require significant infrastructure costs and could potentially expose the server's IP address (doxing risk). 
                            <strong>Do not use these generated configurations for sensitive activities.</strong>
                        </p>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; max-width: 1200px; margin: 0 auto; margin-bottom: 2rem;">
                        
                        <!-- Connection Center -->
                        <div class="card glass fade-in" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; position: relative; overflow: hidden;">
                            <!-- Connection Status -->
                            <div id="connection-status" style="position: absolute; top: 1.5rem; left: 1.5rem; display: flex; align-items: center; gap: 0.5rem; opacity: 0.7;">
                                <span class="material-symbols-outlined" style="color: var(--text-muted);">public</span>
                                <span id="status-text" style="font-size: 0.9rem; letter-spacing: 1px;">DISCONNECTED</span>
                            </div>

                            <!-- Big Connect Button -->
                            <div id="connect-wrapper">
                                <button id="connect-btn" class="big-connect-btn">
                                    <span class="material-symbols-outlined" style="font-size: 3rem; margin-bottom: 0.5rem;">power_settings_new</span>
                                    CONNECT
                                </button>
                            </div>

                            <!-- Selected Server Info -->
                            <div id="selected-info" style="margin-top: 2rem; text-align: center; height: 50px;">
                                <div style="font-size: 1.2rem; font-weight: bold; color: var(--text-main);">Select a Node</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted);">Choose a location to route traffic</div>
                            </div>

                            <!-- Progress Bar -->
                            <div style="width: 80%; max-width: 400px;">
                                ${Components.renderProgressBar('vpn-connect')}
                            </div>

                            <!-- Download Ready Action (Hidden initially) -->
                            <div id="download-action" style="display: none; text-align: center; margin-top: 1rem;">
                                <div style="font-size: 1.1rem; color: var(--primary); margin-bottom: 0.5rem;">Secure Tunnel Ready</div>
                                <button id="dl-config-btn" class="btn" style="display: flex; align-items: center; gap: 0.5rem; margin: 0 auto;">
                                    <span class="material-symbols-outlined">download</span> Download VPN Profile (.ovpn)
                                </button>
                            </div>
                        </div>

                        <!-- Server & Config Sidebar -->
                        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
                            
                            <!-- Server List -->
                            <div class="card glass fade-in" style="flex: 1; max-height: 400px; display: flex; flex-direction: column;">
                                <h3 style="margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-muted); letter-spacing: 1px;">AVAILABLE NODES</h3>
                                <div id="node-list" style="overflow-y: auto; flex: 1; padding-right: 0.5rem;">
                                    <p style="color: var(--text-muted); text-align: center;">Scanning network...</p>
                                </div>
                            </div>

                            <!-- Recent Configs -->
                            <div class="card glass fade-in" style="flex: 1; animation-delay: 0.1s;">
                                <h3 style="margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-muted); letter-spacing: 1px;">HISTORY</h3>
                                <div id="config-list" style="display: flex; flex-direction: column; gap: 0.8rem;"></div>
                            </div>
                        </div>

                    </div>

                    <!-- Server Node Administration (Admin Only) -->
                    ${this.currentUser?.role === 'admin' ? `
                    <div class="card glass fade-in" style="max-width: 1200px; margin: 0 auto 2rem auto; border-left: 4px solid var(--secondary);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h3 style="color: var(--secondary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined">admin_panel_settings</span> Server Node Administration
                                </h3>
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
                                    Use the following command on your Linux/WSL machine to deploy a functional VPN server node.
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <div id="node-ip-badge" style="background: rgba(0,255,157,0.1); color: var(--primary); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; border: 1px solid var(--primary);">
                                    MASTER NODE: ACTIVE
                                </div>
                            </div>
                        </div>

                        <div style="background: rgba(0,0,0,0.4); padding: 1.2rem; border-radius: 8px; position: relative;">
                            <code id="setup-command" style="color: var(--secondary); font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
                                sudo python3 setup_vpn_server.py
                            </code>
                            <button class="btn-outline" style="position: absolute; right: 1rem; top: 0.8rem; padding: 4px 10px; font-size: 0.7rem; color: var(--secondary); border-color: var(--secondary);" 
                                    onclick="navigator.clipboard.writeText('sudo python3 setup_vpn_server.py'); Utils.showToast('Copied to clipboard!', 'info')">
                                COPY
                            </button>
                        </div>
                        <div style="margin-top: 1rem; font-size: 0.75rem; color: var(--text-muted);">
                             ℹ️ Ensure the Fsociety backend is running with <code>--host 0.0.0.0</code> for the node to sync PKI certificates.
                        </div>
                    </div>
                    ` : ''}

                    <!-- Usage Guide Section -->
                    <div class="card glass fade-in" style="margin-top: 2rem; max-width: 1200px; margin-left: auto; margin-right: auto;">
                        <h3 style="margin-bottom: 1.5rem; color: var(--primary); display: flex; align-items: center; gap: 0.5rem;">
                            <span class="material-symbols-outlined">help</span> How to Use Your VPN Profile
                        </h3>
                        
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
                            
                            <!-- GUI Method -->
                            <div>
                                <h4 style="color: var(--secondary); margin-bottom: 1rem; font-size: 0.9rem;">
                                    <span class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.3rem; font-size: 1rem;">desktop_windows</span>
                                    Desktop (GUI)
                                </h4>
                                <ol style="color: var(--text-main); font-size: 0.85rem; line-height: 1.8; padding-left: 1.2rem;">
                                    <li>Download <a href="https://openvpn.net/client/" target="_blank" style="color: var(--primary);">OpenVPN Connect</a></li>
                                    <li>Open the app and click <strong>Import Profile</strong></li>
                                    <li>Select your downloaded <code>.ovpn</code> file</li>
                                    <li>Toggle the connection switch to <strong>ON</strong></li>
                                </ol>
                            </div>

                            <!-- CLI Method -->
                            <div>
                                <h4 style="color: var(--secondary); margin-bottom: 1rem; font-size: 0.9rem;">
                                    <span class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.3rem; font-size: 1rem;">terminal</span>
                                    Command Line (Linux/macOS)
                                </h4>
                                <div style="background: rgba(0,0,0,0.4); padding: 1rem; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; line-height: 1.8; overflow-x: auto;">
                                    <div style="color: var(--text-muted);"># Install OpenVPN (Ubuntu/Debian)</div>
                                    <div style="color: var(--primary);">sudo apt install openvpn -y</div>
                                    <br>
                                    <div style="color: var(--text-muted);"># Install OpenVPN (macOS)</div>
                                    <div style="color: var(--primary);">brew install openvpn</div>
                                    <br>
                                    <div style="color: var(--text-muted);"># Connect using your profile</div>
                                    <div style="color: var(--primary);">sudo openvpn --config ~/Downloads/<span id="cli-filename">[your_file].ovpn</span></div>
                                    <br>
                                    <div style="color: var(--text-muted);"># Run in background (daemon mode)</div>
                                    <div style="color: var(--primary);">sudo openvpn --config ~/Downloads/[file].ovpn --daemon</div>
                                </div>
                            </div>

                            <!-- Mobile Method -->
                            <div>
                                <h4 style="color: var(--secondary); margin-bottom: 1rem; font-size: 0.9rem;">
                                    <span class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.3rem; font-size: 1rem;">smartphone</span>
                                    Mobile (iOS/Android)
                                </h4>
                                <ol style="color: var(--text-main); font-size: 0.85rem; line-height: 1.8; padding-left: 1.2rem;">
                                    <li>Install <strong>OpenVPN Connect</strong> from App/Play Store</li>
                                    <li>Transfer <code>.ovpn</code> file to your device</li>
                                    <li>Open the file with OpenVPN Connect</li>
                                    <li>Tap <strong>Add</strong> then toggle to connect</li>
                                </ol>
                            </div>

                        </div>

                        <div id="server-status-notice" style="margin-top: 1.5rem; padding: 1rem; background: rgba(0,255,157,0.1); border-left: 3px solid var(--primary); border-radius: 4px;">
                            <strong style="color: var(--primary);">✅ Real Certificates:</strong>
                            <span style="color: var(--text-muted); font-size: 0.85rem;">
                                These configurations use valid X.509 certificates signed by the Fsociety CA. 
                                To connect, you need an OpenVPN server configured with the matching PKI files.
                                See <code>docs/vpn_server_setup.md</code> for setup instructions.
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        this.loadServers();
        this.loadConfigs();

        const connectBtn = document.getElementById('connect-btn');
        const list = document.getElementById('node-list');
        const dlAction = document.getElementById('download-action');
        const dlBtn = document.getElementById('dl-config-btn');
        const statusText = document.getElementById('status-text');
        const selectedInfo = document.getElementById('selected-info');

        // Connect Button Click Handler
        connectBtn.addEventListener('click', async () => {
            if (!this.selectedServer) {
                Utils.showToast('Please select a server node first', 'info');
                list.style.borderColor = 'var(--primary)';
                setTimeout(() => list.style.borderColor = 'transparent', 500);
                return;
            }

            // Reset UI
            dlAction.style.display = 'none';
            connectBtn.disabled = true;
            connectBtn.style.opacity = '0.5';
            statusText.textContent = 'SECURE HANDSHAKE...';
            statusText.style.color = '#ffa502';

            // Start Progress Simulation AND Backend Call simultaneously for real feel
            const progressPromise = Utils.visualizeProgress('vpn-connect', 2500,
                ['Initializing RSA...', 'Exchanging Keys...', 'Signing X.509 Certificate...', 'Embedding TLS-Auth...', 'Finalizing Profile...']);

            const configPromise = Api.post('/vpn/openvpn', {
                server_address: this.selectedServer.address,
                port: 1194,
                protocol: 'udp'
            });

            try {
                const [_, response] = await Promise.all([progressPromise, configPromise]);

                if (response && response.config_content) {
                    this.latestConfig = response;

                    // "Connection" Complete
                    statusText.textContent = 'TUNNEL READY';
                    statusText.style.color = 'var(--primary)';
                    connectBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 3rem;">verified_user</span>READY';
                    connectBtn.disabled = false;
                    connectBtn.style.opacity = '1';
                    connectBtn.style.borderColor = 'var(--primary)';
                    connectBtn.style.boxShadow = '0 0 50px rgba(0,255,157,0.4)';
                    connectBtn.style.animation = 'none';

                    dlAction.style.display = 'block';
                    Utils.showToast('Secure profile generated!', 'success');
                    this.loadConfigs();

                    // Setup Download Handler
                    dlBtn.onclick = () => this.downloadLatest();
                } else {
                    throw new Error('Invalid response');
                }
            } catch (err) {
                statusText.textContent = 'CONNECTION FAILED';
                statusText.style.color = '#ff4757';
                connectBtn.disabled = false;
                connectBtn.style.opacity = '1';
                Utils.showToast('Failed to generate secure tunnel.', 'error');
            }
        });
    }

    async loadServers() {
        try {
            const servers = await Api.get('/vpn/servers');
            const list = document.getElementById('node-list');

            if (servers) {
                list.innerHTML = servers.map(srv => `
                    <div class="server-node glass-hover" data-id="${srv.id}" 
                         style="padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; cursor: pointer; border: 1px solid transparent; transition: all 0.2s;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="display: flex; align-items: center; gap: 0.8rem;">
                                <span class="material-symbols-outlined" style="color: var(--primary);">dns</span>
                                <div>
                                    <div style="font-weight: 600; font-size: 0.9rem;">${srv.name}</div>
                                    <div style="font-size: 0.75rem; color: var(--text-muted);">${srv.region}</div>
                                </div>
                            </div>
                            <div style="font-size: 0.75rem; color: ${parseInt(srv.load) > 50 ? '#ff4757' : '#00ff9d'};">
                                ${srv.load} Load
                            </div>
                        </div>
                    </div>
                `).join('');

                // Add selection logic
                list.querySelectorAll('.server-node').forEach(node => {
                    node.addEventListener('click', () => {
                        // Clear previous selection
                        list.querySelectorAll('.server-node').forEach(n => n.style.background = 'transparent');
                        list.querySelectorAll('.server-node').forEach(n => n.style.borderColor = 'transparent');

                        // Set active
                        node.style.background = 'rgba(0,255,157,0.1)';
                        node.style.borderColor = 'var(--primary)';

                        // Update State & UI
                        const srv = servers.find(s => s.id === node.dataset.id);
                        this.selectedServer = srv;

                        const selectedInfo = document.getElementById('selected-info');
                        selectedInfo.innerHTML = `
                            <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">${srv.name}</div>
                            <div style="font-size: 0.9rem; color: var(--text-muted);">${Utils.maskIP(srv.address)} • UDP 1194</div>
                        `;

                        // Update CLI example filename
                        const username = this.currentUser?.username || 'user';
                        const cliFilename = document.getElementById('cli-filename');
                        if (cliFilename) {
                            cliFilename.textContent = `${username}_fsociety_${srv.id.replace('-', '_')}.ovpn`;
                        }

                        // Reset Button State
                        const btn = document.getElementById('connect-btn');
                        btn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 3rem; margin-bottom: 0.5rem;">power_settings_new</span>CONNECT';
                        btn.disabled = false;
                        btn.style.opacity = '1';
                        document.getElementById('download-action').style.display = 'none';
                        document.getElementById('status-text').textContent = 'READY TO CONNECT';
                        document.getElementById('status-text').style.color = 'var(--text-main)';
                    });
                });
            }
        } catch (e) { console.error(e); }
    }

    async downloadLatest() {
        if (!this.latestConfig) return;

        const response = this.latestConfig;
        const srv = this.selectedServer;

        const blob = new Blob([response.config_content], { type: 'application/x-openvpn-profile' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const filename = response.filename || `${this.currentUser?.username || 'user'}_fsociety_${srv.id}`;
        a.download = `${filename}.ovpn`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        Utils.showToast('Profile downloaded! Use OpenVPN Connect to connect.', 'success');
    }

    async loadConfigs() {
        try {
            const configs = await Api.get('/vpn/configs');
            const list = document.getElementById('config-list');
            if (configs && configs.length > 0) {
                list.innerHTML = configs.slice(0, 3).map(cfg => `
                    <div style="background: rgba(255,255,255,0.03); padding: 0.8rem; border-radius: 6px; font-size: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600;">${cfg.name}</div>
                            <div style="color: var(--text-muted); font-size: 0.7rem;">${Utils.parseDate(cfg.created_at)}</div>
                        </div>
                        <button class="btn-outline" style="padding: 2px 6px; font-size: 0.7rem;" onclick="downloadRaw('${btoa(cfg.config_content)}', '${cfg.filename || cfg.name}')">GET</button>
                    </div>
                `).join('');
            } else {
                list.innerHTML = '<div style="text-align: center; font-size: 0.8rem; color: var(--text-muted);">No history</div>';
            }
        } catch (e) { console.error(e); }

        window.downloadRaw = (contentB64, name) => {
            const content = atob(contentB64);
            const blob = new Blob([content], { type: 'application/x-openvpn-profile' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${name.replace(/\s+/g, '_')}.ovpn`;
            a.click();
            window.URL.revokeObjectURL(url);
        };
    }
}

export default new VpnView();
