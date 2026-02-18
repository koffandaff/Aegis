import Api from './api.js';
import Router from './router.js';

class Auth {
    static async login(email, password) {
        try {
            const formData = { email, password };
            const response = await Api.post('/auth/login', formData);

            // If response is null, the disabled modal was shown by Api
            if (!response) {
                return null;
            }

            // Refresh token is handled via HttpOnly cookie by the backend, so we don't need to save it here.
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('user', JSON.stringify(response.user));

            return response.user;
        } catch (error) {
            throw error;
        }
    }

    static async signup(userData) {
        return await Api.post('/auth/signup', userData);
    }

    static logout() {
        // Optimistic Logout: Clear state immediately for UI responsiveness
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');

        // Fire-and-forget backend call (don't await)
        try {
            Api.post('/auth/logout').catch(err => console.warn('Logout API failed:', err));
        } catch (e) {
            // Ignore errors
        }

        window.location.hash = '/login';
        window.location.reload(); // Force reload to clear memory/states
    }

    static isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }

    static getUser() {
        return JSON.parse(localStorage.getItem('user'));
    }

    static getCurrentUser() {
        return this.getUser();
    }

    static async forgotPassword(email) {
        return await Api.post('/auth/forgot-password', { email });
    }

    static async verifyOtp(email, otp) {
        return await Api.post('/auth/verify-otp', { email, otp });
    }

    static async resetPassword(email, otp, new_password) {
        return await Api.post('/auth/reset-password', { email, otp, new_password });
    }
}

export default Auth;
