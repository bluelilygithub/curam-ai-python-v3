/**
 * framework/mcp-core.js - Core MCP Workflow and Orchestration Logic
 * 
 * Provides the foundational MCP workflow management, tool discovery,
 * and intelligent orchestration capabilities for all MCP applications.
 */

class MCPWorkflow {
    constructor(stepNames = ['User Input', 'Tool Discovery', 'Text Generation', 'Context Analysis', 'Image Chaining', 'Complete']) {
        this.currentStep = 0;
        this.stepNames = stepNames;
        this.toolsChainedCount = 0;
        this.workflowContainer = null;
    }

    /**
     * Initialize workflow visualization in a container
     * @param {HTMLElement} container - Container element for workflow
     */
    initialize(container) {
        this.workflowContainer = container;
        this.renderWorkflowSteps();
    }

    /**
     * Render workflow steps HTML
     */
    renderWorkflowSteps() {
        if (!this.workflowContainer) return;

        const workflowHTML = `
            <div class="mcp-workflow" id="mcpWorkflow">
                ${this.stepNames.map((stepName, index) => `
                    <div class="workflow-step" id="step${index + 1}">
                        <span class="step-icon">${this.getStepIcon(index)}</span>
                        <div class="step-text">${stepName}</div>
                    </div>
                `).join('')}
            </div>
        `;

        this.workflowContainer.innerHTML = workflowHTML;
    }

    /**
     * Get appropriate icon for workflow step
     * @param {number} stepIndex - Step index
     * @returns {string} - Emoji icon
     */
    getStepIcon(stepIndex) {
        const icons = ['👤', '🔧', '🤖', '🧠', '🎨', '✅'];
        return icons[stepIndex] || '⚡';
    }

    /**
     * Update workflow step status
     * @param {number} stepNumber - Step number (1-based)
     * @param {string} status - Status: 'active', 'completed', 'waiting'
     */
    updateWorkflowStep(stepNumber, status = 'active') {
        // Reset all steps
        for (let i = 1; i <= this.stepNames.length; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                step.classList.remove('active', 'completed');
                if (i < stepNumber) {
                    step.classList.add('completed');
                } else if (i === stepNumber) {
                    step.classList.add(status);
                }
            }
        }
        this.currentStep = stepNumber;
        this.logMCP(`Workflow step ${stepNumber} (${this.stepNames[stepNumber - 1]}) -> ${status}`);
    }

    /**
     * Complete the entire workflow
     */
    completeWorkflow() {
        this.updateWorkflowStep(this.stepNames.length, 'completed');
        this.logMCP('Workflow completed successfully');
    }

    /**
     * Reset workflow to initial state
     */
    resetWorkflow() {
        this.currentStep = 0;
        this.toolsChainedCount = 0;
        for (let i = 1; i <= this.stepNames.length; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                step.classList.remove('active', 'completed');
            }
        }
        this.logMCP('Workflow reset');
    }

    /**
     * Log MCP activity
     * @param {string} message - Log message
     */
    logMCP(message) {
        if (typeof ConfigUtils !== 'undefined' && ConfigUtils.isFeatureEnabled && ConfigUtils.isFeatureEnabled('debugMode')) {
            console.log(`🔧 MCP Core: ${message}`);
        } else {
            console.log(`🔧 MCP Core: ${message}`);
        }
    }
}

class MCPDecisionEngine {
    constructor() {
        this.decisionContainer = null;
    }

    /**
     * Initialize decision display
     * @param {HTMLElement} container - Container for decision display
     */
    initialize(container) {
        this.decisionContainer = container;
        if (container) {
            container.innerHTML = `
                <div class="mcp-decision" id="mcpDecision" style="display: none;">
                    <h4>🧠 MCP Intelligence Active</h4>
                    <p id="decisionText">Analyzing context for intelligent tool chaining...</p>
                </div>
            `;
        }
    }

    /**
     * Show MCP decision with reasoning
     * @param {string} text - Decision explanation
     * @param {number} duration - How long to show (ms), 0 = permanent
     */
    showDecision(text, duration = 5000) {
        const decisionDiv = document.getElementById('mcpDecision');
        const decisionText = document.getElementById('decisionText');
        
        if (decisionDiv && decisionText) {
            decisionText.textContent = text;
            decisionDiv.style.display = 'block';
            
            if (duration > 0) {
                setTimeout(() => {
                    decisionDiv.style.display = 'none';
                }, duration);
            }
        }
        
        console.log(`🧠 MCP Decision: ${text}`);
    }

    /**
     * Hide decision display
     */
    hideDecision() {
        const decisionDiv = document.getElementById('mcpDecision');
        if (decisionDiv) {
            decisionDiv.style.display = 'none';
        }
    }
}

class MCPToolOrchestrator {
    constructor() {
        this.availableTools = [];
        this.executionHistory = [];
    }

    /**
     * Register available tools
     * @param {Array} tools - Array of tool objects
     */
    registerTools(tools) {
        this.availableTools = tools;
        this.logMCP(`Registered ${tools.length} tools: ${tools.map(t => t.name).join(', ')}`);
    }

    /**
     * Discover and display available tools
     * @param {HTMLElement} container - Container for tool display
     */
    displayToolDiscovery(container) {
        if (!container) return;

        const toolsHTML = `
            <div class="tool-discovery">
                <h4>🔧 Available Tools (Auto-Discovered)</h4>
                <ul class="tool-list">
                    ${this.availableTools.map(tool => `
                        <li>
                            <span class="tool-status">✅</span>
                            <span class="tool-name">${tool.name}</span>
                            <span class="tool-description">${tool.description}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;

        container.innerHTML = toolsHTML;
    }

    /**
     * Execute tool orchestration workflow
     * @param {string} prompt - User input prompt
     * @param {Object} context - Current context
     * @param {Function} progressCallback - Callback for progress updates
     * @returns {Object} - Execution results
     */
    async executeWorkflow(prompt, context = {}, progressCallback = null) {
        const execution = {
            id: Date.now(),
            prompt: prompt,
            context: context,
            toolsUsed: [],
            results: {},
            startTime: new Date(),
            endTime: null
        };

        try {
            // Step 1: Analyze prompt for tool requirements
            if (progressCallback) progressCallback(1, 'Analyzing prompt for tool requirements');
            const requiredTools = this.analyzePromptForTools(prompt);
            
            // Step 2: Execute primary tool (usually text generation)
            if (progressCallback) progressCallback(2, 'Executing primary text generation');
            const primaryResult = await this.executePrimaryTool(prompt, context);
            execution.results.primary = primaryResult;
            execution.toolsUsed.push('text_generation');

            // Step 3: Determine if secondary tools should be chained
            if (progressCallback) progressCallback(3, 'Analyzing for intelligent tool chaining');
            const shouldChainTools = this.shouldChainAdditionalTools(prompt, primaryResult, context);
            
            if (shouldChainTools.should) {
                // Step 4: Execute secondary tools
                if (progressCallback) progressCallback(4, `Chaining ${shouldChainTools.tools.join(', ')}`);
                
                for (const toolName of shouldChainTools.tools) {
                    const secondaryResult = await this.executeSecondaryTool(toolName, prompt, primaryResult, context);
                    execution.results[toolName] = secondaryResult;
                    execution.toolsUsed.push(toolName);
                }
            }

            execution.endTime = new Date();
            this.executionHistory.push(execution);
            
            this.logMCP(`Workflow completed. Tools used: ${execution.toolsUsed.join(', ')}`);
            return execution;

        } catch (error) {
            execution.error = error.message;
            execution.endTime = new Date();
            this.logMCP(`Workflow failed: ${error.message}`);
            throw error;
        }
    }

    /**
     * Analyze prompt to determine required tools
     * @param {string} prompt - User prompt
     * @returns {Array} - Array of required tool names
     */
    analyzePromptForTools(prompt) {
        const requiredTools = ['text_generation']; // Always need text generation
        
        // Check for image-related keywords
        const imageKeywords = ['image', 'picture', 'draw', 'visualize', 'show me', 'create'];
        if (imageKeywords.some(keyword => prompt.toLowerCase().includes(keyword))) {
            requiredTools.push('image_generation');
        }

        // Check for comparison keywords
        const compareKeywords = ['compare', 'versus', 'vs', 'difference', 'better'];
        if (compareKeywords.some(keyword => prompt.toLowerCase().includes(keyword))) {
            requiredTools.push('model_comparison');
        }

        return requiredTools;
    }

    /**
     * Execute primary tool (text generation)
     * @param {string} prompt - User prompt
     * @param {Object} context - Context object
     * @returns {Object} - Primary tool results
     */
    async executePrimaryTool(prompt, context) {
        // This should be overridden by the implementing application
        // Default implementation returns a placeholder
        return {
            response: "Primary tool executed successfully",
            metadata: { tool: 'text_generation', timestamp: new Date() }
        };
    }

    /**
     * Determine if additional tools should be chained
     * @param {string} prompt - Original prompt
     * @param {Object} primaryResult - Result from primary tool
     * @param {Object} context - Current context
     * @returns {Object} - Decision object with should and tools properties
     */
    shouldChainAdditionalTools(prompt, primaryResult, context) {
        const decision = { should: false, tools: [], reasoning: '' };

        // Check if auto-chaining is enabled
        const autoChainEnabled = typeof ConfigUtils !== 'undefined' && 
                                 ConfigUtils.isFeatureEnabled && 
                                 ConfigUtils.isFeatureEnabled('autoImageGeneration');
        if (!autoChainEnabled) {
            decision.reasoning = 'Auto-chaining disabled in configuration';
            return decision;
        }

        // Analyze primary result for visual concepts
        if (primaryResult && primaryResult.response && typeof primaryResult.response === 'string') {
            const visualKeywords = this.extractVisualKeywords(primaryResult.response);
            
            if (visualKeywords.length > 0) {
                decision.should = true;
                decision.tools.push('image_generation');
                decision.reasoning = `Detected visual concepts: ${visualKeywords.join(', ')}`;
            }
        }

        return decision;
    }

    /**
     * Execute secondary/chained tool
     * @param {string} toolName - Name of tool to execute
     * @param {string} originalPrompt - Original user prompt
     * @param {Object} primaryResult - Result from primary tool
     * @param {Object} context - Current context
     * @returns {Object} - Secondary tool results
     */
    async executeSecondaryTool(toolName, originalPrompt, primaryResult, context) {
        // This should be overridden by implementing applications
        // Default implementation returns a placeholder
        return {
            response: `Secondary tool ${toolName} executed successfully`,
            metadata: { 
                tool: toolName, 
                timestamp: new Date(),
                triggeredBy: 'intelligent_chaining'
            }
        };
    }

    /**
     * Extract visual keywords from text
     * @param {string} text - Text to analyze
     * @returns {Array} - Array of visual keywords found
     */
    extractVisualKeywords(text) {
        const visualTerms = [
            'architecture', 'building', 'city', 'landscape', 'mountain', 'river', 'ocean', 'forest',
            'castle', 'bridge', 'tower', 'church', 'temple', 'garden', 'park', 'street', 'market',
            'sunset', 'sunrise', 'sky', 'clouds', 'nature', 'flowers', 'trees', 'animals', 'people',
            'map', 'nation', 'country', 'region', 'territory', 'historical', 'cultural'
        ];

        return visualTerms.filter(term => text.toLowerCase().includes(term));
    }

    /**
     * Get execution statistics
     * @returns {Object} - Statistics about tool usage
     */
    getExecutionStats() {
        return {
            totalExecutions: this.executionHistory.length,
            toolUsageCount: this.executionHistory.reduce((acc, exec) => {
                exec.toolsUsed.forEach(tool => {
                    acc[tool] = (acc[tool] || 0) + 1;
                });
                return acc;
            }, {}),
            averageExecutionTime: this.executionHistory.length > 0 
                ? this.executionHistory.reduce((acc, exec) => 
                    acc + (exec.endTime - exec.startTime), 0) / this.executionHistory.length 
                : 0
        };
    }

    /**
     * Log MCP orchestrator activity
     * @param {string} message - Log message
     */
    logMCP(message) {
        if (typeof ConfigUtils !== 'undefined' && ConfigUtils.isFeatureEnabled && ConfigUtils.isFeatureEnabled('debugMode')) {
            console.log(`🔧 MCP Orchestrator: ${message}`);
        } else {
            console.log(`🔧 MCP Orchestrator: ${message}`);
        }
    }
}

// Export classes for global use
if (typeof window !== 'undefined') {
    window.MCPWorkflow = MCPWorkflow;
    window.MCPDecisionEngine = MCPDecisionEngine;
    window.MCPToolOrchestrator = MCPToolOrchestrator;
}

// Also export for ES6 module usage
// export { MCPWorkflow, MCPDecisionEngine, MCPToolOrchestrator };