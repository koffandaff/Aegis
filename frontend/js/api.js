const storedApiUrl = localStorage.getItem('api_url');
const isProduction = window.location.hostname.includes('vercel.app');

// Prioritize stored URL, then environment detection. 
// Only use config.js override if we are in production or if it's explicitly set for dev but we want to ignore it for localhost unless forced.
let API_URL = storedApiUrl;

if (!API_URL) {
    if (isProduction) {
        API_URL = window.APP_CONFIG?.API_URL || 'https://reconauto-backend.vercel.app/api';
    } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        API_URL = `http://${window.location.hostname}:8000/api`;
    } else {
        // Network access (e.g. 192.168.x.x)
        API_URL = `${window.location.protocol}//${window.location.hostname}:8000/api`;
    }
}


class Api {
    static baseUrl = API_URL;

    static async request(endpoint, method = 'GET', body = null) {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers,
            credentials: 'include'
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_URL}${endpoint}`, config);

            // Handle Unauthorized (Token Expired)
            if (response.status === 401) {
                // Prevent infinite loops: if refresh fails, logout immediately
                if (endpoint.includes('/auth/refresh')) {
                    this.handleLogout();
                    return null;
                }

                // If login fails (401), it means Invalid Credentials. 
                // We MUST throw an error so the UI shows the toast.
                if (endpoint.includes('/auth/login')) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Invalid credentials');
                }

                try {
                    console.log('Token expired. Attempting refresh...');
                    console.log(`[API] Attempting refresh on ${API_URL}/auth/refresh`);
                    // Attempt to refresh token
                    // We use fetch directly here to avoid circular dependency on this interceptor, 
                    // though recursion protection above handles it too. 
                    // But using this.post('/auth/refresh') is cleaner.

                    const refreshResponse = await this.post('/auth/refresh');

                    if (refreshResponse && refreshResponse.access_token) {
                        console.log('Token refresh successful');
                        localStorage.setItem('access_token', refreshResponse.access_token);

                        // Update authorization header with new token
                        const newHeaders = { ...headers };
                        newHeaders['Authorization'] = `Bearer ${refreshResponse.access_token}`;

                        // Retry original request with new config (mark as retry)
                        const retryConfig = { ...config, headers: newHeaders, _isRetry: true };

                        // Prevent infinite recursion if retry fails again
                        if (config._isRetry) {
                            console.error('Retry failed after refresh. Logging out.');
                            this.handleLogout();
                            return null;
                        }

                        const retryResponse = await fetch(`${API_URL}${endpoint}`, retryConfig);

                        if (retryResponse.status === 401) {
                            this.handleLogout();
                            return null;
                        }

                        return await retryResponse.json();
                    } else {
                        console.warn('Refresh failed: No token returned');
                        this.handleLogout();
                        return null;
                    }
                } catch (e) {
                    console.error('Session expired or refresh failed:', e);
                    this.handleLogout();
                    return null;
                }
            }

            const data = await response.json();

            // Check for account disabled by admin
            if (response.status === 403 && data.detail?.code === 'ACCOUNT_DISABLED') {
                this.showDisabledModal(data.detail.message);
                return null;
            }

            // Handle Rate Limiting (429)
            if (response.status === 429) {
                const message = data.detail?.message || 'Too many requests. Please wait and try again.';
                this.showRateLimitToast(message);
                throw new Error(message);
            }

            if (!response.ok) {
                let errorMessage = data.detail || 'API Request Failed';
                if (typeof errorMessage === 'object') {
                    if (Array.isArray(errorMessage)) {
                        // Handle Pydantic validation errors
                        errorMessage = errorMessage.map(err => err.msg).join(', ');
                    } else if (errorMessage.message) {
                        errorMessage = errorMessage.message;
                    } else {
                        errorMessage = JSON.stringify(errorMessage);
                    }
                }
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            // Distinguish between network failures (cold start) and actual API errors
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                console.error('[API] Network error — server may be in cold start:', endpoint);
                throw new Error('Server is waking up from cold start. Please wait 30–60 seconds and try again.');
            }
            console.group('API Request Failed');
            console.error('Endpoint:', endpoint);
            console.error('Method:', method);
            console.error('Error:', error);
            console.groupEnd();
            throw error;
        }
    }

    static showDisabledModal(message) {
        // Remove any existing modal
        const existingModal = document.getElementById('disabled-modal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.id = 'disabled-modal';
        modal.innerHTML = `
            <div style="position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 10000; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(10px);">
                <div style="background: linear-gradient(145deg, rgba(30,30,35,0.95), rgba(15,15,20,0.98)); border: 1px solid #ff4757; border-radius: 16px; padding: 3rem; max-width: 450px; text-align: center; box-shadow: 0 0 50px rgba(255,71,87,0.3);">
                    <div style="width: 80px; height: 80px; margin: 0 auto 1.5rem; background: rgba(255,71,87,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <span class="material-symbols-outlined" style="font-size: 3rem; color: #ff4757;">block</span>
                    </div>
                    <h2 style="color: #ff4757; margin-bottom: 1rem; font-size: 1.5rem;">Account Disabled</h2>
                    <p style="color: #a0a0a0; margin-bottom: 2rem; line-height: 1.6;">${message}</p>
                    <button id="disabled-logout-btn" style="background: #ff4757; color: #fff; border: none; padding: 1rem 2rem; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 1rem; transition: all 0.3s;">
                        Logout & Exit
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('disabled-logout-btn').addEventListener('click', () => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.hash = '/login';
            modal.remove();
        });
    }

    static showRateLimitToast(message) {
        // Remove existing rate limit toast if any
        const existingToast = document.getElementById('rate-limit-toast');
        if (existingToast) existingToast.remove();

        const toast = document.createElement('div');
        toast.id = 'rate-limit-toast';
        toast.innerHTML = `
            <div style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 10001; 
                        background: linear-gradient(135deg, #ff4757, #c0392b); color: white; 
                        padding: 1rem 2rem; border-radius: 12px; box-shadow: 0 8px 32px rgba(255,71,87,0.4);
                        display: flex; align-items: center; gap: 1rem; animation: slideDown 0.3s ease;">
                <span class="material-symbols-outlined" style="font-size: 1.5rem;">speed</span>
                <div>
                    <div style="font-weight: bold; margin-bottom: 0.25rem;">Rate Limit Exceeded</div>
                    <div style="font-size: 0.85rem; opacity: 0.9;">${message}</div>
                </div>
            </div>
        `;
        document.body.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    static get(endpoint) {
        return this.request(endpoint, 'GET');
    }

    static post(endpoint, body) {
        return this.request(endpoint, 'POST', body);
    }

    static put(endpoint, body) {
        return this.request(endpoint, 'PUT', body);
    }

    static delete(endpoint) {
        return this.request(endpoint, 'DELETE');
    }

    static handleLogout() {
        console.log('Logging out due to session expiration');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.hash = '/login';
    }
}

export default Api;
