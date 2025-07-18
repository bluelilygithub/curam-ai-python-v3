/**
 * framework/mcp-huggingface.js - Hugging Face API Integration Template
 *
 * USAGE (in apps directory):
 *
 * // If using ES6 modules:
 * import MCPHuggingFace from '../framework/mcp-huggingface.js';
 * const hf = new MCPHuggingFace();
 * await hf.init();
 *
 * // If using global (script tag):
 * const hf = new window.MCPHuggingFace();
 * await hf.init();
 *
 * This class is fully modular and can be imported by any app in the apps directory.
 */

class MCPHuggingFace {
    constructor() {
        this.isEnabled = ConfigUtils.isHuggingFaceEnabled();
        this.apiConfig = ConfigUtils.getHuggingFaceConfig();
        this.availableModels = {
            text: ConfigUtils.getHuggingFaceModels('textModels'),
            image: ConfigUtils.getHuggingFaceModels('imageModels')
        };
    }

    /**
     * Initialize Hugging Face integration
     */
    async init() {
        if (!this.isEnabled) {
            console.log('🔧 MCP Hugging Face: Integration disabled');
            return false;
        }

        try {
            // Test API connection
            const healthCheck = await this.checkHealth();
            if (healthCheck.status === 'healthy') {
                console.log('✅ MCP Hugging Face: Integration initialized');
                return true;
            } else {
                throw new Error('Health check failed');
            }
        } catch (error) {
            console.error('❌ MCP Hugging Face: Initialization failed:', error);
            return false;
        }
    }

    /**
     * Check Hugging Face API health
     */
    async checkHealth() {
        try {
            const response = await fetch(ConfigUtils.getApiUrl('huggingFace') + '/health', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            return { status: 'unhealthy', error: error.message };
        }
    }

    /**
     * Generate text using Hugging Face models
     * @param {string} prompt - Input prompt
     * @param {string} modelId - Model ID (e.g., 'gpt2')
     * @param {Object} options - Generation options
     */
    async generateText(prompt, modelId = 'gpt2', options = {}) {
        if (!this.isEnabled) {
            throw new Error('Hugging Face integration is disabled');
        }

        const defaultOptions = {
            max_length: 100,
            temperature: 0.7,
            do_sample: true
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(ConfigUtils.getApiUrl('huggingFace') + '/generate-text', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt,
                    modelId,
                    options: config
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('MCP Hugging Face Text Generation Error:', error);
            throw error;
        }
    }

    /**
     * Generate image using Hugging Face models
     * @param {string} prompt - Image description
     * @param {string} modelId - Model ID (e.g., 'runwayml/stable-diffusion-v1-5')
     * @param {Object} options - Generation options
     */
    async generateImage(prompt, modelId = 'runwayml/stable-diffusion-v1-5', options = {}) {
        if (!this.isEnabled) {
            throw new Error('Hugging Face integration is disabled');
        }

        const defaultOptions = {
            width: 512,
            height: 512,
            num_inference_steps: 50,
            guidance_scale: 7.5
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(ConfigUtils.getApiUrl('huggingFace') + '/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt,
                    modelId,
                    options: config
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('MCP Hugging Face Image Generation Error:', error);
            throw error;
        }
    }

    /**
     * Compare multiple Hugging Face models
     * @param {string} prompt - Input prompt
     * @param {Array} modelIds - Array of model IDs to compare
     * @param {string} taskType - 'text' or 'image'
     */
    async compareModels(prompt, modelIds, taskType = 'text') {
        if (!this.isEnabled) {
            throw new Error('Hugging Face integration is disabled');
        }

        const results = {};
        const promises = modelIds.map(async (modelId) => {
            try {
                const startTime = Date.now();
                let result;

                if (taskType === 'text') {
                    result = await this.generateText(prompt, modelId);
                } else if (taskType === 'image') {
                    result = await this.generateImage(prompt, modelId);
                }

                const endTime = Date.now();
                const responseTime = endTime - startTime;

                return {
                    modelId,
                    result,
                    responseTime,
                    success: true
                };
            } catch (error) {
                return {
                    modelId,
                    error: error.message,
                    success: false
                };
            }
        });

        const modelResults = await Promise.all(promises);
        modelResults.forEach(result => {
            results[result.modelId] = result;
        });

        return results;
    }

    /**
     * Get available models for a specific task
     * @param {string} taskType - 'text' or 'image'
     * @returns {Array} - Available models
     */
    getAvailableModels(taskType) {
        return this.availableModels[taskType] || [];
    }

    /**
     * Get model information
     * @param {string} modelId - Model ID
     * @returns {Object} - Model information
     */
    getModelInfo(modelId) {
        const allModels = [
            ...this.availableModels.text,
            ...this.availableModels.image
        ];
        return allModels.find(model => model.modelId === modelId) || null;
    }

    /**
     * Log Hugging Face activity
     * @param {string} message - Log message
     */
    logActivity(message) {
        if (ConfigUtils.isFeatureEnabled('debugMode')) {
            console.log(`🤗 MCP Hugging Face: ${message}`);
        }
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.MCPHuggingFace = MCPHuggingFace;
}

// Note: Do not add export statements here - this file is loaded as a regular script, not a module
// Use window.MCPHuggingFace = MCPHuggingFace; for browser compatibility

/**
 * USAGE EXAMPLES:
 *
 * // Initialize
 * const hf = new MCPHuggingFace();
 * await hf.init();
 *
 * // Generate text
 * const textResult = await hf.generateText("Hello world", "gpt2");
 *
 * // Generate image
 * const imageResult = await hf.generateImage("A beautiful sunset", "runwayml/stable-diffusion-v1-5");
 *
 * // Compare models
 * const comparison = await hf.compareModels("Hello world", ["gpt2", "gpt2-medium"], "text");
 *
 * // Get available models
 * const textModels = hf.getAvailableModels("text");
 * const imageModels = hf.getAvailableModels("image");
 */ 