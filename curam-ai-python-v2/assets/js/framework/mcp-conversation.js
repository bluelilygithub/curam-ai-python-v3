/**
 * framework/mcp-conversation.js - Conversation and Image Management
 * 
 * Handles conversation display, image gallery management, and related
 * user interactions for MCP applications.
 */

class MCPConversation {
    constructor() {
        this.conversations = new Map();
        this.currentConversationId = null;
        this.storageKey = 'mcp_conversations';
        this.loadFromStorage();
    }

    /**
     * Start a new conversation
     */
    startConversation(topic = 'New Conversation') {
        const conversationId = this.generateId();
        const conversation = {
            id: conversationId,
            topic: topic,
            messages: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            metadata: {
                appType: null,
                modelUsed: null,
                totalTokens: 0
            }
        };

        this.conversations.set(conversationId, conversation);
        this.currentConversationId = conversationId;
        this.saveToStorage();
        
        return conversationId;
    }

    /**
     * Add message to current conversation
     */
    addMessage(role, content, metadata = {}) {
        if (!this.currentConversationId) {
            this.startConversation();
        }

        const conversation = this.conversations.get(this.currentConversationId);
        if (!conversation) {
            throw new Error('No active conversation');
        }

        const message = {
            id: this.generateId(),
            role: role,
            content: content,
            timestamp: new Date().toISOString(),
            metadata: {
                tokens: metadata.tokens || 0,
                model: metadata.model || null,
                processingTime: metadata.processingTime || null,
                ...metadata
            }
        };

        conversation.messages.push(message);
        conversation.updatedAt = new Date().toISOString();
        conversation.metadata.totalTokens += message.metadata.tokens;

        this.saveToStorage();
        return message;
    }

    /**
     * Get current conversation
     */
    getCurrentConversation() {
        if (!this.currentConversationId) {
            return null;
        }
        return this.conversations.get(this.currentConversationId);
    }

    /**
     * Get conversation by ID
     */
    getConversation(conversationId) {
        return this.conversations.get(conversationId);
    }

    /**
     * Get all conversations
     */
    getAllConversations() {
        return Array.from(this.conversations.values()).sort((a, b) => 
            new Date(b.updatedAt) - new Date(a.updatedAt)
        );
    }

    /**
     * Switch to a different conversation
     */
    switchConversation(conversationId) {
        if (this.conversations.has(conversationId)) {
            this.currentConversationId = conversationId;
            return true;
        }
        return false;
    }

    /**
     * Delete conversation
     */
    deleteConversation(conversationId) {
        if (this.conversations.has(conversationId)) {
            this.conversations.delete(conversationId);
            
            // If we deleted the current conversation, switch to the most recent one
            if (this.currentConversationId === conversationId) {
                const conversations = this.getAllConversations();
                this.currentConversationId = conversations.length > 0 ? conversations[0].id : null;
            }
            
            this.saveToStorage();
            return true;
        }
        return false;
    }

    /**
     * Clear all conversations
     */
    clearAllConversations() {
        this.conversations.clear();
        this.currentConversationId = null;
        this.saveToStorage();
    }

    /**
     * Export conversation to various formats
     */
    exportConversation(conversationId, format = 'json') {
        const conversation = this.getConversation(conversationId);
        if (!conversation) {
            throw new Error('Conversation not found');
        }

        switch (format.toLowerCase()) {
            case 'json':
                return JSON.stringify(conversation, null, 2);
            
            case 'text':
                return this.formatConversationAsText(conversation);
            
            case 'markdown':
                return this.formatConversationAsMarkdown(conversation);
            
            case 'html':
                return this.formatConversationAsHTML(conversation);
            
            default:
                throw new Error(`Unsupported format: ${format}`);
        }
    }

    /**
     * Format conversation as plain text
     */
    formatConversationAsText(conversation) {
        let text = `Conversation: ${conversation.topic}\n`;
        text += `Created: ${new Date(conversation.createdAt).toLocaleString()}\n`;
        text += `Updated: ${new Date(conversation.updatedAt).toLocaleString()}\n`;
        text += `Messages: ${conversation.messages.length}\n\n`;
        text += '='.repeat(50) + '\n\n';

        conversation.messages.forEach((message, index) => {
            text += `${message.role.toUpperCase()} (${new Date(message.timestamp).toLocaleTimeString()}):\n`;
            text += `${message.content}\n\n`;
        });

        return text;
    }

    /**
     * Format conversation as markdown
     */
    formatConversationAsMarkdown(conversation) {
        let markdown = `# ${conversation.topic}\n\n`;
        markdown += `**Created:** ${new Date(conversation.createdAt).toLocaleString()}\n`;
        markdown += `**Updated:** ${new Date(conversation.updatedAt).toLocaleString()}\n`;
        markdown += `**Messages:** ${conversation.messages.length}\n\n`;
        markdown += '---\n\n';

        conversation.messages.forEach((message, index) => {
            const role = message.role === 'user' ? '👤 User' : '🤖 Assistant';
            markdown += `## ${role} - ${new Date(message.timestamp).toLocaleTimeString()}\n\n`;
            markdown += `${message.content}\n\n`;
        });

        return markdown;
    }

    /**
     * Format conversation as HTML
     */
    formatConversationAsHTML(conversation) {
        let html = `
        <div class="conversation-export">
            <h1>${conversation.topic}</h1>
            <div class="conversation-meta">
                <p><strong>Created:</strong> ${new Date(conversation.createdAt).toLocaleString()}</p>
                <p><strong>Updated:</strong> ${new Date(conversation.updatedAt).toLocaleString()}</p>
                <p><strong>Messages:</strong> ${conversation.messages.length}</p>
            </div>
            <hr>
        `;

        conversation.messages.forEach((message, index) => {
            const roleClass = message.role === 'user' ? 'user-message' : 'assistant-message';
            const roleIcon = message.role === 'user' ? '👤' : '🤖';
            
            html += `
            <div class="message ${roleClass}">
                <div class="message-header">
                    <span class="role-icon">${roleIcon}</span>
                    <span class="role-name">${message.role.toUpperCase()}</span>
                    <span class="timestamp">${new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
                <div class="message-content">
                    ${message.content.replace(/\n/g, '<br>')}
                </div>
            </div>
            `;
        });

        html += '</div>';
        return html;
    }

    /**
     * Search conversations
     */
    searchConversations(query) {
        const results = [];
        const searchTerm = query.toLowerCase();

        this.conversations.forEach((conversation) => {
            let match = false;
            let matchContext = '';

            // Search in topic
            if (conversation.topic.toLowerCase().includes(searchTerm)) {
                match = true;
                matchContext = `Topic: ${conversation.topic}`;
            }

            // Search in messages
            conversation.messages.forEach((message) => {
                if (message.content.toLowerCase().includes(searchTerm)) {
                    match = true;
                    if (!matchContext) {
                        matchContext = `Message: ${message.content.substring(0, 100)}...`;
                    }
                }
            });

            if (match) {
                results.push({
                    conversation,
                    matchContext
                });
            }
        });

        return results;
    }

    /**
     * Get conversation statistics
     */
    getConversationStats(conversationId = null) {
        const conversations = conversationId ? 
            [this.getConversation(conversationId)] : 
            this.getAllConversations();

        const stats = {
            totalConversations: conversations.length,
            totalMessages: 0,
            totalTokens: 0,
            averageMessagesPerConversation: 0,
            averageTokensPerMessage: 0,
            mostActiveDay: null,
            messageTypes: { user: 0, assistant: 0 }
        };

        const dayCounts = {};

        conversations.forEach(conversation => {
            if (!conversation) return;
            
            stats.totalMessages += conversation.messages.length;
            stats.totalTokens += conversation.metadata.totalTokens || 0;

            conversation.messages.forEach(message => {
                stats.messageTypes[message.role] = (stats.messageTypes[message.role] || 0) + 1;
                
                const day = new Date(message.timestamp).toDateString();
                dayCounts[day] = (dayCounts[day] || 0) + 1;
            });
        });

        if (stats.totalConversations > 0) {
            stats.averageMessagesPerConversation = stats.totalMessages / stats.totalConversations;
        }

        if (stats.totalMessages > 0) {
            stats.averageTokensPerMessage = stats.totalTokens / stats.totalMessages;
        }

        // Find most active day
        let maxCount = 0;
        Object.entries(dayCounts).forEach(([day, count]) => {
            if (count > maxCount) {
                maxCount = count;
                stats.mostActiveDay = day;
            }
        });

        return stats;
    }

    /**
     * Load conversations from localStorage
     */
    loadFromStorage() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                this.conversations = new Map(data.conversations || []);
                this.currentConversationId = data.currentConversationId || null;
            }
        } catch (error) {
            console.warn('Failed to load conversations from storage:', error);
        }
    }

    /**
     * Save conversations to localStorage
     */
    saveToStorage() {
        try {
            const data = {
                conversations: Array.from(this.conversations.entries()),
                currentConversationId: this.currentConversationId
            };
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (error) {
            console.warn('Failed to save conversations to storage:', error);
        }
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * Update conversation history display
     * @param {Object} session - MCP session object
     * @param {HTMLElement} container - Container element (optional)
     */
    static updateConversationDisplay(session, container = null) {
        const historyDiv = container || document.getElementById('conversationHistory');
        if (!historyDiv) {
            console.warn('MCP Conversation: conversationHistory element not found');
            return;
        }
        
        if (!session || !session.conversationHistory || session.conversationHistory.length === 0) {
            historyDiv.innerHTML = `
                <div class="conversation-entry empty">
                    <em>No conversation history yet. Ask a question to start building context memory.</em>
                </div>
            `;
            return;
        }
        
        const conversationHTML = session.conversationHistory.map((entry, index) => `
            <div class="conversation-entry" data-entry-id="${entry.id || index}">
                <div class="conversation-question">
                    👤 Q${index + 1}: ${this.escapeHtml(entry.question)}
                </div>
                <div class="conversation-response">
                    🤖 ${this.truncateText(this.escapeHtml(entry.response), 200)}
                </div>
                <div class="conversation-timestamp">
                    ${entry.timestamp}
                    ${entry.metadata && entry.metadata.contextUsed ? ' • Context Used' : ''}
                </div>
                ${this.renderConversationActions(entry, index)}
            </div>
        `).join('');
        
        historyDiv.innerHTML = conversationHTML;
        console.log('🔄 MCP Conversation: Updated display with', session.conversationHistory.length, 'entries');
    }

    /**
     * Render conversation entry actions
     * @param {Object} entry - Conversation entry
     * @param {number} index - Entry index
     * @returns {string} - Actions HTML
     */
    static renderConversationActions(entry, index) {
        return `
            <div class="conversation-actions" style="margin-top: 8px; font-size: 0.7em;">
                <button class="btn btn-tiny" onclick="window.MCPConversation.expandConversationEntry(${entry.id || index})" 
                        style="padding: 2px 6px; margin-right: 5px;">
                    Expand
                </button>
                <button class="btn btn-tiny" onclick="window.MCPConversation.copyConversationEntry(${entry.id || index})" 
                        style="padding: 2px 6px; margin-right: 5px; background: #46b450;">
                    Copy
                </button>
                <button class="btn btn-tiny" onclick="window.MCPConversation.shareConversationEntry(${entry.id || index})" 
                        style="padding: 2px 6px; background: #0073aa;">
                    Share
                </button>
            </div>
        `;
    }

    /**
     * Update image gallery display
     * @param {Object} session - MCP session object
     * @param {HTMLElement} galleryContainer - Gallery container (optional)
     * @param {HTMLElement} gridContainer - Grid container (optional)
     */
    static updateImageGalleryDisplay(session, galleryContainer = null, gridContainer = null) {
        const galleryDiv = galleryContainer || document.getElementById('imageGallery');
        const thumbnailGrid = gridContainer || document.getElementById('thumbnailGrid');
        
        if (!galleryDiv || !thumbnailGrid) {
            console.warn('MCP Conversation: Image gallery elements not found');
            return;
        }
        
        if (!session || !session.imageGallery || session.imageGallery.length === 0) {
            galleryDiv.style.display = 'none';
            return;
        }
        
        galleryDiv.style.display = 'block';
        
        const thumbnailHTML = session.imageGallery.map((image, index) => `
            <div class="thumbnail-item" onclick="window.MCPConversation.openImageLightbox('${image.imageBase64}', '${this.escapeHtml(image.prompt)}', ${index})"
                 data-image-id="${image.id || index}">
                <div class="thumbnail-number">${index + 1}</div>
                <img src="data:image/png;base64,${image.imageBase64}" 
                     alt="Generated Image ${index + 1}" 
                     loading="lazy" />
                <div class="thumbnail-info">
                    <div class="thumbnail-prompt" title="${this.escapeHtml(image.prompt)}">
                        ${this.truncateText(image.prompt, 20)}
                    </div>
                    <div class="thumbnail-timestamp">
                        ${image.style} • ${image.timestamp}
                        ${image.isAutoGenerated ? ' • 🤖 Auto' : ''}
                    </div>
                    ${this.renderImageActions(image, index)}
                </div>
            </div>
        `).join('');
        
        thumbnailGrid.innerHTML = thumbnailHTML;
        console.log('🔄 MCP Conversation: Updated image gallery with', session.imageGallery.length, 'images');
    }

    /**
     * Render image thumbnail actions
     * @param {Object} image - Image object
     * @param {number} index - Image index
     * @returns {string} - Actions HTML
     */
    static renderImageActions(image, index) {
        return `
            <div class="thumbnail-actions" style="margin-top: 4px; font-size: 0.6em;">
                <button class="btn btn-micro" onclick="event.stopPropagation(); window.MCPConversation.downloadImage(${image.id || index})" 
                        style="padding: 1px 4px; margin-right: 3px; background: #46b450;" title="Download">
                    ⬇
                </button>
                <button class="btn btn-micro" onclick="event.stopPropagation(); window.MCPConversation.shareImage(${image.id || index})" 
                        style="padding: 1px 4px; margin-right: 3px; background: #0073aa;" title="Share">
                    📤
                </button>
                <button class="btn btn-micro" onclick="event.stopPropagation(); window.MCPConversation.deleteImage(${image.id || index})" 
                        style="padding: 1px 4px; background: #dc3232;" title="Delete">
                    🗑
                </button>
            </div>
        `;
    }

    /**
     * Open image lightbox with navigation
     * @param {string} imageBase64 - Base64 image data
     * @param {string} prompt - Image prompt
     * @param {number} imageIndex - Current image index
     */
    static openImageLightbox(imageBase64, prompt, imageIndex = 0) {
        // Remove existing lightbox
        const existingLightbox = document.getElementById('mcpImageLightbox');
        if (existingLightbox) {
            existingLightbox.remove();
        }
        
        // Get total images for navigation
        const session = window.mcpSession;
        const totalImages = session && session.imageGallery ? session.imageGallery.length : 1;
        
        // Create lightbox
        const lightbox = document.createElement('div');
        lightbox.id = 'mcpImageLightbox';
        lightbox.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            backdrop-filter: blur(5px);
        `;
        
        const lightboxContent = document.createElement('div');
        lightboxContent.style.cssText = `
            max-width: 90%;
            max-height: 90%;
            position: relative;
            background: white;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            overflow: hidden;
        `;
        
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${imageBase64}`;
        img.style.cssText = `
            width: 100%;
            height: auto;
            max-width: 100%;
            max-height: 80vh;
            object-fit: contain;
            display: block;
        `;
        
        const infoPanel = document.createElement('div');
        infoPanel.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0,0,0,0.8));
            color: white;
            padding: 20px;
            font-size: 14px;
        `;
        infoPanel.innerHTML = `
            <div style="margin-bottom: 8px; font-weight: bold;">Image ${imageIndex + 1} of ${totalImages}</div>
            <div style="margin-bottom: 8px;">Prompt: ${this.escapeHtml(prompt)}</div>
            <div style="display: flex; gap: 10px; margin-top: 12px;">
                <button onclick="window.MCPConversation.downloadImageFromLightbox('${imageBase64}', '${this.escapeHtml(prompt)}', ${imageIndex})" 
                        style="padding: 6px 12px; background: #46b450; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Download
                </button>
                <button onclick="window.MCPConversation.shareImageFromLightbox('${imageBase64}', '${this.escapeHtml(prompt)}', ${imageIndex})" 
                        style="padding: 6px 12px; background: #0073aa; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Share
                </button>
            </div>
        `;
        
        // Navigation buttons
        if (totalImages > 1) {
            const prevBtn = document.createElement('button');
            prevBtn.innerHTML = '‹';
            prevBtn.style.cssText = `
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(0,0,0,0.5);
                color: white;
                border: none;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                font-size: 20px;
                cursor: pointer;
                transition: background 0.3s;
            `;
            prevBtn.onclick = () => this.navigateImage(imageIndex - 1);
            
            const nextBtn = document.createElement('button');
            nextBtn.innerHTML = '›';
            nextBtn.style.cssText = `
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(0,0,0,0.5);
                color: white;
                border: none;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                font-size: 20px;
                cursor: pointer;
                transition: background 0.3s;
            `;
            nextBtn.onclick = () => this.navigateImage(imageIndex + 1);
            
            lightboxContent.appendChild(prevBtn);
            lightboxContent.appendChild(nextBtn);
        }
        
        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.5);
            color: white;
            border: none;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            font-size: 20px;
            cursor: pointer;
            z-index: 10001;
        `;
        closeBtn.onclick = () => this.closeLightbox();
        
        lightboxContent.appendChild(img);
        lightboxContent.appendChild(infoPanel);
        lightboxContent.appendChild(closeBtn);
        lightbox.appendChild(lightboxContent);
        
        // Close on backdrop click
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                this.closeLightbox();
            }
        });
        
        // Keyboard navigation
        const keyHandler = (e) => {
            switch(e.key) {
                case 'Escape':
                    this.closeLightbox();
                    break;
                case 'ArrowLeft':
                    if (totalImages > 1) this.navigateImage(imageIndex - 1);
                    break;
                case 'ArrowRight':
                    if (totalImages > 1) this.navigateImage(imageIndex + 1);
                    break;
            }
        };
        
        document.addEventListener('keydown', keyHandler);
        lightbox.addEventListener('remove', () => {
            document.removeEventListener('keydown', keyHandler);
        });
        
        document.body.appendChild(lightbox);
        
        // Store current index for navigation
        lightbox.dataset.currentIndex = imageIndex;
        
        console.log('🖼️ MCP Conversation: Opened lightbox for image', imageIndex + 1, 'of', totalImages);
    }

    /**
     * Navigate to different image in lightbox
     * @param {number} newIndex - New image index
     */
    static navigateImage(newIndex) {
        const session = window.mcpSession;
        if (!session || !session.imageGallery) return;
        
        const totalImages = session.imageGallery.length;
        if (totalImages === 0) return;
        
        // Handle wrap-around
        if (newIndex < 0) newIndex = totalImages - 1;
        if (newIndex >= totalImages) newIndex = 0;
        
        const image = session.imageGallery[newIndex];
        if (!image) return;
        
        this.openImageLightbox(image.imageBase64, image.prompt, newIndex);
    }

    /**
     * Close image lightbox
     */
    static closeLightbox() {
        const lightbox = document.getElementById('mcpImageLightbox');
        if (lightbox) {
            lightbox.remove();
            console.log('🖼️ MCP Conversation: Closed lightbox');
        }
    }

    /**
     * Expand conversation entry to show full content
     * @param {number} entryId - Entry ID or index
     */
    static expandConversationEntry(entryId) {
        const session = window.mcpSession;
        if (!session || !session.conversationHistory) return;
        
        const entry = session.conversationHistory.find(e => e.id === entryId) || 
                     session.conversationHistory[entryId];
        
        if (!entry) {
            console.warn('MCP Conversation: Entry not found for ID', entryId);
            return;
        }
        
        // Create modal for expanded view
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 20px;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 20px;
            max-width: 80%;
            max-height: 80%;
            overflow-y: auto;
            position: relative;
        `;
        
        modalContent.innerHTML = `
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="position: absolute; top: 10px; right: 10px; background: #dc3232; color: white; border: none; border-radius: 4px; padding: 5px 10px; cursor: pointer;">
                Close
            </button>
            <h3 style="margin-top: 0;">Conversation Entry Details</h3>
            <div style="margin-bottom: 20px;">
                <strong>Question:</strong>
                <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 5px;">
                    ${this.escapeHtml(entry.question)}
                </div>
            </div>
            <div style="margin-bottom: 20px;">
                <strong>Response:</strong>
                <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 5px; white-space: pre-wrap;">
                    ${this.escapeHtml(entry.response)}
                </div>
            </div>
            <div style="font-size: 0.9em; color: #666;">
                <strong>Timestamp:</strong> ${entry.timestamp}<br>
                ${entry.metadata && entry.metadata.contextUsed ? '<strong>Context Used:</strong> Yes<br>' : ''}
                ${entry.metadata && entry.metadata.tokens ? '<strong>Tokens:</strong> ' + entry.metadata.tokens + '<br>' : ''}
            </div>
        `;
        
        modal.appendChild(modalContent);
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        document.body.appendChild(modal);
        
        console.log('📖 MCP Conversation: Expanded entry', entryId);
    }

    /**
     * Copy conversation entry to clipboard
     * @param {number} entryId - Entry ID or index
     */
    static async copyConversationEntry(entryId) {
        const session = window.mcpSession;
        if (!session || !session.conversationHistory) return;
        
        const entry = session.conversationHistory.find(e => e.id === entryId) || 
                     session.conversationHistory[entryId];
        
        if (!entry) {
            console.warn('MCP Conversation: Entry not found for ID', entryId);
            return;
        }
        
        const textToCopy = `Q: ${entry.question}\n\nA: ${entry.response}\n\nTimestamp: ${entry.timestamp}`;
        
        try {
            await navigator.clipboard.writeText(textToCopy);
            this.showNotification('Conversation entry copied to clipboard', 'success');
            console.log('📋 MCP Conversation: Copied entry', entryId);
        } catch (err) {
            console.error('Failed to copy text:', err);
            this.showNotification('Failed to copy to clipboard', 'error');
        }
    }

    /**
     * Share conversation entry
     * @param {number} entryId - Entry ID or index
     */
    static shareConversationEntry(entryId) {
        const session = window.mcpSession;
        if (!session || !session.conversationHistory) return;
        
        const entry = session.conversationHistory.find(e => e.id === entryId) || 
                     session.conversationHistory[entryId];
        
        if (!entry) {
            console.warn('MCP Conversation: Entry not found for ID', entryId);
            return;
        }
        
        const shareData = {
            title: 'MCP Conversation Entry',
            text: `Q: ${entry.question}\n\nA: ${entry.response.substring(0, 200)}${entry.response.length > 200 ? '...' : ''}`
        };
        
        if (navigator.share) {
            navigator.share(shareData).catch(err => {
                console.error('Error sharing:', err);
                this.fallbackShare(shareData);
            });
        } else {
            this.fallbackShare(shareData);
        }
        
        console.log('🔗 MCP Conversation: Shared entry', entryId);
    }

    /**
     * Download image from gallery
     * @param {number} imageId - Image ID or index
     */
    static downloadImage(imageId) {
        const session = window.mcpSession;
        if (!session || !session.imageGallery) return;
        
        const image = session.imageGallery.find(img => img.id === imageId) || 
                     session.imageGallery[imageId];
        
        if (!image) {
            console.warn('MCP Conversation: Image not found for ID', imageId);
            return;
        }
        
        this.downloadImageFromLightbox(image.imageBase64, image.prompt, imageId);
    }

    /**
     * Download image from lightbox
     * @param {string} imageBase64 - Base64 image data
     * @param {string} prompt - Image prompt
     * @param {number} imageIndex - Image index
     */
    static downloadImageFromLightbox(imageBase64, prompt, imageIndex) {
        try {
            // Create download link
            const link = document.createElement('a');
            link.href = `data:image/png;base64,${imageBase64}`;
            
            // Generate filename from prompt
            const filename = `mcp-image-${imageIndex + 1}-${prompt.substring(0, 30).replace(/[^a-zA-Z0-9]/g, '_')}.png`;
            link.download = filename;
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showNotification('Image downloaded successfully', 'success');
            console.log('⬇️ MCP Conversation: Downloaded image', imageIndex + 1);
        } catch (err) {
            console.error('Failed to download image:', err);
            this.showNotification('Failed to download image', 'error');
        }
    }

    /**
     * Share image
     * @param {number} imageId - Image ID or index
     */
    static shareImage(imageId) {
        const session = window.mcpSession;
        if (!session || !session.imageGallery) return;
        
        const image = session.imageGallery.find(img => img.id === imageId) || 
                     session.imageGallery[imageId];
        
        if (!image) {
            console.warn('MCP Conversation: Image not found for ID', imageId);
            return;
        }
        
        this.shareImageFromLightbox(image.imageBase64, image.prompt, imageId);
    }

    /**
     * Share image from lightbox
     * @param {string} imageBase64 - Base64 image data
     * @param {string} prompt - Image prompt
     * @param {number} imageIndex - Image index
     */
    static shareImageFromLightbox(imageBase64, prompt, imageIndex) {
        try {
            // Convert base64 to blob
            const byteCharacters = atob(imageBase64);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'image/png' });
            
            const file = new File([blob], `mcp-image-${imageIndex + 1}.png`, { type: 'image/png' });
            
            const shareData = {
                title: 'MCP Generated Image',
                text: `Generated image: ${prompt}`,
                files: [file]
            };
            
            if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
                navigator.share(shareData).catch(err => {
                    console.error('Error sharing image:', err);
                    this.fallbackShareImage(imageBase64, prompt);
                });
            } else {
                this.fallbackShareImage(imageBase64, prompt);
            }
            
            console.log('🔗 MCP Conversation: Shared image', imageIndex + 1);
        } catch (err) {
            console.error('Failed to share image:', err);
            this.showNotification('Failed to share image', 'error');
        }
    }

    /**
     * Delete image from gallery
     * @param {number} imageId - Image ID or index
     */
    static deleteImage(imageId) {
        const session = window.mcpSession;
        if (!session || !session.imageGallery) return;
        
        if (confirm('Are you sure you want to delete this image?')) {
            const imageIndex = session.imageGallery.findIndex(img => img.id === imageId);
            const actualIndex = imageIndex !== -1 ? imageIndex : imageId;
            
            if (actualIndex >= 0 && actualIndex < session.imageGallery.length) {
                session.imageGallery.splice(actualIndex, 1);
                this.updateImageGalleryDisplay(session);
                this.showNotification('Image deleted successfully', 'success');
                console.log('🗑️ MCP Conversation: Deleted image', actualIndex + 1);
            } else {
                console.warn('MCP Conversation: Image not found for deletion', imageId);
            }
        }
    }

    /**
     * Fallback share method using clipboard
     * @param {Object} shareData - Share data object
     */
    static fallbackShare(shareData) {
        const textToShare = `${shareData.title}\n\n${shareData.text}`;
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(textToShare).then(() => {
                this.showNotification('Content copied to clipboard for sharing', 'success');
            }).catch(err => {
                console.error('Failed to copy for sharing:', err);
                this.showNotification('Failed to prepare content for sharing', 'error');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = textToShare;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                this.showNotification('Content copied to clipboard for sharing', 'success');
            } catch (err) {
                console.error('Failed to copy for sharing:', err);
                this.showNotification('Failed to prepare content for sharing', 'error');
            }
            document.body.removeChild(textArea);
        }
    }

    /**
     * Fallback image share method
     * @param {string} imageBase64 - Base64 image data
     * @param {string} prompt - Image prompt
     */
    static fallbackShareImage(imageBase64, prompt) {
        // Create a temporary link for the image
        const link = document.createElement('a');
        link.href = `data:image/png;base64,${imageBase64}`;
        link.target = '_blank';
        link.download = `mcp-image-${prompt.substring(0, 30).replace(/[^a-zA-Z0-9]/g, '_')}.png`;
        
        // Try to open in new tab for manual sharing
        link.click();
        
        this.showNotification('Image opened in new tab for manual sharing', 'info');
    }

    /**
     * Show notification to user
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, info)
     */
    static showNotification(message, type = 'info') {
        // Remove existing notification
        const existingNotification = document.getElementById('mcpNotification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Create notification
        const notification = document.createElement('div');
        notification.id = 'mcpNotification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-size: 14px;
            z-index: 10001;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        `;
        
        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.background = '#46b450';
                break;
            case 'error':
                notification.style.background = '#dc3232';
                break;
            case 'info':
            default:
                notification.style.background = '#0073aa';
                break;
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }
        }, 3000);
    }

    /**
     * Escape HTML entities
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    static escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Truncate text to specified length
     * @param {string} text - Text to truncate
     * @param {number} length - Maximum length
     * @returns {string} - Truncated text
     */
    static truncateText(text, length) {
        if (!text || text.length <= length) return text || '';
        return text.substring(0, length) + '...';
    }

    /**
     * Initialize conversation management
     */
    static init() {
        // Ensure global availability
        window.MCPConversation = this;
        
        console.log('🔄 MCP Conversation: Initialized conversation management');
        
        // Set up periodic auto-save if session exists
        if (window.mcpSession) {
            setInterval(() => {
                if (window.mcpSession.conversationHistory?.length > 0 || 
                    window.mcpSession.imageGallery?.length > 0) {
                    // Auto-save session data to localStorage if available
                    try {
                        const sessionData = {
                            conversationHistory: window.mcpSession.conversationHistory || [],
                            imageGallery: window.mcpSession.imageGallery || [],
                            timestamp: new Date().toISOString()
                        };
                        localStorage.setItem('mcpSessionData', JSON.stringify(sessionData));
                    } catch (err) {
                        console.warn('MCP Conversation: Failed to auto-save session data:', err);
                    }
                }
            }, 30000); // Auto-save every 30 seconds
        }
    }

    /**
     * Load saved session data
     */
    static loadSessionData() {
        try {
            const savedData = localStorage.getItem('mcpSessionData');
            if (savedData) {
                const sessionData = JSON.parse(savedData);
                
                // Initialize session if it doesn't exist
                if (!window.mcpSession) {
                    window.mcpSession = {};
                }
                
                // Restore conversation history
                if (sessionData.conversationHistory) {
                    window.mcpSession.conversationHistory = sessionData.conversationHistory;
                }
                
                // Restore image gallery
                if (sessionData.imageGallery) {
                    window.mcpSession.imageGallery = sessionData.imageGallery;
                }
                
                console.log('🔄 MCP Conversation: Loaded session data from storage');
                return true;
            }
        } catch (err) {
            console.warn('MCP Conversation: Failed to load session data:', err);
        }
        return false;
    }

    /**
     * Clear all conversation and image data
     */
    static clearAllData() {
        if (confirm('Are you sure you want to clear all conversation history and images? This cannot be undone.')) {
            try {
                // Clear session data
                if (window.mcpSession) {
                    window.mcpSession.conversationHistory = [];
                    window.mcpSession.imageGallery = [];
                }
                
                // Clear localStorage
                localStorage.removeItem('mcpSessionData');
                
                // Update displays
                this.updateConversationDisplay(window.mcpSession);
                this.updateImageGalleryDisplay(window.mcpSession);
                
                this.showNotification('All data cleared successfully', 'success');
                console.log('🗑️ MCP Conversation: Cleared all data');
            } catch (err) {
                console.error('Failed to clear data:', err);
                this.showNotification('Failed to clear data', 'error');
            }
        }
    }

    /**
     * Export conversation data as JSON
     */
    static exportData() {
        try {
            const session = window.mcpSession;
            if (!session || (!session.conversationHistory?.length && !session.imageGallery?.length)) {
                this.showNotification('No data to export', 'info');
                return;
            }
            
            const exportData = {
                conversationHistory: session.conversationHistory || [],
                imageGallery: session.imageGallery || [],
                exportTimestamp: new Date().toISOString(),
                version: '1.0'
            };
            
            const dataStr = JSON.stringify(exportData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `mcp-session-${new Date().toISOString().split('T')[0]}.json`;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showNotification('Data exported successfully', 'success');
            console.log('📁 MCP Conversation: Exported session data');
        } catch (err) {
            console.error('Failed to export data:', err);
            this.showNotification('Failed to export data', 'error');
        }
    }

    /**
     * Import conversation data from JSON file
     * @param {File} file - JSON file to import
     */
    static async importData(file) {
        try {
            const text = await file.text();
            const importData = JSON.parse(text);
            
            // Validate import data structure
            if (!importData.conversationHistory && !importData.imageGallery) {
                throw new Error('Invalid data format');
            }
            
            // Initialize session if needed
            if (!window.mcpSession) {
                window.mcpSession = {};
            }
            
            // Merge or replace data based on user choice
            const shouldMerge = confirm('Would you like to merge with existing data? Click Cancel to replace all data.');
            
            if (shouldMerge) {
                // Merge conversation history
                if (importData.conversationHistory) {
                    window.mcpSession.conversationHistory = [
                        ...(window.mcpSession.conversationHistory || []),
                        ...importData.conversationHistory
                    ];
                }
                
                // Merge image gallery
                if (importData.imageGallery) {
                    window.mcpSession.imageGallery = [
                        ...(window.mcpSession.imageGallery || []),
                        ...importData.imageGallery
                    ];
                }
            } else {
                // Replace all data
                window.mcpSession.conversationHistory = importData.conversationHistory || [];
                window.mcpSession.imageGallery = importData.imageGallery || [];
            }
            
            // Update displays
            this.updateConversationDisplay(window.mcpSession);
            this.updateImageGalleryDisplay(window.mcpSession);
            
            this.showNotification('Data imported successfully', 'success');
            console.log('📁 MCP Conversation: Imported session data');
        } catch (err) {
            console.error('Failed to import data:', err);
            this.showNotification('Failed to import data: ' + err.message, 'error');
        }
    }

    /**
     * Search conversation history
     * @param {string} searchTerm - Term to search for
     * @returns {Array} - Filtered conversation entries
     */
    static searchConversationHistory(searchTerm) {
        const session = window.mcpSession;
        if (!session || !session.conversationHistory) return [];
        
        if (!searchTerm.trim()) return session.conversationHistory;
        
        const term = searchTerm.toLowerCase();
        return session.conversationHistory.filter(entry => 
            entry.question.toLowerCase().includes(term) ||
            entry.response.toLowerCase().includes(term)
        );
    }

    /**
     * Get conversation statistics
     * @returns {Object} - Statistics object
     */
    static getConversationStats() {
        const session = window.mcpSession;
        if (!session) return null;
        
        const conversationCount = session.conversationHistory?.length || 0;
        const imageCount = session.imageGallery?.length || 0;
        
        let totalQuestionLength = 0;
        let totalResponseLength = 0;
        let contextUsedCount = 0;
        
        if (session.conversationHistory) {
            session.conversationHistory.forEach(entry => {
                totalQuestionLength += entry.question.length;
                totalResponseLength += entry.response.length;
                if (entry.metadata?.contextUsed) {
                    contextUsedCount++;
                }
            });
        }
        
        return {
            conversationCount,
            imageCount,
            averageQuestionLength: conversationCount > 0 ? Math.round(totalQuestionLength / conversationCount) : 0,
            averageResponseLength: conversationCount > 0 ? Math.round(totalResponseLength / conversationCount) : 0,
            contextUsedPercentage: conversationCount > 0 ? Math.round((contextUsedCount / conversationCount) * 100) : 0
        };
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => MCPConversation.init());
} else {
    MCPConversation.init();
}

// Load saved session data on initialization
MCPConversation.loadSessionData();