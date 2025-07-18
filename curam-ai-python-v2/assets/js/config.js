/**
 * Australian Property Intelligence - Frontend Configuration
 * 
 * Environment-specific configuration for the frontend application.
 * Update these settings based on your deployment environment.
 * 
 * @version 2.0.0
 * @author Property Intelligence Team
 */

const APP_CONFIG = {
    // API Configuration
    api: {
        // Production API URL (Railway deployment)
        // TODO: Update this with your actual Railway URL
        baseUrl: 'https://curam-ai-python-v2-production.up.railway.app',
        
        // Request configuration
        timeout: 30000, // 30 seconds
        retries: 3,
        
        // Headers for all API requests
        defaultHeaders: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        
        // CORS configuration
        mode: 'cors',
        credentials: 'omit',
        
        // API endpoints
        endpoints: {
            health: '/health',
            healthDeep: '/health/deep',
            questions: '/api/property/questions',
            analyze: '/api/property/analyze',
            history: '/api/property/history',
            stats: '/api/property/stats',
            reset: '/api/property/reset'
        }
    },
    
    // UI Configuration
    ui: {
        // Auto-refresh intervals (milliseconds)
        healthCheckInterval: 30000, // 30 seconds
        
        // Animation delays
        typingDelay: 50,
        fadeDelay: 300,
        loadingMinDelay: 1000, // Minimum loading time for UX
        
        // Pagination
        defaultHistoryLimit: 50,
        maxResultsDisplay: 100,
        
        // Themes
        theme: 'professional', // 'professional', 'modern', 'minimal'
        
        // Features flags
        features: {
            autoRefresh: true,
            exportFunctionality: false, // Future feature
            darkMode: false, // Future feature
            notifications: true,
            loadingOverlay: true,
            animatedResults: true,
            soundEffects: false
        },
        
        // Responsive breakpoints
        breakpoints: {
            mobile: 768,
            tablet: 1024,
            desktop: 1200
        }
    },
    
    // Application Information
    app: {
        name: 'Australian Property Intelligence',
        version: '2.0.0',
        description: 'AI-Powered Property Market Analysis for Queensland',
        author: 'Property Intelligence Team',
        buildDate: new Date().toISOString(),
        
        // Support information
        support: {
            email: 'support@curam-ai.com.au',
            website: 'https://curam-ai.com.au',
            documentation: 'https://curam-ai.com.au/docs',
            github: null // Add if open source
        },
        
        // Social links
        social: {
            twitter: null,
            linkedin: null,
            facebook: null
        }
    },
    
    // Environment detection and settings
    environment: {
        // Auto-detect environment
        current: detectEnvironment(),
        
        // Environment-specific settings
        development: {
            apiUrl: 'http://localhost:5000',
            debug: true,
            mockData: false,
            showConsoleInfo: true,
            enablePerformanceMonitoring: false
        },
        
        staging: {
            apiUrl: 'https://staging-Australian-property.up.railway.app',
            debug: true,
            mockData: false,
            showConsoleInfo: true,
            enablePerformanceMonitoring: true
        },
        
        production: {
            // UPDATE THIS LINE (around line 118):
            apiUrl: 'https://curam-ai-python-v2-production.up.railway.app',
            debug: false,
            mockData: false,
            showConsoleInfo: false,
            enablePerformanceMonitoring: true
        }
    },
    
    // Performance monitoring
    performance: {
        enableTiming: true,
        enableMemoryTracking: false,
        logSlowRequests: true,
        slowRequestThreshold: 5000, // 5 seconds
        
        // Request caching
        enableCache: true,
        cacheExpiry: 300000, // 5 minutes
        maxCacheSize: 50
    },
    
    // Analytics & Monitoring (for future use)
    analytics: {
        enabled: false,
        provider: 'none', // 'google', 'mixpanel', 'amplitude'
        trackingId: '',
        
        events: {
            pageView: true,
            apiCalls: true,
            errors: true,
            userInteractions: true,
            performanceMetrics: false
        }
    },
    
    // Error handling
    errors: {
        showUserFriendlyMessages: true,
        logToConsole: true,
        enableErrorReporting: false,
        retryFailedRequests: true,
        maxRetries: 3,
        retryDelay: 1000, // 1 second
        fallbackToMockData: false,
        
        // User-friendly error messages
        messages: {
            networkError: 'Unable to connect to Australian Property Intelligence. Please check your internet connection.',
            serverError: 'Our servers are experiencing issues. Please try again in a moment.',
            timeoutError: 'The request took too long. Please try again.',
            parseError: 'Unable to process the response. Please try again.',
            genericError: 'Something went wrong. Please try again.'
        }
    },
    
    // Australian-specific configuration
    Australian: {
        timezone: 'Australia/Australian',
        currency: 'AUD',
        locale: 'en-AU',
        
        // Default areas of interest
        defaultSuburbs: [
            'South Australian',
            'Fortitude Valley', 
            'New Farm',
            'Paddington',
            'Teneriffe',
            'West End',
            'Woolloongabba'
        ],
        
        // Property types
        propertyTypes: [
            'Apartment',
            'House',
            'Townhouse',
            'Unit',
            'Land',
            'Commercial'
        ]
    }
};

/**
 * Detect current environment based on URL and other factors
 */
function detectEnvironment() {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // Development environment
    if (hostname === 'localhost' || 
        hostname === '127.0.0.1' || 
        hostname.startsWith('192.168.') ||
        hostname.startsWith('10.') ||
        protocol === 'file:') {
        return 'development';
    }
    
    // Staging environment
    if (hostname.includes('staging') || 
        hostname.includes('test') || 
        hostname.includes('dev.') ||
        hostname.includes('preview')) {
        return 'staging';
    }
    
    // Production environment
    return 'production';
}

/**
 * Get API base URL based on current environment
 */
function getApiBaseUrl() {
    return 'https://curam-ai-python-v2-production.up.railway.app';
}

/**
 * Get full API endpoint URL
 */
function getApiEndpoint(endpoint) {
    const baseUrl = getApiBaseUrl();
    const endpointPath = APP_CONFIG.api.endpoints[endpoint];
    
    if (!endpointPath) {
        throw new Error(`Unknown API endpoint: ${endpoint}`);
    }
    
    return `${baseUrl}${endpointPath}`;
}

/**
 * Get API request configuration with defaults
 */
function getApiConfig(options = {}) {
    const config = {
        mode: APP_CONFIG.api.mode,
        credentials: APP_CONFIG.api.credentials,
        headers: {
            ...APP_CONFIG.api.defaultHeaders,
            ...options.headers
        },
        ...options
    };
    
    // Add timeout if supported
    if ('signal' in options && options.signal === undefined) {
        const controller = new AbortController();
        setTimeout(() => controller.abort(), APP_CONFIG.api.timeout);
        config.signal = controller.signal;
    }
    
    return config;
}

/**
 * Check if debug mode is enabled
 */
function isDebugMode() {
    const env = APP_CONFIG.environment.current;
    return APP_CONFIG.environment[env]?.debug || false;
}

/**
 * Check if feature is enabled
 */
function isFeatureEnabled(feature) {
    return APP_CONFIG.ui.features[feature] || false;
}

/**
 * Log debug information (only in debug mode)
 */
function debugLog(...args) {
    if (isDebugMode()) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] [Australian Property Intelligence]`, ...args);
    }
}

/**
 * Log performance information
 */
function performanceLog(operation, duration) {
    if (APP_CONFIG.performance.enableTiming) {
        const message = `${operation} completed in ${duration}ms`;
        
        if (duration > APP_CONFIG.performance.slowRequestThreshold) {
            console.warn(`[SLOW] ${message}`);
        } else if (isDebugMode()) {
            console.log(`[PERF] ${message}`);
        }
    }
}

/**
 * Get user-friendly error message
 */
function getUserFriendlyError(error) {
    if (!APP_CONFIG.errors.showUserFriendlyMessages) {
        return error.message;
    }
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        return APP_CONFIG.errors.messages.networkError;
    }
    
    if (error.name === 'AbortError') {
        return APP_CONFIG.errors.messages.timeoutError;
    }
    
    if (error.message.includes('500') || error.message.includes('502') || error.message.includes('503')) {
        return APP_CONFIG.errors.messages.serverError;
    }
    
    if (error.message.includes('JSON')) {
        return APP_CONFIG.errors.messages.parseError;
    }
    
    return APP_CONFIG.errors.messages.genericError;
}

// Export configuration for use in main application
window.APP_CONFIG = APP_CONFIG;
window.getApiBaseUrl = getApiBaseUrl;
window.getApiEndpoint = getApiEndpoint;
window.getApiConfig = getApiConfig;
window.isDebugMode = isDebugMode;
window.isFeatureEnabled = isFeatureEnabled;
window.debugLog = debugLog;
window.performanceLog = performanceLog;
window.getUserFriendlyError = getUserFriendlyError;

// Initialize configuration logging
document.addEventListener('DOMContentLoaded', function() {
    debugLog('Configuration loaded:', {
        environment: APP_CONFIG.environment.current,
        apiUrl: getApiBaseUrl(),
        debug: isDebugMode(),
        version: APP_CONFIG.app.version,
        features: Object.keys(APP_CONFIG.ui.features).filter(f => isFeatureEnabled(f))
    });
    
    // Validate critical configuration
    if (!getApiBaseUrl() || getApiBaseUrl().includes('your-railway-app')) {
        console.warn('⚠️ WARNING: API URL not configured properly. Please update config.js');
    }
});