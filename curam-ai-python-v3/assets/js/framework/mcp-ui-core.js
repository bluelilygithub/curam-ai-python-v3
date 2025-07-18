/**
 * framework/mcp-ui-core.js - Core UI Components and Utilities
 * 
 * Provides foundational UI components and utilities that can be used
 * across all MCP applications for consistent user interface elements.
 */

class MCPUICore {
    
    /**
     * Render input group with label and validation
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Input configuration
     */
    static renderInputGroup(container, config) {
        if (!container) return;
        
        const defaultConfig = {
            type: 'text',
            required: false,
            disabled: false,
            placeholder: '',
            help: null,
            style: '',
            value: ''
        };
        
        const inputConfig = { ...defaultConfig, ...config };
        const inputType = inputConfig.type;
        const inputElement = inputType === 'textarea' ? 'textarea' : 'input';
        const typeAttr = inputType !== 'textarea' ? `type="${inputType}"` : '';
        const rows = inputConfig.rows ? `rows="${inputConfig.rows}"` : '';
        const value = inputType === 'textarea' ? inputConfig.value : '';
        const valueAttr = inputType !== 'textarea' && inputConfig.value ? `value="${inputConfig.value}"` : '';
        
        const inputHTML = `
            <div class="input-group">
                <label for="${inputConfig.id}">${inputConfig.label}:</label>
                <${inputElement} 
                    id="${inputConfig.id}" 
                    ${typeAttr}
                    ${valueAttr}
                    ${rows}
                    placeholder="${inputConfig.placeholder}"
                    ${inputConfig.required ? 'required' : ''}
                    ${inputConfig.disabled ? 'disabled' : ''}
                    ${inputConfig.maxlength ? `maxlength="${inputConfig.maxlength}"` : ''}
                    style="${inputConfig.style}"
                >${value}</${inputElement}>
                ${inputConfig.help ? `<small class="input-help">${inputConfig.help}</small>` : ''}
            </div>
        `;
        
        container.innerHTML = inputHTML;
        
        // Return the input element for further manipulation
        return document.getElementById(inputConfig.id);
    }

    /**
     * Render button with MCP styling and functionality
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Button configuration
     */
    static renderButton(container, config) {
        if (!container) return;
        
        const defaultConfig = {
            variant: '',
            disabled: false,
            style: '',
            onClick: '',
            title: ''
        };
        
        const buttonConfig = { ...defaultConfig, ...config };
        const buttonClass = `btn ${buttonConfig.variant}`.trim();
        
        const buttonHTML = `
            <button 
                class="${buttonClass}" 
                id="${buttonConfig.id || ''}"
                onclick="${buttonConfig.onClick}"
                ${buttonConfig.disabled ? 'disabled' : ''}
                ${buttonConfig.title ? `title="${buttonConfig.title}"` : ''}
                style="${buttonConfig.style}"
            >
                ${buttonConfig.text}
            </button>
        `;
        
        container.innerHTML = buttonHTML;
        
        // Return the button element for further manipulation
        return document.getElementById(buttonConfig.id);
    }

    /**
     * Render checkbox with label and styling
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Checkbox configuration
     */
    static renderCheckbox(container, config) {
        if (!container) return;
        
        const defaultConfig = {
            checked: false,
            disabled: false,
            help: null
        };
        
        const checkboxConfig = { ...defaultConfig, ...config };
        
        const checkboxHTML = `
            <div class="input-group">
                <label class="checkbox-label">
                    <input 
                        type="checkbox" 
                        id="${checkboxConfig.id}"
                        ${checkboxConfig.checked ? 'checked' : ''}
                        ${checkboxConfig.disabled ? 'disabled' : ''}
                        ${checkboxConfig.value ? `value="${checkboxConfig.value}"` : ''}
                    >
                    <span>${checkboxConfig.label}</span>
                </label>
                ${checkboxConfig.help ? `<small class="checkbox-help">${checkboxConfig.help}</small>` : ''}
            </div>
        `;
        
        container.innerHTML = checkboxHTML;
        
        // Return the checkbox element for further manipulation
        return document.getElementById(checkboxConfig.id);
    }

    /**
     * Render select dropdown with options
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Select configuration
     */
    static renderSelect(container, config) {
        if (!container) return;
        
        const defaultConfig = {
            disabled: false,
            help: null,
            options: []
        };
        
        const selectConfig = { ...defaultConfig, ...config };
        
        const selectHTML = `
            <div class="input-group">
                <label for="${selectConfig.id}">${selectConfig.label}:</label>
                <select id="${selectConfig.id}" ${selectConfig.disabled ? 'disabled' : ''}>
                    ${selectConfig.options.map(option => `
                        <option value="${option.value}" ${option.selected ? 'selected' : ''}>
                            ${option.label}
                        </option>
                    `).join('')}
                </select>
                ${selectConfig.help ? `<small class="input-help">${selectConfig.help}</small>` : ''}
            </div>
        `;
        
        container.innerHTML = selectHTML;
        
        // Return the select element for further manipulation
        return document.getElementById(selectConfig.id);
    }

    /**
     * Render loading spinner with customizable message
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Loading configuration
     */
    static renderLoading(container, config = {}) {
        if (!container) return;
        
        const defaultConfig = {
            message: 'Loading...',
            show: true,
            spinner: true,
            size: 'normal' // 'small', 'normal', 'large'
        };
        
        const loadingConfig = { ...defaultConfig, ...config };
        
        if (!loadingConfig.show) {
            container.style.display = 'none';
            return;
        }
        
        const sizeClass = loadingConfig.size !== 'normal' ? ` loading-${loadingConfig.size}` : '';
        
        const loadingHTML = `
            <div class="loading${sizeClass}">
                ${loadingConfig.spinner ? '<div class="spinner"></div>' : ''}
                <p>${loadingConfig.message}</p>
            </div>
        `;
        
        container.innerHTML = loadingHTML;
        container.style.display = 'block';
    }

    /**
     * Render error message with styling
     * @param {HTMLElement} container - Container element
     * @param {string} message - Error message
     * @param {string} details - Additional error details (optional)
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
     * Render success message with styling
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
     * Render warning message with styling
     * @param {HTMLElement} container - Container element
     * @param {string} message - Warning message
     */
    static renderWarning(container, message) {
        if (!container) return;
        
        const warningHTML = `
            <div class="warning">
                <strong>Warning:</strong> ${message}
            </div>
        `;
        
        container.innerHTML = warningHTML;
    }

    /**
     * Render info message with styling
     * @param {HTMLElement} container - Container element
     * @param {string} message - Info message
     */
    static renderInfo(container, message) {
        if (!container) return;
        
        const infoHTML = `
            <div class="info">
                <strong>Info:</strong> ${message}
            </div>
        `;
        
        container.innerHTML = infoHTML;
    }

    /**
     * Render status badge with dynamic styling
     * @param {HTMLElement} container - Container element
     * @param {string} status - Status type ('online', 'offline', 'connecting', 'processing')
     * @param {string} text - Status text
     * @param {Object} options - Additional options
     */
    static renderStatusBadge(container, status, text, options = {}) {
        if (!container) return;
        
        const statusColors = {
            online: '#46b450',
            offline: '#dc3232',
            connecting: '#ff9800',
            processing: '#0073aa',
            warning: '#ff9800',
            error: '#dc3232'
        };
        
        const defaultOptions = {
            animated: false,
            size: 'normal' // 'small', 'normal', 'large'
        };
        
        const config = { ...defaultOptions, ...options };
        const sizeClass = config.size !== 'normal' ? ` status-badge-${config.size}` : '';
        const animationClass = config.animated ? ' status-badge-animated' : '';
        
        const badgeHTML = `
            <span class="status-badge${sizeClass}${animationClass}" 
                  style="background: ${statusColors[status] || statusColors.offline}">
                ${text}
            </span>
        `;
        
        container.innerHTML = badgeHTML;
    }

    /**
     * Create and show notification/toast message
     * @param {string} message - Notification message
     * @param {string} type - Notification type ('success', 'error', 'warning', 'info')
     * @param {number} duration - Duration in milliseconds (0 = permanent)
     * @param {Object} options - Additional options
     * @returns {HTMLElement} - The notification element
     */
    static showNotification(message, type = 'info', duration = 5000, options = {}) {
        const defaultOptions = {
            position: 'top-right', // 'top-right', 'top-left', 'bottom-right', 'bottom-left', 'top-center'
            closable: true,
            maxWidth: '400px',
            zIndex: 10000
        };
        
        const config = { ...defaultOptions, ...options };
        
        // Remove existing notifications of the same type if specified
        if (config.replaceExisting) {
            const existingNotifications = document.querySelectorAll(`.mcp-notification.${type}`);
            existingNotifications.forEach(notification => notification.remove());
        }
        
        const notification = document.createElement('div');
        notification.className = `mcp-notification ${type}`;
        notification.style.cssText = this.getNotificationStyles(config, type);
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2em;">${this.getNotificationIcon(type)}</span>
                <span style="flex: 1;">${message}</span>
                ${config.closable ? `
                    <button onclick="this.parentElement.parentElement.remove()" 
                            style="background: none; border: none; color: white; font-size: 1.2em; cursor: pointer; padding: 0; margin-left: 10px;">&times;</button>
                ` : ''}
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
        
        return notification;
    }

    /**
     * Get notification styles based on position and type
     * @param {Object} config - Notification configuration
     * @param {string} type - Notification type
     * @returns {string} - CSS styles
     */
    static getNotificationStyles(config, type) {
        const baseStyles = `
            position: fixed;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: ${config.zIndex};
            max-width: ${config.maxWidth};
            font-family: 'Montserrat', sans-serif;
            font-size: 0.9em;
            line-height: 1.4;
        `;
        
        const positionStyles = {
            'top-right': 'top: 20px; right: 20px;',
            'top-left': 'top: 20px; left: 20px;',
            'bottom-right': 'bottom: 20px; right: 20px;',
            'bottom-left': 'bottom: 20px; left: 20px;',
            'top-center': 'top: 20px; left: 50%; transform: translateX(-50%);'
        };
        
        return baseStyles + positionStyles[config.position];
    }

    /**
     * Get notification icon for type
     * @param {string} type - Notification type
     * @returns {string} - Icon emoji
     */
    static getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    /**
     * Get notification color for type
     * @param {string} type - Notification type
     * @returns {string} - Color hex code
     */
    static getNotificationColor(type) {
        const colors = {
            success: '#46b450',
            error: '#dc3232',
            warning: '#ff9800',
            info: '#0073aa'
        };
        return colors[type] || colors.info;
    }

    /**
     * Create modal dialog with customizable content
     * @param {Object} config - Modal configuration
     * @returns {HTMLElement} - Modal element
     */
    static createModal(config) {
        const defaultConfig = {
            id: 'mcpModal' + Date.now(),
            title: 'Modal',
            content: '',
            closable: true,
            size: 'medium', // 'small', 'medium', 'large', 'fullscreen'
            backdrop: true,
            keyboard: true
        };
        
        const modalConfig = { ...defaultConfig, ...config };
        
        // Remove existing modal with same ID
        const existingModal = document.getElementById(modalConfig.id);
        if (existingModal) {
            existingModal.remove();
        }
        
        const modal = document.createElement('div');
        modal.id = modalConfig.id;
        modal.className = `mcp-modal ${modalConfig.size}`;
        modal.style.cssText = `
            display: flex;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 10000;
            align-items: center;
            justify-content: center;
        `;
        
        const sizeStyles = {
            small: 'max-width: 400px; width: 90%;',
            medium: 'max-width: 600px; width: 90%;',
            large: 'max-width: 900px; width: 95%;',
            fullscreen: 'width: 95%; height: 90%;'
        };
        
        modal.innerHTML = `
            <div class="mcp-modal-content" style="
                background: white;
                border-radius: 8px;
                ${sizeStyles[modalConfig.size]}
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                position: relative;
            ">
                ${modalConfig.closable ? `
                    <button class="mcp-modal-close" onclick="document.getElementById('${modalConfig.id}').remove()" style="
                        position: absolute;
                        top: 15px;
                        right: 20px;
                        background: none;
                        border: none;
                        font-size: 1.5em;
                        cursor: pointer;
                        color: #999;
                        padding: 5px;
                        z-index: 1;
                    ">&times;</button>
                ` : ''}
                
                <div class="mcp-modal-header" style="
                    padding: 25px 25px 15px 25px;
                    border-bottom: 1px solid #e0e0e0;
                ">
                    <h3 style="margin: 0; color: #0073aa; font-size: 1.3em;">${modalConfig.title}</h3>
                </div>
                
                <div class="mcp-modal-body" style="padding: 20px 25px;">
                    ${modalConfig.content}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Set up event handlers
        if (modalConfig.backdrop) {
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            };
        }
        
        if (modalConfig.keyboard) {
            const escapeHandler = (e) => {
                if (e.key === 'Escape') {
                    modal.remove();
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
        }
        
        return modal;
    }

    /**
     * Create progress bar component
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Progress configuration
     */
    static renderProgressBar(container, config) {
        if (!container) return;
        
        const defaultConfig = {
            value: 0,
            max: 100,
            label: '',
            showPercentage: true,
            animated: false,
            color: '#0073aa'
        };
        
        const progressConfig = { ...defaultConfig, ...config };
        const percentage = Math.round((progressConfig.value / progressConfig.max) * 100);
        const animationClass = progressConfig.animated ? ' progress-animated' : '';
        
        const progressHTML = `
            <div class="progress-container">
                ${progressConfig.label ? `<label class="progress-label">${progressConfig.label}</label>` : ''}
                <div class="progress-bar${animationClass}" style="
                    width: 100%;
                    height: 20px;
                    background: #f0f0f0;
                    border-radius: 10px;
                    overflow: hidden;
                    position: relative;
                ">
                    <div class="progress-fill" style="
                        width: ${percentage}%;
                        height: 100%;
                        background: ${progressConfig.color};
                        transition: width 0.3s ease;
                        position: relative;
                    "></div>
                    ${progressConfig.showPercentage ? `
                        <span class="progress-text" style="
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            font-size: 0.8em;
                            font-weight: 600;
                            color: ${percentage > 50 ? 'white' : '#333'};
                        ">${percentage}%</span>
                    ` : ''}
                </div>
            </div>
        `;
        
        container.innerHTML = progressHTML;
        
        // Return update function
        return {
            update: (newValue) => {
                const fillElement = container.querySelector('.progress-fill');
                const textElement = container.querySelector('.progress-text');
                const newPercentage = Math.round((newValue / progressConfig.max) * 100);
                
                if (fillElement) {
                    fillElement.style.width = `${newPercentage}%`;
                }
                if (textElement) {
                    textElement.textContent = `${newPercentage}%`;
                    textElement.style.color = newPercentage > 50 ? 'white' : '#333';
                }
            }
        };
    }

    /**
     * Create tabs component
     * @param {HTMLElement} container - Container element
     * @param {Object} config - Tabs configuration
     */
    static renderTabs(container, config) {
        if (!container) return;
        
        const defaultConfig = {
            tabs: [],
            activeTab: 0,
            onChange: null
        };
        
        const tabsConfig = { ...defaultConfig, ...config };
        
        const tabsHTML = `
            <div class="mcp-tabs">
                <div class="tab-headers" style="
                    display: flex;
                    border-bottom: 2px solid #e0e0e0;
                    margin-bottom: 20px;
                ">
                    ${tabsConfig.tabs.map((tab, index) => `
                        <button class="tab-header ${index === tabsConfig.activeTab ? 'active' : ''}" 
                                data-tab-index="${index}"
                                style="
                                    padding: 10px 20px;
                                    border: none;
                                    background: ${index === tabsConfig.activeTab ? '#0073aa' : 'transparent'};
                                    color: ${index === tabsConfig.activeTab ? 'white' : '#666'};
                                    cursor: pointer;
                                    border-radius: 4px 4px 0 0;
                                    font-family: 'Montserrat', sans-serif;
                                    font-weight: 600;
                                    transition: all 0.3s ease;
                                ">
                            ${tab.title}
                        </button>
                    `).join('')}
                </div>
                <div class="tab-content">
                    ${tabsConfig.tabs[tabsConfig.activeTab]?.content || ''}
                </div>
            </div>
        `;
        
        container.innerHTML = tabsHTML;
        
        // Set up tab switching
        const tabHeaders = container.querySelectorAll('.tab-header');
        const tabContent = container.querySelector('.tab-content');
        
        tabHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const tabIndex = parseInt(header.dataset.tabIndex);
                
                // Update active tab styling
                tabHeaders.forEach(h => {
                    h.classList.remove('active');
                    h.style.background = 'transparent';
                    h.style.color = '#666';
                });
                
                header.classList.add('active');
                header.style.background = '#0073aa';
                header.style.color = 'white';
                
                // Update content
                if (tabContent && tabsConfig.tabs[tabIndex]) {
                    tabContent.innerHTML = tabsConfig.tabs[tabIndex].content;
                }
                
                // Call onChange callback
                if (tabsConfig.onChange) {
                    tabsConfig.onChange(tabIndex, tabsConfig.tabs[tabIndex]);
                }
            });
        });
        
        return {
            switchTo: (tabIndex) => {
                const header = container.querySelector(`[data-tab-index="${tabIndex}"]`);
                if (header) {
                    header.click();
                }
            }
        };
    }

    /**
     * Utility method to safely get element by ID
     * @param {string} id - Element ID
     * @returns {HTMLElement|null} - Element or null
     */
    static getElementById(id) {
        return document.getElementById(id);
    }

    /**
     * Utility method to safely query selector
     * @param {string} selector - CSS selector
     * @param {HTMLElement} parent - Parent element (optional)
     * @returns {HTMLElement|null} - Element or null
     */
    static querySelector(selector, parent = document) {
        return parent.querySelector(selector);
    }

    /**
     * Utility method to query all matching selectors
     * @param {string} selector - CSS selector
     * @param {HTMLElement} parent - Parent element (optional)
     * @returns {NodeList} - List of matching elements
     */
    static querySelectorAll(selector, parent = document) {
        return parent.querySelectorAll(selector);
    }

    /**
     * Add CSS class to element safely
     * @param {HTMLElement|string} element - Element or element ID
     * @param {string} className - Class name to add
     */
    static addClass(element, className) {
        const el = typeof element === 'string' ? this.getElementById(element) : element;
        if (el && el.classList) {
            el.classList.add(className);
        }
    }

    /**
     * Remove CSS class from element safely
     * @param {HTMLElement|string} element - Element or element ID
     * @param {string} className - Class name to remove
     */
    static removeClass(element, className) {
        const el = typeof element === 'string' ? this.getElementById(element) : element;
        if (el && el.classList) {
            el.classList.remove(className);
        }
    }

    /**
     * Toggle CSS class on element safely
     * @param {HTMLElement|string} element - Element or element ID
     * @param {string} className - Class name to toggle
     * @returns {boolean} - Whether class is now present
     */
    static toggleClass(element, className) {
        const el = typeof element === 'string' ? this.getElementById(element) : element;
        if (el && el.classList) {
            return el.classList.toggle(className);
        }
        return false;
    }

    /**
     * Show element by setting display style
     * @param {HTMLElement|string} element - Element or element ID
     * @param {string} display - Display style (default: 'block')
     */
    static show(element, display = 'block') {
        const el = typeof element === 'string' ? this.getElementById(element) : element;
        if (el) {
            el.style.display = display;
        }
    }

    /**
     * Hide element by setting display to none
     * @param {HTMLElement|string} element - Element or element ID
     */
    static hide(element) {
        const el = typeof element === 'string' ? this.getElementById(element) : element;
        if (el) {
            el.style.display = 'none';
        }
    }

    /**
     * Set element visibility
     * @param {HTMLElement|string} element - Element or element ID
     * @param {boolean} visible - Whether element should be visible
     * @param {string} display - Display style when visible
     */
    static setVisibility(element, visible, display = 'block') {
        if (visible) {
            this.show(element, display);
        } else {
            this.hide(element);
        }
    }

    /**
     * Validate form elements
     * @param {HTMLElement} form - Form element
     * @returns {Object} - Validation result
     */
    static validateForm(form) {
        if (!form) return { valid: false, errors: ['Form not found'] };
        
        const errors = [];
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                errors.push(`${field.name || field.id || 'Field'} is required`);
            }
        });
        
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value.trim() && !this.isValidEmail(field.value)) {
                errors.push(`${field.name || field.id || 'Email field'} must be a valid email address`);
            }
        });
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Check if email address is valid
     * @param {string} email - Email to validate
     * @returns {boolean} - Whether email is valid
     */
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Debounce function calls
     * @param {Function} func - Function to debounce
     * @param {number} delay - Delay in milliseconds
     * @returns {Function} - Debounced function
     */
    static debounce(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    /**
     * Throttle function calls
     * @param {Function} func - Function to throttle
     * @param {number} delay - Delay in milliseconds
     * @returns {Function} - Throttled function
     */
    static throttle(func, delay) {
        let lastCall = 0;
        return function (...args) {
            const now = Date.now();
            if (now - lastCall >= delay) {
                lastCall = now;
                return func.apply(this, args);
            }
        };
    }

    /**
     * Format file size for display
     * @param {number} bytes - File size in bytes
     * @returns {string} - Formatted file size
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Copy text to clipboard
     * @param {string} text - Text to copy
     * @returns {Promise<boolean>} - Success status
     */
    static async copyToClipboard(text) {
        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                return true;
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                const result = document.execCommand('copy');
                document.body.removeChild(textArea);
                return result;
            }
        } catch (error) {
            console.error('Failed to copy text:', error);
            return false;
        }
    }
}

// Export for global use
if (typeof window !== 'undefined') {
    window.MCPUICore = MCPUICore;
}

// Also export for ES6 module usage
// export { MCPUICore };