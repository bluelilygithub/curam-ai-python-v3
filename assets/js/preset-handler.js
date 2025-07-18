
// Add this JavaScript to handle the select box functionality
// Add to your existing app.js or create separate preset-handler.js

class PresetQuestionHandler {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateButtonState();
    }
    
    setupEventListeners() {
        const presetSelect = document.getElementById('preset-questions');
        const usePresetBtn = document.getElementById('use-preset-btn');
        const questionInput = document.getElementById('property-question');
        const analyzeBtn = document.getElementById('analyze-btn');
        
        // Handle preset selection change
        if (presetSelect) {
            presetSelect.addEventListener('change', () => {
                this.updateButtonState();
            });
        }
        
        // Handle "Use This Question" button
        if (usePresetBtn) {
            usePresetBtn.addEventListener('click', () => {
                this.useSelectedPreset();
            });
        }
        
        // Handle question input changes
        if (questionInput) {
            questionInput.addEventListener('input', () => {
                this.clearPresetSelection();
            });
        }
        
        // Handle analyze button
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                this.analyzeQuestion();
            });
        }
        
        console.log('✅ Preset question handler initialized');
    }
    
    updateButtonState() {
        const presetSelect = document.getElementById('preset-questions');
        const usePresetBtn = document.getElementById('use-preset-btn');
        
        if (presetSelect && usePresetBtn) {
            const hasSelection = presetSelect.value !== '';
            usePresetBtn.disabled = !hasSelection;
            
            if (hasSelection) {
                usePresetBtn.textContent = 'Use This Question';
                usePresetBtn.style.background = '#4f46e5';
                usePresetBtn.style.color = '#ffffff';
                usePresetBtn.style.border = '1px solid #4f46e5';
            } else {
                usePresetBtn.textContent = 'Select a Question First';
                usePresetBtn.style.background = '#f3f4f6';
                usePresetBtn.style.color = '#9ca3af';
                usePresetBtn.style.border = '1px solid #d1d5db';
            }
        }
    }
    
useSelectedPreset() {
    const presetSelect = document.getElementById('preset-questions');
    const questionInput = document.getElementById('property-question');
    
    console.log('🔍 useSelectedPreset called');
    console.log('🔍 presetSelect:', presetSelect);
    console.log('🔍 presetSelect.value:', presetSelect?.value);
    console.log('🔍 questionInput:', questionInput);
    
    if (presetSelect && questionInput && presetSelect.value) {
        console.log('✅ Setting question value to:', presetSelect.value);
        questionInput.value = presetSelect.value;
        questionInput.focus();
        
        // Add visual feedback
        questionInput.style.borderColor = '#059669';
        setTimeout(() => {
            questionInput.style.borderColor = '#4f46e5';
        }, 1000);
        
        console.log('✅ Question set. New value:', questionInput.value);
        console.log('📋 Preset question loaded:', presetSelect.value);
    } else {
        console.error('❌ Missing elements or no preset value');
        console.log('presetSelect exists:', !!presetSelect);
        console.log('questionInput exists:', !!questionInput);
        console.log('presetSelect has value:', !!presetSelect?.value);
    }
}
    
    clearPresetSelection() {
        const presetSelect = document.getElementById('preset-questions');
        const questionInput = document.getElementById('property-question');
        
        // Only clear if user is typing in the input
        if (presetSelect && questionInput && questionInput.value.length > 0) {
            presetSelect.value = '';
            this.updateButtonState();
        }
    }
    
analyzeQuestion() {
    const questionInput = document.getElementById('property-question');
    
    if (!questionInput || !questionInput.value.trim()) {
        this.showError('Please enter a question or select a preset question.');
        return;
    }
    
    const question = questionInput.value.trim();
    
    // FIXED: Connect to your actual app instance
    if (typeof window.app?.analyzeQuestion === 'function') {
        // Set the question in the existing input field
        const customInput = document.getElementById('customQuestion');
        if (customInput) {
            customInput.value = question;
        }
        
        // Call your existing analyze method
        window.app.analyzeQuestion();
    } else {
        // Fallback: trigger the existing analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            // Set the question first
            const customInput = document.getElementById('customQuestion');
            if (customInput) {
                customInput.value = question;
            }
            // Then click the button
            analyzeBtn.click();
        } else {
            this.showError('Analysis function not available. Please refresh the page.');
        }
    }
}
    
    showError(message) {
        // Create temporary error message
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            background: #fef2f2;
            border: 1px solid #fecaca;
            color: #dc2626;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 14px;
            text-align: center;
        `;
        errorDiv.textContent = message;
        
        const analyzeSection = document.querySelector('.analyze-section');
        if (analyzeSection) {
            analyzeSection.insertBefore(errorDiv, analyzeSection.firstChild);
            
            // Remove error after 5 seconds
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
            }, 5000);
        }
    }
    
    // Method to programmatically set a question (useful for external calls)
    setQuestion(question) {
        const questionInput = document.getElementById('property-question');
        const presetSelect = document.getElementById('preset-questions');
        
        if (questionInput) {
            questionInput.value = question;
            
            // Check if it matches a preset
            if (presetSelect) {
                const matchingOption = Array.from(presetSelect.options).find(option => option.value === question);
                if (matchingOption) {
                    presetSelect.value = question;
                } else {
                    presetSelect.value = '';
                }
                this.updateButtonState();
            }
        }
    }
    
    // Get current question
    getCurrentQuestion() {
        const questionInput = document.getElementById('property-question');
        return questionInput ? questionInput.value.trim() : '';
    }
}

// Replace this at the bottom of preset-handler.js:
// Initialize the preset question handler when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.presetHandler = new PresetQuestionHandler();
});

// Also initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.presetHandler = new PresetQuestionHandler();
    });
} else {
    window.presetHandler = new PresetQuestionHandler();
}

// With this:
// Initialize with a delay to ensure all elements are ready
setTimeout(() => {
    window.presetHandler = new PresetQuestionHandler();
    console.log('✅ Preset handler initialized');
}, 1000);