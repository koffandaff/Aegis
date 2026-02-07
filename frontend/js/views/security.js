import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class SecurityView {
    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('security')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                        <h1 class="page-title fade-in">Advanced Security Audit</h1>
                    </div>
                    
                    <div class="card glass fade-in" style="max-width: 900px; margin-bottom: 2rem;">
                        <form id="security-form" style="display: grid; grid-template-columns: 2fr 4fr 1fr; gap: 1rem; align-items: end;">
                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.8rem;">AUDIT VECTOR</label>
                                <select id="sec-type" style="width: 100%; padding: 0.8rem; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: white; border-radius: 4px;">
                                    <option value="ssl">SSL/TLS Configuration</option>
                                    <option value="headers">HTTP Security Headers</option>
                                    <option value="tech-stack">Technology Stack Detection</option>
                                    <option value="http-security">Full HTTP Security Audit</option>
                                </select>
                            </div>

                            <div>
                                <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.8rem;">TARGET ASSET</label>
                                <input type="text" id="sec-target" required 
                                    style="width: 100%; padding: 0.8rem; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: white; border-radius: 4px; font-family: 'JetBrains Mono';">
                            </div>

                            <button type="submit" class="btn" id="sec-btn" style="height: 42px;">AUDIT</button>
                        </form>
                    </div>

                    <!-- Security Report Container -->
                    <div id="sec-results" class="fade-in" style="display: none; max-width: 900px;">
                        
                        <!-- Report Controls -->
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <div class="tabs">
                                <button class="tab-btn active" data-tab="report">STRATEGIC REPORT</button>
                                <button class="tab-btn" data-tab="raw">RAW DATA</button>
                            </div>
                            <button onclick="downloadSecurityPDF()" style="background: var(--primary); color: black; border: none; padding: 0.5rem 1rem; border-radius: 4px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.1rem;">picture_as_pdf</span> EXPORT PDF
                            </button>
                        </div>

                        <div class="tab-content" id="tab-report" style="display: block;">
                            <div id="security-report" class="card glass" style="padding: 0;">
                                
                                <!-- Report Header -->
                                <div style="padding: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2);">
                                    <div>
                                        <div style="color: var(--text-muted); font-size: 0.8rem; letter-spacing: 1px;">AUDIT TARGET</div>
                                        <div id="report-target" style="font-size: 1.2rem; font-weight: bold; color: var(--primary);">Loading...</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="color: var(--text-muted); font-size: 0.8rem;">TIMESTAMP</div>
                                        <div id="report-date" style="font-family: 'JetBrains Mono'; font-size: 0.9rem;">--/--/----</div>
                                    </div>
                                </div>

                                <!-- Scorecard Area -->
                                <div style="padding: 2rem; display: flex; gap: 2rem; align-items: center; justify-content: center; background: radial-gradient(circle at center, rgba(0, 255, 157, 0.05) 0%, transparent 70%);">
                                    <div style="text-align: center;">
                                        <div id="security-grade" style="font-size: 4rem; font-weight: bold; color: var(--primary); text-shadow: 0 0 20px rgba(0,255,157,0.3);">A</div>
                                        <div style="font-size: 0.8rem; color: var(--text-muted); letter-spacing: 2px;">SECURITY GRADE</div>
                                    </div>
                                    <div style="height: 60px; width: 1px; background: rgba(255,255,255,0.1);"></div>
                                    <div style="width: 300px; height: 150px;">
                                        <canvas id="sec-chart"></canvas>
                                    </div>
                                </div>

                                <!-- Accordion Sections -->
                                <div style="padding: 1.5rem;">
                                    
                                    <!-- SSL/TLS Section -->
                                    <div class="accordion-item" id="acc-ssl" style="display: none;">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span>🔒 SSL/TLS CONFIGURATION</span>
                                            <span class="acc-badge">SECURE</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="ssl-content" style="padding-top: 1rem; color: var(--text-main);"></div>
                                        </div>
                                    </div>

                                    <!-- Headers Section -->
                                    <div class="accordion-item" id="acc-headers" style="display: none;">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span>🛡️ HTTP SECURITY HEADERS</span>
                                            <span class="acc-badge">ANALYSIS</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="headers-content" style="padding-top: 1rem;"></div>
                                        </div>
                                    </div>

                                    <!-- Tech Stack -->
                                    <div class="accordion-item" id="acc-tech" style="display: none;">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span>💻 TECHNOLOGY STACK</span>
                                            <span class="acc-badge">DETECTED</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="tech-content" style="padding-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap;"></div>
                                        </div>
                                    </div>

                                    <!-- Phishing Indicators -->
                                    <div class="accordion-item" id="acc-phishing" style="display: none;">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span>🎣 PHISHING INDICATORS</span>
                                            <span class="acc-badge">CHECK</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="phishing-content" style="padding-top: 1rem;"></div>
                                        </div>
                                    </div>

                                </div>
                            </div>
                        </div>

                        <div class="tab-content" id="tab-raw" style="display: none;">
                            <pre id="json-output" class="json-box"></pre>
                            <button onclick="downloadJSON()" class="btn" style="margin-top: 1rem;">DOWNLOAD JSON</button>
                        </div>

                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        const form = document.getElementById('security-form');
        const btn = document.getElementById('sec-btn');
        const resultsArea = document.getElementById('sec-results');
        const jsonOutput = document.getElementById('json-output');

        // Tab Switching
        document.querySelectorAll('.tab-btn').forEach(button => {
            button.onclick = () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
                button.classList.add('active');
                document.getElementById(`tab-${button.dataset.tab}`).style.display = 'block';
            };
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const type = document.getElementById('sec-type').value;
            const target = document.getElementById('sec-target').value;

            btn.textContent = 'AUDITING...';
            btn.disabled = true;
            resultsArea.style.display = 'none';

            try {
                let body = {};
                const cleanUrl = target.startsWith('http') ? target : `https://${target}`;
                const cleanDomain = target.replace(/^https?:\/\//, '').split('/')[0];

                // Handle different request bodies per type
                if (type === 'ssl') {
                    body = { domain: cleanDomain, port: 443 };
                } else if (type === 'headers') {
                    body = { url: cleanUrl };
                } else if (type === 'http-security') {
                    body = { url: cleanUrl };
                } else if (type === 'tech-stack') {
                    body = { domain: cleanDomain };
                }

                const response = await Api.post(`/security/${type}`, body);

                if (response) {
                    // Populate Header
                    document.getElementById('report-target').textContent = target.toUpperCase();
                    document.getElementById('report-date').textContent = new Date().toLocaleString();

                    // Populate JSON
                    jsonOutput.innerHTML = Utils.formatJSON(response);

                    // Populate Report
                    populateSecurityReport(type, response);

                    resultsArea.style.display = 'block';
                    Utils.showToast('Security Audit Completed', 'success');
                }
            } catch (error) {
                Utils.showToast(error.message, 'error');
                console.error(error);
            } finally {
                btn.textContent = 'AUDIT';
                btn.disabled = false;
            }
        });

        // Global Helpers
        window.toggleAccordion = function (header) {
            header.parentElement.classList.toggle('active');
        };

        window.downloadJSON = function () {
            const content = jsonOutput.innerText;
            const blob = new Blob([content], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `security_audit_${Date.now()}.json`;
            a.click();
        };

        window.downloadSecurityPDF = async function () {
            Utils.showToast('Compiling Security Report...', 'info');
            const { jsPDF } = window.jspdf;
            const element = document.getElementById('security-report');

            // Expand all for PDF capture
            document.querySelectorAll('.accordion-item').forEach(i => i.classList.add('active'));

            try {
                // Capture full element height
                const canvas = await html2canvas(element, {
                    backgroundColor: '#0a0a0b',
                    scale: 2,
                    useCORS: true,
                    scrollY: -window.scrollY,
                    windowHeight: element.scrollHeight,
                    height: element.scrollHeight
                });

                const imgData = canvas.toDataURL('image/png');
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
                    pdf.setFillColor(10, 10, 11);
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
                    pdf.text(`Page ${i} of ${totalPages} | Fsociety Security Audit`, pageWidth / 2, pageHeight - 5, { align: 'center' });
                }

                pdf.save(`fsociety_security_report_${Date.now()}.pdf`);
                Utils.showToast('Report Exported Successfully', 'success');
            } catch (e) {
                console.error('PDF Export Error:', e);
                Utils.showToast('PDF Export Error: ' + e.message, 'error');
            }
        };
    }
}

function populateSecurityReport(type, data) {
    // Hide all first
    ['acc-ssl', 'acc-headers', 'acc-tech', 'acc-phishing'].forEach(id => {
        document.getElementById(id).style.display = 'none';
        document.getElementById(id).classList.remove('active');
    });

    let grade = 'A';
    let gradeColor = '#00ff9d';
    let chartData = [100, 0]; // Safe, Risk

    // SSL Report
    if (type === 'ssl') {
        const item = document.getElementById('acc-ssl');
        item.style.display = 'block';
        item.classList.add('active');

        const cert = data.certificate || {};
        const vulns = data.vulnerabilities || [];
        const isValid = !data.error && !vulns.some(v => v.affected);

        grade = isValid ? 'A' : 'F';
        gradeColor = isValid ? '#00ff9d' : '#ff4757';
        chartData = isValid ? [100, 0] : [20, 80];

        item.querySelector('.acc-badge').textContent = isValid ? 'SECURE' : 'VULNERABLE';
        item.querySelector('.acc-badge').style.background = gradeColor;

        const content = document.getElementById('ssl-content');
        content.innerHTML = `
            <div class="grid-list">
                <div class="geo-info">
                    <div><label>ISSUER</label> ${cert.issuer?.organizationName || 'Unknown'}</div>
                    <div><label>VALID FROM</label> ${cert.not_before?.split('T')[0]}</div>
                    <div><label>VALID UNTIL</label> ${cert.not_after?.split('T')[0]}</div>
                    <div><label>PROTOCOL</label> ${data.tls_versions?.find(v => v.preferred)?.version || 'Unknown'}</div>
                </div>
                <div>
                    <strong style="color: var(--secondary)">Vulnerabilities Checked:</strong>
                    <ul style="list-style: none; padding: 0; margin-top: 0.5rem;">
                         ${vulns.map(v => `
                            <li style="margin-bottom: 0.2rem; color: ${v.affected ? '#ff4757' : '#888'}; display: flex; align-items: center; gap: 0.4rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.1rem;">
                                    ${v.affected ? 'warning' : 'check_circle'}
                                </span> 
                                ${v.name.toUpperCase()}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    // Headers Report
    else if (type === 'headers' || type === 'http-security') {
        const item = document.getElementById('acc-headers');
        item.style.display = 'block';
        item.classList.add('active');

        const headers = data.security_headers || [];
        const score = data.overall_score || (headers.filter(h => h.present).length / headers.length);

        grade = score > 0.8 ? 'A' : score > 0.6 ? 'B' : score > 0.4 ? 'C' : 'F';
        gradeColor = score > 0.6 ? '#00ff9d' : score > 0.4 ? '#ffa502' : '#ff4757';
        chartData = [Math.round(score * 100), 100 - Math.round(score * 100)];

        item.querySelector('.acc-badge').textContent = `SCORE: ${Math.round(score * 100)}/100`;
        item.querySelector('.acc-badge').style.background = gradeColor;

        const content = document.getElementById('headers-content');
        content.innerHTML = `
            <div style="display: grid; gap: 0.5rem;">
                ${headers.map(h => `
                    <div style="display: flex; justify-content: space-between; padding: 0.5rem; background: rgba(255,255,255,0.02); border-left: 2px solid ${h.present ? '#00ff9d' : '#ff4757'}">
                        <span>${h.header}</span>
                        <span style="color: ${h.present ? '#00ff9d' : '#888'}">${h.present ? 'DETECTED' : 'MISSING'}</span>
                    </div>
                `).join('')}
            </div>
            ${data.warnings?.length ? `
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(255, 71, 87, 0.1); border-radius: 4px;">
                    <strong style="color: #ff4757">Recommendations:</strong>
                    <ul style="margin-top: 0.5rem; padding-left: 1.2rem;">
                        ${data.warnings.map(w => `<li>${w}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
    }

    // Tech Stack
    else if (type === 'tech-stack') {
        const item = document.getElementById('acc-tech');
        item.style.display = 'block';
        item.classList.add('active');

        const techs = data.technologies || [];
        grade = techs.length > 0 ? 'INFO' : '-';
        gradeColor = '#00a8ff';
        chartData = [techs.length * 10, 100 - (techs.length * 10)]; // Dummy visualization

        item.querySelector('.acc-badge').textContent = `${techs.length} TECHNOLOGIES`;
        item.querySelector('.acc-badge').style.background = gradeColor;

        const content = document.getElementById('tech-content');
        content.innerHTML = techs.length ? techs.map(t => `
            <div class="sub-pill" style="border-color: var(--secondary);">
                <strong style="color: var(--primary)">${t.name}</strong> 
                <span style="opacity: 0.7; font-size: 0.7rem;">${t.version || ''}</span>
            </div>
        `).join('') : '<div style="color: #888">No specific technologies detected.</div>';
    }

    // Phishing
    else if (type === 'phishing/check') {
        const item = document.getElementById('acc-phishing');
        item.style.display = 'block';
        item.classList.add('active');

        const isSafe = !data.suspicious;
        grade = isSafe ? 'SAFE' : 'RISK';
        gradeColor = isSafe ? '#00ff9d' : '#ff4757';
        chartData = isSafe ? [100, 0] : [10, 90];

        item.querySelector('.acc-badge').textContent = grade;
        item.querySelector('.acc-badge').style.background = gradeColor;

        document.getElementById('phishing-content').innerHTML = `
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 1.5rem; color: ${gradeColor}; margin-bottom: 0.5rem;">
                    ${isSafe ? 'No Phishing Indicators Found' : 'Potential Phishing Detected'}
                </div>
                <div style="color: #888;">${data.details || 'URL analysis clean.'}</div>
                ${data.keywords_found ? `<div style="margin-top: 1rem;">Keywords: ${data.keywords_found.join(', ')}</div>` : ''}
            </div>
        `;
    }

    // Update Scorecard
    const gradeEl = document.getElementById('security-grade');
    gradeEl.textContent = grade;
    gradeEl.style.color = gradeColor;
    gradeEl.style.textShadow = `0 0 20px ${gradeColor}40`;

    // Update Chart
    renderSecurityChart(chartData, gradeColor);
}

function renderSecurityChart(data, color) {
    const ctx = document.getElementById('sec-chart').getContext('2d');
    if (window.mySecChart) window.mySecChart.destroy();

    window.mySecChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Security Score', 'Risk Exposure'],
            datasets: [{
                data: data,
                backgroundColor: [color, 'rgba(255, 255, 255, 0.05)'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { display: false }
            }
        }
    });
}

export default new SecurityView();
