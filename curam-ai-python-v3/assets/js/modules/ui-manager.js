// =====================================================
// FILE: assets/js/modules/ui-manager.js
// =====================================================
/**
 * UI Manager Module
 * Handles UI interactions, notifications, and display updates
 */
class UIManager {
    constructor() {
        this.setupNotifications();
    }

    /**
     * Setup notification system
     */
    setupNotifications() {
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
     * Render preset questions
     */
    renderPresetQuestions(questions, onSelect) {
        const container = document.getElementById('presetQuestions');
        if (!container) return;
        
        container.innerHTML = '';
        
        questions.forEach((question, index) => {
            const button = document.createElement('button');
            button.className = 'question-btn';
            button.textContent = question;
            button.setAttribute('data-question', question);
            button.setAttribute('data-index', index);
            
            // Add click handler
            button.addEventListener('click', (e) => {
                this.selectQuestion(question, button, onSelect);
            });
            
            // Add keyboard accessibility
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectQuestion(question, button, onSelect);
                }
            });
            
            container.appendChild(button);
        });
    }

    /**
     * Select a preset question
     */
    selectQuestion(question, buttonElement, callback) {
        // Clear previous selection
        document.querySelectorAll('.question-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Mark current selection
        buttonElement.classList.add('active');
        
        // Clear custom input
        const customInput = document.getElementById('customQuestion');
        if (customInput) {
            customInput.value = '';
        }
        
        // Show selection feedback
        this.showNotification(`Selected: ${question.substring(0, 50)}...`, 'info', 2000);
        
        // Call callback
        if (callback) callback(question);
    }

    /**
     * Update status display
     */
    updateStatusDisplay(health) {
        const aiStatus = document.getElementById('aiStatus');
        const aiStatusText = document.getElementById('aiStatusText');
        
        if (!aiStatus || !aiStatusText) return;
        
        if (health.status === 'healthy') {
            aiStatus.className = 'status-indicator status-healthy';
            aiStatusText.textContent = 'AI Services Online';
        } else if (health.status === 'degraded') {
            aiStatus.className = 'status-indicator status-warning';
            aiStatusText.textContent = 'AI Services Limited';
        } else {
            aiStatus.className = 'status-indicator status-error';
            aiStatusText.textContent = 'AI Services Offline';
        }
    }

    /**
     * Set analyze button state
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
     * Show/hide loading overlay
     */
    showLoadingOverlay() {
        if (!isFeatureEnabled('loadingOverlay')) return;
        
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }

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
}