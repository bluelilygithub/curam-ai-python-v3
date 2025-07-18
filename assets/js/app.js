/**
 * Australian Property Intelligence - Main Application
 * 
 * Professional frontend application for Australian property analysis
 * using AI-powered multi-LLM backend services.
 * 
 * @version 2.0.0
 * @author Property Intelligence Team
 */

class AustralianPropertyApp {
    constructor() {
        this.currentQuestion = '';
        this.presetQuestions = [];
        this.isInitialized = false;
        this.cache = new Map();
        this.performanceMetrics = {};
        
        // Initialize application
        this.init();
    }
    
    /**
     * Initialize the application
     */
    async init() {
        debugLog('🚀 Australian Property Intelligence starting...');
        debugLog('🌐 Environment:', APP_CONFIG.environment.current);
        debugLog('🌐 API Base URL:', getApiBaseUrl());
        
        try {
            // Show loading overlay
            this.showLoadingOverlay();
            
            // Initialize components
            await this.initializeComponents();
            
            // Load initial data
            await this.loadInitialData();
            
            // Setup event handlers
            this.setupEventHandlers();
            
            // Start background services
            this.startBackgroundServices();
            
            this.isInitialized = true;
            debugLog('✅ Application initialized successfully');
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.showError('Failed to initialize application. Please refresh the page.');
        } finally {
            // Hide loading overlay
            setTimeout(() => this.hideLoadingOverlay(), 1000);
        }
    }
    
    /**
     * Initialize UI components
     */
    async initializeComponents() {
        // Setup notification system
        this.setupNotifications();
        
        // Initialize responsive handlers
        this.setupResponsiveHandlers();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
    }
    
    /**
     * Load initial application data
     */
    async loadInitialData() {
        const startTime = performance.now();
        
        try {
            // Load preset questions and check health in parallel
            await Promise.all([
                this.loadPresetQuestions(),
                this.checkSystemHealth()
            ]);
            
            const duration = performance.now() - startTime;
            performanceLog('Initial data load', duration);
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            throw error;
        }
    }
    
    /**
     * Load preset questions from API
     */
    async loadPresetQuestions() {
        const cacheKey = 'preset_questions';
        
        // Check cache first
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < APP_CONFIG.performance.cacheExpiry) {
                this.presetQuestions = cached.data;
                this.renderPresetQuestions();
                debugLog('📋 Using cached preset questions');
                return;
            }
        }
        
        try {
            debugLog('📋 Loading preset questions from API...');
            const startTime = performance.now();
            
            const response = await fetch(getApiEndpoint('questions'), getApiConfig());
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            const duration = performance.now() - startTime;
            
            performanceLog('Load preset questions', duration);
            debugLog('✅ Questions loaded:', data);
            
            if (data.success) {
                this.presetQuestions = data.preset_questions;
                this.renderPresetQuestions();
                
                // Cache the results
                this.cache.set(cacheKey, {
                    data: data.preset_questions,
                    timestamp: Date.now()
                });
            }
            
        } catch (error) {
            console.error('❌ Failed to load preset questions:', error);
            
            // Show user-friendly error
            this.showNotification(
                getUserFriendlyError(error),
                'warning'
            );
            
            // Use fallback questions
            this.presetQuestions = [
                "What new development applications were submitted in Australian this month?",
                "Which Australian suburbs are trending in property news?", 
                "Are there any major infrastructure projects affecting property values?",
                "What zoning changes have been approved recently?",
                "Which areas have the most development activity?"
            ];
            this.renderPresetQuestions();
        }
    }
    
    /**
     * Render preset questions as interactive buttons
     */
    renderPresetQuestions() {
        const container = document.getElementById('presetQuestions');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.presetQuestions.forEach((question, index) => {
            const button = document.createElement('button');
            button.className = 'question-btn';
            button.textContent = question;
            button.setAttribute('data-question', question);
            button.setAttribute('data-index', index);
            
            // Add click handler
            button.addEventListener('click', (e) => {
                this.selectQuestion(question, button);
            });
            
            // Add keyboard accessibility
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectQuestion(question, button);
                }
            });
            
            container.appendChild(button);
        });
        
        debugLog(`📋 Rendered ${this.presetQuestions.length} preset questions`);
    }
    
    /**
     * Select a preset question
     */
    selectQuestion(question, buttonElement) {
        // Clear previous selection
        document.querySelectorAll('.question-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Mark current selection
        buttonElement.classList.add('active');
        this.currentQuestion = question;
        
        // Clear custom input
        const customInput = document.getElementById('customQuestion');
        if (customInput) {
            customInput.value = '';
        }
        
        // Show selection feedback
        this.showNotification(`Selected: ${question.substring(0, 50)}...`, 'info', 2000);
        
        debugLog('📝 Question selected:', question);
    }
    
    /**
     * Check system health
     */
    async checkSystemHealth() {
        try {
            debugLog('💓 Checking system health...');
            const startTime = performance.now();
            
            const response = await fetch(getApiEndpoint('health'), getApiConfig());
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const health = await response.json();
            const duration = performance.now() - startTime;
            
            performanceLog('Health check', duration);
            debugLog('✅ Health check successful:', health);
            
            this.updateStatusDisplay(health);
            this.updateLastUpdated();
            
        } catch (error) {
            console.error('❌ Health check failed:', error);
            this.updateStatusDisplay({ status: 'error' });
            
            // Only show error notification on first failure
            if (!this.healthCheckFailed) {
                this.showNotification('Unable to connect to API services', 'warning');
                this.healthCheckFailed = true;
            }
        }
    }
    
    /**
     * Update status display based on health data
     */
    updateStatusDisplay(health) {
        const aiStatus = document.getElementById('aiStatus');
        const aiStatusText = document.getElementById('aiStatusText');
        
        if (!aiStatus || !aiStatusText) return;
        
        if (health.status === 'healthy') {
            aiStatus.className = 'status-indicator status-healthy';
            aiStatusText.textContent = 'AI Services Online';
            this.healthCheckFailed = false;
        } else if (health.status === 'degraded') {
            aiStatus.className = 'status-indicator status-warning';
            aiStatusText.textContent = 'AI Services Limited';
        } else {
            aiStatus.className = 'status-indicator status-error';
            aiStatusText.textContent = 'AI Services Offline';
        }
    }
    
    /**
     * Update last updated timestamp
     */
    updateLastUpdated() {
        const element = document.getElementById('lastUpdated');
        if (element) {
            element.textContent = `Last Updated: ${new Date().toLocaleTimeString()}`;
        }
    }
    
    /**
     * Analyze property question
     */
    async analyzeQuestion() {
        const customInput = document.getElementById('customQuestion');
        const questionToAnalyze = customInput?.value.trim() || this.currentQuestion;
        
        if (!questionToAnalyze) {
            this.showNotification('Please select a preset question or enter your own question.', 'warning');
            return;
        }
        
        const analyzeBtn = document.getElementById('analyzeBtn');
        const resultsContent = document.getElementById('resultsContent');
        
        if (!analyzeBtn || !resultsContent) return;
        
        try {
            // Show loading state
            this.setAnalyzeButtonState(true);
            this.showAnalysisLoading();
            
            debugLog('🔍 Starting analysis for:', questionToAnalyze);
            const startTime = performance.now();
            
            const requestConfig = getApiConfig({
                method: 'POST',
                body: JSON.stringify({
                    question: questionToAnalyze,
                    include_details: false
                })
            });
            
            const response = await fetch(getApiEndpoint('analyze'), requestConfig);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            const duration = performance.now() - startTime;
            
            performanceLog('Property analysis', duration);
            debugLog('✅ Analysis completed:', result);
            
            if (result.success) {
                this.displayAnalysisResult(result);
                this.showNotification('Analysis completed successfully!', 'success');
            } else {
                throw new Error(result.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('❌ Analysis failed:', error);
            this.showError(getUserFriendlyError(error));
        } finally {
            this.setAnalyzeButtonState(false);
        }
    }
    
    /**
     * Set analyze button state (loading/normal)
     */
    setAnalyzeButtonState(isLoading) {
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (!analyzeBtn) return;
        
        analyzeBtn.disabled = isLoading;
        analyzeBtn.textContent = isLoading ? '🔄 Analyzing...' : '🔍 Analyze Property Question';
    }
    
    /**
     * Show analysis loading state
     */
    showAnalysisLoading() {
        const resultsContent = document.getElementById('resultsContent');
        if (!resultsContent) return;
        
        resultsContent.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <div class="loading-text">
                    <h4>Analyzing Your Australian Property Question</h4>
                    <p>Our AI is processing your request using Australian-specific data...</p>
                </div>
            </div>
        `;
    }
    
    /**
     * Display analysis results
     */
    displayAnalysisResult(result) {
        const resultsContent = document.getElementById('resultsContent');
        if (!resultsContent) return;
        
        // Convert markdown-style content to HTML
        const htmlContent = this.convertMarkdownToHTML(result.answer);
        
        resultsContent.innerHTML = `
            <div class="success-message">
                ✅ Analysis completed successfully for: "${result.question}"
            </div>
            <div class="analysis-result">
                ${htmlContent}
            </div>
        `;
        
        // Scroll to top of results
        resultsContent.scrollTop = 0;
        
        // Add smooth reveal animation if enabled
        if (isFeatureEnabled('animatedResults')) {
            resultsContent.style.opacity = '0';
            setTimeout(() => {
                resultsContent.style.transition = 'opacity 0.5s ease';
                resultsContent.style.opacity = '1';
            }, 100);
        }
    }
    
    /**
     * Convert markdown-style content to HTML
     */
    convertMarkdownToHTML(markdown) {
        return markdown
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^\*\*(.*?)\*\*/gm, '<strong>$1</strong>')
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^(?!<[h|u|l])(.+)$/gm, '<p>$1</p>')
            .replace(/<p><\/p>/g, '')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
    
    /**
     * Show error message
     */
    showError(message) {
        const resultsContent = document.getElementById('resultsContent');
        if (!resultsContent) return;
        
        resultsContent.innerHTML = `
            <div class="error-message">
                <div class="error-header">
                    <strong>❌ Analysis Failed</strong>
                </div>
                <div class="error-content">
                    <p>${message}</p>
                    <div class="error-actions">
                        <button onclick="app.retryLastRequest()" class="retry-btn">🔄 Try Again</button>
                        <button onclick="app.showConnectionHelp()" class="help-btn">🔧 Connection Help</button>
                    </div>
                </div>
            </div>
        `;
        
        this.showNotification(message, 'error');
    }
    
    /**
     * Setup event handlers
     */
    setupEventHandlers() {
        // Analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeQuestion());
        }
        
        // Custom question input - Enter key handler
        const customInput = document.getElementById('customQuestion');
        if (customInput) {
            customInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    this.analyzeQuestion();
                }
            });
            
            // Clear selection when typing
            customInput.addEventListener('input', () => {
                document.querySelectorAll('.question-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                this.currentQuestion = '';
            });
        }
        
        debugLog('🎮 Event handlers setup complete');
    }
    
    /**
     * Setup background services
     */
    startBackgroundServices() {
        // Auto-refresh health check
        if (isFeatureEnabled('autoRefresh')) {
            setInterval(() => {
                this.checkSystemHealth();
            }, APP_CONFIG.ui.healthCheckInterval);
            
            debugLog('🔄 Auto-refresh service started');
        }
        
        // Cache cleanup
        setInterval(() => {
            this.cleanupCache();
        }, APP_CONFIG.performance.cacheExpiry);
    }
    
    /**
     * Cleanup expired cache entries
     */
    cleanupCache() {
        const now = Date.now();
        const expiry = APP_CONFIG.performance.cacheExpiry;
        
        for (const [key, value] of this.cache.entries()) {
            if (now - value.timestamp > expiry) {
                this.cache.delete(key);
            }
        }
        
        // Limit cache size
        if (this.cache.size > APP_CONFIG.performance.maxCacheSize) {
            const entries = Array.from(this.cache.entries());
            entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
            
            // Remove oldest entries
            const toRemove = this.cache.size - APP_CONFIG.performance.maxCacheSize;
            for (let i = 0; i < toRemove; i++) {
                this.cache.delete(entries[i][0]);
            }
        }
        
        debugLog('🧹 Cache cleanup completed');
    }
    
    /**
     * Setup notification system
     */
    setupNotifications() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notificationContainer')) {
            const container = document.createElement('div');
            container.id = 'notificationContainer';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info', duration = 5000) {
        if (!isFeatureEnabled('notifications')) return;
        
        const container = document.getElementById('notificationContainer');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${icon}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
        
        // Limit number of notifications
        const notifications = container.querySelectorAll('.notification');
        if (notifications.length > 5) {
            notifications[0].remove();
        }
    }
    
    /**
     * Get notification icon based on type
     */
    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }
    
    /**
     * Setup responsive handlers
     */
    setupResponsiveHandlers() {
        const handleResize = () => {
            const width = window.innerWidth;
            const isMobile = width <= APP_CONFIG.ui.breakpoints.mobile;
            const isTablet = width <= APP_CONFIG.ui.breakpoints.tablet;
            
            document.body.classList.toggle('mobile', isMobile);
            document.body.classList.toggle('tablet', isTablet);
            document.body.classList.toggle('desktop', !isTablet);
        };
        
        window.addEventListener('resize', handleResize);
        handleResize(); // Initial call
    }
    
    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Enter / Cmd+Enter to analyze
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.analyzeQuestion();
            }
            
            // Escape to clear selection
            if (e.key === 'Escape') {
                document.querySelectorAll('.question-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                this.currentQuestion = '';
                
                const customInput = document.getElementById('customQuestion');
                if (customInput) customInput.value = '';
            }
            
            // Number keys 1-5 to select preset questions
            if (e.key >= '1' && e.key <= '5' && !e.ctrlKey && !e.metaKey) {
                const index = parseInt(e.key) - 1;
                const buttons = document.querySelectorAll('.question-btn');
                if (buttons[index]) {
                    const question = this.presetQuestions[index];
                    this.selectQuestion(question, buttons[index]);
                }
            }
        });
    }
    
    /**
     * Show loading overlay
     */
    showLoadingOverlay() {
        if (!isFeatureEnabled('loadingOverlay')) return;
        
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }
    
    /**
     * Hide loading overlay
     */
    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.style.display = 'none';
                overlay.style.opacity = '1';
            }, 300);
        }
    }
    
    /**
     * Retry last request
     */
    retryLastRequest() {
        this.analyzeQuestion();
    }
    
    /**
     * Show connection help
     */
    showConnectionHelp() {
        const resultsContent = document.getElementById('resultsContent');
        if (!resultsContent) return;
        
        resultsContent.innerHTML = `
            <div class="help-message">
                <div class="help-header">
                    <strong>🔧 Connection Troubleshooting</strong>
                </div>
                <div class="help-content">
                    <h4>Current Setup:</h4>
                    <p><strong>Frontend:</strong> ${window.location.href}</p>
                    <p><strong>API:</strong> ${getApiBaseUrl()}</p>
                    
                    <h4>Possible Issues:</h4>
                    <ul>
                        <li>API server may be temporarily unavailable</li>
                        <li>Network connectivity issues</li>
                        <li>CORS configuration problems</li>
                        <li>API URL misconfiguration</li>
                    </ul>
                    
                    <h4>Next Steps:</h4>
                    <ol>
                        <li>Check your internet connection</li>
                        <li>Test API directly: <a href="${getApiBaseUrl()}/health" target="_blank">Health Check</a></li>
                        <li>Try refreshing the page</li>
                        <li>Contact support if problem persists</li>
                    </ol>
                    
                    <div class="help-actions">
                        <button onclick="app.checkSystemHealth()" class="test-btn">🔍 Test Connection</button>
                        <button onclick="location.reload()" class="refresh-btn">🔄 Refresh Page</button>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Get application statistics
     */
    getStats() {
        return {
            isInitialized: this.isInitialized,
            currentQuestion: this.currentQuestion,
            presetQuestionsCount: this.presetQuestions.length,
            cacheSize: this.cache.size,
            environment: APP_CONFIG.environment.current,
            apiUrl: getApiBaseUrl(),
            performanceMetrics: this.performanceMetrics
        };
    }
}




// Initialize application when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new AustralianPropertyApp();
});

// Export for global access
window.AustralianPropertyApp = AustralianPropertyApp;