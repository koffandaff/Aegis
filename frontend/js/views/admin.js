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
                        <div style="display: flex; gap: 1rem;">
                            <button id="export-btn" class="btn-outline" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem;">
                                <span class="material-symbols-outlined">download</span>
                                Export All JSON
                            </button>
                        </div>
                    </div>
                    
                    <div style="display: grid; gap: 2rem; max-width: 1400px;">
                        
                        <!-- Stats Overview Cards -->
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.2rem;">analytics</span>
                                Platform Statistics
                            </h3>
                            <div class="export-dropdown" style="position: relative;">
                                <button id="stats-export-btn" class="btn-outline" style="padding: 0.3rem 0.6rem; font-size: 0.75rem; display: flex; align-items: center; gap: 0.3rem;">
                                    <span class="material-symbols-outlined" style="font-size: 1rem;">download</span>
                                    Export
                                </button>
                                <div id="stats-export-menu" class="export-menu" style="display: none; position: absolute; right: 0; top: 100%; background: rgba(20,20,20,0.98); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.5rem; z-index: 100; min-width: 120px;">
                                    <button onclick="adminView.exportStatsPDF()" style="width: 100%; padding: 0.5rem; background: transparent; border: none; color: #fff; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; border-radius: 4px;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='transparent'">
                                        <span class="material-symbols-outlined" style="font-size: 1rem; color: #e74c3c;">picture_as_pdf</span> PDF
                                    </button>
                                    <button onclick="adminView.exportStatsCSV()" style="width: 100%; padding: 0.5rem; background: transparent; border: none; color: #fff; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; border-radius: 4px;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='transparent'">
                                        <span class="material-symbols-outlined" style="font-size: 1rem; color: #2ed573;">table_chart</span> CSV
                                    </button>
                                </div>
                            </div>
                        </div>
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
                            <div class="card glass fade-in stat-card-hover" style="animation-delay: 0.5s; border-left: 3px solid #1abc9c;">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(26, 188, 156, 0.1); display: flex; align-items: center; justify-content: center;">
                                        <span class="material-symbols-outlined" style="color: #1abc9c; font-size: 1.5rem;">chat</span>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Chat Sessions</div>
                                        <div id="stat-chat-sessions" style="font-size: 1.75rem; font-weight: bold; color: #1abc9c; font-family: 'JetBrains Mono';">-</div>
                                    </div>
                                </div>
                            </div>
                            <div class="card glass fade-in stat-card-hover" style="animation-delay: 0.6s; border-left: 3px solid #f39c12;">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(243, 156, 18, 0.1); display: flex; align-items: center; justify-content: center;">
                                        <span class="material-symbols-outlined" style="color: #f39c12; font-size: 1.5rem;">forum</span>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Chat Messages</div>
                                        <div id="stat-chat-messages" style="font-size: 1.75rem; font-weight: bold; color: #f39c12; font-family: 'JetBrains Mono';">-</div>
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
                                    <div style="display: flex; gap: 0.5rem; align-items: center;">
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
                                        <div class="export-dropdown" style="position: relative;">
                                            <button id="activity-export-btn" class="btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.7rem;" title="Export Activities">
                                                <span class="material-symbols-outlined" style="font-size: 1rem;">download</span>
                                            </button>
                                            <div id="activity-export-menu" class="export-menu" style="display: none; position: absolute; right: 0; top: 100%; background: rgba(20,20,20,0.98); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.5rem; z-index: 100; min-width: 120px;">
                                                <button onclick="adminView.exportActivitiesPDF()" style="width: 100%; padding: 0.5rem; background: transparent; border: none; color: #fff; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; border-radius: 4px;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='transparent'">
                                                    <span class="material-symbols-outlined" style="font-size: 1rem; color: #e74c3c;">picture_as_pdf</span> PDF
                                                </button>
                                                <button onclick="adminView.exportActivitiesCSV()" style="width: 100%; padding: 0.5rem; background: transparent; border: none; color: #fff; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; border-radius: 4px;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='transparent'">
                                                    <span class="material-symbols-outlined" style="font-size: 1rem; color: #2ed573;">table_chart</span> CSV
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                    <div id="activity-logs" style="max-height: 400px; overflow-y: auto;">
                                        <p style="color: var(--text-muted); text-align: center;">Loading activities...</p>
                                    </div>
                                    <!-- Pagination Controls -->
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 1rem;">
                                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                                            <span style="font-size: 0.8rem; color: var(--text-muted);">Rows per page:</span>
                                            <select id="activity-limit" style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: var(--text-muted); padding: 0.1rem 0.3rem; border-radius: 4px; font-size: 0.8rem; outline: none;">
                                                <option value="10">10</option>
                                                <option value="30" selected>30</option>
                                                <option value="50">50</option>
                                                <option value="100">100</option>
                                            </select>
                                        </div>
                                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                                            <span id="page-info" style="font-size: 0.8rem; color: var(--text-muted); margin-right: 0.5rem;">Page 1</span>
                                            <button id="prev-activity-page" class="btn-outline" style="padding: 0.1rem 0.3rem; opacity: 0.5; cursor: not-allowed;" disabled>
                                                <span class="material-symbols-outlined" style="font-size: 1rem;">chevron_left</span>
                                            </button>
                                            <button id="next-activity-page" class="btn-outline" style="padding: 0.1rem 0.3rem;">
                                                <span class="material-symbols-outlined" style="font-size: 1rem;">chevron_right</span>
                                            </button>
                                        </div>
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
                                        <div class="export-dropdown" style="position: relative;">
                                            <button id="users-export-btn" class="btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.7rem;" title="Export Users">
                                                <span class="material-symbols-outlined" style="font-size: 1rem;">download</span>
                                            </button>
                                            <div id="users-export-menu" class="export-menu" style="display: none; position: absolute; right: 0; top: 100%; background: rgba(20,20,20,0.98); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.5rem; z-index: 100; min-width: 120px;">
                                                <button onclick="adminView.exportUsersPDF()" style="width: 100%; padding: 0.5rem; background: transparent; border: none; color: #fff; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; border-radius: 4px;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='transparent'">
                                                    <span class="material-symbols-outlined" style="font-size: 1rem; color: #e74c3c;">picture_as_pdf</span> PDF
                                                </button>
                                                <button onclick="adminView.exportUsersCSV()" style="width: 100%; padding: 0.5rem; background: transparent; border: none; color: #fff; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; border-radius: 4px;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='transparent'">
                                                    <span class="material-symbols-outlined" style="font-size: 1rem; color: #2ed573;">table_chart</span> CSV
                                                </button>
                                            </div>
                                        </div>
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

                        <!-- SQL Query Console -->
                        <div class="card glass fade-in" style="animation-delay: 0.8s;">
                            <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="color: #f39c12;">terminal</span>
                                SQL Query Console
                            </h3>
                            <div style="margin-bottom: 1rem;">
                                <textarea id="sql-query-input" rows="4" style="width: 100%; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 1rem; color: #00ff9d; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; resize: vertical;" placeholder="-- Enter SQL Query here&#10;SELECT * FROM users;"></textarea>
                            </div>
                            <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
                                <button id="sql-execute-btn" class="btn-primary" style="padding: 0.5rem 1rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span class="material-symbols-outlined" style="font-size: 1rem;">play_arrow</span>
                                    Execute Query
                                </button>
                                <button id="sql-clear-btn" class="btn-outline" style="padding: 0.5rem 1rem;">
                                    Clear
                                </button>
                                <div id="sql-export-dropdown" class="export-dropdown" style="position: relative; display: none;">
                                    <button id="sql-export-btn" class="btn-outline" style="padding: 0.5rem 1rem; display: flex; align-items: center; gap: 0.5rem; border-color: var(--secondary); color: var(--secondary);">
                                        <span class="material-symbols-outlined" style="font-size: 1rem;">download</span>
                                        Export Results
                                    </button>
                                    <div id="sql-export-menu" class="export-menu" style="display: none; position: absolute; left: 0; top: 100%; background: rgba(20,20,20,0.98); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.5rem; z-index: 100; min-width: 120px;">
                                        <button onclick="adminView.exportSQLResultsPDF()" style="width: 100%; padding: 0.5rem; background: transparent; border: none; color: #fff; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; border-radius: 4px;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='transparent'">
                                            <span class="material-symbols-outlined" style="font-size: 1rem; color: #e74c3c;">picture_as_pdf</span> PDF
                                        </button>
                                        <button onclick="adminView.exportSQLResultsCSV()" style="width: 100%; padding: 0.5rem; background: transparent; border: none; color: #fff; cursor: pointer; text-align: left; display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; border-radius: 4px;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='transparent'">
                                            <span class="material-symbols-outlined" style="font-size: 1rem; color: #2ed573;">table_chart</span> CSV
                                        </button>
                                    </div>
                                </div>
                                <span id="sql-status" style="margin-left: auto; color: var(--text-muted); font-size: 0.8rem; align-self: center;"></span>
                            </div>
                            <div id="sql-results" style="max-height: 400px; overflow: auto; background: rgba(0,0,0,0.3); border-radius: 8px; display: none;">
                                <!-- Results will be inserted here -->
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
        // Load all data independently (so one failure doesn't break everything)
        await Promise.allSettled([
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

        // Export dropdown toggles
        this.setupExportDropdowns();

        // SQL Console event listeners
        document.getElementById('sql-execute-btn').addEventListener('click', () => this.executeSQL());
        document.getElementById('sql-clear-btn').addEventListener('click', () => {
            document.getElementById('sql-query-input').value = '';
            document.getElementById('sql-results').style.display = 'none';
            document.getElementById('sql-export-dropdown').style.display = 'none';
            document.getElementById('sql-status').textContent = '';
        });
        // Ctrl+Enter to execute
        document.getElementById('sql-query-input').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.executeSQL();
            }
        });

        // Setup live polling intervals
        this.startLiveUpdates();

        // Initialize pagination listeners
        this.initActivityPagination();
    }

    setupExportDropdowns() {
        const dropdowns = [
            { btn: 'stats-export-btn', menu: 'stats-export-menu' },
            { btn: 'activity-export-btn', menu: 'activity-export-menu' },
            { btn: 'users-export-btn', menu: 'users-export-menu' },
            { btn: 'sql-export-btn', menu: 'sql-export-menu' }
        ];

        dropdowns.forEach(({ btn, menu }) => {
            const btnEl = document.getElementById(btn);
            const menuEl = document.getElementById(menu);
            if (btnEl && menuEl) {
                btnEl.addEventListener('click', (e) => {
                    e.stopPropagation();
                    // Close all other menus
                    document.querySelectorAll('.export-menu').forEach(m => {
                        if (m.id !== menu) m.style.display = 'none';
                    });
                    menuEl.style.display = menuEl.style.display === 'none' ? 'block' : 'none';
                });
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            document.querySelectorAll('.export-menu').forEach(m => m.style.display = 'none');
        });
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
            const searchQuery = document.getElementById('user-search')?.value;
            this.loadStats();
            if (!searchQuery) this.loadUsers();
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
                document.getElementById('stat-chat-sessions').textContent = stats.total_chat_sessions || 0;
                document.getElementById('stat-chat-messages').textContent = stats.total_chat_messages || 0;
            }
        } catch (e) {
            console.error('Failed to load stats:', e);
        }
    }

    async loadUsers(search = '') {
        try {
            let url = '/admin/users?limit=50';
            if (search) url += `&search=${encodeURIComponent(search)}`;

            const response = await Api.get(url);
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
                        <span class="badge" style="background: ${user.role === 'admin' ? 'var(--secondary)' : 'rgba(52, 152, 219, 0.2)'}; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.7rem; color: ${user.role === 'admin' ? '#000' : '#3498db'}; font-weight: bold; display: flex; align-items: center; gap: 4px;">
                            <span class="material-symbols-outlined" style="font-size: 0.8rem; vertical-align: middle;">${user.role === 'admin' ? 'shield_person' : 'person'}</span>
                            ${user.role.toUpperCase()}
                        </span>
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
        if (query.length > 2) {
            // Server-side search for longer queries
            this.loadUsers(query);
        } else if (query.length === 0) {
            // Reload all if cleared
            this.loadUsers();
        } else {
            // Local filtering for short strings
            const filtered = this.users.filter(user =>
                (user.username || '').toLowerCase().includes(query.toLowerCase()) ||
                (user.email || '').toLowerCase().includes(query.toLowerCase())
            );
            this.renderUsers(filtered);
        }
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
            const limit = document.getElementById('activity-limit')?.value || 30;
            const page = this.currentActivityPage || 1;

            let url = `/admin/activities?limit=${limit}&page=${page}`;
            if (actionFilter) url += `&action=${actionFilter}`;

            const response = await Api.get(url);
            this.activities = response?.activities || [];
            this.renderActivities();

            // Update pagination UI
            const hasNext = this.activities.length === parseInt(limit);
            this.updatePaginationControls(page, hasNext);

        } catch (e) {
            console.error('Failed to load activities:', e);
            document.getElementById('activity-logs').innerHTML = '<p style="color: #ff4757; text-align: center;">Failed to load activities</p>';
        }
    }

    updatePaginationControls(page, hasNext) {
        const prevBtn = document.getElementById('prev-activity-page');
        const nextBtn = document.getElementById('next-activity-page');
        const pageInfo = document.getElementById('page-info');

        if (pageInfo) pageInfo.textContent = `Page ${page}`;

        if (prevBtn) {
            prevBtn.disabled = page <= 1;
            prevBtn.style.opacity = page <= 1 ? '0.5' : '1';
            prevBtn.style.cursor = page <= 1 ? 'not-allowed' : 'pointer';
        }

        if (nextBtn) {
            nextBtn.disabled = !hasNext;
            nextBtn.style.opacity = !hasNext ? '0.5' : '1';
            nextBtn.style.cursor = !hasNext ? 'not-allowed' : 'pointer';
        }
    }

    async exportActivitiesPDF() {
        // Fetch ALL activities for the current filter for export, up to a reasonable limit (e.g. 200)
        // or just export current view?
        // User requested "edit them for pdf and show and all" implying ability to see more.
        // I will export up to 1000 items of the current filter to give a comprehensive report.

        try {
            const actionFilter = document.getElementById('activity-filter')?.value || '';
            let url = `/admin/activities?limit=1000&page=1`; // Fetch up to 1000
            if (actionFilter) url += `&action=${actionFilter}`;

            Utils.showToast('Generating PDF...', 'info');

            const response = await Api.get(url);
            const activitiesToExport = response?.activities || [];

            if (activitiesToExport.length === 0) {
                Utils.showToast('No activities to export', 'warning');
                return;
            }

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();

            // ... (rest of export logic uses activitiesToExport) ...
            // Need to update the existing exportActivitiesPDF to use activitiesToExport variable
            // instead of this.activities

            // Reuse explicit export logic logic here or call a helper
            // I will inject the full method body below

            doc.setFont("helvetica");
            doc.setFontSize(22);
            doc.setTextColor(0, 255, 157); // Neon green
            doc.text("Activity Log Report", 20, 20);

            doc.setFontSize(10);
            doc.setTextColor(100);
            doc.text(`Generated on: ${new Date().toLocaleString()}`, 20, 30);
            doc.text(`Filter: ${actionFilter || 'All Actions'}`, 20, 35);

            const tableColumn = ["Time", "User", "Action", "Details", "IP"];
            const tableRows = [];

            activitiesToExport.forEach(log => {
                const date = new Date(log.timestamp).toLocaleString();
                // Safely handle details
                let detailsStr = '';
                if (typeof log.details === 'string') {
                    detailsStr = log.details;
                } else if (log.details && typeof log.details === 'object') {
                    // Start with basic info
                    if (log.details.target) detailsStr += `Target: ${log.details.target} `;
                    if (log.details.status) detailsStr += `Status: ${log.details.status} `;

                    // If empty string so far, just JSON stringify
                    if (!detailsStr) detailsStr = JSON.stringify(log.details).substring(0, 50);
                }

                const row = [
                    date,
                    log.user_email || 'Unknown',
                    log.action.toUpperCase(),
                    detailsStr,
                    log.ip_address || 'N/A'
                ];
                tableRows.push(row);
            });

            doc.autoTable({
                head: [tableColumn],
                body: tableRows,
                startY: 45,
                theme: 'grid',
                styles: { fontSize: 8, cellPadding: 2 },
                headStyles: { fillColor: [20, 20, 30], textColor: [0, 255, 157] },
                alternateRowStyles: { fillColor: [245, 245, 245] }
            });

            doc.save(`activity_log_${new Date().toISOString().split('T')[0]}.pdf`);
            Utils.showToast('PDF Exported successfully', 'success');

        } catch (e) {
            console.error('Export failed:', e);
            Utils.showToast('Export failed', 'error');
        }
    }

    initActivityPagination() {
        const prevBtn = document.getElementById('prev-activity-page');
        const nextBtn = document.getElementById('next-activity-page');
        const limitSelect = document.getElementById('activity-limit');

        if (prevBtn) {
            prevBtn.onclick = () => {
                if (this.currentActivityPage > 1) {
                    this.currentActivityPage--;
                    this.loadActivities(document.getElementById('activity-filter').value);
                }
            };
        }

        if (nextBtn) {
            nextBtn.onclick = () => {
                // If we have full page, assume there might be more
                const limit = parseInt(document.getElementById('activity-limit').value);
                if (this.activities.length === limit) {
                    this.currentActivityPage = (this.currentActivityPage || 1) + 1;
                    this.loadActivities(document.getElementById('activity-filter').value);
                }
            };
        }

        if (limitSelect) {
            limitSelect.onchange = () => {
                this.currentActivityPage = 1;
                this.loadActivities(document.getElementById('activity-filter').value);
            };
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
                        borderColor: '#00ff9d',
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
                    backgroundColor: ['#3498db', '#00ff9d', '#9b59b6', '#e74c3c', '#f39c12'],
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

    // ==================== SQL CONSOLE ====================
    async executeSQL() {
        const queryInput = document.getElementById('sql-query-input');
        const resultsContainer = document.getElementById('sql-results');
        const statusSpan = document.getElementById('sql-status');
        const executeBtn = document.getElementById('sql-execute-btn');

        const query = queryInput.value.trim();
        if (!query) {
            Utils.showToast('Please enter a SQL query', 'warning');
            return;
        }

        // Show loading state
        executeBtn.disabled = true;
        executeBtn.innerHTML = '<span class="material-symbols-outlined rotating" style="font-size: 1rem;">sync</span> Executing...';
        statusSpan.textContent = 'Running query...';
        statusSpan.style.color = 'var(--text-muted)';

        try {
            const response = await Api.post('/admin/sql', { query });

            if (response.success) {
                statusSpan.textContent = response.message;
                statusSpan.style.color = '#2ed573';

                if (response.columns.length > 0 && response.rows.length > 0) {
                    // Save results for PDF export
                    this.lastSQLResults = response;
                    // Render table
                    resultsContainer.innerHTML = this.renderSQLTable(response.columns, response.rows);
                    resultsContainer.style.display = 'block';
                    document.getElementById('sql-export-dropdown').style.display = 'flex';
                } else if (response.row_count > 0) {
                    // For UPDATE/INSERT/DELETE
                    resultsContainer.innerHTML = `
                        <div style="padding: 1rem; text-align: center; color: #2ed573;">
                            <span class="material-symbols-outlined" style="font-size: 2rem;">check_circle</span>
                            <p style="margin-top: 0.5rem;">${response.message}</p>
                        </div>
                    `;
                    resultsContainer.style.display = 'block';
                } else {
                    resultsContainer.innerHTML = `
                        <div style="padding: 1rem; text-align: center; color: var(--text-muted);">
                            <span class="material-symbols-outlined" style="font-size: 2rem;">inbox</span>
                            <p style="margin-top: 0.5rem;">No rows returned</p>
                        </div>
                    `;
                    resultsContainer.style.display = 'block';
                }
            } else {
                statusSpan.textContent = response.message;
                statusSpan.style.color = '#e74c3c';
                resultsContainer.innerHTML = `
                    <div style="padding: 1rem; color: #e74c3c;">
                        <span class="material-symbols-outlined">error</span>
                        <code style="display: block; margin-top: 0.5rem; white-space: pre-wrap;">${response.message}</code>
                    </div>
                `;
                resultsContainer.style.display = 'block';
            }
        } catch (error) {
            statusSpan.textContent = 'Error executing query';
            statusSpan.style.color = '#e74c3c';
            resultsContainer.innerHTML = `
                <div style="padding: 1rem; color: #e74c3c;">
                    <span class="material-symbols-outlined">error</span>
                    <code style="display: block; margin-top: 0.5rem;">${error.message}</code>
                </div>
            `;
            resultsContainer.style.display = 'block';
        } finally {
            executeBtn.disabled = false;
            executeBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 1rem;">play_arrow</span> Execute Query';
        }
    }

    renderSQLTable(columns, rows) {
        const headerCells = columns.map(col => `<th style="padding: 0.75rem 1rem; text-align: left; background: rgba(0,255,157,0.1); color: var(--primary); font-weight: 600; white-space: nowrap; font-size: 0.8rem;">${col}</th>`).join('');

        const bodyRows = rows.map(row => {
            const cells = row.map(cell => {
                let displayValue = cell;
                // Format different types
                if (cell === null) {
                    displayValue = '<span style="color: var(--text-muted); font-style: italic;">NULL</span>';
                } else if (typeof cell === 'object') {
                    displayValue = `<code style="font-size: 0.7rem;">${JSON.stringify(cell)}</code>`;
                } else if (typeof cell === 'boolean') {
                    displayValue = cell ? '<span style="color: #2ed573;">true</span>' : '<span style="color: #e74c3c;">false</span>';
                }
                return `<td style="padding: 0.5rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 0.8rem;" title="${String(cell).replace(/"/g, '&quot;')}">${displayValue}</td>`;
            }).join('');
            return `<tr style="transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">${cells}</tr>`;
        }).join('');

        return `
            <div style="overflow-x: auto; overflow-y: auto; max-height: 400px; max-width: 100%;">
                <table style="min-width: 100%; border-collapse: collapse; font-size: 0.8rem; table-layout: auto;">
                    <thead style="position: sticky; top: 0; z-index: 1;"><tr>${headerCells}</tr></thead>
                    <tbody>${bodyRows}</tbody>
                </table>
            </div>
        `;
    }

    // ==================== PDF EXPORTS ====================
    async exportUsersPDF() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const width = doc.internal.pageSize.getWidth();
        const height = doc.internal.pageSize.getHeight();

        // Dark Background
        doc.setFillColor(15, 15, 15);
        doc.rect(0, 0, width, height, 'F');

        // Fsociety Branding
        doc.setFont("courier", "bold");
        doc.setFontSize(28);
        doc.setTextColor(0, 255, 157); // fsociety green
        doc.text("FSOCIETY", 14, 25);

        doc.setFontSize(10);
        doc.setTextColor(52, 152, 219); // secondary blue
        doc.text("INTERNAL ASSET: USER_MANIFEST.DAT", 14, 32);

        doc.setDrawColor(0, 255, 157);
        doc.setLineWidth(0.5);
        doc.line(14, 35, width - 14, 35);

        const tableData = this.users.map(u => [
            u.username || 'N/A',
            u.email,
            u.role.toUpperCase(),
            u.is_active ? 'ACTIVE' : 'INACTIVE',
            new Date(u.created_at).toLocaleDateString()
        ]);

        doc.autoTable({
            startY: 45,
            head: [['Username', 'Email', 'Role', 'Status', 'Joined']],
            body: tableData,
            theme: 'grid',
            styles: {
                fillColor: [25, 25, 25],
                textColor: [255, 255, 255],
                fontSize: 9,
                font: "courier",
                lineColor: [40, 40, 40]
            },
            headStyles: {
                fillColor: [0, 255, 157],
                textColor: [0, 0, 0],
                fontStyle: 'bold'
            },
            alternateRowStyles: {
                fillColor: [20, 20, 20]
            }
        });

        doc.save(`fsociety_users_manifest_${new Date().getTime()}.pdf`);
        Utils.showToast("Secure PDF Manifest Exported", "success");
    }

    async exportSQLResultsPDF() {
        if (!this.lastSQLResults) return;

        const { jsPDF } = window.jspdf;
        const columns = this.lastSQLResults.columns;
        const rows = this.lastSQLResults.rows.map(row =>
            row.map(cell => {
                if (cell === null) return 'NULL';
                if (typeof cell === 'object') return JSON.stringify(cell);
                return String(cell);
            })
        );

        // DYNAMIC PAGE SIZING based on column count
        // Default is A4 Landscape (297mm width)
        let format = 'a4';
        let orientation = 'l';
        let fontSize = 8;

        if (columns.length > 15) {
            format = 'a3'; // 420mm width
            fontSize = 7;
        }
        if (columns.length > 25) {
            format = 'a2'; // 594mm width
            fontSize = 6;
        }

        const doc = new jsPDF(orientation, 'mm', format);
        const width = doc.internal.pageSize.getWidth();
        const height = doc.internal.pageSize.getHeight();

        // Dark Background
        doc.setFillColor(10, 10, 10);
        doc.rect(0, 0, width, height, 'F');

        const querySnippet = document.getElementById('sql-query-input').value.substring(0, 60).replace(/\n/g, ' ');

        doc.setFont("courier", "bold");
        doc.setFontSize(22);
        doc.setTextColor(243, 156, 18); // Amber/Orange for SQL
        doc.text("DATABASE_QUERY_RESULTS", 14, 20);

        doc.setFontSize(9);
        doc.setTextColor(150, 150, 150);
        doc.text(`QUERY_HASH: ${Utils.generateId().toUpperCase()}`, 14, 28);
        doc.text(`TIMESTAMP: ${new Date().toISOString()}`, 14, 33);
        doc.text(`ORIGIN: FSOCIETY_SQL_CONSOLE | FORMAT: ${format.toUpperCase()}`, 14, 38);

        doc.autoTable({
            startY: 45,
            head: [columns],
            body: rows,
            theme: 'grid',
            horizontalPageBreak: true,
            horizontalPageBreakRepeat: 0,
            styles: {
                fontSize: fontSize,
                cellPadding: 1.5,
                font: "courier",
                fillColor: [20, 20, 20],
                textColor: [200, 200, 200],
                lineColor: [40, 40, 40],
                overflow: 'linebreak',
                valign: 'middle'
            },
            headStyles: {
                fillColor: [243, 156, 18],
                textColor: [0, 0, 0],
                fontStyle: 'bold'
            },
            didParseCell: function (data) {
                // Only truncate if extremely long and columns are many
                if (data.section === 'body' && data.cell.raw && columns.length > 10) {
                    const val = String(data.cell.raw);
                    if (val.length > 100) {
                        data.cell.text = [val.substring(0, 30) + '...' + val.substring(val.length - 20)];
                    }
                }
            },
            alternateRowStyles: {
                fillColor: [15, 15, 15]
            },
            margin: { left: 10, right: 10, bottom: 20 }
        });

        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.setTextColor(100);
            doc.text(`Page ${i} of ${pageCount} | Fsociety Secure Audit`, width - 60, height - 10);
        }

        doc.save(`sql_manifest_${new Date().getTime()}.pdf`);
        Utils.showToast(`Exported ${format.toUpperCase()} Report`, "success");
    }

    // ==================== STATS EXPORTS ====================
    async exportStatsPDF() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        const width = doc.internal.pageSize.getWidth();
        const height = doc.internal.pageSize.getHeight();

        // Dark Background
        doc.setFillColor(15, 15, 15);
        doc.rect(0, 0, width, height, 'F');

        // Header
        doc.setFont("courier", "bold");
        doc.setFontSize(28);
        doc.setTextColor(0, 255, 157);
        doc.text("FSOCIETY", 14, 25);

        doc.setFontSize(10);
        doc.setTextColor(52, 152, 219);
        doc.text("PLATFORM STATISTICS REPORT", 14, 32);
        doc.text(`Generated: ${new Date().toISOString()}`, 14, 38);

        doc.setDrawColor(0, 255, 157);
        doc.setLineWidth(0.5);
        doc.line(14, 42, width - 14, 42);

        // Collect stats
        const stats = [
            ['Metric', 'Value'],
            ['Total Users', document.getElementById('stat-users')?.textContent || 'N/A'],
            ['Active Users', document.getElementById('stat-active')?.textContent || 'N/A'],
            ['Total Scans', document.getElementById('stat-scans')?.textContent || 'N/A'],
            ['Phishing Checks', document.getElementById('stat-phishing')?.textContent || 'N/A'],
            ['VPN Configs', document.getElementById('stat-vpn')?.textContent || 'N/A'],
            ['Chat Sessions', document.getElementById('stat-chat-sessions')?.textContent || 'N/A'],
            ['Chat Messages', document.getElementById('stat-chat-messages')?.textContent || 'N/A']
        ];

        doc.autoTable({
            startY: 50,
            head: [stats[0]],
            body: stats.slice(1),
            theme: 'grid',
            styles: {
                fillColor: [25, 25, 25],
                textColor: [255, 255, 255],
                fontSize: 11,
                font: "courier",
                lineColor: [40, 40, 40]
            },
            headStyles: {
                fillColor: [0, 255, 157],
                textColor: [0, 0, 0],
                fontStyle: 'bold'
            },
            alternateRowStyles: { fillColor: [20, 20, 20] }
        });

        doc.save(`fsociety_stats_${new Date().getTime()}.pdf`);
        Utils.showToast("Stats PDF Exported", "success");
    }

    exportStatsCSV() {
        const stats = [
            ['Metric', 'Value'],
            ['Total Users', document.getElementById('stat-users')?.textContent || 'N/A'],
            ['Active Users', document.getElementById('stat-active')?.textContent || 'N/A'],
            ['Total Scans', document.getElementById('stat-scans')?.textContent || 'N/A'],
            ['Phishing Checks', document.getElementById('stat-phishing')?.textContent || 'N/A'],
            ['VPN Configs', document.getElementById('stat-vpn')?.textContent || 'N/A'],
            ['Chat Sessions', document.getElementById('stat-chat-sessions')?.textContent || 'N/A'],
            ['Chat Messages', document.getElementById('stat-chat-messages')?.textContent || 'N/A']
        ];

        const csv = stats.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
        this.downloadCSV(csv, `fsociety_stats_${new Date().getTime()}.csv`);
        Utils.showToast("Stats CSV Exported", "success");
    }

    // ==================== ACTIVITIES EXPORTS ====================
    async exportActivitiesPDF() {
        if (!this.activities || this.activities.length === 0) {
            Utils.showToast("No activities to export", "warning");
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('l', 'mm', 'a4');
        const width = doc.internal.pageSize.getWidth();
        const height = doc.internal.pageSize.getHeight();

        // Dark Background
        doc.setFillColor(15, 15, 15);
        doc.rect(0, 0, width, height, 'F');

        // Header
        doc.setFont("courier", "bold");
        doc.setFontSize(22);
        doc.setTextColor(0, 255, 157);
        doc.text("USER ACTIVITY LOG", 14, 20);

        doc.setFontSize(9);
        doc.setTextColor(150, 150, 150);
        doc.text(`Generated: ${new Date().toISOString()} | Total Entries: ${this.activities.length}`, 14, 28);

        // Helper to safely format dates
        const formatDate = (dateStr) => {
            if (!dateStr) return 'N/A';
            try {
                const d = new Date(dateStr);
                if (isNaN(d.getTime())) return 'N/A';
                return d.toLocaleString();
            } catch {
                return 'N/A';
            }
        };

        const tableData = this.activities.map(a => [
            a.user?.username || 'System',
            a.action?.replace(/_/g, ' ').toUpperCase() || 'N/A',
            (a.details?.target || a.details?.url || a.details?.domain || '').substring(0, 40),
            a.ip_address || 'N/A',
            formatDate(a.created_at || a.timestamp || a.date)
        ]);

        doc.autoTable({
            startY: 35,
            head: [['User', 'Action', 'Target', 'IP Address', 'Timestamp']],
            body: tableData,
            theme: 'grid',
            styles: {
                fillColor: [25, 25, 25],
                textColor: [255, 255, 255],
                fontSize: 8,
                font: "courier",
                lineColor: [40, 40, 40]
            },
            headStyles: {
                fillColor: [52, 152, 219],
                textColor: [255, 255, 255],
                fontStyle: 'bold'
            },
            alternateRowStyles: { fillColor: [20, 20, 20] }
        });

        doc.save(`fsociety_activities_${new Date().getTime()}.pdf`);
        Utils.showToast("Activities PDF Exported", "success");
    }

    exportActivitiesCSV() {
        if (!this.activities || this.activities.length === 0) {
            Utils.showToast("No activities to export", "warning");
            return;
        }

        const header = ['User', 'Action', 'Target', 'IP Address', 'User Agent', 'Timestamp'];
        const rows = this.activities.map(a => [
            a.user?.username || 'System',
            a.action || 'N/A',
            a.details?.target || a.details?.url || a.details?.domain || '',
            a.ip_address || 'N/A',
            a.user_agent || 'N/A',
            a.created_at
        ]);

        const csv = [header, ...rows].map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
        this.downloadCSV(csv, `fsociety_activities_${new Date().getTime()}.csv`);
        Utils.showToast("Activities CSV Exported", "success");
    }

    // ==================== USERS CSV EXPORT ====================
    exportUsersCSV() {
        if (!this.users || this.users.length === 0) {
            Utils.showToast("No users to export", "warning");
            return;
        }

        const header = ['Username', 'Email', 'Role', 'Status', 'Created At'];
        const rows = this.users.map(u => [
            u.username || 'N/A',
            u.email,
            u.role,
            u.is_active ? 'Active' : 'Inactive',
            u.created_at
        ]);

        const csv = [header, ...rows].map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
        this.downloadCSV(csv, `fsociety_users_${new Date().getTime()}.csv`);
        Utils.showToast("Users CSV Exported", "success");
    }

    // ==================== SQL RESULTS CSV EXPORT ====================
    exportSQLResultsCSV() {
        if (!this.lastSQLResults) {
            Utils.showToast("No SQL results to export", "warning");
            return;
        }

        const { columns, rows } = this.lastSQLResults;
        const csvRows = [columns, ...rows].map(row =>
            row.map(cell => {
                if (cell === null) return '""';
                const str = typeof cell === 'object' ? JSON.stringify(cell) : String(cell);
                return `"${str.replace(/"/g, '""')}"`;
            }).join(',')
        );

        this.downloadCSV(csvRows.join('\n'), `sql_results_${new Date().getTime()}.csv`);
        Utils.showToast("SQL Results CSV Exported", "success");
    }

    // ==================== CSV UTILITY ====================
    downloadCSV(csvContent, filename) {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Make instance accessible for inline event handlers
window.adminView = new AdminView();
export default window.adminView;
