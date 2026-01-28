import Router from './router.js';
import LoginView from './views/login.js';
import SignupView from './views/signup.js';
import DashboardView from './views/dashboard.js';
import ScanView from './views/scan.js';
import SecurityView from './views/security.js';
import PhishingView from './views/phishing.js';
import FileView from './views/files.js';
import HistoryView from './views/history.js';
import AdminView from './views/admin.js';
import VpnView from './views/vpn.js';
import ProfileView from './views/profile.js';
import ChatView from './views/chat.js';
import FootprintView from './views/footprint.js';
import LandingView from './views/landing.js';

// Register Routes
Router.addRoute('/login', LoginView);
Router.addRoute('/signup', SignupView);
Router.addRoute('/dashboard', DashboardView, true);
Router.addRoute('/chat', ChatView, true);
Router.addRoute('/footprint', FootprintView, true);
Router.addRoute('/scan', ScanView, true);
Router.addRoute('/security', SecurityView, true);
Router.addRoute('/phishing', PhishingView, true);
Router.addRoute('/files', FileView, true);
Router.addRoute('/history', HistoryView, true);
Router.addRoute('/admin', AdminView, true);
Router.addRoute('/vpn', VpnView, true);
Router.addRoute('/profile', ProfileView, true);

// Add default route - Landing Page for unauthenticated users
Router.addRoute('/', LandingView);

// Initialize Router
Router.init();
