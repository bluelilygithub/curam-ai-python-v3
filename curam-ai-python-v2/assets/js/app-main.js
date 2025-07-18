// =====================================================
// FILE: assets/js/app-main.js (ENHANCED VERSION)
// =====================================================
/**
 * Australian Property Intelligence - Main Application (Enhanced Modular)
 * 
 * @version 2.2.0
 * @author Property Intelligence Team
 */

class AustralianPropertyApp {
    constructor() {
        this.currentQuestion = '';
        this.presetQuestions = [];
        this.isInitialized = false;
        this.performanceMetrics = {};
        
        // Initialize modules
        this.activityLogger = new ActivityLogger();
        this.dataManager = new DataManager();
        this.uiManager = new UIManager();
        
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
            this.uiManager.showLoadingOverlay();
            
            // Initialize activity log
            this.activityLogger.initialize();
            this.activityLogger.log('🚀 Initializing Australian Property Intelligence...', 'info');
            
            // Initialize components
            await this.initializeComponents();
            
            // Load initial data
            await this.loadInitialData();
            
            // Setup event handlers
            this.setupEventHandlers();
            
            // Start background services
            this.startBackgroundServices();
            
            this.isInitialized = true;
            this.activityLogger.log('✅ Application initialized successfully', 'success');
            debugLog('✅ Application initialized successfully');
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.activityLogger.log(`❌ Initialization failed: ${error.message}`, 'error');
            this.uiManager.showError('Failed to initialize application. Please refresh the page.');
        } finally {
            // Hide loading overlay
            setTimeout(() => this.uiManager.hideLoadingOverlay(), 1000);
        }
    }
    
    /**
     * Initialize UI components
     */
    async initializeComponents() {
        this.activityLogger.log('🔧 Setting up UI components...', 'info');
        
        // Setup responsive handlers
        this.setupResponsiveHandlers();
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        this.activityLogger.log('✅ UI components initialized', 'success');
    }
    
    /**
     * Load initial application data
     */
    async loadInitialData() {
        const startTime = performance.now();
        this.activityLogger.log('📊 Loading application data...', 'info');
        
        try {
            // Load preset questions and check health in parallel
            const [questions, health] = await Promise.all([
                this.dataManager.loadPresetQuestions(),
                this.dataManager.checkSystemHealth()
            ]);
            
            this.presetQuestions = questions;
            this.uiManager.renderPresetQuestions(questions, (question) => {
                this.currentQuestion = question;
                this.activityLogger.log(`📝 Question selected: ${question.substring(0, 50)}...`, 'info');
            });
            
            this.uiManager.updateStatusDisplay(health);
            this.updateLastUpdated();
            
            const duration = performance.now() - startTime;
            performanceLog('Initial data load', duration);
            this.activityLogger.log(`✅ Data loaded in ${duration.toFixed(1)}ms`, 'success');
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.activityLogger.log(`❌ Data loading failed: ${error.message}`, 'error');
            throw error;
        }
    }
    
    /**
     * Analyze property question with enhanced detailed logging
     */
/**
 * Quick Fix: Add this RSS simulation to your analyzeQuestion() method
 * 
 * Replace the section in your app-main.js analyzeQuestion() method where you have:
 * 
 * this.activityLogger.log('📡 Connecting to Australian Property Intelligence API...', 'info');
 * 
 * With this enhanced RSS simulation:
 */

// In your analyzeQuestion() method, replace this section:
/**
 * Debug the API response issue in your app-main.js
 * 
 * The problem is likely in the analyzeQuestion() method where the actual API call happens.
 * Let's add comprehensive debugging and error handling.
 */

// Find this section in your app-main.js analyzeQuestion() method and replace it:

async analyzeQuestion() {
    const customInput = document.getElementById('customQuestion');
    const questionToAnalyze = customInput?.value.trim() || this.currentQuestion;
    
    if (!questionToAnalyze) {
        this.uiManager.showNotification('Please select a preset question or enter your own question.', 'warning');
        return;
    }
    
    try {
        // Initialize enhanced logging for analysis
        this.activityLogger.initialize();
        this.activityLogger.log('🔍 Starting Australian property analysis...', 'info');
        this.activityLogger.updateTimer('Processing');
        this.activityLogger.startTiming();
        
        // Add loading class to sidebar
        const sidebar = document.getElementById('activityLogSidebar');
        if (sidebar) sidebar.className = 'progress-sidebar loading';
        
        // Show loading state
        this.uiManager.setAnalyzeButtonState(true);
        this.uiManager.showAnalysisLoading();
        
        // Step 1: Log backend request processing
        this.activityLogger.log('📡 Connecting to Australian Property Intelligence API...', 'info');
        await this.delay(200);
        
        this.activityLogger.log(`📥 Backend received ${this.currentQuestion ? 'preset' : 'custom'} question (${questionToAnalyze.length} chars)`, 'api');
        
        debugLog('🔍 Starting analysis for:', questionToAnalyze);

        // Step 2: Enhanced RSS feed processing simulation
        this.activityLogger.log('🔧 Initializing Australian Property RSS Service...', 'info');
        await this.delay(300);
        
        const rssResults = await this.activityLogger.simulateDetailedFeedProcessing();
        
        // Step 3: Context preparation
        await this.delay(300);
        this.activityLogger.logContextPreparation(rssResults.relevantArticles, '12,847');
        
        // Step 4: Enhanced LLM Processing
        this.activityLogger.logLLMProcessing('starting', 'Claude', '3.5 Sonnet');
        await this.delay(200);
        
        this.activityLogger.log('📝 Preparing Claude prompt for Australian property analysis...', 'processing');
        await this.delay(150);
        
        this.activityLogger.log('📤 Sending request to Claude API...', 'api');
        
        // ===== THE ACTUAL API CALL - ADD DEBUGGING HERE =====
        console.log('🔍 DEBUG: About to make API call...');
        console.log('🔍 DEBUG: API Endpoint:', getApiEndpoint('analyze'));
        console.log('🔍 DEBUG: Question:', questionToAnalyze);
        
        const startTime = performance.now();
        const requestConfig = getApiConfig({
            method: 'POST',
            body: JSON.stringify({
                question: questionToAnalyze,
                include_details: false
            })
        });
        
        console.log('🔍 DEBUG: Request config:', requestConfig);
        
        // Add timeout to the fetch request
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            console.error('❌ DEBUG: API request timed out after 30 seconds');
            controller.abort();
        }, 30000); // 30 second timeout
        
        const response = await fetch(getApiEndpoint('analyze'), {
            ...requestConfig,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        console.log('🔍 DEBUG: Response received:', response);
        console.log('🔍 DEBUG: Response status:', response.status);
        console.log('🔍 DEBUG: Response ok:', response.ok);
        
        const apiResponseTime = (performance.now() - startTime).toFixed(0);
        
        if (!response.ok) {
            console.error('❌ DEBUG: Response not ok:', response.status, response.statusText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        this.activityLogger.logApiCall('/api/property/analyze', 'POST', apiResponseTime, true);
        this.activityLogger.log('⚙️ Processing Claude response...', 'processing');
        await this.delay(200);
        
        console.log('🔍 DEBUG: About to parse response as JSON...');
        
        // Parse the response with error handling
        let result;
        try {
            const responseText = await response.text();
            console.log('🔍 DEBUG: Raw response text:', responseText.substring(0, 500) + '...');
            result = JSON.parse(responseText);
            console.log('🔍 DEBUG: Parsed result:', result);
        } catch (parseError) {
            console.error('❌ DEBUG: Failed to parse JSON:', parseError);
            throw new Error('Invalid JSON response from server');
        }
        
        this.activityLogger.logQualityCheck('response_validation', true);
        this.activityLogger.logLLMProcessing('complete', 'Claude', '3.5 Sonnet');
        
        // Step 5: Gemini Processing
        await this.delay(300);
        this.activityLogger.logLLMProcessing('starting', 'Google Gemini', '1.5 Flash');
        this.activityLogger.log('📝 Preparing Gemini prompt for comprehensive analysis...', 'processing');
        this.activityLogger.log('📈 Synthesizing comprehensive property insights...', 'processing');
        
        await this.delay(400);
        this.activityLogger.log('⚙️ Gemini processing response...', 'processing');
        this.activityLogger.logQualityCheck('content_quality', true);
        this.activityLogger.log('🎨 Formatting analysis for display...', 'processing');
        
        const duration = this.activityLogger.getElapsedTime();
        
        console.log('🔍 DEBUG: Processing complete, result:', result);
        console.log('🔍 DEBUG: Result success:', result.success);
        
        if (result.success) {
            console.log('🔍 DEBUG: Analysis successful, displaying result...');
            
            this.activityLogger.logLLMProcessing('complete', 'Google Gemini', '1.5 Flash');
            this.activityLogger.log(`🎉 Analysis completed successfully in ${duration.toFixed(1)}ms`, 'success');
            
            // Update sidebar to completed state
            if (sidebar) sidebar.className = 'progress-sidebar completed';
            
            console.log('🔍 DEBUG: About to call displayAnalysisResult...');
            this.uiManager.displayAnalysisResult(result);
            console.log('🔍 DEBUG: displayAnalysisResult called');
            
            this.activityLogger.updateTimer('Completed');
            this.uiManager.showNotification('Analysis completed successfully!', 'success');
        } else {
            console.error('❌ DEBUG: Analysis failed - result.success is false');
            console.error('❌ DEBUG: Error in result:', result.error);
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('❌ DEBUG: Caught error in analyzeQuestion:', error);
        console.error('❌ DEBUG: Error stack:', error.stack);
        
        this.activityLogger.log(`❌ Analysis failed: ${error.message}`, 'error');
        this.activityLogger.updateTimer('Error');
        
        // Update sidebar to error state
        const sidebar = document.getElementById('activityLogSidebar');
        if (sidebar) sidebar.className = 'progress-sidebar error';
        
        this.uiManager.showError(getUserFriendlyError(error));
    } finally {
        console.log('🔍 DEBUG: Finally block - cleaning up...');
        this.uiManager.setAnalyzeButtonState(false);
    }
}

/**
 * Alternative Quick Fix: Add this method directly to your app-main.js
 * if the enhanced activity-logger.js simulateDetailedFeedProcessing method isn't working
 */

// Add this method to your AustralianPropertyApp class:
async simulateRSSFeeds() {
    const feeds = [
        { name: 'RealEstate.com.au', articles: 25, responseTime: 450 },
        { name: 'Smart Property Investment', articles: 12, responseTime: 320 },
        { name: 'View.com.au Property News', articles: 18, responseTime: 380 },
        { name: 'First National Real Estate', articles: 8, responseTime: 290 },
        { name: 'PropertyMe Blog', articles: 6, responseTime: 250 },
        { name: 'Real Estate Talk', articles: 15, responseTime: 410 }
    ];

    this.activityLogger.log(`🔧 Initializing RSS service for ${feeds.length} Australian property feeds...`, 'info');
    this.activityLogger.updateTimer('Fetching Feeds');

    let totalArticles = 0;

    for (const feed of feeds) {
        // Log feed connection
        this.activityLogger.log(`📰 Connecting to ${feed.name}...`, 'feed', {
            source: feed.name,
            articleCount: feed.articles,
            responseTime: feed.responseTime
        });
        
        // Simulate network delay
        await this.delay(Math.random() * 400 + 200);
        
        // Log successful retrieval
        this.activityLogger.log(`✓ ${feed.name} - ${feed.articles} articles retrieved`, 'success', {
            source: feed.name,
            articleCount: feed.articles,
            responseTime: feed.responseTime
        });
        
        totalArticles += feed.articles;

        // Simulate processing key articles for major feeds
        if (feed.articles > 10) {
            await this.delay(150);
            if (feed.name === 'RealEstate.com.au') {
                this.activityLogger.log(`📄 Processing: "Pet tax: Why having a pet could be costing renters $14k a year"`, 'article', {
                    title: "Pet tax: Why having a pet could be costing renters $14k a year",
                    publishDate: "2 hours ago",
                    source: feed.name
                });
            } else if (feed.name === 'Smart Property Investment') {
                this.activityLogger.log(`📄 Processing: "Regional property markets outperforming capital cities"`, 'article', {
                    title: "Regional property markets outperforming capital cities",
                    publishDate: "4 hours ago",
                    source: feed.name
                });
            }
        }
    }

    // Log summary
    const duration = this.activityLogger.getElapsedTime() / 1000;
    this.activityLogger.log(`📊 RSS Summary: ${feeds.length} feeds, ${totalArticles} articles in ${duration.toFixed(1)}s`, 'data');
    
    // Log filtering
    const relevantArticles = Math.floor(totalArticles * 0.7);
    this.activityLogger.log(`🔍 Filtered ${totalArticles} articles → ${relevantArticles} relevant`, 'data');

    return { feedsProcessed: feeds.length, totalArticles, relevantArticles };
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
        this.activityLogger.log('🔄 Starting background services...', 'info');
        
        // Auto-refresh health check
        if (isFeatureEnabled('autoRefresh')) {
            setInterval(async () => {
                const health = await this.dataManager.checkSystemHealth();
                this.uiManager.updateStatusDisplay(health);
                this.updateLastUpdated();
            }, APP_CONFIG.ui.healthCheckInterval);
            
            debugLog('🔄 Auto-refresh service started');
        }
        
        // Cache cleanup
        setInterval(() => {
            this.dataManager.cleanupCache();
        }, APP_CONFIG.performance.cacheExpiry);
        
        this.activityLogger.updateTimer('Ready');
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
                if (buttons[index] && this.presetQuestions[index]) {
                    const question = this.presetQuestions[index];
                    this.uiManager.selectQuestion(question, buttons[index], (q) => {
                        this.currentQuestion = q;
                        this.activityLogger.log(`📝 Question selected: ${q.substring(0, 50)}...`, 'info');
                    });
                }
            }
        });
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
                        <button onclick="app.dataManager.checkSystemHealth().then(h => app.uiManager.updateStatusDisplay(h))" class="test-btn">🔍 Test Connection</button>
                        <button onclick="location.reload()" class="refresh-btn">🔄 Refresh Page</button>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Helper delay function for simulations
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Get application statistics
     */
    getStats() {
        return {
            isInitialized: this.isInitialized,
            currentQuestion: this.currentQuestion,
            presetQuestionsCount: this.presetQuestions.length,
            cacheSize: this.dataManager.cache.size,
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