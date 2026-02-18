import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class FootprintView {
    constructor() {
        this.scanId = null;
        this.isScanning = false;
        this.pollInterval = null;
        this.platforms = [];
    }

    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; min-height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('footprint')}
                <main style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <div style="max-width: 1000px; margin: 0 auto;">
                        <!-- Header -->
                        <div style="margin-bottom: 2rem;">
                            <h1 style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 2rem; color: var(--primary);">fingerprint</span>
                                Digital Footprint Scanner
                            </h1>
                            <p style="color: var(--text-muted);">Analyze your digital presence and discover potential security risks.</p>
                        </div>

                        <!-- Main Content: Form or Results -->
                        <div id="footprint-container">
                            ${this.renderForm()}
                        </div>

                        <!-- History Section -->
                        <div class="glass" style="margin-top: 2rem; padding: 1.5rem; border-radius: 12px;">
                            <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined">history</span>
                                Scan History
                            </h3>
                            <div id="scan-history">
                                <div style="color: var(--text-muted); text-align: center; padding: 1rem;">Loading history...</div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
            ${Components.renderFloatingChat()}
        `;
    }

    renderForm() {
        return `
            <div class="glass" style="padding: 2rem; border-radius: 12px;">
                <form id="footprint-form">
                    <!-- Consent Notice -->
                    <div style="background: rgba(0, 255, 157, 0.1); border: 1px solid rgba(0, 255, 157, 0.3); border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;">
                        <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                            <span class="material-symbols-outlined" style="color: var(--primary);">info</span>
                            <div>
                                <strong style="color: var(--primary);">Privacy Notice</strong>
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">
                                    This scan uses publicly available information to assess your digital footprint. 
                                    No data is shared with third parties. Results are stored securely and can be deleted anytime.
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Email, Username & Phone -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Email Address *</label>
                            <input type="email" id="scan-email" required style="width: 100%;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Common Username *</label>
                            <input type="text" id="scan-username" required minlength="2" maxlength="50" style="width: 100%;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Mobile Number (Optional)</label>
                            <input type="tel" id="scan-phone" placeholder="+1 234 567 890" style="width: 100%;">
                        </div>
                    </div>

                    <!-- Social Platforms -->
                    <div style="margin-bottom: 1.5rem;">
                        <label style="display: block; margin-bottom: 0.75rem; font-weight: 500;">Social Platforms You Use</label>
                        <div id="platforms-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 1rem; max-height: 300px; overflow-y: auto; padding-right: 0.5rem;">
                            <!-- Platforms loaded dynamically -->
                            <div style="color: var(--text-muted);">Loading platforms...</div>
                        </div>
                    </div>

                    <!-- Additional Questions -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Do you reuse passwords?</label>
                            <div style="display: flex; gap: 1.5rem;">
                                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                                    <input type="radio" name="password-reuse" value="yes"> Yes
                                </label>
                                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                                    <input type="radio" name="password-reuse" value="no" checked> No
                                </label>
                            </div>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Email in public directories?</label>
                            <div style="display: flex; gap: 1.2rem; flex-wrap: wrap;">
                                <label style="display: flex; align-items: center; gap: 0.4rem; cursor: pointer;">
                                    <input type="radio" name="email-public" value="yes"> Yes
                                </label>
                                <label style="display: flex; align-items: center; gap: 0.4rem; cursor: pointer;">
                                    <input type="radio" name="email-public" value="no"> No
                                </label>
                                <label style="display: flex; align-items: center; gap: 0.4rem; cursor: pointer;">
                                    <input type="radio" name="email-public" value="unsure" checked> Unsure
                                </label>
                            </div>
                        </div>
                    </div>

                    <!-- Consent Checkbox -->
                    <div style="margin-bottom: 1.5rem;">
                        <label style="display: flex; align-items: flex-start; gap: 0.75rem; cursor: pointer; padding: 0.5rem; background: rgba(255,255,255,0.02); border-radius: 6px;">
                            <input type="checkbox" id="consent-checkbox" required style="margin-top: 0.25rem;">
                            <span style="font-size: 0.9rem; line-height: 1.4; color: var(--text-muted);">
                                I consent to scanning my digital footprint using publicly available information. 
                                I understand that this is for security assessment purposes only.
                            </span>
                        </label>
                    </div>

                    <!-- Submit Button -->
                    <button type="submit" id="scan-btn" class="btn" style="width: 100%; padding: 1rem; font-size: 1rem;">
                        <span class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem;">search</span>
                        Start Scan
                    </button>
                </form>
            </div>
        `;
    }

    renderScanProgress(progress, status) {
        return `
            <div class="glass" style="padding: 2rem; border-radius: 12px; text-align: center;">
                <div style="margin-bottom: 1.5rem;">
                    <div class="scanning-animation" style="width: 100px; height: 100px; margin: 0 auto; border-radius: 50%; border: 4px solid rgba(0, 255, 157, 0.2); border-top-color: var(--primary); animation: spin 1s linear infinite;"></div>
                </div>
                <h3 style="margin-bottom: 0.5rem;">Scanning Your Digital Footprint</h3>
                <p style="color: var(--text-muted); margin-bottom: 1.5rem;">${status || 'Analyzing...'}</p>
                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 10px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, var(--primary), var(--secondary)); height: 100%; width: ${progress}%; transition: width 0.3s;"></div>
                </div>
                <p style="margin-top: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">${progress}% Complete</p>
            </div>
            <style>
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            </style>
        `;
    }

    renderResults(data) {
        const scoreColor = data.score >= 70 ? 'var(--primary)' : data.score >= 40 ? '#ffa502' : '#ff4757';

        return `
            <div id="report-container">
                <!-- Score Card -->
                <div class="glass" style="padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem;">
                        <div>
                            <h2 style="margin-bottom: 0.5rem;">Security Score</h2>
                            <p style="color: var(--text-muted);">Based on ${data.findings?.length || 0} findings</p>
                        </div>
                        <div style="position: relative; width: 150px; height: 150px;">
                            <canvas id="score-chart"></canvas>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="font-size: 2.5rem; font-weight: bold; color: ${scoreColor};">${data.score}</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted);">/ 100</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Findings -->
                <div class="glass" style="padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;">
                    <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span class="material-symbols-outlined">search</span>
                        Findings (${data.findings?.length || 0})
                    </h3>
                    ${data.findings && data.findings.length > 0 ? `
                        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                            ${data.findings.map(f => this.renderFinding(f)).join('')}
                        </div>
                    ` : `
                        <p style="color: var(--text-muted); text-align: center; padding: 1rem;">No significant findings detected. Great job!</p>
                    `}
                </div>

                <!-- Recommendations -->
                <div class="glass" style="padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;">
                    <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span class="material-symbols-outlined">lightbulb</span>
                        Recommendations
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                        ${(data.recommendations || []).map(r => `
                            <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                                <span style="font-size: 1.2rem;">${r.charAt(0)}</span>
                                <span>${r.slice(2)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Actions -->
                <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                    <button id="download-pdf-btn" class="btn" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                        <span class="material-symbols-outlined">picture_as_pdf</span>
                        EXPORT PDF
                    </button>
                    <button id="new-scan-btn" class="btn-outline" style="flex: 1;">
                        <span class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem;">refresh</span>
                        New Scan
                    </button>
                </div>
            </div>
        `;
    }

    renderFinding(finding) {
        const severityColors = {
            low: '#2ed573',
            medium: '#ffa502',
            high: '#ff6348',
            critical: '#ff4757'
        };
        const color = severityColors[finding.severity] || '#666';

        return `
            <div style="display: flex; align-items: center; gap: 1rem; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid ${color};">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                        <strong>${Utils.escapeHtml(finding.title)}</strong>
                        <span style="font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; background: ${color}20; color: ${color}; text-transform: uppercase;">${finding.severity}</span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-muted);">${Utils.escapeHtml(finding.description)}</p>
                </div>
                ${finding.url ? `<a href="${finding.url}" target="_blank" class="btn-outline" style="padding: 0.5rem; font-size: 0.8rem;">View</a>` : ''}
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());

        // Load platforms
        await this.loadPlatforms();

        // Load history
        await this.loadHistory();

        // Form submission
        document.getElementById('footprint-form')?.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async loadPlatforms() {
        try {
            const data = await Api.get('/footprint/platforms');
            this.platforms = data.platforms || [];

            const grid = document.getElementById('platforms-grid');
            if (grid) {
                grid.innerHTML = this.platforms.map(p => `
                    <label style="display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem; cursor: pointer;">
                        <input type="checkbox" name="platform" value="${p.id}" style="margin: 0;">
                        <span class="material-symbols-outlined" style="font-size: 1.1rem; color: var(--primary);">${p.icon}</span>
                        <span style="font-size: 0.85rem; color: var(--text-main);">${p.name}</span>
                    </label>
                `).join('');
            }
        } catch (error) {
            console.error('Failed to load platforms:', error);
        }
    }

    async loadHistory() {
        try {
            const history = await Api.get('/footprint/history');
            const container = document.getElementById('scan-history');

            if (!history || history.length === 0) {
                container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 1rem;">No previous scans found.</p>';
                return;
            }

            container.innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    ${history.map(s => `
                        <div class="history-item" data-id="${s.id}" style="display: flex; align-items: center; justify-content: space-between; padding: 0.75rem; background: rgba(255,255,255,0.03); border-radius: 8px; cursor: pointer; transition: background 0.2s;"
                             onmouseover="this.style.background='rgba(255,255,255,0.08)'" onmouseout="this.style.background='rgba(255,255,255,0.03)'">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <div style="width: 40px; height: 40px; border-radius: 50%; background: ${s.score >= 70 ? 'rgba(0,255,157,0.2)' : s.score >= 40 ? 'rgba(255,165,2,0.2)' : 'rgba(255,71,87,0.2)'}; display: flex; align-items: center; justify-content: center;">
                                    <span style="font-weight: bold; color: ${s.score >= 70 ? 'var(--primary)' : s.score >= 40 ? '#ffa502' : '#ff4757'};">${s.score}</span>
                                </div>
                                <div>
                                    <div style="font-weight: 500;">${Utils.escapeHtml(s.email_scanned)}</div>
                                    <div style="font-size: 0.8rem; color: var(--text-muted);">${s.findings_count} findings • ${new Date(s.started_at).toLocaleDateString()}</div>
                                </div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; background: ${s.status === 'completed' ? 'rgba(0,255,157,0.2)' : 'rgba(255,165,2,0.2)'}; color: ${s.status === 'completed' ? 'var(--primary)' : '#ffa502'};">${s.status}</span>
                                <button class="delete-history-btn" data-id="${s.id}" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 0.25rem;" title="Delete">
                                    <span class="material-symbols-outlined" style="font-size: 1.2rem;">delete</span>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;

            // Add click listeners for viewing
            container.querySelectorAll('.history-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    if (!e.target.closest('.delete-history-btn')) {
                        this.loadScanResults(item.dataset.id);
                    }
                });
            });

            // Add click listeners for deleting
            container.querySelectorAll('.delete-history-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm('Delete this scan?')) {
                        try {
                            await Api.delete(`/footprint/scan/${btn.dataset.id}`);
                            await this.loadHistory();
                            Utils.showToast('Scan deleted', 'success');
                        } catch (err) {
                            Utils.showToast('Failed to delete', 'error');
                        }
                    }
                });
            });
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }

    async handleSubmit(e) {
        e.preventDefault();

        const email = document.getElementById('scan-email').value.trim();
        const username = document.getElementById('scan-username').value.trim();
        const phoneNumber = document.getElementById('scan-phone').value.trim();
        const consent = document.getElementById('consent-checkbox').checked;

        const platforms = Array.from(document.querySelectorAll('input[name="platform"]:checked')).map(cb => cb.value);
        const reusesPasswords = document.querySelector('input[name="password-reuse"]:checked')?.value === 'yes';
        const emailInDirectories = document.querySelector('input[name="email-public"]:checked')?.value || 'unsure';

        if (!consent) {
            Utils.showToast('Please provide consent to proceed', 'error');
            return;
        }

        this.isScanning = true;
        document.getElementById('footprint-container').innerHTML = this.renderScanProgress(0, 'Initializing scan...');

        try {
            const response = await Api.post('/footprint/scan', {
                email,
                username,
                phone_number: phoneNumber || null,
                platforms,
                reuses_passwords: reusesPasswords,
                email_in_directories: emailInDirectories,
                consent_given: consent
            });

            this.scanId = response.id;
            this.startPolling();
        } catch (error) {
            Utils.showToast('Failed to start scan: ' + error.message, 'error');
            document.getElementById('footprint-container').innerHTML = this.renderForm();
            this.isScanning = false;
        }
    }

    startPolling() {
        this.pollInterval = setInterval(async () => {
            try {
                const data = await Api.get(`/footprint/scan/${this.scanId}`);

                if (data.status === 'running') {
                    document.getElementById('footprint-container').innerHTML = this.renderScanProgress(data.progress, 'Analyzing your digital presence...');
                } else if (data.status === 'completed') {
                    this.stopPolling();
                    this.showResults(data);
                } else if (data.status === 'failed') {
                    this.stopPolling();
                    Utils.showToast('Scan failed: ' + (data.error_message || 'Unknown error'), 'error');
                    document.getElementById('footprint-container').innerHTML = this.renderForm();
                }
            } catch (error) {
                this.stopPolling();
                Utils.showToast('Failed to get scan status', 'error');
            }
        }, 1500);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        this.isScanning = false;
    }

    async loadScanResults(scanId) {
        try {
            const data = await Api.get(`/footprint/scan/${scanId}`);
            if (data.status === 'completed') {
                this.showResults(data);
            } else {
                Utils.showToast('Scan is not yet complete', 'info');
            }
        } catch (error) {
            Utils.showToast('Failed to load scan results', 'error');
        }
    }

    showResults(data) {
        document.getElementById('footprint-container').innerHTML = this.renderResults(data);
        this.loadHistory();
        this.initChart(data.score);
        this.initResultListeners();
    }

    initChart(score) {
        const ctx = document.getElementById('score-chart');
        if (!ctx) return;

        const scoreColor = score >= 70 ? '#00ff9d' : score >= 40 ? '#ffa502' : '#ff4757';

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [scoreColor, 'rgba(255,255,255,0.1)'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '80%',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }

    initResultListeners() {
        document.getElementById('download-pdf-btn')?.addEventListener('click', () => this.downloadPDF());
        document.getElementById('new-scan-btn')?.addEventListener('click', () => {
            document.getElementById('footprint-container').innerHTML = this.renderForm();
            this.loadPlatforms();
            document.getElementById('footprint-form')?.addEventListener('submit', (e) => this.handleSubmit(e));
        });
    }

    async downloadPDF() {
        const reportEl = document.getElementById('report-container');
        if (!reportEl) return;

        Utils.showToast('Generating PDF...', 'info');

        try {
            // Capture full element with scrolling support
            const canvas = await html2canvas(reportEl, {
                backgroundColor: '#0a0a0f',
                scale: 2,
                scrollY: -window.scrollY,
                windowHeight: reportEl.scrollHeight,
                height: reportEl.scrollHeight
            });

            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pageWidth = pdf.internal.pageSize.getWidth();
            const pageHeight = pdf.internal.pageSize.getHeight();
            const margin = 10;
            const contentWidth = pageWidth - (margin * 2);
            const contentHeight = pageHeight - (margin * 2) - 10;

            const imgWidth = contentWidth;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            // Calculate how many pages we need
            const totalPDFPages = Math.ceil(imgHeight / contentHeight);

            for (let page = 0; page < totalPDFPages; page++) {
                if (page > 0) pdf.addPage();

                // Fill background
                pdf.setFillColor(10, 10, 15);
                pdf.rect(0, 0, pageWidth, pageHeight, 'F');

                // Calculate the portion of the image to show on this page
                const sourceY = page * (canvas.height / totalPDFPages);
                const sourceHeight = canvas.height / totalPDFPages;

                // Create a temporary canvas for this page's portion
                const pageCanvas = document.createElement('canvas');
                pageCanvas.width = canvas.width;
                pageCanvas.height = sourceHeight;
                const ctx = pageCanvas.getContext('2d');

                // Draw the portion of the original canvas
                ctx.drawImage(
                    canvas,
                    0, sourceY,
                    canvas.width, sourceHeight,
                    0, 0,
                    canvas.width, sourceHeight
                );

                // Add this page's image portion
                const pageImgData = pageCanvas.toDataURL('image/png');
                pdf.addImage(pageImgData, 'PNG', margin, margin, imgWidth, contentHeight);
            }

            // Page numbers
            const totalPages = pdf.internal.getNumberOfPages();
            for (let i = 1; i <= totalPages; i++) {
                pdf.setPage(i);
                pdf.setFontSize(8);
                pdf.setTextColor(100, 100, 100);
                pdf.text(`Page ${i} of ${totalPages} | Aegis Digital Footprint`, pageWidth / 2, pageHeight - 5, { align: 'center' });
            }

            pdf.save(`digital-footprint-report_${Date.now()}.pdf`);
            Utils.showToast('PDF downloaded successfully!', 'success');
        } catch (error) {
            Utils.showToast('Failed to generate PDF: ' + error.message, 'error');
            console.error(error);
        }
    }
}

export default new FootprintView();
