/**
 * framework/mcp-ui-components.js - Reusable UI Components for MCP Applications
 * 
 * Provides standardized UI components that can be used across different
 * MCP applications for consistent user experience and functionality.
 */

class MCPUIComponents {
    constructor() {
        this.components = new Map();
        this.modalStack = [];
        this.notificationQueue = [];
        this.init();
    }

    /**
     * Initialize UI components
     */
    init() {
        this.createGlobalStyles();
        this.setupEventListeners();
    }

    /**
     * Create global styles for components
     */
    createGlobalStyles() {
        const styleId = 'mcp-ui-components-styles';
        if (document.getElementById(styleId)) return;

        const styles = `
            .mcp-modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .mcp-modal-overlay.active {
                opacity: 1;
            }

            .mcp-modal {
                background: white;
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                max-width: 90vw;
                max-height: 90vh;
                overflow: auto;
                transform: scale(0.9);
                transition: transform 0.3s ease;
            }

            .mcp-modal.active {
                transform: scale(1);
            }

            .mcp-modal-header {
                padding: 20px 20px 0 20px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .mcp-modal-title {
                margin: 0;
                font-size: 1.2em;
                font-weight: 600;
            }

            .mcp-modal-close {
                background: none;
                border: none;
                font-size: 1.5em;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background-color 0.2s;
            }

            .mcp-modal-close:hover {
                background-color: #f0f0f0;
            }

            .mcp-modal-body {
                padding: 20px;
            }

            .mcp-modal-footer {
                padding: 0 20px 20px 20px;
                display: flex;
                justify-content: flex-end;
                gap: 10px;
            }

            .mcp-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 15px 20px;
                max-width: 400px;
                z-index: 2000;
                transform: translateX(100%);
                transition: transform 0.3s ease;
                border-left: 4px solid #007bff;
            }

            .mcp-notification.show {
                transform: translateX(0);
            }

            .mcp-notification.success {
                border-left-color: #28a745;
            }

            .mcp-notification.error {
                border-left-color: #dc3545;
            }

            .mcp-notification.warning {
                border-left-color: #ffc107;
            }

            .mcp-notification.info {
                border-left-color: #17a2b8;
            }

            .mcp-notification-title {
                font-weight: 600;
                margin: 0 0 5px 0;
                font-size: 0.9em;
            }

            .mcp-notification-message {
                margin: 0;
                font-size: 0.85em;
                color: #666;
            }

            .mcp-notification-close {
                position: absolute;
                top: 10px;
                right: 10px;
                background: none;
                border: none;
                font-size: 1.2em;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .mcp-button {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9em;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-block;
                text-align: center;
            }

            .mcp-button.primary {
                background: #007bff;
                color: white;
            }

            .mcp-button.primary:hover {
                background: #0056b3;
            }

            .mcp-button.secondary {
                background: #6c757d;
                color: white;
            }

            .mcp-button.secondary:hover {
                background: #545b62;
            }

            .mcp-button.success {
                background: #28a745;
                color: white;
            }

            .mcp-button.success:hover {
                background: #1e7e34;
            }

            .mcp-button.danger {
                background: #dc3545;
                color: white;
            }

            .mcp-button.danger:hover {
                background: #c82333;
            }

            .mcp-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .mcp-input {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 0.9em;
                transition: border-color 0.2s;
            }

            .mcp-input:focus {
                outline: none;
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }

            .mcp-textarea {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 0.9em;
                font-family: inherit;
                resize: vertical;
                min-height: 100px;
                transition: border-color 0.2s;
            }

            .mcp-textarea:focus {
                outline: none;
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }

            .mcp-select {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 0.9em;
                background: white;
                cursor: pointer;
            }

            .mcp-select:focus {
                outline: none;
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }

            .mcp-loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #007bff;
                border-radius: 50%;
                animation: mcp-spin 1s linear infinite;
            }

            @keyframes mcp-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .mcp-tooltip {
                position: relative;
                display: inline-block;
            }

            .mcp-tooltip .mcp-tooltip-text {
                visibility: hidden;
                width: 200px;
                background-color: #333;
                color: white;
                text-align: center;
                border-radius: 6px;
                padding: 8px;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -100px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 0.8em;
            }

            .mcp-tooltip:hover .mcp-tooltip-text {
                visibility: visible;
                opacity: 1;
            }

            .mcp-badge {
                display: inline-block;
                padding: 2px 8px;
                font-size: 0.75em;
                font-weight: 600;
                border-radius: 12px;
                background: #007bff;
                color: white;
            }

            .mcp-badge.success {
                background: #28a745;
            }

            .mcp-badge.warning {
                background: #ffc107;
                color: #212529;
            }

            .mcp-badge.danger {
                background: #dc3545;
            }

            .mcp-badge.info {
                background: #17a2b8;
            }
        `;

        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Close modals on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalStack.length > 0) {
                this.closeTopModal();
            }
        });

        // Close modals on overlay click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('mcp-modal-overlay')) {
                this.closeTopModal();
            }
        });
    }

    /**
     * Create a modal dialog
     */
    createModal(options = {}) {
        const {
            title = 'Modal',
            content = '',
            width = 'auto',
            height = 'auto',
            closable = true,
            onClose = null,
            buttons = []
        } = options;

        const modalId = 'mcp-modal-' + Date.now();
        
        const modalHTML = `
            <div id="${modalId}" class="mcp-modal-overlay">
                <div class="mcp-modal" style="width: ${width}; height: ${height};">
                    <div class="mcp-modal-header">
                        <h3 class="mcp-modal-title">${title}</h3>
                        ${closable ? '<button class="mcp-modal-close">&times;</button>' : ''}
                    </div>
                    <div class="mcp-modal-body">
                        ${content}
                    </div>
                    ${buttons.length > 0 ? `
                        <div class="mcp-modal-footer">
                            ${buttons.map(btn => `
                                <button class="mcp-button ${btn.type || 'secondary'}" 
                                        onclick="${btn.onClick || ''}">
                                    ${btn.text}
                                </button>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        const modalElement = document.getElementById(modalId);
        const modalContent = modalElement.querySelector('.mcp-modal');
        const closeButton = modalElement.querySelector('.mcp-modal-close');

        // Setup close functionality
        if (closable && closeButton) {
            closeButton.addEventListener('click', () => {
                this.closeModal(modalId, onClose);
            });
        }

        // Show modal
        setTimeout(() => {
            modalElement.classList.add('active');
            modalContent.classList.add('active');
        }, 10);

        this.modalStack.push(modalId);
        this.components.set(modalId, { type: 'modal', element: modalElement });

        return modalId;
    }

    /**
     * Close a specific modal
     */
    closeModal(modalId, onClose = null) {
        const modalData = this.components.get(modalId);
        if (!modalData || modalData.type !== 'modal') return;

        const modalElement = modalData.element;
        const modalContent = modalElement.querySelector('.mcp-modal');

        modalElement.classList.remove('active');
        modalContent.classList.remove('active');

        setTimeout(() => {
            if (modalElement.parentNode) {
                modalElement.parentNode.removeChild(modalElement);
            }
            this.components.delete(modalId);
            this.modalStack = this.modalStack.filter(id => id !== modalId);
            
            if (onClose && typeof onClose === 'function') {
                onClose();
            }
        }, 300);
    }

    /**
     * Close the top modal
     */
    closeTopModal() {
        if (this.modalStack.length > 0) {
            const topModalId = this.modalStack[this.modalStack.length - 1];
            this.closeModal(topModalId);
        }
    }

    /**
     * Show a notification
     */
    showNotification(options = {}) {
        const {
            title = 'Notification',
            message = '',
            type = 'info',
            duration = 5000,
            closable = true
        } = options;

        const notificationId = 'mcp-notification-' + Date.now();
        
        const notificationHTML = `
            <div id="${notificationId}" class="mcp-notification ${type}">
                ${closable ? '<button class="mcp-notification-close">&times;</button>' : ''}
                <div class="mcp-notification-title">${title}</div>
                <div class="mcp-notification-message">${message}</div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', notificationHTML);
        
        const notificationElement = document.getElementById(notificationId);
        const closeButton = notificationElement.querySelector('.mcp-notification-close');

        // Setup close functionality
        if (closable && closeButton) {
            closeButton.addEventListener('click', () => {
                this.hideNotification(notificationId);
            });
        }

        // Show notification
        setTimeout(() => {
            notificationElement.classList.add('show');
        }, 10);

        // Auto-hide after duration
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notificationId);
            }, duration);
        }

        this.components.set(notificationId, { type: 'notification', element: notificationElement });
        return notificationId;
    }

    /**
     * Hide a notification
     */
    hideNotification(notificationId) {
        const notificationData = this.components.get(notificationId);
        if (!notificationData || notificationData.type !== 'notification') return;

        const notificationElement = notificationData.element;
        notificationElement.classList.remove('show');

        setTimeout(() => {
            if (notificationElement.parentNode) {
                notificationElement.parentNode.removeChild(notificationElement);
            }
            this.components.delete(notificationId);
        }, 300);
    }

    /**
     * Create a button element
     */
    createButton(options = {}) {
        const {
            text = 'Button',
            type = 'primary',
            onClick = null,
            disabled = false,
            className = '',
            icon = null
        } = options;

        const button = document.createElement('button');
        button.className = `mcp-button ${type} ${className}`;
        button.textContent = text;
        button.disabled = disabled;

        if (icon) {
            button.innerHTML = `${icon} ${text}`;
        }

        if (onClick && typeof onClick === 'function') {
            button.addEventListener('click', onClick);
        }

        return button;
    }

    /**
     * Create an input element
     */
    createInput(options = {}) {
        const {
            type = 'text',
            placeholder = '',
            value = '',
            className = '',
            required = false,
            onChange = null
        } = options;

        const input = document.createElement('input');
        input.type = type;
        input.className = `mcp-input ${className}`;
        input.placeholder = placeholder;
        input.value = value;
        input.required = required;

        if (onChange && typeof onChange === 'function') {
            input.addEventListener('input', onChange);
        }

        return input;
    }

    /**
     * Create a textarea element
     */
    createTextarea(options = {}) {
        const {
            placeholder = '',
            value = '',
            className = '',
            rows = 4,
            onChange = null
        } = options;

        const textarea = document.createElement('textarea');
        textarea.className = `mcp-textarea ${className}`;
        textarea.placeholder = placeholder;
        textarea.value = value;
        textarea.rows = rows;

        if (onChange && typeof onChange === 'function') {
            textarea.addEventListener('input', onChange);
        }

        return textarea;
    }

    /**
     * Create a select element
     */
    createSelect(options = {}) {
        const {
            options: selectOptions = [],
            selectedValue = '',
            className = '',
            onChange = null
        } = options;

        const select = document.createElement('select');
        select.className = `mcp-select ${className}`;

        selectOptions.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.value;
            optionElement.textContent = option.text;
            optionElement.selected = option.value === selectedValue;
            select.appendChild(optionElement);
        });

        if (onChange && typeof onChange === 'function') {
            select.addEventListener('change', onChange);
        }

        return select;
    }

    /**
     * Create a loading spinner
     */
    createLoadingSpinner(size = '20px') {
        const spinner = document.createElement('div');
        spinner.className = 'mcp-loading';
        spinner.style.width = size;
        spinner.style.height = size;
        return spinner;
    }

    /**
     * Create a tooltip
     */
    createTooltip(element, text) {
        element.classList.add('mcp-tooltip');
        element.innerHTML += `<span class="mcp-tooltip-text">${text}</span>`;
        return element;
    }

    /**
     * Create a badge
     */
    createBadge(text, type = 'primary') {
        const badge = document.createElement('span');
        badge.className = `mcp-badge ${type}`;
        badge.textContent = text;
        return badge;
    }

    /**
     * Show confirmation dialog
     */
    showConfirmation(options = {}) {
        const {
            title = 'Confirm',
            message = 'Are you sure?',
            confirmText = 'Yes',
            cancelText = 'No',
            onConfirm = null,
            onCancel = null
        } = options;

        return new Promise((resolve) => {
            const modalId = this.createModal({
                title,
                content: `<p>${message}</p>`,
                buttons: [
                    {
                        text: cancelText,
                        type: 'secondary',
                        onClick: `window.mcpUI.closeModal('${modalId}'); window.mcpUI.resolveConfirmation(false);`
                    },
                    {
                        text: confirmText,
                        type: 'danger',
                        onClick: `window.mcpUI.closeModal('${modalId}'); window.mcpUI.resolveConfirmation(true);`
                    }
                ]
            });

            // Store resolve function globally for button callbacks
            window.mcpUI = window.mcpUI || {};
            window.mcpUI.resolveConfirmation = (result) => {
                if (result && onConfirm) onConfirm();
                if (!result && onCancel) onCancel();
                resolve(result);
                delete window.mcpUI.resolveConfirmation;
            };
        });
    }

    /**
     * Show prompt dialog
     */
    showPrompt(options = {}) {
        const {
            title = 'Input Required',
            message = 'Please enter a value:',
            defaultValue = '',
            placeholder = '',
            onConfirm = null,
            onCancel = null
        } = options;

        return new Promise((resolve) => {
            const inputId = 'mcp-prompt-input-' + Date.now();
            const modalId = this.createModal({
                title,
                content: `
                    <p>${message}</p>
                    <input id="${inputId}" class="mcp-input" type="text" 
                           value="${defaultValue}" placeholder="${placeholder}" 
                           style="width: 100%; margin-top: 10px;">
                `,
                buttons: [
                    {
                        text: 'Cancel',
                        type: 'secondary',
                        onClick: `window.mcpUI.closeModal('${modalId}'); window.mcpUI.resolvePrompt(null);`
                    },
                    {
                        text: 'OK',
                        type: 'primary',
                        onClick: `window.mcpUI.closeModal('${modalId}'); window.mcpUI.resolvePrompt(document.getElementById('${inputId}').value);`
                    }
                ]
            });

            // Focus input
            setTimeout(() => {
                const input = document.getElementById(inputId);
                if (input) input.focus();
            }, 100);

            // Store resolve function globally for button callbacks
            window.mcpUI = window.mcpUI || {};
            window.mcpUI.resolvePrompt = (value) => {
                if (value !== null && onConfirm) onConfirm(value);
                if (value === null && onCancel) onCancel();
                resolve(value);
                delete window.mcpUI.resolvePrompt;
            };
        });
    }

    /**
     * Clean up all components
     */
    cleanup() {
        this.components.forEach((component, id) => {
            if (component.element && component.element.parentNode) {
                component.element.parentNode.removeChild(component.element);
            }
        });
        this.components.clear();
        this.modalStack = [];
    }

    /**
     * Render complete MCP dashboard
     * @param {HTMLElement} container - Container element
     * @param {Object} options - Configuration options
     */
    static renderMCPDashboard(container, options = {}) {
        const defaultOptions = {
            showWorkflow: true,
            showContextMemory: true,
            showToolDiscovery: true,
            showComparison: true,
            title: '🧠 MCP Tool Orchestration in Real-Time'
        };
        
        const config = { ...defaultOptions, ...options };
        
        const dashboardHTML = `
            <div class="mcp-dashboard">
                <h3>${config.title}</h3>
                
                ${config.showWorkflow ? `
                    <div id="mcpWorkflowContainer">
                        <!-- Workflow will be rendered here -->
                    </div>
                ` : ''}
                
                ${config.showContextMemory ? `
                    <div id="mcpContextMemoryContainer">
                        <!-- Context memory will be rendered here -->
                    </div>
                ` : ''}
                
                ${config.showToolDiscovery ? `
                    <div id="mcpToolDiscoveryContainer">
                        <!-- Tool discovery will be rendered here -->
                    </div>
                ` : ''}
                
                ${config.showComparison ? `
                    <div id="mcpComparisonContainer">
                        <!-- MCP vs Traditional comparison will be rendered here -->
                    </div>
                ` : ''}
            </div>
        `;
        
        container.innerHTML = dashboardHTML;
        
        // Render individual components
        if (config.showContextMemory) {
            this.renderContextMemory(document.getElementById('mcpContextMemoryContainer'));
        }
        
        if (config.showToolDiscovery) {
            this.renderToolDiscovery(document.getElementById('mcpToolDiscoveryContainer'));
        }
        
        if (config.showComparison) {
            this.renderMCPComparison(document.getElementById('mcpComparisonContainer'));
        }
    }

    /**
     * Render context memory component
     * @param {HTMLElement} container - Container element
     * @param {Object} initialData - Initial context data
     */
    static renderContextMemory(container, initialData = {}) {
        if (!container) return;
        
        const contextHTML = `
            <div class="context-memory">
                <h4>📚 Context Memory (MCP Advantage)</h4>
                <div class="context-item">
                    <span class="context-label">Previous Question:</span>
                    <span class="context-value" id="lastQuestion">${initialData.lastQuestion || 'None yet'}</span>
                </div>
                <div class="context-item">
                    <span class="context-label">Context Entries:</span>
                    <span class="context-value" id="contextEntries">${initialData.contextEntries || 0}</span>
                </div>
                <div class="context-item">
                    <span class="context-label">Tools Chained:</span>
                    <span class="context-value" id="toolsChained">${initialData.toolsChained || 0}</span>
                </div>
                <div class="context-item">
                    <button class="btn" onclick="window.MCPUIComponents.toggleConversationWindow()" id="showConversationBtn" style="padding: 6px 12px; font-size: 0.8em; margin-top: 10px;">
                        Show Conversation History
                    </button>
                </div>
                
                <!-- Conversation Window - Rendered directly below the button -->
                <div class="conversation-window" id="conversationWindow" style="display: none; margin-top: 15px;">
                    <h4>💬 Session Conversation History</h4>
                    <div class="conversation-controls">
                        <button class="btn" onclick="window.MCPUIComponents.exportToPDF()" style="padding: 4px 8px; font-size: 0.8em; background: #46b450;">
                            📄 Export PDF
                        </button>
                        <button class="btn" onclick="window.MCPUIComponents.emailReport()" style="padding: 4px 8px; font-size: 0.8em; background: #0073aa;">
                            📧 Email PDF
                        </button>
                        <button class="btn" onclick="window.MCPUIComponents.clearConversation()" style="padding: 4px 8px; font-size: 0.8em; background: #dc3232;">
                            Clear All History
                        </button>
                        <button class="btn" onclick="window.MCPUIComponents.toggleConversationWindow()" style="padding: 4px 8px; font-size: 0.8em;">
                            Hide
                        </button>
                    </div>
                    
                    <div class="image-gallery" id="imageGallery" style="display: none;">
                        <h5>🎨 Generated Images This Session</h5>
                        <div class="thumbnail-grid" id="thumbnailGrid">
                            <div class="no-images">No images generated yet</div>
                        </div>
                    </div>
                    
                    <div class="conversation-history" id="conversationHistory">
                        <div class="conversation-entry empty">
                            <em>No conversation history yet. Ask a question to start building context memory.</em>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = contextHTML;
        console.log('✅ MCPUIComponents: Context memory with embedded conversation window rendered');
    }

    /**
     * Render conversation history window - DEPRECATED
     * Now rendered directly in context memory section
     * @param {HTMLElement} container - Container element
     */
    static renderConversationWindow(container) {
        if (!container) {
            console.log('ℹ️ MCPUIComponents: Conversation window now embedded in context memory - no separate rendering needed');
            return;
        }
        
        // Clear the container since conversation window is now embedded
        container.innerHTML = '<!-- Conversation window now embedded in context memory section -->';
        console.log('ℹ️ MCPUIComponents: Conversation window is now embedded in context memory section');
    }

    /**
     * Render tool discovery component
     * @param {HTMLElement} container - Container element
     * @param {Array} tools - Array of available tools
     */
    static renderToolDiscovery(container, tools = null) {
        if (!container) return;
        
        const defaultTools = [
            { name: 'compare_gemini_models', description: 'Compare AI responses', status: '✅' },
            { name: 'generate_contextual_image', description: 'Create images from text', status: '✅' },
            { name: 'format_response', description: 'Rich text formatting', status: '✅' },
            { name: 'analyze_context', description: 'Intelligent content analysis', status: '✅' }
        ];
        
        const toolList = tools || defaultTools;
        
        const toolHTML = `
            <div class="tool-discovery">
                <h4>🔧 Available Tools (Auto-Discovered)</h4>
                <ul class="tool-list">
                    ${toolList.map(tool => `
                        <li>
                            <span class="tool-status">${tool.status}</span>
                            <span class="tool-name">${tool.name}</span>
                            <span class="tool-description">${tool.description}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
        
        container.innerHTML = toolHTML;
    }

    /**
     * Render MCP vs Traditional comparison
     * @param {HTMLElement} container - Container element
     */
    static renderMCPComparison(container) {
        if (!container) return;
        
        const comparisonHTML = `
            <div class="mcp-comparison">
                <div class="comparison-box traditional-api">
                    <h4>❌ Traditional REST API</h4>
                    <ul class="comparison-list">
                        <li>Fixed endpoints</li>
                        <li>No context memory</li>
                        <li>Manual orchestration</li>
                        <li>Stateless operations</li>
                    </ul>
                </div>
                <div class="comparison-box mcp-approach">
                    <h4>✅ MCP (This Demo)</h4>
                    <ul class="comparison-list">
                        <li>Dynamic tool discovery</li>
                        <li>Context-aware chaining</li>
                        <li>Intelligent tool selection</li>
                        <li>Contextual workflows</li>
                    </ul>
                </div>
            </div>
        `;
        
        container.innerHTML = comparisonHTML;
    }

    /**
     * Render loading component
     * @param {HTMLElement} container - Container element
     * @param {string} message - Loading message
     * @param {boolean} show - Whether to show or hide
     */
    static renderLoading(container, message = 'Loading...', show = true) {
        if (!container) return;
        
        if (!show) {
            container.style.display = 'none';
            return;
        }
        
        const loadingHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        
        container.innerHTML = loadingHTML;
        container.style.display = 'block';
    }

    /**
     * Render error message
     * @param {HTMLElement} container - Container element
     * @param {string} message - Error message
     * @param {string} details - Additional error details
     */
    static renderError(container, message, details = null) {
        if (!container) return;
        
        const errorHTML = `
            <div class="error">
                <strong>Error:</strong> ${message}
                ${details ? `<br><small>${details}</small>` : ''}
            </div>
        `;
        
        container.innerHTML = errorHTML;
    }

    /**
     * Render success message
     * @param {HTMLElement} container - Container element
     * @param {string} message - Success message
     */
    static renderSuccess(container, message) {
        if (!container) return;
        
        const successHTML = `
            <div class="success">
                <strong>Success:</strong> ${message}
            </div>
        `;
        
        container.innerHTML = successHTML;
    }

    /**
     * Render image result component
     * @param {HTMLElement} container - Container element
     * @param {Object} imageData - Image data object
     * @param {Object} options - Rendering options
     */
    static renderImageResult(container, imageData, options = {}) {
        if (!container || !imageData) return;
        
        const defaultOptions = {
            showExplanation: true,
            showMetadata: true,
            isAutoGenerated: false,
            imageNumber: null
        };
        
        const config = { ...defaultOptions, ...options };
        
        const autoIndicator = config.isAutoGenerated ? 
            '<div class="auto-generation-indicator"><strong>🤖 MCP Auto-Generated from Context Analysis</strong></div>' : '';
        
        const imageNumber = config.imageNumber ? 
            `<div style="text-align: right; margin-bottom: 10px; color: #666; font-size: 0.9em;">
                Image #${config.imageNumber} • <a href="#" onclick="window.MCPUIComponents.toggleConversationWindow(); return false;">View All Images</a>
            </div>` : '';
        
        const explanation = config.showExplanation && imageData.explanation ? 
            `<div class="image-explanation">
                <h4>🧠 MCP Context Analysis:</h4>
                <p>${imageData.explanation}</p>
            </div>` : '';
        
        const metadata = config.showMetadata ? 
            `<p style="margin-top: 15px; color: #666;">
                <strong>Prompt:</strong> ${imageData.prompt}<br>
                <strong>Style:</strong> ${imageData.style}<br>
                ${imageData.seed ? `<strong>Seed:</strong> ${imageData.seed}<br>` : ''}
                ${config.isAutoGenerated ? '<strong>Generation:</strong> Intelligent MCP auto-creation' : ''}
            </p>` : '';
        
        const imageHTML = `
            ${autoIndicator}
            <div class="image-result">
                ${imageNumber}
                <div class="session-image-background" 
                     style="background-image: url('data:image/png;base64,${imageData.imageBase64}');"
                     onclick="window.MCPUIComponents.openLightbox('${imageData.imageBase64}', '${imageData.prompt.replace(/'/g, "\\'")}'); return false;" 
                     style="cursor: pointer;" 
                     title="Click to view full size"></div>
                ${explanation}
                ${metadata}
            </div>
        `;
        
        container.innerHTML = imageHTML;
    }

    /**
     * Create and show lightbox for image viewing
     * @param {string} imageBase64 - Base64 image data
     * @param {string} prompt - Image prompt for alt text
     */
    static openLightbox(imageBase64, prompt) {
        // Remove existing lightbox
        const existingLightbox = document.getElementById('mcpLightbox');
        if (existingLightbox) {
            existingLightbox.remove();
        }
        
        // Create new lightbox
        const lightbox = document.createElement('div');
        lightbox.id = 'mcpLightbox';
        lightbox.className = 'lightbox active';
        lightbox.innerHTML = `
            <span class="lightbox-close" onclick="window.MCPUIComponents.closeLightbox()">&times;</span>
            <img src="data:image/png;base64,${imageBase64}" alt="${prompt}" />
        `;
        
        document.body.appendChild(lightbox);
        
        // Close on background click
        lightbox.onclick = function(e) {
            if (e.target === lightbox) {
                window.MCPUIComponents.closeLightbox();
            }
        };
        
        // Close on escape key
        const escapeHandler = function(e) {
            if (e.key === 'Escape') {
                window.MCPUIComponents.closeLightbox();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }

    /**
     * Close lightbox
     */
    static closeLightbox() {
        const lightbox = document.getElementById('mcpLightbox');
        if (lightbox) {
            lightbox.remove();
        }
    }

    /**
     * Toggle conversation window visibility - FIXED VERSION
     */
    static toggleConversationWindow() {
        console.log('🔍 MCPUIComponents: toggleConversationWindow called');
        
        const conversationWindow = document.getElementById('conversationWindow');
        const btn = document.getElementById('showConversationBtn');
        
        console.log('🔍 MCPUIComponents: conversationWindow element:', conversationWindow);
        console.log('🔍 MCPUIComponents: showConversationBtn element:', btn);
        
        if (!conversationWindow) {
            console.error('❌ MCPUIComponents: conversationWindow element not found!');
            return;
        }
        
        if (!btn) {
            console.error('❌ MCPUIComponents: showConversationBtn element not found!');
            return;
        }
        
        // Get computed style to check actual visibility
        const computedStyle = window.getComputedStyle(conversationWindow);
        const currentDisplay = computedStyle.display;
        const buttonText = btn.textContent.trim(); // Remove whitespace
        
        console.log('🔍 MCPUIComponents: Current display style:', currentDisplay);
        console.log('🔍 MCPUIComponents: Button text (trimmed):', `"${buttonText}"`);
        
        // Check based on button text, but clean it first
        const shouldShow = buttonText.includes('Show');
        
        console.log('🔍 MCPUIComponents: Should show?', shouldShow);
        
        if (shouldShow) {
            conversationWindow.style.display = 'block';
            conversationWindow.style.visibility = 'visible'; // Force visibility
            btn.textContent = 'Hide Conversation History';
            console.log('✅ MCPUIComponents: Conversation window shown - display set to block');
            
            // Double-check that it's actually visible
            setTimeout(() => {
                const finalStyle = window.getComputedStyle(conversationWindow);
                console.log('🔍 MCPUIComponents: Final display style after show:', finalStyle.display);
                console.log('🔍 MCPUIComponents: Final visibility:', finalStyle.visibility);
            }, 100);
            
            // Trigger updates if session exists
            if (window.mcpSession) {
                console.log('🔄 MCPUIComponents: Updating displays with session data');
                window.mcpSession.updateConversationDisplay();
                window.mcpSession.updateImageGalleryDisplay();
            }
        } else {
            conversationWindow.style.display = 'none';
            btn.textContent = 'Show Conversation History';
            console.log('✅ MCPUIComponents: Conversation window hidden');
        }
    }

    /**
     * Clear conversation (requires MCP session to be available)
     */
    static clearConversation() {
        if (window.mcpSession && window.mcpSession.clearSession) {
            window.mcpSession.clearSession();
        } else {
            console.warn('MCP Session not available for clearing conversation');
        }
    }

    /**
     * Export to PDF with images - RESTORED FULL FUNCTIONALITY
     */
    static async exportToPDF() {
        if (!window.mcpSession || (window.mcpSession.conversationHistory.length === 0 && window.mcpSession.imageGallery.length === 0)) {
            this.showNotification('No conversation history or images to export!', 'warning', 3000);
            return;
        }

        // Show loading state
        const exportBtn = event.target;
        const originalText = exportBtn.textContent;
        exportBtn.textContent = '📄 Generating PDF...';
        exportBtn.disabled = true;

        try {
            // Check if jsPDF is available
            if (typeof window.jspdf !== 'undefined') {
                await this.generateAdvancedPDFWithImages();
            } else {
                // Fallback to print method
                const pdfContent = await this.generatePDFContent();
                this.downloadPDF(pdfContent);
            }
            
            console.log('🔧 MCP: PDF export completed successfully');
            this.showNotification('PDF exported successfully with images!', 'success', 3000);
            
        } catch (error) {
            console.error('PDF Export Error:', error);
            this.showNotification(`Error generating PDF: ${error.message}`, 'error', 5000);
        } finally {
            exportBtn.textContent = originalText;
            exportBtn.disabled = false;
        }
    }

    /**
     * Generate advanced PDF with images included
     */
    static async generateAdvancedPDFWithImages() {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        let yPosition = 20;
        
        // Header
        pdf.setFontSize(20);
        pdf.setTextColor(0, 115, 170);
        pdf.text('Curam AI MCP Session Report', pageWidth / 2, yPosition, { align: 'center' });
        
        yPosition += 10;
        pdf.setFontSize(12);
        pdf.setTextColor(102, 102, 102);
        pdf.text('Model Context Protocol - Intelligent Tool Orchestration', pageWidth / 2, yPosition, { align: 'center' });
        
        yPosition += 8;
        pdf.text(`Generated on ${new Date().toLocaleString()}`, pageWidth / 2, yPosition, { align: 'center' });
        
        yPosition += 20;
        
        // Session Summary Box
        pdf.setDrawColor(0, 115, 170);
        pdf.setFillColor(240, 248, 255);
        pdf.rect(20, yPosition - 5, pageWidth - 40, 30, 'FD');
        
        pdf.setFontSize(14);
        pdf.setTextColor(0, 115, 170);
        pdf.text('Session Summary', 25, yPosition + 5);
        
        pdf.setFontSize(10);
        pdf.setTextColor(51, 51, 51);
        pdf.text(`Total Questions: ${window.mcpSession.conversationHistory.length}`, 25, yPosition + 12);
        pdf.text(`Images Generated: ${window.mcpSession.imageGallery.length}`, 25, yPosition + 18);
        pdf.text(`MCP Features: Context Memory, Tool Chaining`, pageWidth / 2, yPosition + 12);
        pdf.text(`Session Duration: ${this.getSessionDuration()}`, pageWidth / 2, yPosition + 18);
        
        yPosition += 35;
        
        // Conversation History
        if (window.mcpSession.conversationHistory.length > 0) {
            pdf.setFontSize(14);
            pdf.setTextColor(0, 115, 170);
            pdf.text('Conversation History', 20, yPosition);
            yPosition += 10;
            
            for (let i = 0; i < window.mcpSession.conversationHistory.length; i++) {
                const entry = window.mcpSession.conversationHistory[i];
                
                // Check if we need a new page
                if (yPosition > pageHeight - 50) {
                    pdf.addPage();
                    yPosition = 20;
                }
                
                // Question
                pdf.setFontSize(11);
                pdf.setTextColor(0, 115, 170);
                pdf.text(`Question ${i + 1}: ${entry.question}`, 20, yPosition);
                yPosition += 8;
                
                // Response (truncated and formatted)
                pdf.setFontSize(9);
                pdf.setTextColor(51, 51, 51);
                const responseText = this.formatResponseForPDF(entry.response);
                const splitText = pdf.splitTextToSize(responseText, pageWidth - 50);
                pdf.text(splitText, 30, yPosition);
                yPosition += splitText.length * 4 + 5;
                
                // Timestamp
                pdf.setFontSize(8);
                pdf.setTextColor(153, 153, 153);
                pdf.text(`Time: ${entry.timestamp}`, pageWidth - 30, yPosition - 2, { align: 'right' });
                yPosition += 10;
            }
        }
        
        // Images Section with actual thumbnails
        if (window.mcpSession.imageGallery.length > 0) {
            pdf.addPage();
            yPosition = 20;
            
            pdf.setFontSize(14);
            pdf.setTextColor(0, 115, 170);
            pdf.text('Generated Images', 20, yPosition);
            yPosition += 15;
            
            for (let i = 0; i < window.mcpSession.imageGallery.length; i++) {
                const image = window.mcpSession.imageGallery[i];
                
                // Check if we need a new page (need space for image + text)
                if (yPosition > pageHeight - 80) {
                    pdf.addPage();
                    yPosition = 20;
                }
                
                try {
                    // Add image to PDF using the stored base64 data
                    const imgData = `data:image/png;base64,${image.imageBase64}`;
                    
                    // Add image with consistent sizing
                    const imgWidth = 60;  // Fixed width
                    const imgHeight = 45; // Fixed height
                    pdf.addImage(imgData, 'PNG', 20, yPosition, imgWidth, imgHeight);
                    
                    // Image info next to the image
                    pdf.setFontSize(10);
                    pdf.setTextColor(51, 51, 51);
                    pdf.text(`Image ${i + 1}`, 85, yPosition + 10);
                    
                    pdf.setFontSize(9);
                    pdf.setTextColor(102, 102, 102);
                    pdf.text('Prompt:', 85, yPosition + 18);
                    
                    // Wrap prompt text
                    const promptText = image.prompt.length > 60 ? 
                        image.prompt.substring(0, 60) + '...' : image.prompt;
                    const splitPrompt = pdf.splitTextToSize(promptText, pageWidth - 110);
                    pdf.text(splitPrompt, 85, yPosition + 23);
                    
                    pdf.setFontSize(8);
                    pdf.setTextColor(102, 102, 102);
                    pdf.text(`Style: ${image.style}`, 85, yPosition + 35);
                    pdf.text(`Generated: ${image.timestamp}`, 85, yPosition + 40);
                    
                    if (image.isAutoGenerated) {
                        pdf.setTextColor(70, 180, 80);
                        pdf.text('🤖 MCP Auto-Generated', 85, yPosition + 45);
                    }
                    
                    yPosition += 60; // Move down for next image
                    
                    console.log(`✅ Added image ${i + 1} to PDF`);
                    
                } catch (error) {
                    console.warn(`Could not add image ${i + 1} to PDF:`, error);
                    
                    // Add placeholder text instead
                    pdf.setFontSize(10);
                    pdf.setTextColor(200, 200, 200);
                    pdf.rect(20, yPosition, 60, 45); // Draw placeholder rectangle
                    pdf.text('Image not', 30, yPosition + 20);
                    pdf.text('available', 30, yPosition + 30);
                    
                    // Still add the image info
                    pdf.setFontSize(10);
                    pdf.setTextColor(51, 51, 51);
                    pdf.text(`Image ${i + 1} (Error loading)`, 85, yPosition + 10);
                    
                    yPosition += 60;
                }
            }
        }
        
        // Footer on all pages
        const totalPages = pdf.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            pdf.setPage(i);
            pdf.setFontSize(8);
            pdf.setTextColor(153, 153, 153);
            pdf.text('Generated by Curam AI MCP Agent', pageWidth / 2, pageHeight - 10, { align: 'center' });
            pdf.text(`Page ${i} of ${totalPages}`, pageWidth - 20, pageHeight - 10, { align: 'right' });
        }
        
        // Save the PDF
        const filename = `MCP_Session_Report_${new Date().toISOString().slice(0, 10)}.pdf`;
        pdf.save(filename);
    }

    /**
     * Email report - RESTORED FUNCTIONALITY
     */
    static emailReport() {
        if (window.mcpSession && (window.mcpSession.conversationHistory.length > 0 || window.mcpSession.imageGallery.length > 0)) {
            // Pre-fill email message with session summary
            const sessionSummary = `${window.mcpSession.conversationHistory.length} questions and ${window.mcpSession.imageGallery.length} generated images`;
            
            // Show email modal
            this.showEmailModal(sessionSummary);
        } else {
            this.showNotification('No conversation history or images to email!', 'warning', 3000);
        }
    }

    /**
     * Show email modal with form
     * @param {string} sessionSummary - Summary of the session
     */
    static showEmailModal(sessionSummary) {
        // Remove existing modal
        const existingModal = document.getElementById('emailModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create email modal
        const emailModal = document.createElement('div');
        emailModal.id = 'emailModal';
        emailModal.className = 'email-modal active';
        emailModal.innerHTML = `
            <div class="email-modal-content">
                <button class="close-modal" onclick="window.MCPUIComponents.closeEmailModal()">&times;</button>
                <h3>📧 Email MCP Session Report</h3>
                
                <div class="email-info">
                    <strong>Real Email Delivery:</strong> This will generate a PDF and send it directly via our MCP email service. 
                    The recipient will receive an actual email with the report attached.
                </div>
                
                <form class="email-form" id="emailForm">
                    <div>
                        <label for="emailTo">To (Email Address):</label>
                        <input type="email" id="emailTo" placeholder="boss@company.com" required>
                    </div>
                    
                    <div>
                        <label for="emailSubject">Subject:</label>
                        <input type="text" id="emailSubject" value="MCP Session Report - Curam AI Demo" required>
                    </div>
                    
                    <div>
                        <label for="emailMessage">Message:</label>
                        <textarea id="emailMessage" placeholder="Please find attached the MCP session report...">Hi,

Please find attached the MCP (Model Context Protocol) session report from our Curam AI demonstration.

This report showcases:
- Intelligent tool orchestration and context memory
- Auto-generated images based on conversation context  
- Real-time workflow visualization
- Context-aware AI responses

The session included ${sessionSummary} demonstrating the advanced capabilities of our MCP implementation.

Best regards</textarea>
                    </div>
                    
                    <div class="email-buttons">
                        <button type="button" class="btn" onclick="window.MCPUIComponents.closeEmailModal()" style="background: #999;">
                            Cancel
                        </button>
                        <button type="submit" class="btn" style="background: #0073aa;">
                            📧 Send Email
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(emailModal);

        // Set up form submission
        const emailForm = document.getElementById('emailForm');
        emailForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendEmailWithPDF();
        });

        // Close on background click
        emailModal.onclick = (e) => {
            if (e.target === emailModal) {
                this.closeEmailModal();
            }
        };
    }

    /**
     * Close email modal
     */
    static closeEmailModal() {
        const modal = document.getElementById('emailModal');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * Send email with PDF attachment - FIXED FOR SIZE LIMITS
     */
    static async sendEmailWithPDF() {
        const emailTo = document.getElementById('emailTo').value;
        const emailSubject = document.getElementById('emailSubject').value;
        const emailMessage = document.getElementById('emailMessage').value;

        if (!emailTo || !emailSubject) {
            this.showNotification('Please fill in the email address and subject.', 'warning', 3000);
            return;
        }

        // Show loading state
        const sendBtn = document.querySelector('#emailForm button[type="submit"]');
        const originalText = sendBtn.textContent;
        sendBtn.textContent = '📧 Sending Email...';
        sendBtn.disabled = true;

        try {
            // Generate OPTIMIZED PDF data for email (smaller size)
            let pdfBase64 = null;
            
            if (typeof window.jspdf !== 'undefined') {
                console.log('🔧 MCP: Generating optimized PDF for email attachment');
                const { jsPDF } = window.jspdf;
                const pdf = new jsPDF('p', 'mm', 'a4');
                await this.generatePDFForEmail(pdf); // This is now the optimized version
                
                // Get base64 without data URI prefix
                const pdfDataUri = pdf.output('datauristring');
                pdfBase64 = pdfDataUri.split(',')[1]; // Remove "data:application/pdf;base64," prefix
                
                // Check PDF size and warn if still large
                const pdfSizeKB = Math.round((pdfBase64.length * 3/4) / 1024);
                console.log(`🔧 MCP: PDF size: ${pdfSizeKB}KB`);
                
                if (pdfSizeKB > 5000) { // If larger than 5MB
                    console.warn('🔧 MCP: PDF is large, might hit email size limits');
                }
                
                console.log('🔧 MCP: Optimized PDF generated successfully for email');
            } else {
                console.warn('PDF generation not available - sending email without attachment');
            }

            // Send email via API - using ConfigUtils if available
            console.log('🔧 MCP: Sending email via MCP email service');
            const apiBaseUrl = (typeof ConfigUtils !== 'undefined') ? 
                ConfigUtils.getApiUrl('').replace(/\/$/, '') : 
                'https://curam-ai-agent-mcp-production.up.railway.app';
                
            const response = await fetch(`${apiBaseUrl}/api/send-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    to: emailTo,
                    subject: emailSubject,
                    message: emailMessage,
                    pdf_base64: pdfBase64
                })
            });

            // Handle different response types
            let result;
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                result = await response.json();
            } else {
                // Handle HTML error responses (like 413 errors)
                const textResponse = await response.text();
                console.error('🔧 MCP: Received HTML response instead of JSON:', textResponse.substring(0, 200));
                
                if (response.status === 413) {
                    throw new Error('PDF attachment too large for email service');
                } else {
                    throw new Error(`Server error: ${response.status} ${response.statusText}`);
                }
            }

            if (response.ok && result.status === 'sent') {
                // Success!
                console.log('🔧 MCP: Email sent successfully via MCP email service');
                
                // Close modal
                this.closeEmailModal();
                
                // Show success message
                this.showNotification(
                    `✅ Email sent successfully to ${emailTo}! The recipient received an optimized MCP session report.`,
                    'success',
                    5000
                );
                
            } else {
                // API returned error
                throw new Error(result.error || result.message || 'Email sending failed');
            }

        } catch (error) {
            console.error('Email sending error:', error);
            console.log(`🔧 MCP: Email sending failed: ${error.message}`);
            
            // Handle specific error types
            if (error.message.includes('PDF attachment too large') || error.message.includes('413')) {
                this.showNotification(
                    `📧 PDF too large for email! 
                    
The generated images make the PDF too big for email delivery.

✅ Alternative options:
1. Use "Export PDF" to download the full report with images
2. Try email again (this sends a summary without embedded images)
3. Share the PDF file manually after download`,
                    'warning',
                    8000
                );
            } else {
                // Other errors
                let errorMessage = 'Failed to send email. ';
                if (error.message.includes('network') || error.message.includes('fetch')) {
                    errorMessage += 'Network connection issue. Please check your internet connection.';
                } else if (error.message.includes('MAILCHANNELS_API_KEY')) {
                    errorMessage += 'Email service configuration issue. Please contact support.';
                } else {
                    errorMessage += `Error: ${error.message}`;
                }
                
                this.showNotification(
                    `❌ ${errorMessage}

📄 Backup option: Click "Export PDF" to download the full report with images, then attach it to your own email manually.`,
                    'error',
                    7000
                );
            }
            
        } finally {
            sendBtn.textContent = originalText;
            sendBtn.disabled = false;
        }
    }

    /**
     * Generate PDF for email attachment - HYBRID VERSION WITH COMPRESSED IMAGES
     * @param {jsPDF} pdf - PDF instance
     */
    static async generatePDFForEmail(pdf) {
        if (!window.mcpSession) return;

        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        let yPosition = 20;
        
        // Set default font to avoid encoding issues
        pdf.setFont('helvetica');
        
        // Header
        pdf.setFontSize(20);
        pdf.setTextColor(0, 115, 170);
        pdf.text('Curam AI MCP Session Report', pageWidth / 2, yPosition, { align: 'center' });
        
        yPosition += 10;
        pdf.setFontSize(12);
        pdf.setTextColor(102, 102, 102);
        pdf.text('Model Context Protocol - Intelligent Tool Orchestration', pageWidth / 2, yPosition, { align: 'center' });
        
        yPosition += 8;
        pdf.text('Generated on ' + new Date().toLocaleString(), pageWidth / 2, yPosition, { align: 'center' });
        
        yPosition += 20;
        
        // Session Summary Box
        pdf.setDrawColor(0, 115, 170);
        pdf.setFillColor(240, 248, 255);
        pdf.rect(20, yPosition - 5, pageWidth - 40, 25, 'FD');
        
        pdf.setFontSize(14);
        pdf.setTextColor(0, 115, 170);
        pdf.text('Session Summary', 25, yPosition + 5);
        
        pdf.setFontSize(10);
        pdf.setTextColor(51, 51, 51);
        pdf.text('Total Questions: ' + window.mcpSession.conversationHistory.length, 25, yPosition + 12);
        pdf.text('Images Generated: ' + window.mcpSession.imageGallery.length, 25, yPosition + 18);
        pdf.text('MCP Features: Context Memory, Tool Chaining', pageWidth / 2, yPosition + 12);
        
        yPosition += 35;
        
        // Key Conversation Points (LIMITED for email size)
        if (window.mcpSession.conversationHistory.length > 0) {
            pdf.setFontSize(14);
            pdf.setTextColor(0, 115, 170);
            pdf.text('Key Conversation Points', 20, yPosition);
            yPosition += 10;
            
            // Show first 3 conversations for email to keep size manageable
            const maxConversations = Math.min(3, window.mcpSession.conversationHistory.length);
            for (let i = 0; i < maxConversations; i++) {
                const entry = window.mcpSession.conversationHistory[i];
                
                // Check if we need a new page
                if (yPosition > pageHeight - 40) {
                    pdf.addPage();
                    yPosition = 20;
                }
                
                // Question - Clean text and avoid special characters
                pdf.setFontSize(10);
                pdf.setTextColor(0, 115, 170);
                const cleanQuestion = this.cleanTextForPDF(entry.question);
                pdf.text('Q' + (i + 1) + ': ' + cleanQuestion, 20, yPosition);
                yPosition += 6;
                
                // Response (shortened for email) - Clean text
                pdf.setFontSize(8);
                pdf.setTextColor(51, 51, 51);
                const cleanResponse = this.cleanTextForPDF(entry.response.substring(0, 100)) + '...';
                const splitText = pdf.splitTextToSize(cleanResponse, pageWidth - 40);
                pdf.text(splitText, 25, yPosition);
                yPosition += splitText.length * 3 + 8;
            }
            
            if (window.mcpSession.conversationHistory.length > 3) {
                pdf.setFontSize(9);
                pdf.setTextColor(102, 102, 102);
                const moreText = '... and ' + (window.mcpSession.conversationHistory.length - 3) + ' more questions (full report available via Export PDF)';
                pdf.text(moreText, 20, yPosition);
                yPosition += 15;
            }
        }

        // Include COMPRESSED Images for email (like legacy version)
        if (window.mcpSession.imageGallery.length > 0) {
            // Add new page for images if needed
            if (yPosition > pageHeight - 80) {
                pdf.addPage();
                yPosition = 20;
            }
            
            pdf.setFontSize(14);
            pdf.setTextColor(0, 115, 170);
            pdf.text('Generated Images', 20, yPosition);
            yPosition += 15;
            
            // Include first 2-3 images with smaller size to match legacy behavior
            const maxImages = Math.min(3, window.mcpSession.imageGallery.length);
            for (let i = 0; i < maxImages; i++) {
                const image = window.mcpSession.imageGallery[i];
                
                // Check if we need a new page (need space for image + text)
                if (yPosition > pageHeight - 70) {
                    pdf.addPage();
                    yPosition = 20;
                }
                
                try {
                    // Add SMALLER image to keep email size down (like legacy)
                    const imgData = 'data:image/png;base64,' + image.imageBase64;
                    
                    // Use smaller dimensions for email (40x30 instead of 60x45)
                    const imgWidth = 40;  
                    const imgHeight = 30; 
                    pdf.addImage(imgData, 'PNG', 20, yPosition, imgWidth, imgHeight);
                    
                    // Image info next to the image
                    pdf.setFontSize(10);
                    pdf.setTextColor(51, 51, 51);
                    pdf.text('Image ' + (i + 1), 65, yPosition + 8);
                    
                    pdf.setFontSize(8);
                    pdf.setTextColor(102, 102, 102);
                    pdf.text('Prompt:', 65, yPosition + 15);
                    
                    // Wrap prompt text properly
                    const cleanPrompt = this.cleanTextForPDF(image.prompt);
                    const promptText = cleanPrompt.length > 60 ? 
                        cleanPrompt.substring(0, 60) + '...' : cleanPrompt;
                    const splitPrompt = pdf.splitTextToSize(promptText, pageWidth - 90);
                    pdf.text(splitPrompt, 65, yPosition + 20);
                    
                    pdf.setFontSize(7);
                    pdf.setTextColor(102, 102, 102);
                    pdf.text('Style: ' + image.style, 65, yPosition + 27);
                    
                    if (image.isAutoGenerated) {
                        pdf.setTextColor(70, 180, 80);
                        pdf.text('MCP Auto-Generated', 65, yPosition + 32);
                    }
                    
                    yPosition += 45;
                    
                    console.log('✅ Added compressed image ' + (i + 1) + ' to email PDF');
                    
                } catch (error) {
                    console.warn('Could not add image ' + (i + 1) + ' to email PDF:', error);
                    
                    // Add placeholder for failed image
                    pdf.setFontSize(10);
                    pdf.setTextColor(200, 200, 200);
                    pdf.rect(20, yPosition, 40, 30);
                    pdf.text('Image not', 25, yPosition + 15);
                    pdf.text('available', 25, yPosition + 20);
                    
                    // Still add the image info
                    pdf.setFontSize(10);
                    pdf.setTextColor(51, 51, 51);
                    pdf.text('Image ' + (i + 1) + ' (Error loading)', 65, yPosition + 15);
                    
                    yPosition += 45;
                }
            }
            
            // Add note if there are more images
            if (window.mcpSession.imageGallery.length > maxImages) {
                pdf.setFontSize(9);
                pdf.setTextColor(102, 102, 102);
                pdf.text('... and ' + (window.mcpSession.imageGallery.length - maxImages) + ' more images in full export', 20, yPosition);
            }
        }
    }

    /**
     * Clean text for PDF generation to avoid encoding issues
     * @param {string} text - Text to clean
     * @returns {string} - Cleaned text safe for PDF
     */
    static cleanTextForPDF(text) {
        if (!text || typeof text !== 'string') return '';
        
        return text
            // Remove or replace problematic Unicode characters
            .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII characters
            .replace(/[""]/g, '"') // Replace smart quotes
            .replace(/['']/g, "'") // Replace smart apostrophes
            .replace(/[–—]/g, '-') // Replace em/en dashes
            .replace(/…/g, '...') // Replace ellipsis
            .replace(/\u00A0/g, ' ') // Replace non-breaking space
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim();
    }

    /**
     * Render status badge
     * @param {HTMLElement} container - Container element
     * @param {string} status - Status ('online', 'offline', 'connecting')
     * @param {string} text - Status text
     */
    static renderStatusBadge(container, status, text) {
        if (!container) return;
        
        const statusColors = {
            online: '#46b450',
            offline: '#dc3232',
            connecting: '#ff9800'
        };
        
        const badgeHTML = `
            <span class="status-badge" style="background: ${statusColors[status] || statusColors.offline}">
                ${text}
            </span>
        `;
        
        container.innerHTML = badgeHTML;
    }

    /**
     * Render input group with label and validation
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Input configuration
     */
    static renderInputGroup(container, config) {
        if (!container) return;
        
        const inputType = config.type || 'text';
        const inputElement = inputType === 'textarea' ? 'textarea' : 'input';
        const typeAttr = inputType !== 'textarea' ? `type="${inputType}"` : '';
        const rows = config.rows ? `rows="${config.rows}"` : '';
        
        const inputHTML = `
            <div class="input-group">
                <label for="${config.id}">${config.label}:</label>
                <${inputElement} 
                    id="${config.id}" 
                    ${typeAttr}
                    ${rows}
                    placeholder="${config.placeholder || ''}"
                    ${config.required ? 'required' : ''}
                    ${config.disabled ? 'disabled' : ''}
                    style="${config.style || ''}"
                ></${inputElement}>
                ${config.help ? `<small class="input-help">${config.help}</small>` : ''}
            </div>
        `;
        
        container.innerHTML = inputHTML;
    }

    /**
     * Render button with MCP styling
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Button configuration
     */
    static renderButton(container, config) {
        if (!container) return;
        
        const buttonClass = `btn ${config.variant || ''}`;
        const buttonHTML = `
            <button 
                class="${buttonClass}" 
                id="${config.id || ''}"
                onclick="${config.onClick || ''}"
                ${config.disabled ? 'disabled' : ''}
                style="${config.style || ''}"
            >
                ${config.text}
            </button>
        `;
        
        container.innerHTML = buttonHTML;
    }

    /**
     * Render checkbox with label
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Checkbox configuration
     */
    static renderCheckbox(container, config) {
        if (!container) return;
        
        const checkboxHTML = `
            <div class="input-group">
                <label class="checkbox-label">
                    <input 
                        type="checkbox" 
                        id="${config.id}"
                        ${config.checked ? 'checked' : ''}
                        ${config.disabled ? 'disabled' : ''}
                    >
                    <span>${config.label}</span>
                </label>
                ${config.help ? `<small class="checkbox-help">${config.help}</small>` : ''}
            </div>
        `;
        
        container.innerHTML = checkboxHTML;
    }

    /**
     * Render select dropdown
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Select configuration
     */
    static renderSelect(container, config) {
        if (!container) return;
        
        const selectHTML = `
            <div class="input-group">
                <label for="${config.id}">${config.label}:</label>
                <select id="${config.id}" ${config.disabled ? 'disabled' : ''}>
                    ${config.options.map(option => `
                        <option value="${option.value}" ${option.selected ? 'selected' : ''}>
                            ${option.label}
                        </option>
                    `).join('')}
                </select>
                ${config.help ? `<small class="input-help">${config.help}</small>` : ''}
            </div>
        `;
        
        container.innerHTML = selectHTML;
    }

    /**
     * Render model comparison results
     * @param {HTMLElement} container - Container element
     * @param {Object} results - Comparison results
     */
    static renderModelComparison(container, results) {
        if (!container || !results) return;
        
        const comparisonHTML = `
            <div class="model-comparison-results">
                ${Object.entries(results).map(([modelName, result]) => `
                    <div class="model-result">
                        <h3>
                            ${result.displayName || modelName}
                            <span class="model-badge">${result.badge || 'AI Model'}</span>
                        </h3>
                        <div class="model-response">
                            ${result.formattedResponse || result.response || 'No response available'}
                        </div>
                        ${result.metadata ? `
                            <div class="model-metadata">
                                <small>
                                    ${Object.entries(result.metadata).map(([key, value]) => 
                                        `<strong>${key}:</strong> ${value}`
                                    ).join(' • ')}
                                </small>
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = comparisonHTML;
    }

    /**
     * Get session duration for PDF
     * @returns {string} - Formatted session duration
     */
    static getSessionDuration() {
        if (!window.mcpSession || window.mcpSession.conversationHistory.length === 0) {
            return 'No activity';
        }
        
        const firstTime = window.mcpSession.conversationHistory[0].timestamp;
        const lastTime = window.mcpSession.conversationHistory[window.mcpSession.conversationHistory.length - 1].timestamp;
        
        return `${firstTime} - ${lastTime}`;
    }

    /**
     * Format response text for PDF display - FIXED ENCODING
     * @param {string} response - AI response text
     * @returns {string} - Cleaned response for PDF
     */
    static formatResponseForPDF(response) {
        if (!response || typeof response !== 'string') return '';
        
        // Clean up response for PDF - remove excessive formatting but preserve more content
        return this.cleanTextForPDF(response)
            .replace(/\*\*/g, '') // Remove bold markers
            .replace(/\*/g, '') // Remove bullet markers
            .replace(/\n/g, ' ') // Replace newlines with spaces
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim()
            .substring(0, 500) + (response.length > 500 ? '...' : ''); // Keep more content - increased from 300 to 500
    }

    /**
     * Generate PDF content as HTML (fallback method)
     */
    static async generatePDFContent() {
        const timestamp = new Date().toLocaleString();
        const sessionDuration = this.getSessionDuration();
        
        let htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>MCP Session Report</title>
                <style>
                    body { 
                        font-family: 'Arial', sans-serif; 
                        line-height: 1.6; 
                        color: #333; 
                        max-width: 800px; 
                        margin: 0 auto; 
                        padding: 20px;
                    }
                    .header { 
                        text-align: center; 
                        border-bottom: 3px solid #0073aa; 
                        padding-bottom: 20px; 
                        margin-bottom: 30px;
                    }
                    .header h1 { 
                        color: #0073aa; 
                        margin: 0 0 10px 0; 
                        font-size: 2.2em;
                    }
                    .session-info {
                        background: #f0f8ff;
                        border: 1px solid #0073aa;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 30px;
                    }
                    .conversation-item {
                        background: #f9f9f9;
                        border: 1px solid #e0e0e0;
                        border-left: 4px solid #0073aa;
                        padding: 15px;
                        margin-bottom: 15px;
                        border-radius: 6px;
                    }
                    .image-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin: 20px 0;
                    }
                    .image-item {
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 15px;
                        text-align: center;
                    }
                    .image-item img {
                        max-width: 100%;
                        height: 200px;
                        object-fit: cover;
                        border-radius: 6px;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Curam AI MCP Session Report</h1>
                    <p><strong>Model Context Protocol</strong> - Intelligent Tool Orchestration</p>
                    <p>Generated on ${timestamp}</p>
                </div>

                <div class="session-info">
                    <h3>Session Summary</h3>
                    <p><strong>Total Questions:</strong> ${window.mcpSession.conversationHistory.length}</p>
                    <p><strong>Images Generated:</strong> ${window.mcpSession.imageGallery.length}</p>
                    <p><strong>Session Duration:</strong> ${sessionDuration}</p>
                    <p><strong>MCP Features:</strong> Context Memory, Tool Chaining</p>
                </div>
        `;

        // Add conversation history
        if (window.mcpSession.conversationHistory.length > 0) {
            htmlContent += `<h2>Conversation History</h2>`;
            
            window.mcpSession.conversationHistory.forEach((entry, index) => {
                htmlContent += `
                    <div class="conversation-item">
                        <div><strong>Question ${index + 1}:</strong> ${entry.question}</div>
                        <div style="margin-top: 10px;"><strong>Response:</strong> ${this.formatResponseForPDF(entry.response)}</div>
                        <div style="margin-top: 10px; color: #666; font-size: 0.9em;">${entry.timestamp}</div>
                    </div>
                `;
            });
        }

        // Add images section
        if (window.mcpSession.imageGallery.length > 0) {
            htmlContent += `
                <h2>Generated Images</h2>
                <div class="image-grid">
            `;
            
            window.mcpSession.imageGallery.forEach((image, index) => {
                htmlContent += `
                    <div class="image-item">
                        <img src="data:image/png;base64,${image.imageBase64}" alt="Generated Image ${index + 1}" />
                        <div style="margin-top: 10px;">
                            <strong>Image ${index + 1}</strong><br>
                            <em>${image.prompt.substring(0, 60)}${image.prompt.length > 60 ? '...' : ''}</em><br>
                            <small>Style: ${image.style} • ${image.timestamp}</small>
                            ${image.isAutoGenerated ? '<br><small style="color: #46b450;">🤖 MCP Auto-Generated</small>' : ''}
                        </div>
                    </div>
                `;
            });
            
            htmlContent += `</div>`;
        }

        htmlContent += `
                <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #999;">
                    <p>Generated by Curam AI MCP Agent • Model Context Protocol Technology</p>
                </div>
            </body>
            </html>
        `;

        return htmlContent;
    }

    /**
     * Download PDF using print dialog (fallback)
     */
    static downloadPDF(htmlContent) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(htmlContent);
        printWindow.document.close();
        
        printWindow.onload = function() {
            setTimeout(function() {
                printWindow.print();
                printWindow.onafterprint = function() {
                    printWindow.close();
                };
            }, 500);
        };
    }
}

// Export for global use
if (typeof window !== 'undefined') {
    window.MCPUIComponents = MCPUIComponents;
}

// Also export for ES6 module usage
// export { MCPUIComponents };