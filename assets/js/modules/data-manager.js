// =====================================================
// FILE: assets/js/modules/data-manager.js
// =====================================================
/**
 * Data Manager Module
 * Handles API calls, caching, and data loading
 */
class DataManager {
    constructor() {
        this.cache = new Map();
        this.healthCheckFailed = false;
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
                return cached.data;
            }
        }
        
        try {
            debugLog('📋 Loading preset questions from API...');
            const response = await fetch(getApiEndpoint('questions'), getApiConfig());
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Cache the results
                this.cache.set(cacheKey, {
                    data: data.preset_questions,
                    timestamp: Date.now()
                });
                
                return data.preset_questions;
            }
            
        } catch (error) {
            console.error('❌ Failed to load preset questions:', error);
            
            // Return fallback questions
            return [
                "What new development applications were submitted in Australian this month?",
                "Which Australian suburbs are trending in property news?", 
                "Are there any major infrastructure projects affecting property values?",
                "What zoning changes have been approved recently?",
                "Which areas have the most development activity?"
            ];
        }
    }

    /**
     * Check system health
     */
    async checkSystemHealth() {
        try {
            debugLog('💓 Checking system health...');
            const response = await fetch(getApiEndpoint('health'), getApiConfig());
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const health = await response.json();
            this.healthCheckFailed = false;
            return health;
            
        } catch (error) {
            console.error('❌ Health check failed:', error);
            this.healthCheckFailed = true;
            return { status: 'error', error: error.message };
        }
    }

    /**
     * Analyze property question
     */
    async analyzeProperty(question) {
        try {
            const requestConfig = getApiConfig({
                method: 'POST',
                body: JSON.stringify({
                    question: question,
                    include_details: false
                })
            });
            
            const response = await fetch(getApiEndpoint('analyze'), requestConfig);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('❌ Analysis failed:', error);
            throw error;
        }
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
    }
}
