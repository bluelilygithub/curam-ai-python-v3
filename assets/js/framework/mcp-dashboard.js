/**
 * framework/mcp-dashboard.js - MCP Dashboard Components
 * 
 * Provides MCP-specific dashboard components including:
 * - Complete MCP dashboard orchestration
 * - Context memory display and management
 * - Tool discovery visualization
 * - MCP vs Traditional comparison
 * - Model comparison results display
 */

class MCPDashboard {
    
    /**
     * Render complete MCP dashboard with all components
     * @param {HTMLElement} container - Container element
     * @param {Object} options - Dashboard configuration options
     */
    static renderMCPDashboard(container, options = {}) {
        if (!container) return;
        
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
                        <!-- Workflow will be rendered here by MCPWorkflow class -->
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
        
        console.log('✅ MCP Dashboard: Complete dashboard rendered with all components');
    }

    /**
     * Render context memory component with conversation window
     * @param {HTMLElement} container - Container element
     * @param {Object} initialData - Initial context data
     */
    static renderContextMemory(container, initialData = {}) {
        if (!container) return;
        
        const defaultData = {
            lastQuestion: 'None yet',
            contextEntries: 0,
            toolsChained: 0
        };
        
        const data = { ...defaultData, ...initialData };
        
        const contextHTML = `
            <div class="context-memory">
                <h4>📚 Context Memory (MCP Advantage)</h4>
                <div class="context-item">
                    <span class="context-label">Previous Question:</span>
                    <span class="context-value" id="lastQuestion">${data.lastQuestion}</span>
                </div>
                <div class="context-item">
                    <span class="context-label">Context Entries:</span>
                    <span class="context-value" id="contextEntries">${data.contextEntries}</span>
                </div>
                <div class="context-item">
                    <span class="context-label">Tools Chained:</span>
                    <span class="context-value" id="toolsChained">${data.toolsChained}</span>
                </div>
                <div class="context-item">
                    <button class="btn" onclick="window.MCPDashboard.toggleConversationWindow()" id="showConversationBtn" style="padding: 6px 12px; font-size: 0.8em; margin-top: 10px;">
                        Show Conversation History
                    </button>
                </div>
                
                <!-- Embedded Conversation Window -->
                <div class="conversation-window" id="conversationWindow" style="display: none; margin-top: 15px;">
                    <h4>💬 Session Conversation History</h4>
                    <div class="conversation-controls">
                        <button class="btn" onclick="window.MCPDashboard.exportToPDF()" style="padding: 4px 8px; font-size: 0.8em; background: #46b450;">
                            📄 Export PDF
                        </button>
                        <button class="btn" onclick="window.MCPDashboard.emailReport()" style="padding: 4px 8px; font-size: 0.8em; background: #0073aa;">
                            📧 Email PDF
                        </button>
                        <button class="btn" onclick="window.MCPDashboard.clearConversation()" style="padding: 4px 8px; font-size: 0.8em; background: #dc3232;">
                            Clear All History
                        </button>
                        <button class="btn" onclick="window.MCPDashboard.toggleConversationWindow()" style="padding: 4px 8px; font-size: 0.8em;">
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
        console.log('✅ MCP Dashboard: Context memory with embedded conversation window rendered');
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
        console.log('✅ MCP Dashboard: Tool discovery rendered with', toolList.length, 'tools');
    }

    /**
     * Render MCP vs Traditional comparison
     * @param {HTMLElement} container - Container element
     * @param {Object} options - Comparison options
     */
    static renderMCPComparison(container, options = {}) {
        if (!container) return;
        
        const defaultOptions = {
            showAdvantages: true,
            customComparison: null
        };
        
        const config = { ...defaultOptions, ...options };
        
        const comparisonData = config.customComparison || {
            traditional: {
                title: '❌ Traditional REST API',
                items: ['Fixed endpoints', 'No context memory', 'Manual orchestration', 'Stateless operations']
            },
            mcp: {
                title: '✅ MCP (This Demo)',
                items: ['Dynamic tool discovery', 'Context-aware chaining', 'Intelligent tool selection', 'Contextual workflows']
            }
        };
        
        const comparisonHTML = `
            <div class="mcp-comparison">
                <div class="comparison-box traditional-api">
                    <h4>${comparisonData.traditional.title}</h4>
                    <ul class="comparison-list">
                        ${comparisonData.traditional.items.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
                <div class="comparison-box mcp-approach">
                    <h4>${comparisonData.mcp.title}</h4>
                    <ul class="comparison-list">
                        ${comparisonData.mcp.items.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        container.innerHTML = comparisonHTML;
        console.log('✅ MCP Dashboard: MCP vs Traditional comparison rendered');
    }

    /**
     * Render model comparison results
     * @param {HTMLElement} container - Container element
     * @param {Object} results - Comparison results
     * @param {Object} options - Display options
     */
    static renderModelComparison(container, results, options = {}) {
        if (!container || !results) return;
        
        const defaultOptions = {
            showMetadata: true,
            showTimestamps: true,
            allowExpansion: false
        };
        
        const config = { ...defaultOptions, ...options };
        
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
                        ${config.showMetadata && result.metadata ? `
                            <div class="model-metadata">
                                <small>
                                    ${Object.entries(result.metadata).map(([key, value]) => 
                                        `<strong>${key}:</strong> ${value}`
                                    ).join(' • ')}
                                </small>
                            </div>
                        ` : ''}
                        ${config.allowExpansion ? `
                            <div class="model-actions">
                                <button class="btn btn-small" onclick="window.MCPDashboard.expandModelResult('${modelName}')">
                                    Expand
                                </button>
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = comparisonHTML;
        console.log('✅ MCP Dashboard: Model comparison results rendered for', Object.keys(results).length, 'models');
    }

    /**
     * Render image result component with MCP context analysis
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
            imageNumber: null,
            allowLightbox: true
        };
        
        const config = { ...defaultOptions, ...options };
        
        const autoIndicator = config.isAutoGenerated ? 
            '<div class="auto-generation-indicator"><strong>🤖 MCP Auto-Generated from Context Analysis</strong></div>' : '';
        
        const imageNumber = config.imageNumber ? 
            `<div style="text-align: right; margin-bottom: 10px; color: #666; font-size: 0.9em;">
                Image #${config.imageNumber} • <a href="#" onclick="window.MCPDashboard.toggleConversationWindow(); return false;">View All Images</a>
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
        
        const lightboxHandler = config.allowLightbox ? 
            `onclick="window.MCPDashboard.openLightbox('${imageData.imageBase64}', '${imageData.prompt.replace(/'/g, "\\'")}'); return false;" 
             style="cursor: pointer;" 
             title="Click to view full size"` : '';
        
        const imageHTML = `
            ${autoIndicator}
            <div class="image-result">
                ${imageNumber}
                <div class="session-image-background" 
                     style="background-image: url('data:image/png;base64,${imageData.imageBase64}');"
                     ${lightboxHandler}></div>
                ${explanation}
                ${metadata}
            </div>
        `;
        
        container.innerHTML = imageHTML;
        console.log('✅ MCP Dashboard: Image result rendered', config.isAutoGenerated ? '(auto-generated)' : '(manual)');
    }

    /**
     * Toggle conversation window visibility
     */
    static toggleConversationWindow() {
        console.log('🔍 MCP Dashboard: toggleConversationWindow called');
        
        const conversationWindow = document.getElementById('conversationWindow');
        const btn = document.getElementById('showConversationBtn');
        
        if (!conversationWindow || !btn) {
            console.error('❌ MCP Dashboard: Required elements not found for conversation toggle');
            return;
        }
        
        const isCurrentlyHidden = conversationWindow.style.display === 'none';
        
        if (isCurrentlyHidden) {
            conversationWindow.style.display = 'block';
            conversationWindow.style.visibility = 'visible';
            btn.textContent = 'Hide Conversation History';
            console.log('✅ MCP Dashboard: Conversation window shown');
            
            // Trigger updates if session exists
            if (window.mcpSession) {
                window.mcpSession.updateConversationDisplay();
                window.mcpSession.updateImageGalleryDisplay();
            }
        } else {
            conversationWindow.style.display = 'none';
            btn.textContent = 'Show Conversation History';
            console.log('✅ MCP Dashboard: Conversation window hidden');
        }
    }

    /**
     * Clear conversation (delegates to session if available)
     */
    static clearConversation() {
        if (window.mcpSession && window.mcpSession.clearSession) {
            window.mcpSession.clearSession();
        } else {
            console.warn('MCP Session not available for clearing conversation');
            // Fallback notification
            if (window.MCPUICore && window.MCPUICore.showNotification) {
                window.MCPUICore.showNotification(
                    'MCP Session not available. Please reload the page.',
                    'warning',
                    3000
                );
            }
        }
    }

    /**
     * Export to PDF (delegates to PDF export module)
     */
    static async exportToPDF() {
        try {
            if (window.MCPPDFExport && window.mcpSession) {
                // Show loading notification
                if (window.MCPUICore && window.MCPUICore.showNotification) {
                    window.MCPUICore.showNotification(
                        'Generating PDF with images...',
                        'info',
                        2000
                    );
                }
                
                await window.MCPPDFExport.exportToPDF(window.mcpSession);
                
                // Show success notification
                if (window.MCPUICore && window.MCPUICore.showNotification) {
                    window.MCPUICore.showNotification(
                        'PDF exported successfully!',
                        'success',
                        3000
                    );
                }
            } else {
                throw new Error('PDF export module or session not available');
            }
        } catch (error) {
            console.error('PDF Export Error:', error);
            if (window.MCPUICore && window.MCPUICore.showNotification) {
                window.MCPUICore.showNotification(
                    `PDF export failed: ${error.message}`,
                    'error',
                    5000
                );
            }
        }
    }

    /**
     * Email report (delegates to email module)
     */
    static async emailReport() {
        try {
            if (window.MCPEmail && window.mcpSession) {
                await window.MCPEmail.emailReport(window.mcpSession);
                
                // Success notification will be handled by the email module
            } else {
                throw new Error('Email module or session not available');
            }
        } catch (error) {
            console.error('Email Report Error:', error);
            if (window.MCPUICore && window.MCPUICore.showNotification) {
                window.MCPUICore.showNotification(
                    `Email failed: ${error.message}`,
                    'error',
                    5000
                );
            }
        }
    }

    /**
     * Open lightbox for image viewing
     * @param {string} imageBase64 - Base64 image data
     * @param {string} prompt - Image prompt for alt text
     */
    static openLightbox(imageBase64, prompt) {
        // Remove existing lightbox
        const existingLightbox = document.getElementById('mcpDashboardLightbox');
        if (existingLightbox) {
            existingLightbox.remove();
        }
        
        // Create new lightbox
        const lightbox = document.createElement('div');
        lightbox.id = 'mcpDashboardLightbox';
        lightbox.className = 'lightbox active';
        lightbox.innerHTML = `
            <span class="lightbox-close" onclick="window.MCPDashboard.closeLightbox()">&times;</span>
            <img src="data:image/png;base64,${imageBase64}" alt="${prompt}" />
        `;
        
        document.body.appendChild(lightbox);
        
        // Close on background click
        lightbox.onclick = function(e) {
            if (e.target === lightbox) {
                window.MCPDashboard.closeLightbox();
            }
        };
        
        // Close on escape key
        const escapeHandler = function(e) {
            if (e.key === 'Escape') {
                window.MCPDashboard.closeLightbox();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        console.log('✅ MCP Dashboard: Lightbox opened for image');
    }

    /**
     * Close lightbox
     */
    static closeLightbox() {
        const lightbox = document.getElementById('mcpDashboardLightbox');
        if (lightbox) {
            lightbox.remove();
            console.log('✅ MCP Dashboard: Lightbox closed');
        }
    }

    /**
     * Expand model result (for detailed view)
     * @param {string} modelName - Name of the model to expand
     */
    static expandModelResult(modelName) {
        console.log('🔍 MCP Dashboard: Expanding model result for', modelName);
        
        // Find the model result element
        const modelResults = document.querySelectorAll('.model-result');
        modelResults.forEach(result => {
            const title = result.querySelector('h3');
            if (title && title.textContent.includes(modelName)) {
                const response = result.querySelector('.model-response');
                if (response) {
                    // Toggle expansion
                    const isExpanded = response.classList.contains('expanded');
                    
                    if (!isExpanded) {
                        response.classList.add('expanded');
                        response.style.maxHeight = 'none';
                        response.style.overflow = 'visible';
                        
                        // Update button text
                        const expandBtn = result.querySelector('.model-actions button');
                        if (expandBtn) expandBtn.textContent = 'Collapse';
                    } else {
                        response.classList.remove('expanded');
                        response.style.maxHeight = '';
                        response.style.overflow = '';
                        
                        // Update button text
                        const expandBtn = result.querySelector('.model-actions button');
                        if (expandBtn) expandBtn.textContent = 'Expand';
                    }
                }
            }
        });
    }

    /**
     * Update context memory display
     * @param {Object} data - Context data to update
     */
    static updateContextMemory(data = {}) {
        if (data.lastQuestion !== undefined) {
            const lastQuestionEl = document.getElementById('lastQuestion');
            if (lastQuestionEl) {
                lastQuestionEl.textContent = data.lastQuestion;
            }
        }

        if (data.contextEntries !== undefined) {
            const contextEntriesEl = document.getElementById('contextEntries');
            if (contextEntriesEl) {
                contextEntriesEl.textContent = data.contextEntries;
            }
        }

        if (data.toolsChained !== undefined) {
            const toolsChainedEl = document.getElementById('toolsChained');
            if (toolsChainedEl) {
                toolsChainedEl.textContent = data.toolsChained;
            }
        }
        
        console.log('🔄 MCP Dashboard: Context memory updated', data);
    }

    /**
     * Add tool to discovery list dynamically
     * @param {Object} tool - Tool object to add
     */
    static addToolToDiscovery(tool) {
        const toolList = document.querySelector('.tool-list');
        if (!toolList) return;
        
        const toolItem = document.createElement('li');
        toolItem.innerHTML = `
            <span class="tool-status">${tool.status || '✅'}</span>
            <span class="tool-name">${tool.name}</span>
            <span class="tool-description">${tool.description}</span>
        `;
        
        toolList.appendChild(toolItem);
        console.log('✅ MCP Dashboard: Added tool to discovery:', tool.name);
    }

    /**
     * Update tool status in discovery list
     * @param {string} toolName - Name of tool to update
     * @param {string} status - New status
     */
    static updateToolStatus(toolName, status) {
        const toolItems = document.querySelectorAll('.tool-list li');
        toolItems.forEach(item => {
            const nameSpan = item.querySelector('.tool-name');
            if (nameSpan && nameSpan.textContent === toolName) {
                const statusSpan = item.querySelector('.tool-status');
                if (statusSpan) {
                    statusSpan.textContent = status;
                }
            }
        });
        
        console.log('🔄 MCP Dashboard: Updated tool status:', toolName, '->', status);
    }

    /**
     * Show MCP decision with reasoning
     * @param {string} text - Decision explanation
     * @param {number} duration - How long to show (ms), 0 = permanent
     */
    static showMCPDecision(text, duration = 5000) {
        // Try to find existing decision container or create one
        let decisionContainer = document.getElementById('mcpDecisionContainer');
        
        if (!decisionContainer) {
            // Create decision container if it doesn't exist
            const dashboard = document.querySelector('.mcp-dashboard');
            if (dashboard) {
                decisionContainer = document.createElement('div');
                decisionContainer.id = 'mcpDecisionContainer';
                dashboard.appendChild(decisionContainer);
            }
        }
        
        if (decisionContainer) {
            decisionContainer.innerHTML = `
                <div class="mcp-decision" id="mcpDecision">
                    <h4>🧠 MCP Intelligence Active</h4>
                    <p id="decisionText">${text}</p>
                </div>
            `;
            
            if (duration > 0) {
                setTimeout(() => {
                    const decisionDiv = document.getElementById('mcpDecision');
                    if (decisionDiv) {
                        decisionDiv.style.display = 'none';
                    }
                }, duration);
            }
        }
        
        console.log('🧠 MCP Dashboard: Decision shown -', text);
    }

    /**
     * Get dashboard statistics
     * @returns {Object} - Dashboard statistics
     */
    static getDashboardStats() {
        const stats = {
            contextMemoryVisible: !!document.getElementById('mcpContextMemoryContainer'),
            toolDiscoveryVisible: !!document.getElementById('mcpToolDiscoveryContainer'),
            comparisonVisible: !!document.getElementById('mcpComparisonContainer'),
            conversationWindowOpen: false,
            toolsDiscovered: 0,
            conversationEntries: 0
        };
        
        // Check conversation window state
        const conversationWindow = document.getElementById('conversationWindow');
        if (conversationWindow) {
            stats.conversationWindowOpen = conversationWindow.style.display !== 'none';
        }
        
        // Count discovered tools
        const toolItems = document.querySelectorAll('.tool-list li');
        stats.toolsDiscovered = toolItems.length;
        
        // Count conversation entries
        const conversationEntries = document.querySelectorAll('.conversation-entry:not(.empty)');
        stats.conversationEntries = conversationEntries.length;
        
        return stats;
    }

    /**
     * Reset dashboard to initial state
     */
    static resetDashboard() {
        // Reset context memory
        this.updateContextMemory({
            lastQuestion: 'None yet',
            contextEntries: 0,
            toolsChained: 0
        });
        
        // Hide conversation window
        const conversationWindow = document.getElementById('conversationWindow');
        const showBtn = document.getElementById('showConversationBtn');
        
        if (conversationWindow && showBtn) {
            conversationWindow.style.display = 'none';
            showBtn.textContent = 'Show Conversation History';
        }
        
        // Reset conversation history display
        const conversationHistory = document.getElementById('conversationHistory');
        if (conversationHistory) {
            conversationHistory.innerHTML = `
                <div class="conversation-entry empty">
                    <em>No conversation history yet. Ask a question to start building context memory.</em>
                </div>
            `;
        }
        
        // Reset image gallery
        const imageGallery = document.getElementById('imageGallery');
        const thumbnailGrid = document.getElementById('thumbnailGrid');
        
        if (imageGallery && thumbnailGrid) {
            imageGallery.style.display = 'none';
            thumbnailGrid.innerHTML = '<div class="no-images">No images generated yet</div>';
        }
        
        // Hide MCP decision
        const mcpDecision = document.getElementById('mcpDecision');
        if (mcpDecision) {
            mcpDecision.style.display = 'none';
        }
        
        console.log('🔄 MCP Dashboard: Reset to initial state');
    }
}

// Export for global use
if (typeof window !== 'undefined') {
    window.MCPDashboard = MCPDashboard;
}

// Also export for ES6 module usage
// export { MCPDashboard };