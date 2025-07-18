// =====================================================
// FILE: assets/js/modules/activity-logger.js (COMPLETE OPTIMIZED VERSION)
// =====================================================
/**
 * Enhanced Activity Logger Module - OPTIMIZED
 * Handles detailed real-time activity logging with RSS feed processing details
 * Optimized for faster performance while maintaining user engagement
 */
class ActivityLogger {
    constructor() {
        this.startTime = null;
        this.processingStage = 'ready';
        this.feedCount = 0;
        this.articleCount = 0;
    }

    /**
     * Initialize the activity log
     */
    initialize() {
        const logContainer = document.getElementById('activityLog');
        if (logContainer) {
            logContainer.innerHTML = '';
            this.startTime = Date.now();
            this.processingStage = 'starting';
            this.feedCount = 0;
            this.articleCount = 0;
        }
        this.updateTimer('Initializing');
    }

    /**
     * Enhanced logging with feed-specific details
     * @param {string} message - Log message
     * @param {string} type - Log type: 'info', 'success', 'warning', 'error', 'feed', 'article', 'api', 'processing', 'data'
     * @param {Object} metadata - Additional metadata for specialized logging
     */
    log(message, type = 'info', metadata = {}) {
        const logContainer = document.getElementById('activityLog');
        if (!logContainer) return;

        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        
        // Enhanced styling for different log types
        const icon = this.getLogIcon(type);
        const timestamp = new Date().toLocaleTimeString();
        const elapsed = this.startTime ? ((Date.now() - this.startTime) / 1000).toFixed(1) : '0.0';
        
        logEntry.innerHTML = `
            <div class="log-content">
                <span class="log-icon">${icon}</span>
                <span class="log-message">${message}</span>
                <span class="log-meta">
                    <span class="log-time">${timestamp}</span>
                    <span class="log-elapsed">+${elapsed}s</span>
                </span>
            </div>
        `;

        // Add metadata display for feed/article logs
        if (metadata && Object.keys(metadata).length > 0 && (type === 'feed' || type === 'article')) {
            const metaDiv = document.createElement('div');
            metaDiv.className = 'log-metadata';
            metaDiv.innerHTML = this.formatMetadata(metadata, type);
            logEntry.appendChild(metaDiv);
        }

        // Add fade-in animation
        logEntry.style.opacity = '0';
        logContainer.appendChild(logEntry);
        
        // Trigger animation
        setTimeout(() => {
            logEntry.style.opacity = '1';
            logEntry.style.transition = 'opacity 0.3s ease';
        }, 10);
        
        // No entry limit - let sidebar grow dynamically
    }

    /**
     * Get appropriate icon for log type
     */
    getLogIcon(type) {
        const icons = {
            'info': '🔍',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'feed': '📰',
            'article': '📄',
            'api': '🔗',
            'processing': '⚙️',
            'data': '📊'
        };
        return icons[type] || '📝';
    }

    /**
     * Format metadata for feed and article logs
     */
    formatMetadata(metadata, type) {
        if (type === 'feed') {
            return `
                <span class="meta-item">Source: ${metadata.source || 'Unknown'}</span>
                <span class="meta-item">Articles: ${metadata.articleCount || 0}</span>
                ${metadata.responseTime ? `<span class="meta-item">${metadata.responseTime}ms</span>` : ''}
            `;
        } else if (type === 'article') {
            return `
                <span class="meta-item">${metadata.title ? metadata.title.substring(0, 50) + '...' : 'Processing article'}</span>
                ${metadata.publishDate ? `<span class="meta-item">${metadata.publishDate}</span>` : ''}
            `;
        }
        return '';
    }

    /**
     * Log RSS feed processing start
     */
    logFeedProcessingStart(totalFeeds) {
        this.feedCount = 0;
        this.articleCount = 0;
        this.log(`🔧 Initializing RSS service for ${totalFeeds} Australian property feeds...`, 'info');
        this.updateTimer('Fetching Feeds');
    }

    /**
     * Log individual feed being read
     */
    logFeedReading(feedSource, metadata = {}) {
        this.feedCount++;
        const message = `📡 Connecting to ${feedSource}...`;
        this.log(message, 'feed', {
            source: feedSource,
            articleCount: metadata.articleCount,
            responseTime: metadata.responseTime
        });
    }

    /**
     * Log feed reading completion
     */
    logFeedComplete(feedSource, articleCount, responseTime) {
        const message = `✓ ${feedSource} - ${articleCount} articles retrieved`;
        this.log(message, 'success', {
            source: feedSource,
            articleCount: articleCount,
            responseTime: responseTime
        });
        this.articleCount += articleCount;
    }

    /**
     * Log individual article processing
     */
    logArticleProcessing(articleTitle, publishDate, source) {
        const message = `📄 Processing: "${articleTitle.substring(0, 40)}..."`;
        this.log(message, 'article', {
            title: articleTitle,
            publishDate: publishDate,
            source: source
        });
    }

    /**
     * Log RSS processing summary
     */
    logRSSProcessingSummary(totalFeeds, totalArticles, duration) {
        const message = `📊 RSS Summary: ${totalFeeds} feeds, ${totalArticles} articles in ${duration}s`;
        this.log(message, 'data');
    }

    /**
     * Log article filtering and relevance scoring
     */
    logArticleFiltering(totalArticles, relevantArticles, keywords = []) {
        const message = `🔍 Filtered ${totalArticles} articles → ${relevantArticles} relevant`;
        this.log(message, 'data');
        
        if (keywords.length > 0) {
            this.log(`🏷️ Keywords: ${keywords.join(', ')}`, 'info');
        }
    }

    /**
     * Log LLM processing stages
     */
    logLLMProcessing(stage, provider, model) {
        const messages = {
            'starting': `🤖 Initializing ${provider} ${model}...`,
            'sending': `📤 Sending property analysis request to ${provider}...`,
            'processing': `⚙️ ${provider} analyzing Australian property data...`,
            'complete': `✅ ${provider} analysis completed successfully`
        };
        
        this.log(messages[stage] || `${stage} - ${provider}`, 'processing');
        
        if (stage === 'starting') {
            this.updateTimer(`${provider} Analysis`);
        }
    }

    /**
     * Log context preparation
     */
    logContextPreparation(articleCount, contextSize) {
        this.log(`📋 Prepared context: ${articleCount} articles, ${contextSize} tokens`, 'processing');
    }

    /**
     * Log API calls and responses
     */
    logApiCall(endpoint, method, responseTime, success = true) {
        const status = success ? '✅' : '❌';
        const message = `${status} ${method} ${endpoint} - ${responseTime}ms`;
        this.log(message, success ? 'api' : 'error');
    }

    /**
     * Log quality assurance checks
     */
    logQualityCheck(checkType, passed) {
        const icon = passed ? '✅' : '⚠️';
        const status = passed ? 'passed' : 'flagged';
        this.log(`${icon} Quality check (${checkType}): ${status}`, passed ? 'success' : 'warning');
    }

    /**
     * Update the processing timer
     * @param {string} status - Timer status
     */
    updateTimer(status) {
        const timer = document.getElementById('processingTimer');
        if (timer) {
            timer.textContent = status;
            timer.className = `sidebar-timer ${status.toLowerCase().replace(' ', '-')}`;
        }
    }

    /**
     * Start timing for analysis
     */
    startTiming() {
        this.startTime = performance.now();
    }

    /**
     * Get elapsed time since start
     */
    getElapsedTime() {
        return this.startTime ? performance.now() - this.startTime : 0;
    }

    /**
     * OPTIMIZED: Simulate detailed RSS feed processing for enhanced user experience
     * Reduced delays for faster performance while maintaining engagement
     */
    async simulateDetailedFeedProcessing() {
        const feeds = [
            {
                name: 'RealEstate.com.au',
                articles: 25,
                responseTime: 450,
                keyArticles: [
                    "Pet tax: Why having a pet could be costing renters $14k a year",
                    "Sydney property prices show resilience despite market headwinds"
                ]
            },
            {
                name: 'Smart Property Investment',
                articles: 12,
                responseTime: 320,
                keyArticles: [
                    "Regional property markets outperforming capital cities"
                ]
            },
            {
                name: 'View.com.au Property News',
                articles: 18,
                responseTime: 380,
                keyArticles: [
                    "First home buyer activity surges in affordable markets",
                    "Interest rate predictions for the remainder of 2025"
                ]
            },
            {
                name: 'First National Real Estate',
                articles: 8,
                responseTime: 290,
                keyArticles: []
            },
            {
                name: 'PropertyMe Blog',
                articles: 6,
                responseTime: 250,
                keyArticles: []
            },
            {
                name: 'Real Estate Talk',
                articles: 15,
                responseTime: 410,
                keyArticles: [
                    "Investment property tax changes: What landlords need to know"
                ]
            }
        ];

        this.logFeedProcessingStart(feeds.length);

        for (const feed of feeds) {
            // Log feed reading start
            this.logFeedReading(feed.name, {
                articleCount: feed.articles,
                responseTime: feed.responseTime
            });
            
            // OPTIMIZED: Reduced network delay from 200-600ms to 50-150ms
            await this.delay(Math.random() * 100 + 50);
            
            // Log feed completion
            this.logFeedComplete(feed.name, feed.articles, feed.responseTime);
            
            // Process key articles if available
            for (const article of feed.keyArticles) {
                // OPTIMIZED: Reduced article delay from 100-300ms to 25-75ms
                await this.delay(Math.random() * 50 + 25);
                this.logArticleProcessing(
                    article,
                    this.getRandomTimeAgo(),
                    feed.name
                );
            }
        }

        const totalArticles = feeds.reduce((sum, feed) => sum + feed.articles, 0);
        const duration = ((Date.now() - this.startTime) / 1000).toFixed(1);
        this.logRSSProcessingSummary(feeds.length, totalArticles, duration);

        // OPTIMIZED: Reduced article filtering delay from 200ms to 50ms
        await this.delay(50);
        const relevantArticles = Math.floor(totalArticles * 0.7);
        this.logArticleFiltering(totalArticles, relevantArticles, ['property', 'real estate', 'housing']);

        return {
            feedsProcessed: feeds.length,
            totalArticles: totalArticles,
            relevantArticles: relevantArticles,
            duration: duration
        };
    }

    /**
     * Get random realistic time ago
     */
    getRandomTimeAgo() {
        const options = [
            "2 hours ago",
            "4 hours ago", 
            "6 hours ago",
            "1 day ago",
            "2 days ago",
            "Just now",
            "1 hour ago"
        ];
        return options[Math.floor(Math.random() * options.length)];
    }

    /**
     * Delay helper for simulations
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}