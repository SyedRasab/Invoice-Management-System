/*
 * Invoice Management System - Main JavaScript
 * Handles API communication, form validation, and dynamic UI updates
 */

// API Base URL
// API Base URL
const API_BASE_URL = '/api';

// ==================== UTILITY FUNCTIONS ====================

/**
 * Make API request
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Request failed');
        }

        // Handle file downloads
        if (response.headers.get('content-type')?.includes('application/pdf') ||
            response.headers.get('content-type')?.includes('spreadsheet')) {
            return response.blob();
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return `$ ${parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Download file from blob
 */
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
}

// ==================== CUSTOMER FUNCTIONS ====================

/**
 * Load all customers
 */
async function loadCustomers() {
    try {
        const customers = await apiRequest('/customers');
        return customers;
    } catch (error) {
        showAlert('Failed to load customers: ' + error.message, 'error');
        return [];
    }
}

/**
 * Load customer by ID
 */
async function loadCustomer(customerId) {
    try {
        const customer = await apiRequest(`/customers/${customerId}`);
        return customer;
    } catch (error) {
        showAlert('Failed to load customer: ' + error.message, 'error');
        return null;
    }
}

/**
 * Create new customer
 */
async function createCustomer(customerData) {
    try {
        const customer = await apiRequest('/customers', 'POST', customerData);
        showAlert('Customer created successfully!', 'success');
        return customer;
    } catch (error) {
        showAlert('Failed to create customer: ' + error.message, 'error');
        return null;
    }
}

// ==================== INVOICE FUNCTIONS ====================

/**
 * Load all invoices
 */
async function loadInvoices() {
    try {
        const invoices = await apiRequest('/invoices');
        return invoices;
    } catch (error) {
        showAlert('Failed to load invoices: ' + error.message, 'error');
        return [];
    }
}

/**
 * Load invoice by ID
 */
async function loadInvoice(invoiceId) {
    try {
        const invoice = await apiRequest(`/invoices/${invoiceId}`);
        return invoice;
    } catch (error) {
        showAlert('Failed to load invoice: ' + error.message, 'error');
        return null;
    }
}

/**
 * Create new invoice
 */
async function createInvoice(invoiceData) {
    try {
        const invoice = await apiRequest('/invoices', 'POST', invoiceData);
        showAlert('Invoice created successfully!', 'success');
        return invoice;
    } catch (error) {
        showAlert('Failed to create invoice: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Download invoice PDF
 */
async function downloadInvoicePDF(invoiceId, invoiceNumber) {
    try {
        const blob = await apiRequest(`/invoices/${invoiceId}/pdf`);
        downloadFile(blob, `${invoiceNumber}.pdf`);
        showAlert('PDF downloaded successfully!', 'success');
    } catch (error) {
        showAlert('Failed to download PDF: ' + error.message, 'error');
    }
}

// ==================== CALCULATION FUNCTIONS ====================

/**
 * Calculate number of pieces
 */
async function calculatePieces(silverWeight, pieceSize) {
    try {
        const result = await apiRequest('/calculate/pieces', 'POST', {
            silver_weight: silverWeight,
            piece_size: pieceSize
        });
        return result.num_pieces;
    } catch (error) {
        console.error('Calculation error:', error);
        return 0;
    }
}

/**
 * Calculate total amount and balance
 */
async function calculateTotal(billingMode, silverWeight, numPieces, rate, advancePayment = 0) {
    try {
        const result = await apiRequest('/calculate/total', 'POST', {
            billing_mode: billingMode,
            silver_weight: silverWeight,
            num_pieces: numPieces,
            rate: rate,
            advance_payment: advancePayment
        });
        return result;
    } catch (error) {
        console.error('Calculation error:', error);
        return { total_amount: 0, remaining_balance: 0 };
    }
}

// ==================== PAYMENT FUNCTIONS ====================

/**
 * Add payment to invoice
 */
async function addPayment(invoiceId, amount, paymentMethod, notes = '', createdBy = 'System') {
    try {
        const payment = await apiRequest(`/invoices/${invoiceId}/payments`, 'POST', {
            amount: amount,
            payment_method: paymentMethod,
            notes: notes,
            created_by: createdBy
        });
        showAlert('Payment added successfully!', 'success');
        return payment;
    } catch (error) {
        showAlert('Failed to add payment: ' + error.message, 'error');
        throw error;
    }
}

/**
 * Get payments for invoices
 */
async function getInvoicePayments(invoiceId) {
    try {
        const payments = await apiRequest(`/invoices/${invoiceId}/payments`);
        return payments;
    } catch (error) {
        console.error('Failed to load payments:', error);
        return [];
    }
}

/**
 * Load payment methods
 */
async function loadPaymentMethods() {
    try {
        const methods = await apiRequest('/config/payment-methods');
        return methods;
    } catch (error) {
        console.error('Failed to load payment methods:', error);
        return ['Cash', 'Bank Transfer', 'Cheque', 'Mobile Wallet'];
    }
}

// ==================== EXPORT FUNCTIONS ====================

/**
 * Export data to Excel
 */
async function exportToExcel() {
    try {
        const blob = await apiRequest('/export/excel');
        const timestamp = new Date().toISOString().slice(0, 10);
        downloadFile(blob, `invoice_data_${timestamp}.xlsx`);
        showAlert('Data exported successfully!', 'success');
    } catch (error) {
        showAlert('Failed to export data: ' + error.message, 'error');
    }
}

// ==================== CONFIGURATION FUNCTIONS ====================

/**
 * Load piece sizes
 */
async function loadPieceSizes() {
    try {
        const pieceSizes = await apiRequest('/config/piece-sizes');
        return pieceSizes;
    } catch (error) {
        console.error('Failed to load piece sizes:', error);
        return ['10 Tola', '500 g', '1 kg'];
    }
}

/**
 * Load billing modes
 */
async function loadBillingModes() {
    try {
        const billingModes = await apiRequest('/config/billing-modes');
        return billingModes;
    } catch (error) {
        console.error('Failed to load billing modes:', error);
        return ['Ready', 'Mazduri'];
    }
}

// ==================== FORM VALIDATION ====================

/**
 * Validate form field
 */
function validateField(field, value, rules) {
    const errors = [];

    if (rules.required && !value) {
        errors.push(`${field} is required`);
    }

    if (rules.numeric && value && isNaN(value)) {
        errors.push(`${field} must be a number`);
    }

    if (rules.positive && value && parseFloat(value) <= 0) {
        errors.push(`${field} must be greater than 0`);
    }

    if (rules.min && value && parseFloat(value) < rules.min) {
        errors.push(`${field} must be at least ${rules.min}`);
    }

    return errors;
}

/**
 * Show field error
 */
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.classList.add('error');

        // Remove existing error message
        const existingError = field.parentElement.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }
}

/**
 * Clear field error
 */
function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.classList.remove('error');
        const errorDiv = field.parentElement.querySelector('.form-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
}

/**
 * Clear all form errors
 */
function clearAllErrors(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const errorFields = form.querySelectorAll('.error');
        errorFields.forEach(field => field.classList.remove('error'));

        const errorMessages = form.querySelectorAll('.form-error');
        errorMessages.forEach(msg => msg.remove());
    }
}

// ==================== MODAL FUNCTIONS ====================

/**
 * Show modal
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Hide modal
 */
function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// ==================== LOADING STATE ====================

/**
 * Set loading state
 */
function setLoading(elementId, isLoading) {
    const element = document.getElementById(elementId);
    if (element) {
        if (isLoading) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }
}
