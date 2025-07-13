/**
 * Filum.ai Pain Point Agent - Main JavaScript (English Version)
 * ==========================================
 * 
 * This file contains the main JavaScript functionality for the web interface
 * including form handling, API calls, result display, and user interactions.
 * All interface text has been converted to English for international use.
 */

// Global configuration
const CONFIG = {
    API_BASE_URL: '',
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 500,
    MAX_RETRIES: 3
};

// Utility functions
const Utils = {
    /**
     * Debounce function to limit API calls
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Format confidence score as percentage
     */
    formatConfidence(score) {
        return Math.round(score * 100);
    },

    /**
     * Get confidence color based on score
     */
    getConfidenceColor(score) {
        if (score > 0.7) return 'success';
        if (score > 0.5) return 'warning';
        return 'secondary';
    },

    /**
     * Sanitize HTML to prevent XSS
     */
    sanitizeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        toast.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>${this.sanitizeHtml(message)}</span>
                <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    },

    /**
     * Smooth scroll to element
     */
    scrollToElement(element, offset = 0) {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
};

// API service for communicating with backend
const ApiService = {
    /**
     * Analyze pain point
     */
    async analyzePainPoint(formData) {
        try {
            console.log('Sending request to /analyze...');
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const responseText = await response.text();
            console.log('Raw response text:', responseText);
            
            let result;
            try {
                result = JSON.parse(responseText);
            } catch (parseError) {
                console.error('JSON parse error:', parseError);
                console.error('Response text that failed to parse:', responseText);
                throw new Error('Invalid JSON response from server');
            }
            
            console.log('Parsed JSON result:', result);
            return result;
            
        } catch (error) {
            console.error('API Error in analyzePainPoint:', error);
            throw error;
        }
    },

    /**
     * Get all solutions from knowledge base
     */
    async getAllSolutions() {
        try {
            const response = await fetch('/solutions');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await fetch('/health');
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error' };
        }
    }
};

// Form handling
class FormHandler {
    constructor(formSelector, resultsSelector) {
        this.form = document.querySelector(formSelector);
        this.resultsContainer = document.querySelector(resultsSelector);
        this.loadingOverlay = null;
        
        this.init();
    }

    init() {
        console.log('FormHandler init called');
        
        if (this.form) {
            this.form.addEventListener('submit', this.handleSubmit.bind(this));
            console.log('Form submit listener added');
        } else {
            console.warn('Form not found');
        }

        // Initialize loading overlay (simpler than modal)
        this.loadingOverlay = document.getElementById('loadingOverlay');
        console.log('Loading overlay element:', this.loadingOverlay);

        // Add input validation
        this.addValidation();
    }

    addValidation() {
        const painPointField = this.form?.querySelector('#painPoint');
        if (painPointField) {
            painPointField.addEventListener('input', this.validatePainPoint.bind(this));
        }
    }

    validatePainPoint(event) {
        const field = event.target;
        const value = field.value.trim();
        const minLength = 10;

        if (value.length < minLength) {
            field.setCustomValidity(`Please describe at least ${minLength} characters`);
        } else {
            field.setCustomValidity('');
        }
    }

    async handleSubmit(event) {
        event.preventDefault();

        const formData = new FormData(this.form);
        const painPoint = formData.get('pain_point')?.trim();

        if (!painPoint) {
            Utils.showToast('Please describe the customer pain point', 'warning');
            return;
        }

        let timeoutId = null;

        try {
            console.log('Starting pain point analysis...');
            this.showLoading();
            
            // Set timeout to automatically hide loading after 30 seconds
            timeoutId = setTimeout(() => {
                console.warn('Request timeout after 30 seconds');
                this.hideLoading();
                this.displayError('Request is taking too long. Please try again.');
                Utils.showToast('Timeout - Please try again', 'warning');
            }, 30000);
            
            const result = await ApiService.analyzePainPoint(formData);
            console.log('Analysis result:', result);
            
            // Clear timeout as request completed
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
            
            this.hideLoading();
            
            // Kiểm tra response format
            if (!result || typeof result !== 'object') {
                throw new Error('Invalid response format');
            }
            
            this.displayResults(result);
            Utils.showToast('Analysis success!', 'success');
            
        } catch (error) {
            console.error('Error in handleSubmit:', error);
            
            // Clear timeout nếu có error
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
            
            this.hideLoading();
            this.displayError('Có error xảy ra khi analysis. Vui lòng thử lại.');
            Utils.showToast('Error khi analysis pain point: ' + error.message, 'danger');
        }
    }

    showLoading() {
        console.log('showLoading called');
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('d-none');
            console.log('Loading overlay shown');
        } else {
            console.warn('Loading overlay not found');
        }
    }

    hideLoading() {
        console.log('hideLoading called');
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.add('d-none');
            console.log('Loading overlay hidden');
        } else {
            console.warn('Loading overlay not found');
        }
    }

    displayResults(data) {
        console.log('displayResults called with data:', data);
        
        if (!this.resultsContainer) {
            console.error('Results container not found');
            return;
        }

        try {
            const html = this.generateResultsHtml(data);
            console.log('Generated HTML length:', html.length);
            
            this.resultsContainer.innerHTML = html;
            
            // Add fade-in animation
            this.resultsContainer.classList.add('fade-in');
            
            // Scroll to results
            Utils.scrollToElement(this.resultsContainer, 100);
            
            console.log('Results displayed successfully');
        } catch (error) {
            console.error('Error in displayResults:', error);
            this.displayError('Error hiển thị results: ' + error.message);
        }
    }

    generateResultsHtml(data) {
        console.log('generateResultsHtml called with:', data);
        
        // Safe access with fallback values
        const painPointSummary = data?.pain_point_summary || data?.analysis || 'No summary information available';
        const confidenceScore = data?.confidence_score || data?.confidence || 0.5;
        const solutions = data?.recommended_solutions || data?.solutions || [];
        const reasoning = data?.reasoning || data?.explanation || '';
        const nextSteps = data?.next_steps || data?.recommendations || [];

        let html = `
            <div class="alert alert-success border-0 mb-3">
                <h6 class="alert-heading">
                    <i class="fas fa-check-circle me-2"></i>
                    Pain Point Summary
                </h6>
                <p class="mb-2">${Utils.sanitizeHtml(painPointSummary)}</p>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${Utils.formatConfidence(confidenceScore)}%"></div>
                </div>
                <small class="text-muted mt-2 d-block">
                    Confidence Level: ${Utils.formatConfidence(confidenceScore)}%
                </small>
            </div>
        `;

        if (solutions && solutions.length > 0) {
            html += '<h6 class="mb-3"><i class="fas fa-lightbulb me-2"></i>Solution recommend:</h6>';
            
            solutions.forEach((solution, index) => {
                html += this.generateSolutionHtml(solution, index);
            });
        } else {
            html += `
                <div class="alert alert-info border-0">
                    <h6 class="alert-heading">
                        <i class="fas fa-info-circle me-2"></i>
                        Thông tin
                    </h6>
                    <p class="mb-0">Chưa tìm thấy solution phù hợp. Vui lòng mô tả chi tiết hơn về vấn đề.</p>
                </div>
            `;
        }

        if (reasoning) {
            html += this.generateReasoningHtml(reasoning);
        }

        if (nextSteps && nextSteps.length > 0) {
            html += this.generateNextStepsHtml(nextSteps);
        }

        return html;
    }

    generateSolutionHtml(solution, index) {
        // Safe access với fallback values
        const name = solution?.name || solution?.title || `Solution ${index + 1}`;
        const description = solution?.description || solution?.summary || 'Không có mô tả';
        const category = solution?.category || solution?.type || 'Chung';
        const expectedImpact = solution?.expected_impact || solution?.impact || 'Tích cực';
        const confidenceScore = solution?.confidence_score || solution?.confidence || 0.5;
        const keyFeatures = solution?.key_features || solution?.features || [];
        
        const confidenceColor = Utils.getConfidenceColor(confidenceScore);
        
        return `
            <div class="card mb-3 solution-card border-start border-${confidenceColor} border-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title text-${confidenceColor} mb-0">
                            <span class="badge bg-${confidenceColor} me-2">${index + 1}</span>
                            ${Utils.sanitizeHtml(name)}
                        </h6>
                        <span class="badge bg-${confidenceColor}">
                            ${Utils.formatConfidence(confidenceScore)}%
                        </span>
                    </div>
                    
                    <p class="card-text text-muted small mb-2">
                        ${Utils.sanitizeHtml(description)}
                    </p>
                    
                    <div class="row g-2 mb-2">
                        <div class="col-6">
                            <small class="text-muted">
                                <i class="fas fa-layer-group me-1"></i>
                                <strong>Category:</strong> ${Utils.sanitizeHtml(category)}
                            </small>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">
                                <i class="fas fa-chart-line me-1"></i>
                                <strong>Impact:</strong> ${Utils.sanitizeHtml(expectedImpact)}
                            </small>
                        </div>
                    </div>
                    
                    ${keyFeatures && keyFeatures.length > 0 ? `
                        <div class="mb-2">
                            <small class="text-muted">
                                <strong><i class="fas fa-star me-1"></i>Key Features:</strong>
                            </small>
                            <div class="mt-1">
                                ${keyFeatures.slice(0, 3).map(feature => 
                                    `<span class="badge bg-light text-dark me-1 mb-1">${Utils.sanitizeHtml(feature)}</span>`
                                ).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    generateReasoningHtml(reasoning) {
        return `
            <div class="alert alert-info border-0 mt-3">
                <h6 class="alert-heading">
                    <i class="fas fa-brain me-2"></i>
                    Analysis Reasoning
                </h6>
                <p class="mb-0 small">${Utils.sanitizeHtml(reasoning)}</p>
            </div>
        `;
    }

    generateNextStepsHtml(nextSteps) {
        return `
            <div class="alert alert-warning border-0 mt-3">
                <h6 class="alert-heading">
                    <i class="fas fa-tasks me-2"></i>
                    Next Steps
                </h6>
                <ul class="mb-0 small ps-3">
                    ${nextSteps.map(step => `<li>${Utils.sanitizeHtml(step)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    displayError(message) {
        if (!this.resultsContainer) return;

        this.resultsContainer.innerHTML = `
            <div class="alert alert-danger border-0">
                <h6 class="alert-heading">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error analysis
                </h6>
                <p class="mb-0">${Utils.sanitizeHtml(message)}</p>
            </div>
        `;
    }
}

// Example handler for demo and quick examples
class ExampleHandler {
    constructor() {
        this.init();
    }

    init() {
        // Handle example buttons on main page
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', this.handleExampleClick.bind(this));
        });

        // Handle demo cards
        document.querySelectorAll('.run-demo-btn').forEach(btn => {
            btn.addEventListener('click', this.handleDemoClick.bind(this));
        });

        // Handle quick demo buttons
        document.querySelectorAll('.quick-demo-btn').forEach(btn => {
            btn.addEventListener('click', this.handleQuickDemoClick.bind(this));
        });
    }

    handleExampleClick(event) {
        const example = event.target.dataset.example;
        const painPointField = document.getElementById('painPoint');
        
        if (painPointField && example) {
            painPointField.value = example;
            painPointField.focus();
            
            // Add highlight animation
            painPointField.classList.add('border-primary');
            setTimeout(() => {
                painPointField.classList.remove('border-primary');
            }, 1000);
        }
    }

    handleDemoClick(event) {
        const card = event.target.closest('.demo-card');
        if (card) {
            this.runDemo(card);
        }
    }

    handleQuickDemoClick(event) {
        const card = event.target.closest('.quick-example-card');
        if (card) {
            this.runDemo(card);
        }
    }

    async runDemo(card) {
        const data = {
            pain_point: card.dataset.painPoint,
            context: card.dataset.context || '',
            industry: card.dataset.industry || '',
            company_size: card.dataset.companySize || '',
            urgency: card.dataset.urgency || '',
            budget_range: card.dataset.budget || ''
        };

        const resultsContainer = document.getElementById('demoResults');
        if (!resultsContainer) return;

        try {
            // Show loading
            resultsContainer.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Đang analysis...</span>
                    </div>
                    <h5>AI Agent đang analysis...</h5>
                    <p class="text-muted">Đang tìm solution phù hợp từ knowledge base</p>
                </div>
            `;

            // Create form data
            const formData = new FormData();
            Object.keys(data).forEach(key => {
                if (data[key]) formData.append(key, data[key]);
            });

            // Analyze
            const result = await ApiService.analyzePainPoint(formData);
            
            // Display results
            this.displayDemoResults(result, data, resultsContainer);
            
            // Scroll to results
            Utils.scrollToElement(resultsContainer, 100);
            
        } catch (error) {
            console.error('Demo analysis error:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Error analysis</h6>
                    <p class="mb-0">Có error xảy ra khi analysis. Vui lòng thử lại.</p>
                </div>
            `;
        }
    }

    displayDemoResults(result, originalData, container) {
        // Implementation would be similar to the template version
        // but using JavaScript DOM manipulation
        const formHandler = new FormHandler(null, null);
        const resultsHtml = formHandler.generateResultsHtml(result);
        
        // Add original pain point info
        const originalHtml = `
            <div class="alert alert-light border-start border-primary border-3 mb-4">
                <h6 class="alert-heading">
                    <i class="fas fa-file-alt me-2"></i>
                    Pain Point được analysis
                </h6>
                <p class="mb-2"><strong>Mô tả:</strong> ${Utils.sanitizeHtml(originalData.pain_point)}</p>
                ${originalData.context ? `<p class="mb-2"><strong>Bối cảnh:</strong> ${Utils.sanitizeHtml(originalData.context)}</p>` : ''}
                <div class="row g-2 mt-2">
                    ${originalData.industry ? `<div class="col-auto"><span class="badge bg-primary">${originalData.industry}</span></div>` : ''}
                    ${originalData.company_size ? `<div class="col-auto"><span class="badge bg-info">${originalData.company_size}</span></div>` : ''}
                    ${originalData.urgency ? `<div class="col-auto"><span class="badge bg-warning">${originalData.urgency}</span></div>` : ''}
                </div>
            </div>
        `;
        
        container.innerHTML = originalHtml + resultsHtml;
        container.classList.add('fade-in');
    }
}

// App initialization
class App {
    constructor() {
        this.formHandler = null;
        this.exampleHandler = null;
        this.init();
    }

    async init() {
        // Check if DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', this.initializeApp.bind(this));
        } else {
            this.initializeApp();
        }
    }

    async initializeApp() {
        try {
            // Initialize components
            this.formHandler = new FormHandler('#painPointForm', '#resultsContainer');
            this.exampleHandler = new ExampleHandler();
            
            // Check API health
            const health = await ApiService.healthCheck();
            if (health.status !== 'healthy') {
                Utils.showToast('Warning: Dịch vụ backend có thể không hoạt động bình thường', 'warning');
            }
            
            console.log('Filum.ai Pain Point Agent initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize app:', error);
            Utils.showToast('Có error khi initialize ứng dụng', 'danger');
        }
    }
}

// Start the application
const app = new App();

// Export for global access
window.FilumAI = {
    app,
    Utils,
    ApiService,
    FormHandler,
    ExampleHandler
};
