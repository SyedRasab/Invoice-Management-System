/**
 * API Service Module
 * Centralizes all backend communication
 */

const API_BASE_URL = '/api';

class ApiService {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    // Helper for fetch requests
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        // Default headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Include credentials for auth
        const config = {
            ...options,
            headers,
            credentials: 'include'
        };

        try {
            const response = await fetch(url, config);

            // Handle 401 Unauthorized (Redirect to login)
            if (response.status === 401 && !window.location.href.includes('login.html')) {
                window.location.href = 'login.html';
                return;
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.message || `Request failed with status ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Auth
    async login(username, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    }

    async logout() {
        return this.request('/auth/logout', { method: 'POST' });
    }

    async getCurrentUser() {
        return this.request('/auth/check');
    }

    // Customers
    async getCustomers() {
        return this.request('/customers');
    }

    async getCustomer(id) {
        return this.request(`/customers/${id}`);
    }

    async createCustomer(data) {
        return this.request('/customers', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateCustomer(id, data) {
        return this.request(`/customers/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async getCustomerOutstanding(id) {
        return this.request(`/customers/${id}/outstanding`);
    }

    // Invoices
    async getInvoices() {
        return this.request('/invoices');
    }

    async getInvoice(id) {
        return this.request(`/invoices/${id}`);
    }

    async createInvoice(data) {
        return this.request('/invoices', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateInvoiceStatus(id, status) {
        return this.request(`/invoices/${id}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
    }

    // Payments
    async addPayment(invoiceId, data) {
        return this.request(`/invoices/${invoiceId}/payments`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async getPaymentHistory(invoiceId) {
        return this.request(`/invoices/${invoiceId}/payments`);
    }

    // Calculations
    async calculatePieces(weight, size) {
        return this.request('/calculate/pieces', {
            method: 'POST',
            body: JSON.stringify({ silver_weight: weight, piece_size: size })
        });
    }

    async calculateTotal(data) {
        return this.request('/calculate/total', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Config
    async getBillingModes() {
        return this.request('/config/billing-modes');
    }

    async getPieceSizes() {
        return this.request('/config/piece-sizes');
    }

    async getPaymentMethods() {
        return this.request('/config/payment-methods');
    }
}

// Singleton instance
const api = new ApiService();
window.api = api; // Expose globally
