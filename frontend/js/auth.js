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

            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);
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
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.hash = '/login';
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
}

export default Auth;
