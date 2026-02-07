import Auth from './auth.js';
import Components from './components.js';
import LandingView from './views/landing.js';
import LoginView from './views/login.js';
import SignupView from './views/signup.js';
import DashboardView from './views/dashboard.js';
import AdminView from './views/admin.js';
import ScanView from './views/scan.js';
import HistoryView from './views/history.js';
import SecurityView from './views/security.js';
import ChatView from './views/chat.js';
import VpnView from './views/vpn.js';
import FilesView from './views/files.js';
import PhishingView from './views/phishing.js';
import FootprintView from './views/footprint.js';
import ProfileView from './views/profile.js';
import PrivacyView from './views/privacy.js';
import TermsView from './views/terms.js';
import ContactView from './views/contact.js';
import ForgotPasswordView from './views/forgot_password.js';
import ResetPasswordView from './views/reset_password.js';

const routes = {
    '/': LandingView,
    '/login': LoginView,
    '/signup': SignupView,
    '/dashboard': DashboardView,
    '/admin': AdminView,
    '/scan': ScanView,
    '/history': HistoryView,
    '/security': SecurityView,
    '/chat': ChatView,
    '/vpn': VpnView,
    '/files': FilesView,
    '/phishing': PhishingView,
    '/footprint': FootprintView,
    '/profile': ProfileView,
    '/privacy': PrivacyView,
    '/terms': TermsView,
    '/contact': ContactView,
    '/forgot-password': ForgotPasswordView,
    '/reset-password': ResetPasswordView
};

class Router {
    constructor() {
        this.routes = {};
        // Initialize routes from the const routes object
        for (const path in routes) {
            // Determine if authentication is required for the route
            let requiresAuth = false;
            if (['/dashboard', '/admin', '/scan', '/history', '/security', '/chat', '/vpn', '/files', '/phishing', '/footprint', '/profile'].includes(path)) {
                requiresAuth = true;
            }
            this.addRoute(path, routes[path], requiresAuth);
        }
        window.addEventListener('hashchange', () => this.handleRoute());
        this.app = document.getElementById('app');
    }

    addRoute(path, view, requiresAuth = false) {
        this.routes[path] = { view, requiresAuth };
    }

    navigate(path) {
        window.location.hash = path;
    }

    async handleRoute() {
        let fullPath = window.location.hash.slice(1) || '/';

        // Split path and query params
        const [pathOnly, queryString] = fullPath.split('?');
        let path = pathOnly;

        // Normalize paths that don't start with /
        if (path !== '/' && !path.startsWith('/')) {
            path = '/' + path;
        }

        const route = this.routes[path] || this.routes['/login'];

        if (!route) {
            // Load custom 404 page
            try {
                const response = await fetch('/404.html');
                if (response.ok) {
                    this.app.innerHTML = await response.text();
                } else {
                    this.app.innerHTML = '<h1 style="color:red;text-align:center;margin-top:20%">404 - Page Not Found</h1>';
                }
            } catch (e) {
                this.app.innerHTML = '<h1 style="color:red;text-align:center;margin-top:20%">404 - Page Not Found</h1>';
            }
            return;
        }

        if (route.requiresAuth && !Auth.isAuthenticated()) {
            // User requested improvement: Redirect to Home instead of Login
            this.navigate('/');
            return;
        }

        if (path === '/login' && Auth.isAuthenticated()) {
            this.navigate('/dashboard');
            return;
        }

        // Cleanup previous view if it has a destroy method
        if (this.currentView && typeof this.currentView.destroy === 'function') {
            this.currentView.destroy();
        }

        try {
            // Render new view
            this.app.innerHTML = await route.view.render();
            this.currentView = route.view; // Track current view

            // Inject floating chat widget on authenticated pages (except chat page itself)
            if (route.requiresAuth && path !== '/chat') {
                this.app.innerHTML += Components.renderFloatingChat();
            }

            if (route.view.afterRender) {
                await route.view.afterRender();
            }
        } catch (e) {
            console.error('Route Error', e);
            // Improve UX: Don't nuke the page, just show a toast
            // If it's a critical initial load failure, maybe show a better error state
            if (!this.currentView) {
                this.app.innerHTML = `
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; text-align: center;">
                        <span class="material-symbols-outlined" style="font-size: 4rem; color: #ff4757; margin-bottom: 1rem;">error_outline</span>
                        <h1>Something went wrong</h1>
                        <p style="color: var(--text-muted); margin-bottom: 2rem;">Failed to load the requested page.</p>
                        <a href="#/" class="btn-primary">Return Home</a>
                    </div>
                `;
            } else {
                // If we already have a view, just notify
                // Dynamic import to avoid circular dependency if Utils isn't globally available, 
                // but assuming it is or we can get it from somewhere. 
                // For now, let's use a simple alert fallback or console.
                alert("Error loading content: " + e.message);
            }
        }
    }


    init() {
        this.handleRoute();
    }
}

export default new Router();
