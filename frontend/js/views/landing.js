import Auth from '../auth.js';

class LandingView {
    async render() {
        return `
            <!-- Hero Section -->
            <div style="min-height: 100vh; display: flex; flex-direction: column; position: relative; overflow: hidden; background: #000;">
                
                <!-- Animated Background -->
                <div class="hero-gradient" style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; opacity: 0.6; animation: rotateGradient 20s linear infinite;"></div>
                <div style="position: absolute; inset: 0; background: radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 0%, #000 80%); pointer-events: none;"></div>
                
                <!-- Floating Particles Effect -->
                <div id="particles" style="position: absolute; inset: 0; pointer-events: none; overflow: hidden;"></div>

                <!-- Navigation -->
                <nav class="glass" style="position: fixed; top: 0; width: 100%; z-index: 100; display: flex; justify-content: space-between; align-items: center; padding: 1rem 3rem;">
                    <a href="#/" style="text-decoration: none; display: flex; align-items: center;">
                        <span class="material-symbols-outlined" style="color: #fff; font-size: 1.8rem; margin-right: 0.5rem; text-shadow: 0 0 15px rgba(255,255,255,0.4);">security</span>
                        <span style="font-size: 1.5rem; font-weight: 800; color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.3); font-family: 'JetBrains Mono', monospace; letter-spacing: 1px;">Fsociety</span>
                        <span style="color: #fff; animation: blink 1s step-end infinite; font-weight: 300; text-shadow: 0 0 10px rgba(255,255,255,0.5);">_</span>
                    </a>
                    <div style="display: flex; gap: 1rem; align-items: center;">
                        ${Auth.isAuthenticated() ? `
                            <a href="#/dashboard" class="btn" style="padding: 0.5rem 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.2rem;">dashboard</span>
                                Dashboard
                            </a>
                        ` : `
                            <a href="#/login" class="btn-outline" style="padding: 0.5rem 1.5rem;">Login</a>
                            <a href="#/signup" class="btn" style="padding: 0.5rem 1.5rem;">Get Started</a>
                        `}
                    </div>
                </nav>

                <!-- Hero Content -->
                <div style="flex: 1; display: flex; align-items: center; justify-content: center; padding: 6rem 2rem 4rem 2rem; position: relative; z-index: 1;">
                    <div style="display: flex; flex-direction: row; align-items: center; gap: 4rem; max-width: 1200px; width: 100%; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 320px;">
                            <div style="display: inline-block; background: rgba(0, 255, 157, 0.1); border: 1px solid var(--primary); border-radius: 30px; padding: 0.4rem 1.2rem; margin-bottom: 2rem; font-size: 0.85rem; color: var(--primary);">
                                🔒 Enterprise-Grade Security Platform
                            </div>
                            
                            <h1 style="font-size: clamp(2.5rem, 5vw, 4.5rem); font-weight: 800; line-height: 1.1; margin-bottom: 1.5rem;">
                                <span style="background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Protect</span> Your Digital World
                            </h1>
                            
                            <p style="font-size: 1.1rem; color: var(--text-muted); margin-bottom: 2.5rem; line-height: 1.7;">
                                Advanced cybersecurity platform with AI-powered threat detection, real-time network scanning, and comprehensive security audits.
                            </p>
                            
                            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                                <a href="${Auth.isAuthenticated() ? '#/dashboard' : '#/signup'}" class="btn" style="padding: 1rem 2.5rem; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined">${Auth.isAuthenticated() ? 'dashboard' : 'rocket_launch'}</span>
                                    ${Auth.isAuthenticated() ? 'Go to Dashboard' : 'Get Started'}
                                </a>
                                <a href="#features" class="btn-outline" style="padding: 1rem 2.5rem; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined">security</span>
                                    Explore Tools
                                </a>
                            </div>
                        </div>

                        <!-- Recon Terminal Animation -->
                        <div style="flex: 1; min-width: 320px;">
                            <div class="card glass" style="background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(0, 255, 157, 0.2); padding: 0; overflow: hidden; height: 350px; display: flex; flex-direction: column; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                                <div style="background: rgba(255,255,255,0.05); padding: 0.5rem 1rem; display: flex; align-items: center; gap: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                                    <div style="display: flex; gap: 5px;">
                                        <div style="width: 10px; height: 10px; border-radius: 50%; background: #ff5f56;"></div>
                                        <div style="width: 10px; height: 10px; border-radius: 50%; background: #ffbd2e;"></div>
                                        <div style="width: 10px; height: 10px; border-radius: 50%; background: #27c93f;"></div>
                                    </div>
                                    <span style="color: var(--text-muted); font-size: 0.7rem;">recon_engine.log</span>
                                </div>
                                <div id="recon-terminal" style="flex: 1; padding: 1rem; overflow: hidden; color: var(--primary); text-shadow: 0 0 5px rgba(0,255,157,0.5);">
                                    <!-- Log entries will be injected here -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Scroll Indicator -->
                <div style="position: absolute; bottom: 1.5rem; left: 50%; transform: translateX(-50%); animation: bounce 2s infinite;">
                    <span class="material-symbols-outlined" style="font-size: 1.5rem; color: var(--text-muted);">expand_more</span>
                </div>
            </div>

            <!-- Features Section -->
            <section id="features" style="padding: 6rem 2rem; position: relative;">
                <div style="max-width: 1200px; margin: 0 auto;">
                    <div style="text-align: center; margin-bottom: 4rem;">
                        <h2 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;">
                            Complete Security <span style="color: var(--primary);">Suite</span>
                        </h2>
                        <p style="color: var(--text-muted); font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
                            Everything you need to protect your infrastructure, detect threats, and respond to incidents.
                        </p>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem;">
                        
                        <!-- Feature 1: AI Assistant -->
                        <div class="feature-card">
                            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.5rem; color: #000;">smart_toy</span>
                            </div>
                            <h3 style="font-size: 1.25rem; margin-bottom: 0.75rem;">AI Security Assistant</h3>
                            <p style="color: var(--text-muted); line-height: 1.6;">
                                Powered by advanced LLM technology. Get instant answers to security questions, analyze threats, and receive actionable recommendations.
                            </p>
                        </div>

                        <!-- Feature 2: Network Scanning -->
                        <div class="feature-card">
                            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #ff4757, #ffa502); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.5rem; color: #fff;">radar</span>
                            </div>
                            <h3 style="font-size: 1.25rem; margin-bottom: 0.75rem;">Network Scanning</h3>
                            <p style="color: var(--text-muted); line-height: 1.6;">
                                Discover vulnerabilities with comprehensive port scanning, service detection, and OS fingerprinting. Identify risks before attackers do.
                            </p>
                        </div>

                        <!-- Feature 3: Security Audit -->
                        <div class="feature-card">
                            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #4682B4, #00d2d3); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.5rem; color: #fff;">security</span>
                            </div>
                            <h3 style="font-size: 1.25rem; margin-bottom: 0.75rem;">Security Audits</h3>
                            <p style="color: var(--text-muted); line-height: 1.6;">
                                Automated security assessments including SSL/TLS analysis, header checks, and compliance verification. Generate detailed reports.
                            </p>
                        </div>

                        <!-- Feature 4: Digital Footprint -->
                        <div class="feature-card">
                            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #9b59b6, #e056fd); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.5rem; color: #fff;">fingerprint</span>
                            </div>
                            <h3 style="font-size: 1.25rem; margin-bottom: 0.75rem;">Digital Footprint</h3>
                            <p style="color: var(--text-muted); line-height: 1.6;">
                                Discover what information about you is exposed online. Find leaked credentials, social profiles, and sensitive data breaches.
                            </p>
                        </div>

                        <!-- Feature 5: Phishing Detection -->
                        <div class="feature-card">
                            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #ffa502, #ff6b81); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.5rem; color: #fff;">phishing</span>
                            </div>
                            <h3 style="font-size: 1.25rem; margin-bottom: 0.75rem;">Phishing Detector</h3>
                            <p style="color: var(--text-muted); line-height: 1.6;">
                                Analyze suspicious URLs and emails with AI-powered phishing detection. Protect your team from social engineering attacks.
                            </p>
                        </div>

                        <!-- Feature 6: VPN -->
                        <div class="feature-card">
                            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, var(--primary), #00d2d3); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.5rem; color: #000;">vpn_lock</span>
                            </div>
                            <h3 style="font-size: 1.25rem; margin-bottom: 0.75rem;">Secure VPN</h3>
                            <p style="color: var(--text-muted); line-height: 1.6;">
                                Generate OpenVPN configurations with real PKI certificates. Secure your traffic with enterprise-grade encryption.
                            </p>
                        </div>

                    </div>
                </div>
            </section>

            <!-- Stats Section -->
            <section style="padding: 4rem 2rem; background: rgba(0, 255, 157, 0.03);">
                <div style="max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem;">
                    <div class="stat-card">
                        <div class="stat-number">10K+</div>
                        <div style="color: var(--text-muted);">Security Scans</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">500+</div>
                        <div style="color: var(--text-muted);">Companies Protected</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">99.9%</div>
                        <div style="color: var(--text-muted);">Uptime</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">24/7</div>
                        <div style="color: var(--text-muted);">AI Support</div>
                    </div>
                </div>
            </section>

            <!-- Creators Section -->
            <section id="creators" style="padding: 6rem 2rem; background: linear-gradient(to bottom, transparent, rgba(0, 255, 157, 0.05));">
                <div style="max-width: 1200px; margin: 0 auto;">
                    <div style="text-align: center; margin-bottom: 4rem;">
                        <h2 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;">
                            Meet The <span style="color: var(--primary);">Creators</span>
                        </h2>
                        <p style="color: var(--text-muted); font-size: 1.1rem;">The elite engineering team behind Fsociety.</p>
                    </div>

                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 3rem;">
                        <!-- Dhruvil Adroja -->
                        <div class="card glass creator-card" style="text-align: center; padding: 3rem 2rem; border: 1px solid rgba(0, 255, 157, 0.1); transition: all 0.3s ease;">
                            <div style="width: 100px; height: 100px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 50%; margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; color: #000; box-shadow: 0 0 20px rgba(0, 255, 157, 0.3);">
                                <span class="material-symbols-outlined" style="font-size: 3.5rem;">engineering</span>
                            </div>
                            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Dhruvil Adroja</h3>
                            <div style="color: var(--primary); font-size: 0.9rem; margin-bottom: 1rem; font-weight: 500;">Lead Full Stack Developer</div>
                            <div style="background: rgba(0, 255, 157, 0.1); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.8rem; color: var(--text-main); display: inline-block; margin-bottom: 1rem;">
                                <span class="material-symbols-outlined" style="font-size: 0.9rem; vertical-align: middle; margin-right: 0.2rem;">terminal</span>
                                Linux & Recon Engine Architect
                            </div>
                            <div style="margin-top: 0.5rem;">
                                <a href="https://github.com/koffandaff" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 20px; text-decoration: none; color: #fff; border: 1px solid rgba(255,255,255,0.2); transition: all 0.3s; font-size: 0.85rem;">
                                    <svg height="16" viewBox="0 0 16 16" width="16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
                                    GitHub
                                </a>
                            </div>
                        </div>

                        <!-- Vraj Patel -->
                        <div class="card glass creator-card" style="text-align: center; padding: 3rem 2rem; border: 1px solid rgba(0, 255, 157, 0.1); transition: all 0.3s ease;">
                            <div style="width: 100px; height: 100px; background: linear-gradient(135deg, var(--primary), #4682B4); border-radius: 50%; margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; color: #000; box-shadow: 0 0 20px rgba(0, 255, 157, 0.3);">
                                <span class="material-symbols-outlined" style="font-size: 3.5rem;">dns</span>
                            </div>
                            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Vraj Patel</h3>
                            <div style="color: var(--primary); font-size: 0.9rem; margin-bottom: 1rem; font-weight: 500;">Full Stack Developer</div>
                            <p style="color: var(--text-muted); font-size: 0.85rem;">Architecting scalable backend infrastructures and secure communication protocols.</p>
                        </div>

                        <!-- Krisha Patel -->
                        <div class="card glass creator-card" style="text-align: center; padding: 3rem 2rem; border: 1px solid rgba(0, 255, 157, 0.1); transition: all 0.3s ease;">
                            <div style="width: 100px; height: 100px; background: linear-gradient(135deg, var(--secondary), #ff4757); border-radius: 50%; margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; color: #000; box-shadow: 0 0 20px rgba(255, 165, 2, 0.3);">
                                <span class="material-symbols-outlined" style="font-size: 3.5rem;">palette</span>
                            </div>
                            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Krisha Patel</h3>
                            <div style="color: var(--primary); font-size: 0.9rem; margin-bottom: 1rem; font-weight: 500;">Full Stack Developer</div>
                            <p style="color: var(--text-muted); font-size: 0.85rem;">Crafting intuitive security interfaces and advanced data visualizations.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- CTA Section -->
            <section style="padding: 6rem 2rem; text-align: center;">
                <div style="max-width: 700px; margin: 0 auto;">
                    <h2 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1.5rem;">
                        Ready to <span style="color: var(--primary);">Secure</span> Your Future?
                    </h2>
                    <p style="color: var(--text-muted); font-size: 1.1rem; margin-bottom: 2rem; line-height: 1.7;">
                        Join thousands of security professionals who trust Fsociety to protect their digital assets.
                    </p>
                    <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                        <a href="${Auth.isAuthenticated() ? '#/dashboard' : '#/signup'}" class="btn" style="padding: 1rem 3rem; font-size: 1.1rem;">
                            ${Auth.isAuthenticated() ? 'Enter Command Center' : 'Initialize Connection'}
                        </a>
                        <a href="${Auth.isAuthenticated() ? '#/dashboard' : '#/login'}" class="btn-outline" style="padding: 1rem 3rem; font-size: 1.1rem;">
                            ${Auth.isAuthenticated() ? 'View Active Logs' : 'Access Dashboard'}
                        </a>
                    </div>
                </div>
            </section>

            <!-- Footer -->
            <footer style="padding: 3rem 2rem; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span class="material-symbols-outlined" style="color: #fff; font-size: 1.2rem; opacity: 0.8;">security</span>
                        <span style="font-size: 1.2rem; font-weight: 800; color: #fff; font-family: 'JetBrains Mono', monospace;">Fsociety</span>
                        <span style="color: var(--text-muted); margin-left: 1rem; font-size: 0.85rem;">© 2026 All rights reserved</span>
                    </div>
                    <div style="display: flex; gap: 2rem; font-size: 0.9rem;">
                        <a href="#/privacy" style="color: var(--text-muted); text-decoration: none;">Privacy Policy</a>
                        <a href="#/terms" style="color: var(--text-muted); text-decoration: none;">Terms of Service</a>
                        <a href="#/contact" style="color: var(--text-muted); text-decoration: none;">Contact</a>
                    </div>
                </div>
            </footer>

            <style>
                @keyframes rotateGradient {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                @keyframes bounce {
                    0%, 100% { transform: translateX(-50%) translateY(0); }
                    50% { transform: translateX(-50%) translateY(10px); }
                }
                @keyframes float {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-20px); }
                }
            </style>
        `;
    }

    async afterRender() {
        // Create floating particles
        if (document.getElementById('particles')) {
            this.createParticles();
        }
        // Start terminal animation
        if (document.getElementById('recon-terminal')) {
            this.startTerminal();
        }
    }

    createParticles() {
        const container = document.getElementById('particles');
        if (!container) return;
        // Reduce particle count to improve performance
        for (let i = 0; i < 15; i++) {
            const particle = document.createElement('div');
            // ... (keep existing styled but cleaner) ...
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4 + 2}px;
                height: ${Math.random() * 4 + 2}px;
                background: rgba(0, 255, 157, ${Math.random() * 0.3 + 0.1});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: float ${Math.random() * 5 + 5}s ease-in-out infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            container.appendChild(particle);
        }
    }

    startTerminal() {
        const terminal = document.getElementById('recon-terminal');
        if (!terminal) return;

        let isActive = true;
        // Simple cleanup check if terminal is removed from DOM to stop loop
        const observer = new MutationObserver((mutations) => {
            if (!document.contains(terminal)) {
                isActive = false;
                observer.disconnect();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });

        const logs = [
            { type: 'info', msg: 'Initializing Aegis Core...' },
            { type: 'success', msg: 'System Online' },
            { type: 'info', msg: 'Ready for scanning.' }
        ];
        // Reduced logs for cleaner look and performance

        let i = 0;
        const addLog = () => {
            if (!isActive || !document.getElementById('recon-terminal')) return;

            const entry = logs[i % logs.length];
            const line = document.createElement('div');
            line.style.marginBottom = '0.5rem';
            line.style.animation = 'fadeIn 0.3s forwards';

            // ... (keep logging logic simple)
            let icon = '$';
            let color = 'var(--primary)';

            if (entry.type === 'error') { icon = '✖'; color = '#ff4757'; }
            if (entry.type === 'success') { icon = '✓'; color = '#2ed573'; }

            const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });

            line.innerHTML = `
                <span style="color: var(--text-muted); font-size: 0.75rem;">[${timestamp}]</span> 
                <span style="color: ${color}; margin-right: 0.5rem; font-weight: bold;">${icon}</span> 
                <span style="color: ${entry.type === 'info' ? 'var(--text-main)' : color}">${entry.msg}</span>
            `;

            terminal.appendChild(line);
            if (terminal.children.length > 5) {
                terminal.removeChild(terminal.firstChild);
            }
            terminal.scrollTop = terminal.scrollHeight;

            i++;
            setTimeout(addLog, 2000);
        };

        addLog();
    }
}

export default new LandingView();
