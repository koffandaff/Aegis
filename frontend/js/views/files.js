import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class FileView {
    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                ${Components.renderSidebar('files')}

                <div style="flex: 1; padding: 2rem; overflow-y: auto;">
                    <h1 class="page-title fade-in">Malware & File Analysis</h1>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; max-width: 1000px;">
                        <!-- Hash Check Card -->
                        <div class="card glass fade-in">
                            <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="color: var(--primary);">fingerprint</span>
                                Hash Check
                            </h3>
                            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem;">Check file hashes against malware databases including VirusTotal.</p>
                            <form id="hash-form">
                                <div style="margin-bottom: 1rem;">
                                    <label>File Hash</label>
                                    <input type="text" id="file-hash" required>
                                </div>
                                <div style="margin-bottom: 1rem;">
                                    <label>Hash Type</label>
                                    <select id="hash-type">
                                        <option value="sha256">SHA-256</option>
                                        <option value="sha1">SHA-1</option>
                                        <option value="md5">MD5</option>
                                    </select>
                                </div>
                                <div style="margin-bottom: 1.5rem;">
                                    <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                                        <input type="checkbox" id="use-virustotal" checked>
                                        <span>Use VirusTotal API</span>
                                    </label>
                                </div>
                                <button type="submit" class="btn" style="width: 100%;">ANALYZE HASH</button>
                            </form>
                        </div>

                        <!-- Upload Analysis Card -->
                        <div class="card glass fade-in" style="animation-delay: 0.1s;">
                            <h3 style="display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="color: var(--secondary);">upload_file</span>
                                Upload Analysis
                            </h3>
                            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem;">Upload a file for deep static analysis and malware detection.</p>
                            <form id="upload-form">
                                <div id="drop-zone" style="border: 2px dashed rgba(255,255,255,0.1); border-radius: 12px; padding: 2rem; text-align: center; margin-bottom: 1.5rem; transition: all 0.3s ease; cursor: pointer; background: rgba(255,255,255,0.02);">
                                    <input type="file" id="file-input" style="display: none;">
                                    <div style="margin-bottom: 1rem;">
                                        <span class="material-symbols-outlined" style="font-size: 3rem; color: var(--secondary); opacity: 0.7;">cloud_upload</span>
                                    </div>
                                    <p style="color: var(--text-main); font-weight: 500; margin-bottom: 0.5rem;">Click to upload or drag and drop</p>
                                    <p style="color: var(--text-muted); font-size: 0.8rem;">Maximum file size 50MB</p>
                                </div>

                                <!-- Vertical File List -->
                                <div id="file-list" style="margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.5rem;"></div>

                                <!-- Upload Status Indicator -->
                                <div id="upload-status" style="display: none; margin-bottom: 1.5rem; padding: 1rem; border-radius: 8px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05);">
                                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                                        <div id="status-icon" style="width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
                                            <span class="material-symbols-outlined" style="color: var(--secondary); animation: spin 1s linear infinite;">progress_activity</span>
                                        </div>
                                        <div style="flex: 1;">
                                            <div id="status-text" style="font-size: 0.9rem; color: #fff;">Uploading...</div>
                                            <div id="status-detail" style="font-size: 0.75rem; color: var(--text-muted);">Please wait</div>
                                        </div>
                                    </div>
                                </div>

                                <div style="margin-bottom: 1.5rem;">
                                    <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 6px;">
                                        <input type="checkbox" id="upload-virustotal" checked>
                                        <span style="font-size: 0.9rem;">Cross-reference with VirusTotal</span>
                                    </label>
                                </div>
                                <button type="submit" class="btn btn-outline" style="width: 100%;" id="analyze-btn">START ANALYSIS</button>
                            </form>
                        </div>
                    </div>

                    <!-- Results Section -->
                    <div id="file-results" class="card glass fade-in" style="display: none; margin-top: 2rem; max-width: 1000px; padding: 0;">
                        
                        <!-- Results Header -->
                        <div style="padding: 1.5rem; background: rgba(0,0,0,0.2); border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3 style="margin: 0; color: var(--secondary); font-family: 'JetBrains Mono';">ANALYSIS REPORT</h3>
                                <div id="result-filename" style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;"></div>
                            </div>
                            <div id="result-verdict" style="padding: 0.5rem 1rem; border-radius: 4px; font-weight: bold; font-size: 0.85rem;"></div>
                            <button onclick="downloadFileReportPDF()" class="btn" style="margin-left: 1rem; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.1rem;">picture_as_pdf</span> PDF
                            </button>
                        </div>

                        <!-- Tabs -->
                        <div class="tabs" style="display: flex; gap: 1rem; padding: 1rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <button class="tab-btn active" data-tab="visual">VISUAL</button>
                            <button class="tab-btn" data-tab="details">DETAILS</button>
                            <button class="tab-btn" data-tab="raw">RAW JSON</button>
                        </div>

                        <!-- Tab: Visual -->
                        <div id="tab-visual" class="tab-content" style="display: block; padding: 1.5rem;">
                            <!-- Scorecards -->
                            <div id="scorecards" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem;"></div>
                            
                            <!-- Charts Row -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                                <div class="glass" style="padding: 1rem; border-radius: 8px;">
                                    <h4 style="margin: 0 0 1rem 0; color: var(--primary); font-size: 0.85rem; letter-spacing: 1px;">THREAT PROFILE</h4>
                                    <div style="height: 250px;">
                                        <canvas id="radar-chart"></canvas>
                                    </div>
                                </div>
                                <div class="glass" style="padding: 1rem; border-radius: 8px;">
                                    <h4 style="margin: 0 0 1rem 0; color: var(--secondary); font-size: 0.85rem; letter-spacing: 1px;">DETECTION BREAKDOWN</h4>
                                    <div style="height: 250px;">
                                        <canvas id="doughnut-chart"></canvas>
                                    </div>
                                </div>
                            </div>

                            <!-- Warnings -->
                            <div id="warnings-section" style="margin-top: 2rem; display: none;">
                                <h4 style="color: #ff4757; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined">warning</span> WARNINGS
                                </h4>
                                <ul id="warnings-list" style="list-style: none; padding: 0;"></ul>
                            </div>

                            <!-- Recommendations -->
                            <div id="recommendations-section" style="margin-top: 2rem; display: none;">
                                <h4 style="color: var(--primary); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined">lightbulb</span> RECOMMENDATIONS
                                </h4>
                                <ul id="recommendations-list" style="list-style: none; padding: 0;"></ul>
                            </div>
                        </div>

                        <!-- Tab: Details -->
                        <div id="tab-details" class="tab-content" style="display: none; padding: 1.5rem;">
                            <div id="details-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;"></div>
                        </div>

                        <!-- Tab: Raw JSON -->
                        <div id="tab-raw" class="tab-content" style="display: none; padding: 1.5rem;">
                            <pre id="file-output" style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: 'JetBrains Mono'; font-size: 0.8rem; max-height: 500px;"></pre>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());
        const hashForm = document.getElementById('hash-form');
        const uploadForm = document.getElementById('upload-form');

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
                btn.classList.add('active');
                document.getElementById(`tab-${btn.dataset.tab}`).style.display = 'block';
            };
        });

        // PDF Export Function
        window.downloadFileReportPDF = async function () {
            Utils.showToast('Generating File Report PDF...', 'info');
            const { jsPDF } = window.jspdf;
            const element = document.getElementById('file-results');

            if (!element || element.style.display === 'none') {
                Utils.showToast('No results to export', 'warning');
                return;
            }

            try {
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

                const totalPages = pdf.internal.getNumberOfPages();
                for (let i = 1; i <= totalPages; i++) {
                    pdf.setPage(i);
                    pdf.setFontSize(8);
                    pdf.setTextColor(100, 100, 100);
                    pdf.text(`Page ${i} of ${totalPages} | Aegis File Analysis`, pageWidth / 2, pageHeight - 5, { align: 'center' });
                }

                pdf.save(`aegis_file_report_${Date.now()}.pdf`);
                Utils.showToast('Report Exported Successfully', 'success');
            } catch (e) {
                console.error('PDF Export Error:', e);
                Utils.showToast('PDF Export Error: ' + e.message, 'error');
            }
        };

        // Hash Check
        hashForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const hash = document.getElementById('file-hash').value.trim();
            const hashType = document.getElementById('hash-type').value;
            const useVT = document.getElementById('use-virustotal').checked;

            try {
                Utils.showToast('Analyzing hash...', 'info');

                // First check local database
                const localResponse = await Api.post('/files/hash/check', { hash, hash_type: hashType });

                // If VirusTotal enabled, also query VT
                let vtResponse = null;
                if (useVT) {
                    try {
                        vtResponse = await Api.post('/files/virustotal/check', { hash });
                    } catch (vtError) {
                        console.warn('VirusTotal check failed:', vtError);
                    }
                }

                // Merge results
                const mergedResult = this.mergeHashResults(localResponse, vtResponse);
                this.displayResults(mergedResult, 'hash');
                Utils.showToast('Hash analysis complete', 'success');
            } catch (error) {
                Utils.showToast(error.message, 'error');
            }
        });

        // Drag & Drop Logic
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const fileList = document.getElementById('file-list');

        if (dropZone && fileInput) {
            dropZone.addEventListener('click', () => fileInput.click());

            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = 'var(--primary)';
                dropZone.style.background = 'rgba(0, 255, 157, 0.05)';
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.style.borderColor = 'rgba(255,255,255,0.1)';
                dropZone.style.background = 'rgba(255,255,255,0.02)';
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = 'rgba(255,255,255,0.1)';
                dropZone.style.background = 'rgba(255,255,255,0.02)';
                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    updateFileList();
                }
            });

            fileInput.addEventListener('change', updateFileList);
        }

        function updateFileList() {
            fileList.innerHTML = '';
            Array.from(fileInput.files).forEach(file => {
                const item = document.createElement('div');
                item.className = 'fade-in';
                item.style.cssText = `
                    display: flex; 
                    align-items: center; 
                    gap: 1rem; 
                    background: rgba(0,0,0,0.3); 
                    padding: 0.75rem 1rem; 
                    border-radius: 8px; 
                    border: 1px solid rgba(255,255,255,0.05);
                `;
                item.innerHTML = `
                    <div style="width: 36px; height: 36px; border-radius: 6px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center;">
                        <span class="material-symbols-outlined" style="font-size: 1.2rem; color: var(--primary);">description</span>
                    </div>
                    <div style="flex: 1; overflow: hidden;">
                        <div style="font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff;">${file.name}</div>
                        <div style="font-size: 0.75rem; color: var(--text-muted);">${Utils.formatBytes(file.size)}</div>
                    </div>
                    <span class="material-symbols-outlined" style="color: #ff4757; cursor: pointer; font-size: 1.2rem;" onclick="this.parentElement.remove(); document.getElementById('file-input').value = '';">delete</span>
                `;
                fileList.appendChild(item);
            });
        }

        // File Upload Submit
        const uploadStatus = document.getElementById('upload-status');
        const statusIcon = document.getElementById('status-icon');
        const statusText = document.getElementById('status-text');
        const statusDetail = document.getElementById('status-detail');
        const analyzeBtn = document.getElementById('analyze-btn');

        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const useVT = document.getElementById('upload-virustotal').checked;

            if (fileInput.files.length === 0) {
                Utils.showToast('Please select a file first', 'error');
                return;
            }

            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'ANALYZING...';
            uploadStatus.style.display = 'block';

            // Process files sequentially
            for (let i = 0; i < fileInput.files.length; i++) {
                const file = fileInput.files[i];

                // Update status for current file
                statusIcon.innerHTML = '<span class="material-symbols-outlined" style="color: var(--secondary); animation: spin 1s linear infinite;">progress_activity</span>';
                statusText.textContent = `Analyzing ${file.name}...`;
                statusDetail.textContent = `File ${i + 1} of ${fileInput.files.length}`;
                uploadStatus.style.borderColor = 'var(--secondary)';

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const token = localStorage.getItem('access_token');
                    const response = await fetch(`${Api.baseUrl}/files/upload/analyze?use_virustotal=${useVT}`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` },
                        body: formData
                    });

                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || 'Upload failed');

                    // Display results for this file (append or replace? For now replace to assume single view focus, but could accumulate)
                    // Since the UI design seems single-result focused, we'll display the last one or append to a list.
                    // Implementation plan implies "Show list", but let's stick to displayResults for now. 
                    // To handle multiple, we might need a results list, but for now let's just show the last one's detailed result 
                    // and maybe toast success for each.

                    this.displayResults(data, 'file');
                    Utils.showToast(`${file.name} analysis complete`, 'success');

                } catch (error) {
                    Utils.showToast(`${file.name} failed: ${error.message}`, 'error');
                }
            }

            // Final status update
            statusIcon.innerHTML = '<span class="material-symbols-outlined" style="color: var(--primary);">check_circle</span>';
            statusText.textContent = 'Batch Analysis Complete';
            statusDetail.textContent = `Processed ${fileInput.files.length} files`;
            uploadStatus.style.borderColor = 'var(--primary)';

            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'START ANALYSIS';
        });
    }

    mergeHashResults(localResult, vtResult) {
        const merged = { ...localResult };

        if (vtResult) {
            merged.virustotal = {
                positives: vtResult.positives || 0,
                total: vtResult.total || 0,
                permalink: vtResult.permalink,
                scan_date: vtResult.scan_date,
                scans: vtResult.scans
            };

            // If VT found detections, update risk level
            if (vtResult.positives > 0) {
                merged.reputation.known_malicious = true;
                merged.reputation.detection_count = Math.max(merged.reputation.detection_count, vtResult.positives);
                merged.risk_level = vtResult.positives > 10 ? 'critical' : 'high';
            }
        }

        return merged;
    }

    displayResults(data, type) {
        const resultsArea = document.getElementById('file-results');
        const output = document.getElementById('file-output');
        const filenameEl = document.getElementById('result-filename');
        const verdictEl = document.getElementById('result-verdict');

        // Show filename or hash
        filenameEl.textContent = type === 'file'
            ? `${data.filename} (${this.formatBytes(data.file_size)})`
            : `Hash: ${data.hash?.substring(0, 16)}...`;

        // Show verdict
        const riskLevel = data.risk_level || 'info';
        const verdictColors = {
            'critical': { bg: '#ff4757', text: 'CRITICAL THREAT' },
            'high': { bg: '#ff6b6b', text: 'HIGH RISK' },
            'medium': { bg: '#ffa502', text: 'MEDIUM RISK' },
            'low': { bg: '#2ed573', text: 'LOW RISK' },
            'info': { bg: '#3498db', text: 'UNKNOWN' }
        };
        const verdict = verdictColors[riskLevel] || verdictColors.info;
        verdictEl.style.background = verdict.bg;
        verdictEl.style.color = '#fff';
        verdictEl.textContent = verdict.text;

        // Raw JSON
        output.innerHTML = Utils.formatJSON(data);

        // Scorecards
        this.renderScorecards(data, type);

        // Charts
        this.renderCharts(data, type);

        // Warnings
        this.renderWarnings(data.warnings || []);

        // Recommendations
        this.renderRecommendations(data.recommendations || []);

        // Details
        this.renderDetails(data, type);

        resultsArea.style.display = 'block';
    }

    renderScorecards(data, type) {
        const container = document.getElementById('scorecards');
        const cards = [];

        if (type === 'file') {
            cards.push(
                { label: 'ENTROPY', value: data.entropy?.toFixed(2) || '--', color: data.entropy > 7.5 ? '#ff4757' : 'var(--primary)' },
                { label: 'FILE SIZE', value: this.formatBytes(data.file_size), color: 'var(--secondary)' },
                { label: 'MIME TYPE', value: data.mime_type?.split('/')[1]?.toUpperCase() || '--', color: '#ffa502' },
                { label: 'STRINGS', value: data.strings_found?.length || 0, color: '#3498db' }
            );
        }

        // Common cards
        const detections = data.virustotal?.positives || data.reputation?.detection_count || 0;
        const total = data.virustotal?.total || 70;
        cards.push(
            { label: 'DETECTIONS', value: `${detections}/${total}`, color: detections > 0 ? '#ff4757' : '#2ed573' },
            { label: 'CONFIDENCE', value: `${Math.round((data.confidence || 0) * 100)}%`, color: 'var(--primary)' }
        );

        container.innerHTML = cards.map(card => `
            <div class="glass" style="padding: 1rem; border-radius: 8px; text-align: center; border-left: 3px solid ${card.color};">
                <div style="font-size: 1.5rem; font-weight: bold; color: ${card.color}; font-family: 'JetBrains Mono';">${card.value}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted); letter-spacing: 1px; margin-top: 0.3rem;">${card.label}</div>
            </div>
        `).join('');
    }

    renderCharts(data, type) {
        // Destroy existing charts
        if (window.fileRadarChart) window.fileRadarChart.destroy();
        if (window.fileDoughnutChart) window.fileDoughnutChart.destroy();

        // Radar Chart - Threat Profile
        const radarCtx = document.getElementById('radar-chart').getContext('2d');
        const threatFactors = this.calculateThreatFactors(data, type);

        window.fileRadarChart = new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['Malware Match', 'Entropy', 'Executable', 'Macros', 'Encryption', 'VT Detections'],
                datasets: [{
                    label: 'Threat Level',
                    data: threatFactors,
                    backgroundColor: 'rgba(255, 71, 87, 0.3)',
                    borderColor: '#ff4757',
                    pointBackgroundColor: '#ff4757',
                    pointBorderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { display: false },
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        angleLines: { color: 'rgba(255,255,255,0.1)' },
                        pointLabels: { color: '#a0a0a0', font: { size: 10 } }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });

        // Doughnut Chart - Detection Breakdown
        const doughnutCtx = document.getElementById('doughnut-chart').getContext('2d');
        const vtPositives = data.virustotal?.positives || 0;
        const vtTotal = data.virustotal?.total || 70;
        const vtClean = vtTotal - vtPositives;

        window.fileDoughnutChart = new Chart(doughnutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Detected', 'Clean', 'Unknown'],
                datasets: [{
                    data: [vtPositives, vtClean, vtTotal === 0 ? 70 : 0],
                    backgroundColor: ['#ff4757', '#2ed573', '#3498db'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#a0a0a0', padding: 15 } }
                }
            }
        });
    }

    calculateThreatFactors(data, type) {
        const factors = [];

        // Malware Match (0-100)
        factors.push(data.reputation?.known_malicious ? 100 : (data.reputation?.known_clean ? 0 : 30));

        // Entropy (0-100, high = bad)
        const entropy = data.entropy || 0;
        factors.push(Math.min(100, (entropy / 8) * 100));

        // Executable
        factors.push(data.is_executable ? 80 : 0);

        // Macros
        factors.push(data.contains_macros ? 90 : 0);

        // Encryption
        factors.push(data.is_encrypted ? 60 : 0);

        // VT Detections
        const vtRatio = data.virustotal ? (data.virustotal.positives / Math.max(1, data.virustotal.total)) * 100 : 0;
        factors.push(vtRatio);

        return factors;
    }

    renderWarnings(warnings) {
        const section = document.getElementById('warnings-section');
        const list = document.getElementById('warnings-list');

        if (warnings.length === 0) {
            section.style.display = 'none';
            return;
        }

        section.style.display = 'block';
        list.innerHTML = warnings.map(w => `
            <li style="padding: 0.8rem; background: rgba(255, 71, 87, 0.1); border-left: 3px solid #ff4757; margin-bottom: 0.5rem; border-radius: 4px;">
                ${w}
            </li>
        `).join('');
    }

    renderRecommendations(recommendations) {
        const section = document.getElementById('recommendations-section');
        const list = document.getElementById('recommendations-list');

        if (recommendations.length === 0) {
            section.style.display = 'none';
            return;
        }

        section.style.display = 'block';
        list.innerHTML = recommendations.map(r => `
            <li style="padding: 0.8rem; background: rgba(0, 255, 157, 0.05); border-left: 3px solid var(--primary); margin-bottom: 0.5rem; border-radius: 4px;">
                ${r}
            </li>
        `).join('');
    }

    renderDetails(data, type) {
        const grid = document.getElementById('details-grid');
        const sections = [];

        // File Info Section
        if (type === 'file') {
            sections.push(`
                <div class="glass" style="padding: 1rem; border-radius: 8px;">
                    <h4 style="color: var(--primary); margin-bottom: 1rem; font-size: 0.85rem;">FILE INFORMATION</h4>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem;">
                        <div style="margin-bottom: 0.5rem;"><strong>Filename:</strong> ${data.filename}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Size:</strong> ${this.formatBytes(data.file_size)}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>MIME Type:</strong> ${data.mime_type}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Magic Bytes:</strong> ${data.magic_bytes}</div>
                    </div>
                </div>
            `);
        }

        // Hash Section
        sections.push(`
            <div class="glass" style="padding: 1rem; border-radius: 8px;">
                <h4 style="color: var(--secondary); margin-bottom: 1rem; font-size: 0.85rem;">HASH SIGNATURES</h4>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.75rem; word-break: break-all;">
                    <div style="margin-bottom: 0.5rem;"><strong>MD5:</strong> ${data.hash_md5 || data.hash || '--'}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>SHA1:</strong> ${data.hash_sha1 || '--'}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>SHA256:</strong> ${data.hash_sha256 || data.hash || '--'}</div>
                </div>
            </div>
        `);

        // Reputation Section
        sections.push(`
            <div class="glass" style="padding: 1rem; border-radius: 8px;">
                <h4 style="color: #ffa502; margin-bottom: 1rem; font-size: 0.85rem;">REPUTATION</h4>
                <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem;">
                    <div style="margin-bottom: 0.5rem;"><strong>Known Malicious:</strong> ${data.reputation?.known_malicious ? '⚠️ YES' : '✅ NO'}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>Detection Names:</strong> ${data.reputation?.detection_names?.join(', ') || 'None'}</div>
                    <div style="margin-bottom: 0.5rem;"><strong>Tags:</strong> ${data.reputation?.tags?.join(', ') || 'None'}</div>
                </div>
            </div>
        `);

        // VirusTotal Section
        if (data.virustotal) {
            sections.push(`
                <div class="glass" style="padding: 1rem; border-radius: 8px;">
                    <h4 style="color: #3498db; margin-bottom: 1rem; font-size: 0.85rem;">VIRUSTOTAL</h4>
                    <div style="font-family: 'JetBrains Mono'; font-size: 0.8rem;">
                        <div style="margin-bottom: 0.5rem;"><strong>Detections:</strong> ${data.virustotal.positives}/${data.virustotal.total}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Scan Date:</strong> ${data.virustotal.scan_date || 'N/A'}</div>
                        <div style="margin-bottom: 0.5rem;"><a href="${data.virustotal.permalink}" target="_blank" style="color: var(--primary);">View Full Report →</a></div>
                    </div>
                </div>
            `);
        }

        grid.innerHTML = sections.join('');
    }

    formatBytes(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
    }
}

export default new FileView();
