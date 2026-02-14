import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class ScanView {
    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('scan')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">Network Intelligence</h1>
                    
                    <div class="card glass fade-in" style="max-width: 800px;">
                        <form id="scan-form">
                            <div style="margin-bottom: 1.5rem;">
                                <label style="display: block; margin-bottom: 0.5rem;">Scan Type</label>
                                <select id="scan-type">
                                    <option value="domain">Full Domain Scan</option>
                                    <option value="dns">DNS Lookup</option>
                                    <option value="whois">WHOIS Lookup</option>
                                    <option value="subdomains">Subdomain Discovery</option>
                                    <option value="ip">IP Intelligence</option>
                                    <option value="ports">Port Scan</option>
                                </select>
                            </div>

                            <div style="margin-bottom: 2rem;">
                                <label style="display: block; margin-bottom: 0.5rem;">Target</label>
                                <input type="text" id="target" required placeholder="example.com or 8.8.8.8">
                            </div>

                            <button type="submit" class="btn" id="scan-btn">INITIATE SCAN</button>

                            <!-- Progress Bar -->
                            <div style="margin-top: 1rem;">
                                ${Components.renderProgressBar('scan-progress')}
                            </div>
                        </form>
                    </div>

                    <div id="scan-results" class="card glass fade-in" style="display: none; margin-top: 2rem; border-top: 4px solid var(--primary); padding: 0;">
                        <!-- Report Header -->
                        <div style="padding: 1.5rem; display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <div>
                                <h3 style="color: var(--secondary); margin: 0; font-family: 'JetBrains Mono'; letter-spacing: 1px;">STRATEGIC INTELLIGENCE REPORT</h3>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">TARGET: <span id="report-target" style="color: var(--primary);">N/A</span> | <span id="report-date">DATE</span></div>
                            </div>
                            <div class="result-actions" style="display: flex; gap: 0.8rem;">
                                <button class="btn-sm" style="background: var(--primary); color: black; display: flex; align-items: center; gap: 0.5rem;" onclick="downloadPDF()">
                                    <span class="material-symbols-outlined" style="font-size: 1.1rem;">picture_as_pdf</span>
                                    GENERATE PDF
                                </button>
                                <button class="btn-outline btn-sm" onclick="document.querySelector('[data-tab=raw]').click()">RAW JSON</button>
                            </div>
                        </div>

                        <!-- Professional Report Container -->
                        <div id="professional-report" style="padding: 1.5rem;">
                            <!-- Tabs (Hidden in PDF) -->
                            <div class="tabs no-print" style="display: flex; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <button class="tab-btn active" data-tab="report">ASSESSMENT</button>
                                <button class="tab-btn" data-tab="raw">SOURCE</button>
                            </div>

                            <div id="tab-report" class="tab-content">
                                <!-- Analytics Scorecards -->
                                <div id="scan-scorecards" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                                    <div class="scorecard glass" style="padding: 1.2rem; border-radius: 8px; border-left: 4px solid var(--primary); text-align: center;">
                                        <div class="scorecard-value" id="sc-ports" style="font-size: 2rem; font-weight: bold; color: var(--primary);">--</div>
                                        <div class="scorecard-label" style="font-size: 0.7rem; color: var(--text-muted); letter-spacing: 1px;">OPEN PORTS</div>
                                    </div>
                                    <div class="scorecard glass" style="padding: 1.2rem; border-radius: 8px; border-left: 4px solid var(--secondary); text-align: center;">
                                        <div class="scorecard-value" id="sc-subs" style="font-size: 2rem; font-weight: bold; color: var(--secondary);">--</div>
                                        <div class="scorecard-label" style="font-size: 0.7rem; color: var(--text-muted); letter-spacing: 1px;">SUBDOMAINS</div>
                                    </div>
                                    <div class="scorecard glass" style="padding: 1.2rem; border-radius: 8px; border-left: 4px solid #ffa502; text-align: center;">
                                        <div class="scorecard-value" id="sc-dns" style="font-size: 2rem; font-weight: bold; color: #ffa502;">--</div>
                                        <div class="scorecard-label" style="font-size: 0.7rem; color: var(--text-muted); letter-spacing: 1px;">DNS RECORDS</div>
                                    </div>
                                    <div class="scorecard glass" style="padding: 1.2rem; border-radius: 8px; border-left: 4px solid #ff4757; text-align: center;">
                                        <div class="scorecard-value" id="sc-risk" style="font-size: 2rem; font-weight: bold; color: #ff4757;">--</div>
                                        <div class="scorecard-label" style="font-size: 0.7rem; color: var(--text-muted); letter-spacing: 1px;">RISK SCORE</div>
                                    </div>
                                </div>
                                
                                <!-- Top Level Summary -->
                                <div id="analysis-summary" class="glass" style="padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid var(--secondary); background: rgba(0, 255, 157, 0.05); font-family: 'Inter';">
                                </div>

                                <!-- Accordion Sections -->
                                <div class="report-accordion">
                                    <!-- A1: Subdomains -->
                                    <div class="accordion-item glass" id="acc-subdomains">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span><i class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem; font-size: 1.2rem;">lan</i> SUBDOMAIN MAP</span>
                                            <span class="acc-badge" id="badge-subdomains">0 FOUND</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="list-subdomains" class="grid-list"></div>
                                        </div>
                                    </div>

                                    <!-- A2: Services & Ports -->
                                    <div class="accordion-item glass" id="acc-ports">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span><i class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem; font-size: 1.2rem;">router</i> PORT & SERVICE ANALYSIS (NMAP)</span>
                                            <span class="acc-badge" id="badge-ports">0 OPEN</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="list-ports" class="port-grid"></div>
                                            <!-- Chart Container: Relative positioning required for Chart.js responsive mode -->
                                            <div id="scan-chart-container" style="display: none; margin-top: 1.5rem; position: relative; height: 300px; width: 100%; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px;">
                                                <canvas id="scan-chart"></canvas>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- A3: Infrastructure & Geolocation -->
                                    <div class="accordion-item glass" id="acc-geo">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span><i class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem; font-size: 1.2rem;">public</i> GEOLOCATION & NETWORK INTEL</span>
                                            <span class="acc-badge" id="badge-geo">READY</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="geo-content" class="geo-info"></div>
                                        </div>
                                    </div>

                                    <!-- A4: DNS Configuration -->
                                    <div class="accordion-item glass" id="acc-dns">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span><i class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem; font-size: 1.2rem;">dns</i> DNS INFRASTRUCTURE</span>
                                            <span class="acc-badge" id="badge-dns">VERBOSE</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="dns-content" class="dns-grid"></div>
                                        </div>
                                    </div>

                                    <!-- A5: WHOIS Ownership -->
                                    <div class="accordion-item glass" id="acc-whois">
                                        <div class="acc-header" onclick="toggleAccordion(this)">
                                            <span><i class="material-symbols-outlined" style="vertical-align: middle; margin-right: 0.5rem; font-size: 1.2rem;">person_search</i> WHOIS REGISTRY DATA</span>
                                            <span class="acc-badge" id="badge-whois">FETCHED</span>
                                        </div>
                                        <div class="acc-body">
                                            <div id="whois-content" class="whois-list"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div id="tab-raw" class="tab-content" style="display: none;">
                                <pre id="json-output" style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #a0a0a0; max-height: 600px;"></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        const form = document.getElementById('scan-form');
        const btn = document.getElementById('scan-btn');
        const resultsArea = document.getElementById('scan-results');
        const jsonOutput = document.getElementById('json-output');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const type = document.getElementById('scan-type').value;
            const target = document.getElementById('target').value;

            btn.textContent = 'SCANNING...';
            btn.disabled = true;
            resultsArea.style.display = 'none';

            // Start Progress Visualization
            Utils.visualizeProgress('scan-progress', 2500, ['Resolving Host...', 'Mapping Attack Surface...', 'Identifying Services...', 'Finalizing Report...']);

            try {
                let endpoint = `/scans/${type}`;
                let body = {};
                if (type === 'ip') body = { ip: target };
                else if (type === 'ports') body = { target: target, ports: [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 8080], timeout: 2 };
                else body = { domain: target };

                const response = await Api.post(endpoint, body);
                if (response) {
                    const results = response.results;
                    document.getElementById('report-target').textContent = target.toUpperCase();
                    document.getElementById('report-date').textContent = new Date().toLocaleString();

                    // Show IP if available
                    if (results.ip) {
                        Utils.showToast(`Resolved IP: ${results.ip}`, 'info');
                    } else if (results.dns_records && results.dns_records.a_records) {
                        Utils.showToast(`Resolved IP: ${results.dns_records.a_records[0]}`, 'info');
                    }

                    // Debugging Frontend Data
                    console.log('Scan Results received:', results);

                    try {
                        // Populate Summary & JSON
                        if (Utils.renderMarkdown) {
                            document.getElementById('analysis-summary').innerHTML = Utils.renderMarkdown(results.analysis_summary || "No summary available.");
                        } else {
                            document.getElementById('analysis-summary').textContent = results.analysis_summary || "No summary available.";
                        }

                        jsonOutput.innerHTML = Utils.formatJSON(response);

                        // Populate Professional Accordion Sections
                        populateProfessionalReport(type, results);

                        resultsArea.style.display = 'block';

                        // Chart Logic
                        renderUniversalChart(type, results);

                        Utils.showToast('OSINT Aggregation Success', 'success');
                    } catch (renderError) {
                        console.error('Rendering failed:', renderError);
                        alert(`Rendering Error: ${renderError.message}\nCheck console for details.`);
                        Utils.showToast(`Rendering Error: ${renderError.message}`, 'error');
                    }
                }
            } catch (error) {
                Utils.showToast(error.message, 'error');
            } finally {
                btn.textContent = 'INITIATE SCAN';
                btn.disabled = false;
            }
        });

        // Tab Switching Logic
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');

                btn.classList.add('active');
                if (btn.dataset.tab === 'report') document.getElementById('tab-report').style.display = 'block';
                else if (btn.dataset.tab === 'raw') document.getElementById('tab-raw').style.display = 'block';
            };
        });
    }
}

function populateProfessionalReport(type, results) {
    // Determine which sections to show
    const isFullScan = (type === 'domain');
    const sections = {
        'subdomains': document.getElementById('acc-subdomains'),
        'ports': document.getElementById('acc-ports'),
        'geo': document.getElementById('acc-geo'),
        'dns': document.getElementById('acc-dns'),
        'whois': document.getElementById('acc-whois')
    };

    // --- Populate Scorecards ---
    let openPorts = 0;
    let subsCount = 0;
    let dnsCount = 0;
    let riskScore = '--';

    if (type === 'ports') {
        openPorts = results.open_ports?.length || 0;
    } else if (type === 'subdomains') {
        subsCount = results.total_found || 0;
    } else if (type === 'dns') {
        dnsCount = (results.a_records?.length || 0) + (results.mx_records?.length || 0) + (results.ns_records?.length || 0) + (results.txt_records?.length || 0);
    } else if (isFullScan) {
        openPorts = (results.ip_scans && results.ip_scans.length > 0) ? (results.ip_scans[0]?.ports?.open_ports?.length || 0) : 0;
        subsCount = results.subdomains?.total_found || 0;
        const dns = results.dns_records || {};
        dnsCount = (dns.a_records?.length || 0) + (dns.mx_records?.length || 0) + (dns.ns_records?.length || 0) + (dns.txt_records?.length || 0);
        // Calculate simple risk score
        riskScore = Math.min(100, openPorts * 5 + ((results.ip_scans && results.ip_scans.length > 0) ? (results.ip_scans[0]?.ports?.open_ports?.filter(p => p.risk === 'HIGH')?.length || 0) : 0) * 20);
    }

    document.getElementById('sc-ports').textContent = openPorts;
    document.getElementById('sc-subs').textContent = subsCount;
    document.getElementById('sc-dns').textContent = dnsCount;
    document.getElementById('sc-risk').textContent = typeof riskScore === 'number' ? riskScore : '--';

    // Reset visibility and active states
    Object.values(sections).forEach(s => {
        s.style.display = isFullScan ? 'block' : 'none';
        s.classList.remove('active');
    });

    // 1. Subdomains
    const subList = document.getElementById('list-subdomains');
    const subBadge = document.getElementById('badge-subdomains');
    let subs = [];
    if (type === 'subdomains') {
        subs = results.subdomains_found || [];
        sections.subdomains.style.display = 'block';
        sections.subdomains.classList.add('active');
    } else if (isFullScan) {
        subs = results.subdomains?.subdomains_found || [];
    }

    subBadge.textContent = `${subs.length} FOUND`;
    subList.innerHTML = subs.length > 0 ?
        subs.map(s => `<div class="sub-pill">${s}</div>`).join('') :
        '<div style="color: var(--text-muted);">No subdomains discovered.</div>';

    // 2. Ports
    const portList = document.getElementById('list-ports');
    const portBadge = document.getElementById('badge-ports');
    let ports = [];
    if (type === 'ports') {
        ports = results.open_ports || [];
        sections.ports.style.display = 'block';
        sections.ports.classList.add('active');
    } else if (isFullScan && results.ip_scans && results.ip_scans.length > 0) {
        ports = results.ip_scans[0]?.ports?.open_ports || [];
    }

    portBadge.textContent = `${ports.length} OPEN`;
    portList.innerHTML = ports.length > 0 ?
        ports.map(p => `
            <div class="port-card" style="border-color: ${p.risk_color || 'rgba(0, 255, 157, 0.1)'}; background: ${p.risk_color ? p.risk_color + '05' : 'rgba(0, 255, 157, 0.02)'}">
                <div class="port-num" style="color: ${p.risk_color || 'var(--primary)'}">${p.port}</div>
                <div class="port-service">${p.service}</div>
                <div class="port-status" style="color: ${p.risk_color || '#00ff00'}">[ ${p.risk || 'OPEN'} ]</div>
            </div>
        `).join('') :
        '<div style="color: var(--text-muted);">No open ports mapped.</div>';

    // 3. Geolocation
    const geoContent = document.getElementById('geo-content');
    let geo = null;
    if (type === 'ip') {
        geo = results.geolocation;
        sections.geo.style.display = 'block';
        sections.geo.classList.add('active');
    } else if (isFullScan && results.ip_scans && results.ip_scans.length > 0) {
        geo = results.ip_scans[0]?.info?.geolocation;
    }

    if (geo && !geo.note) {
        geoContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div><label>COUNTRY:</label> <span>${geo.country || 'N/A'}</span></div>
                <div><label>CITY:</label> <span>${geo.city || 'N/A'}</span></div>
                <div><label>ISP:</label> <span>${geo.isp || 'N/A'}</span></div>
                <div><label>AS NUMBER:</label> <span>${geo.as || 'N/A'}</span></div>
                <div><label>LATITUDE:</label> <span>${geo.lat || 'N/A'}</span></div>
                <div><label>LONGITUDE:</label> <span>${geo.lon || 'N/A'}</span></div>
            </div>`;
        if (isFullScan) sections.geo.style.display = 'block';
    } else if (type !== 'ip') {
        sections.geo.style.display = 'none';
    }

    // 4. DNS
    const dnsContent = document.getElementById('dns-content');
    const dns = (type === 'dns') ? results : (isFullScan) ? results.dns_records : null;

    if (dns) {
        dnsContent.innerHTML = `
            <div class="dns-section"><strong>A RECORDS:</strong> ${dns.a_records?.join(', ') || 'N/A'}</div>
            <div class="dns-section"><strong>MX RECORDS:</strong> ${dns.mx_records?.join(', ') || 'N/A'}</div>
            <div class="dns-section"><strong>TXT RECORDS:</strong> ${dns.txt_records?.map(t => `<div style="font-size: 0.75rem; color: #888;">${t}</div>`).join('') || 'N/A'}</div>
            <div class="dns-section"><strong>NAME SERVERS:</strong> ${dns.ns_records?.join(', ') || 'N/A'}</div>
        `;
        if (type === 'dns') {
            sections.dns.style.display = 'block';
            sections.dns.classList.add('active');
        } else if (isFullScan) {
            sections.dns.style.display = 'block';
        }
    } else {
        sections.dns.style.display = 'none';
    }

    // 5. WHOIS
    const whoisContent = document.getElementById('whois-content');
    const whois = (type === 'whois') ? results : (isFullScan) ? results.whois : null;

    if (whois) {
        if (whois.error) {
            whoisContent.innerHTML = `<div style="color: var(--danger); font-family: 'JetBrains Mono'; font-size: 0.8rem;">[!] WHOIS ERROR: ${whois.error}</div>`;
            sections.whois.style.display = 'block';
            sections.whois.querySelector('.acc-badge').textContent = 'ERROR';
            sections.whois.querySelector('.acc-badge').style.background = 'var(--danger)';
        } else {
            whoisContent.innerHTML = Object.entries(whois)
                .filter(([k]) => ['registrar', 'creation_date', 'expiration_date', 'emails'].includes(k))
                .map(([k, v]) => `
                    <div style="margin-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 0.4rem;">
                        <strong style="color: var(--primary); text-transform: uppercase; font-size: 0.7rem; display: block; margin-bottom: 0.2rem;">${k}:</strong> 
                        <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem;">${Array.isArray(v) ? v.join(', ') : v}</span>
                    </div>`)
                .join('');

            if (type === 'whois') {
                sections.whois.style.display = 'block';
                sections.whois.classList.add('active');
            } else if (isFullScan) {
                sections.whois.style.display = 'block';
            }
        }
    } else {
        sections.whois.style.display = 'none';
    }
}

window.toggleAccordion = function (header) {
    const item = header.parentElement;
    item.classList.toggle('active');
};

window.downloadPDF = async function () {
    Utils.showToast('Compiling Intelligence Report...', 'info');
    const { jsPDF } = window.jspdf;
    const element = document.getElementById('professional-report');

    // Preparation for PDF: Expand everything, hide non-print elements
    const allItems = document.querySelectorAll('.accordion-item');
    allItems.forEach(i => i.classList.add('active'));
    const tabs = document.querySelector('.tabs');
    if (tabs) tabs.style.display = 'none';

    try {
        // Capture at higher resolution with scrolling support
        const canvas = await html2canvas(element, {
            backgroundColor: '#0a0a0b',
            scale: 2,
            logging: false,
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
        const contentHeight = pageHeight - (margin * 2) - 10; // 10mm for footer

        // Calculate the image dimensions in PDF units
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
                0, sourceY,           // Source x, y
                canvas.width, sourceHeight,  // Source width, height
                0, 0,                 // Dest x, y
                canvas.width, sourceHeight   // Dest width, height
            );

            // Add this page's image portion
            const pageImgData = pageCanvas.toDataURL('image/png');
            pdf.addImage(pageImgData, 'PNG', margin, margin, imgWidth, contentHeight);
        }

        // Add page numbers
        const totalPages = pdf.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            pdf.setPage(i);
            pdf.setFontSize(8);
            pdf.setTextColor(100, 100, 100);
            pdf.text(`Page ${i} of ${totalPages} | Fsociety Intelligence Report`, pageWidth / 2, pageHeight - 5, { align: 'center' });
        }

        pdf.save(`fsociety_intel_report_${new Date().getTime()}.pdf`);
        Utils.showToast('Report Exported Successfully', 'success');
    } catch (error) {
        console.error('PDF Export Error:', error);
        Utils.showToast('PDF Export Error: ' + error.message, 'error');
    } finally {
        // Restore tabs visibility
        if (tabs) tabs.style.display = 'flex';
    }
};

function renderUniversalChart(type, results) {
    const container = document.getElementById('scan-chart-container');
    const ctx = document.getElementById('scan-chart').getContext('2d');

    if (window.myScanChart) window.myScanChart.destroy();

    let chartData = {
        labels: [],
        datasets: [{
            label: 'Results',
            data: [],
            backgroundColor: 'rgba(0, 255, 157, 0.4)',
            borderColor: '#00ff9d',
            borderWidth: 1
        }]
    };
    let chartType = 'bar';
    let showChart = false;

    if (type === 'ports') {
        const ports = results.open_ports || [];
        if (ports.length > 0) {
            chartData.labels = ports.map(p => `Port ${p.port}`);
            chartData.datasets[0].data = ports.map(p => p.risk_score || 50);
            chartData.datasets[0].backgroundColor = ports.map(p => p.risk_color || '#00ff9d');
            chartData.datasets[0].borderColor = ports.map(p => p.risk_color || '#00ff9d');
            chartData.datasets[0].label = 'Vulnerability Exposure (Risk Score)';
            showChart = true;
        }
    } else if (type === 'dns') {
        const records = results;
        const counts = {
            'A': records.a_records?.length || 0,
            'MX': records.mx_records?.length || 0,
            'NS': records.ns_records?.length || 0,
            'TXT': records.txt_records?.length || 0
        };
        chartData.labels = Object.keys(counts);
        chartData.datasets[0].data = Object.values(counts);
        chartData.datasets[0].label = 'Record Count';
        chartType = 'doughnut';
        showChart = true;
    } else if (type === 'subdomains') {
        const found = results.total_found || 0;
        chartData.labels = ['Found', 'Scanned'];
        chartData.datasets[0].data = [found, results.total_scanned || 20];
        chartData.datasets[0].label = 'Discoveries';
        chartType = 'pie';
        showChart = true;
    } else if (type === 'domain') {
        // Mixed for Full Scan
        const dns = results.dns_records || {};
        const subs = results.subdomains?.total_found || 0;
        chartData.labels = ['DNS Records', 'Subdomains', 'Mail Servers'];
        chartData.datasets[0].data = [
            (dns.a_records?.length || 0) + (dns.txt_records?.length || 0),
            subs,
            dns.mx_records?.length || 0
        ];
        showChart = true;
    }

    if (showChart) {
        container.style.display = 'block';
        // Add class to parent to hide port grid on mobile if needed
        const portList = document.getElementById('list-ports');
        if (portList) portList.parentElement.classList.add('show-chart-mobile');

        window.myScanChart = new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: chartType !== 'bar', labels: { color: '#a0a0a0' } }
                },
                scales: chartType === 'bar' ? {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0a0a0' } },
                    x: { grid: { display: false }, ticks: { color: '#a0a0a0' } }
                } : {}
            }
        });
    } else {
        container.style.display = 'none';
    }
}

window.downloadReport = function () {
    const output = document.getElementById('json-output').innerText;
    if (!output) {
        Utils.showToast('No scan results to download', 'error');
        return;
    }

    const blob = new Blob([output], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fsociety_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    Utils.showToast('Report Downloaded', 'success');
};

export default new ScanView();
