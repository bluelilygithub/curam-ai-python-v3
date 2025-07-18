/**
 * framework/mcp-pdf-export.js - PDF Generation and Export Module
 * 
 * Handles all PDF-related functionality including:
 * - Full PDF generation with embedded images
 * - Optimized PDF for email attachments
 * - HTML fallback for print dialog
 * - Text cleaning and formatting for PDF compatibility
 */

class MCPPDFExport {
    constructor() {
        this.jsPDF = window.jspdf.jsPDF;
        this.html2canvas = window.html2canvas;
        this.isAvailable = !!(this.jsPDF && this.html2canvas);
    }

    /**
     * Main PDF export function
     * @param {Object} session - MCP session object with conversation history and images
     * @param {Object} options - Export options
     * @returns {Promise} - Export completion promise
     */
    static async exportToPDF(session, options = {}) {
        if (!session || (session.conversationHistory.length === 0 && session.imageGallery.length === 0)) {
            throw new Error('No conversation history or images to export!');
        }

        const defaultOptions = {
            includeImages: true,
            maxConversations: null, // null = all
            filename: null,
            showProgress: true
        };
        
        const config = { ...defaultOptions, ...options };

        try {
            // Check if jsPDF is available
            if (typeof window.jspdf !== 'undefined') {
                await this.generateAdvancedPDFWithImages(session, config);
            } else {
                // Fallback to print method
                const pdfContent = await this.generatePDFContent(session, config);
                this.downloadPDF(pdfContent);
            }
            
            console.log('🔧 MCP PDF: Export completed successfully');
            return { success: true, method: typeof window.jspdf !== 'undefined' ? 'jsPDF' : 'print' };
            
        } catch (error) {
            console.error('PDF Export Error:', error);
            throw new Error(`PDF generation failed: ${error.message}`);
        }
    }

    /**
     * Generate advanced PDF with full images using jsPDF
     * @param {Object} session - MCP session object
     * @param {Object} config - Generation configuration
     */
    static async generateAdvancedPDFWithImages(session, config) {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        let yPosition = 20;
        
        // Set default font to avoid encoding issues
        pdf.setFont('helvetica');
        
        // Header Section
        yPosition = this.addPDFHeader(pdf, pageWidth, yPosition);
        
        // Session Summary Box
        yPosition = this.addSessionSummary(pdf, session, pageWidth, pageHeight, yPosition);
        
        // Conversation History Section
        if (session.conversationHistory.length > 0) {
            yPosition = await this.addConversationHistory(pdf, session, config, pageWidth, pageHeight, yPosition);
        }
        
        // Images Section with actual embedded images
        if (config.includeImages && session.imageGallery.length > 0) {
            yPosition = await this.addImagesSection(pdf, session, pageWidth, pageHeight, yPosition);
        }
        
        // Add footers to all pages
        this.addPDFFooters(pdf);
        
        // Save the PDF
        const filename = config.filename || `MCP_Session_Report_${new Date().toISOString().slice(0, 10)}.pdf`;
        pdf.save(filename);
        
        console.log(`✅ MCP PDF: Advanced PDF generated with ${session.imageGallery.length} images`);
    }

    /**
     * Generate optimized PDF for email attachments (smaller file size)
     * @param {Object} session - MCP session object
     * @param {Object} pdf - jsPDF instance
     * @param {Object} options - PDF generation options
     */
    static async generatePDFForEmail(session, pdf, options = {}) {
        if (!session) return;

        const defaultOptions = {
            maxImages: 3,  // Default to 3 images for email
            emailOptimized: true
        };
        const config = { ...defaultOptions, ...options };

        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        let yPosition = 20;
        
        // Set default font to avoid encoding issues
        pdf.setFont('helvetica');
        
        // Header (simplified for email)
        yPosition = this.addPDFHeader(pdf, pageWidth, yPosition, { simplified: true });
        
        // Session Summary (compact)
        yPosition = this.addSessionSummary(pdf, session, pageWidth, pageHeight, yPosition, { compact: true });
        
        // Key Conversation Points (LIMITED for email size)
        if (session.conversationHistory.length > 0) {
            yPosition = await this.addConversationHistory(pdf, session, 
                { maxConversations: 3, emailOptimized: true }, 
                pageWidth, pageHeight, yPosition);
        }

        // Include Images for email (configurable count)
        if (session.imageGallery.length > 0 && config.maxImages > 0) {
            yPosition = await this.addImagesSection(pdf, session, pageWidth, pageHeight, yPosition, {
                emailOptimized: true,
                maxImages: config.maxImages,
                imageSize: { width: 40, height: 30 }
            });
        }
        
        console.log(`✅ MCP PDF: Email-optimized PDF generated (maxImages: ${config.maxImages})`);
    }

    /**
     * Generate a PDF with the same layout as the downloadable PDF, but without images.
     * Optionally adds a note that images are attached separately (for email).
     * @param {Object} session - MCP session object
     * @param {Object} options - { noteForEmail: boolean, filename: string }
     * @returns {Promise<string>} - PDF as base64 string (no data URI prefix)
     */
    static async generatePDFWithoutImages(session, options = {}) {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        let yPosition = 20;

        pdf.setFont('helvetica');
        yPosition = this.addPDFHeader(pdf, pageWidth, yPosition);
        yPosition = this.addSessionSummary(pdf, session, pageWidth, pageHeight, yPosition);

        if (session.conversationHistory.length > 0) {
            yPosition = await this.addConversationHistory(pdf, session, options, pageWidth, pageHeight, yPosition);
        }

        // Add note about images if requested
        if (options.noteForEmail) {
            pdf.setFontSize(10);
            pdf.setTextColor(180, 80, 0);
            pdf.text('Note: Images generated in this session are attached separately to this email.', 20, yPosition + 10);
            yPosition += 15;
        }

        this.addPDFFooters(pdf);

        // Return base64 for email attachment
        return pdf.output('datauristring').split(',')[1];
    }

    /**
     * Add PDF header section
     * @param {jsPDF} pdf - PDF instance
     * @param {number} pageWidth - Page width
     * @param {number} yPosition - Current Y position
     * @param {Object} options - Header options
     * @returns {number} - New Y position
     */
    static addPDFHeader(pdf, pageWidth, yPosition, options = {}) {
        const { simplified = false } = options;
        
        // Main title
        pdf.setFontSize(simplified ? 18 : 20);
        pdf.setTextColor(0, 115, 170);
        pdf.text('Curam AI MCP Session Report', pageWidth / 2, yPosition, { align: 'center' });
        
        yPosition += simplified ? 8 : 10;
        
        // Subtitle
        pdf.setFontSize(simplified ? 10 : 12);
        pdf.setTextColor(102, 102, 102);
        pdf.text('Model Context Protocol - Intelligent Tool Orchestration', pageWidth / 2, yPosition, { align: 'center' });
        
        yPosition += simplified ? 6 : 8;
        
        // Generation date
        pdf.text('Generated on ' + new Date().toLocaleString(), pageWidth / 2, yPosition, { align: 'center' });
        
        return yPosition + (simplified ? 15 : 20);
    }

    /**
     * Add session summary section
     * @param {jsPDF} pdf - PDF instance
     * @param {Object} session - Session object
     * @param {number} pageWidth - Page width
     * @param {number} pageHeight - Page height
     * @param {number} yPosition - Current Y position
     * @param {Object} options - Summary options
     * @returns {number} - New Y position
     */
    static addSessionSummary(pdf, session, pageWidth, pageHeight, yPosition, options = {}) {
        const { compact = false } = options;
        const boxHeight = compact ? 20 : 30;
        
        // Summary box background
        pdf.setDrawColor(0, 115, 170);
        pdf.setFillColor(240, 248, 255);
        pdf.rect(20, yPosition - 5, pageWidth - 40, boxHeight, 'FD');
        
        // Title
        pdf.setFontSize(compact ? 12 : 14);
        pdf.setTextColor(0, 115, 170);
        pdf.text('Session Summary', 25, yPosition + 5);
        
        // Summary data
        pdf.setFontSize(compact ? 9 : 10);
        pdf.setTextColor(51, 51, 51);
        pdf.text('Total Questions: ' + session.conversationHistory.length, 25, yPosition + 12);
        pdf.text('Images Generated: ' + session.imageGallery.length, 25, yPosition + (compact ? 16 : 18));
        pdf.text('MCP Features: Context Memory, Tool Chaining', pageWidth / 2, yPosition + 12);
        
        if (!compact) {
            pdf.text('Session Duration: ' + this.getSessionDuration(session), pageWidth / 2, yPosition + 18);
        }
        
        return yPosition + boxHeight + 10;
    }

    /**
     * Add conversation history section
     * @param {jsPDF} pdf - PDF instance
     * @param {Object} session - Session object
     * @param {Object} config - Configuration
     * @param {number} pageWidth - Page width
     * @param {number} pageHeight - Page height
     * @param {number} yPosition - Current Y position
     * @returns {number} - New Y position
     */
    static async addConversationHistory(pdf, session, config, pageWidth, pageHeight, yPosition) {
        const { maxConversations = null, emailOptimized = false } = config;
        
        // Section title
        pdf.setFontSize(14);
        pdf.setTextColor(0, 115, 170);
        const sectionTitle = emailOptimized ? 'Key Conversation Points' : 'Conversation History';
        pdf.text(sectionTitle, 20, yPosition);
        yPosition += 10;
        
        // Determine how many conversations to include
        const conversationsToShow = maxConversations ? 
            Math.min(maxConversations, session.conversationHistory.length) : 
            session.conversationHistory.length;
        
        for (let i = 0; i < conversationsToShow; i++) {
            const entry = session.conversationHistory[i];
            
            // Check if we need a new page
            if (yPosition > pageHeight - (emailOptimized ? 30 : 50)) {
                pdf.addPage();
                yPosition = 20;
            }
            
            // Question
            pdf.setFontSize(emailOptimized ? 10 : 11);
            pdf.setTextColor(0, 115, 170);
            const cleanQuestion = this.cleanTextForPDF(entry.question);
            pdf.text('Q' + (i + 1) + ': ' + cleanQuestion, 20, yPosition);
            yPosition += emailOptimized ? 6 : 8;
            
            // Response
            pdf.setFontSize(emailOptimized ? 8 : 9);
            pdf.setTextColor(51, 51, 51);
            const responseLength = emailOptimized ? 100 : 300;
            const cleanResponse = this.formatResponseForPDF(entry.response.substring(0, responseLength)) + 
                (entry.response.length > responseLength ? '...' : '');
            const splitText = pdf.splitTextToSize(cleanResponse, pageWidth - (emailOptimized ? 40 : 50));
            pdf.text(splitText, emailOptimized ? 25 : 30, yPosition);
            yPosition += splitText.length * (emailOptimized ? 3 : 4) + (emailOptimized ? 8 : 5);
            
            // Timestamp (only for full PDF)
            if (!emailOptimized) {
                pdf.setFontSize(8);
                pdf.setTextColor(153, 153, 153);
                pdf.text('Time: ' + entry.timestamp, pageWidth - 30, yPosition - 2, { align: 'right' });
                yPosition += 10;
            }
        }
        
        // Add note if there are more conversations
        if (maxConversations && session.conversationHistory.length > maxConversations) {
            pdf.setFontSize(9);
            pdf.setTextColor(102, 102, 102);
            const moreText = '... and ' + (session.conversationHistory.length - maxConversations) + 
                ' more questions' + (emailOptimized ? ' (full report available via Export PDF)' : '');
            pdf.text(moreText, 20, yPosition);
            yPosition += 15;
        }
        
        return yPosition;
    }

    /**
     * Add images section to PDF
     * @param {jsPDF} pdf - PDF instance
     * @param {Object} session - Session object
     * @param {number} pageWidth - Page width
     * @param {number} pageHeight - Page height
     * @param {number} yPosition - Current Y position
     * @param {Object} options - Image options
     * @returns {number} - New Y position
     */
    static async addImagesSection(pdf, session, pageWidth, pageHeight, yPosition, options = {}) {
        const defaultOptions = {
            emailOptimized: false,
            maxImages: null,
            imageSize: { width: 60, height: 45 }
        };
        
        const config = { ...defaultOptions, ...options };
        
        // Add new page for images if needed
        if (yPosition > pageHeight - 80) {
            pdf.addPage();
            yPosition = 20;
        }
        
        // Section title
        pdf.setFontSize(14);
        pdf.setTextColor(0, 115, 170);
        pdf.text('Generated Images', 20, yPosition);
        yPosition += 15;
        
        // Determine how many images to include
        const imagesToShow = config.maxImages ? 
            Math.min(config.maxImages, session.imageGallery.length) : 
            session.imageGallery.length;
        
        let validImages = 0;
        for (let i = 0; i < imagesToShow; i++) {
            const image = session.imageGallery[i];
            console.log(`🔍 Processing image ${i + 1}:`, image);
            if (!image.imageBase64 || image.imageBase64.includes('[truncated]')) {
                console.warn(`⚠️ Skipping image ${i + 1}: imageBase64 is missing or truncated.`);
                continue;
            }
            try {
                // Add image to PDF
                const imgData = 'data:image/png;base64,' + image.imageBase64;
                pdf.addImage(imgData, 'PNG', 20, yPosition, config.imageSize.width, config.imageSize.height);
                validImages++;
                // Image info next to the image
                const infoX = 20 + config.imageSize.width + 5;
                let infoY = yPosition + 10;
                pdf.setFontSize(10);
                pdf.setTextColor(51, 51, 51);
                pdf.text('Image ' + (i + 1), infoX, infoY);
                infoY += 8;
                pdf.setFontSize(config.emailOptimized ? 8 : 9);
                pdf.setTextColor(102, 102, 102);
                pdf.text('Prompt:', infoX, infoY);
                infoY += 5;
                const cleanPrompt = this.cleanTextForPDF(image.prompt);
                const promptText = cleanPrompt.length > 60 ? 
                    cleanPrompt.substring(0, 60) + '...' : cleanPrompt;
                const splitPrompt = pdf.splitTextToSize(promptText, pageWidth - infoX - 20);
                pdf.text(splitPrompt, infoX, infoY);
                infoY += splitPrompt.length * 4 + 3;
                pdf.setFontSize(config.emailOptimized ? 7 : 8);
                pdf.setTextColor(102, 102, 102);
                pdf.text('Style: ' + image.style, infoX, infoY);
                if (!config.emailOptimized) {
                    infoY += 5;
                    pdf.text('Generated: ' + image.timestamp, infoX, infoY);
                }
                if (image.isAutoGenerated) {
                    infoY += 5;
                    pdf.setTextColor(70, 180, 80);
                    pdf.text('MCP Auto-Generated', infoX, infoY);
                }
                yPosition += config.imageSize.height + 15;
                console.log(`✅ MCP PDF: Added image ${i + 1} to PDF`);
            } catch (error) {
                console.warn(`Could not add image ${i + 1} to PDF:`, error);
                // Add placeholder for failed image
                pdf.setFontSize(10);
                pdf.setTextColor(200, 200, 200);
                pdf.rect(20, yPosition, config.imageSize.width, config.imageSize.height);
                pdf.text('Image not', 30, yPosition + 20);
                pdf.text('available', 30, yPosition + 30);
                pdf.setFontSize(10);
                pdf.setTextColor(51, 51, 51);
                pdf.text('Image ' + (i + 1) + ' (Error loading)', 90, yPosition + 15);
                yPosition += config.imageSize.height + 15;
            }
        }
        if (validImages === 0 && imagesToShow > 0) {
            pdf.setFontSize(10);
            pdf.setTextColor(200, 0, 0);
            pdf.text('No valid images could be exported. Please clear your session and generate new images.', 20, yPosition + 10);
            yPosition += 20;
        }
        // Add note if there are more images
        if (config.maxImages && session.imageGallery.length > config.maxImages) {
            pdf.setFontSize(9);
            pdf.setTextColor(102, 102, 102);
            const moreText = '... and ' + (session.imageGallery.length - config.maxImages) + 
                ' more images' + (config.emailOptimized ? ' in full export' : '');
            pdf.text(moreText, 20, yPosition);
            yPosition += 15;
        }
        return yPosition;
    }

    /**
     * Add footers to all pages
     * @param {jsPDF} pdf - PDF instance
     */
    static addPDFFooters(pdf) {
        const totalPages = pdf.internal.getNumberOfPages();
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        
        for (let i = 1; i <= totalPages; i++) {
            pdf.setPage(i);
            pdf.setFontSize(8);
            pdf.setTextColor(153, 153, 153);
            pdf.text('Generated by Curam AI MCP Agent', pageWidth / 2, pageHeight - 10, { align: 'center' });
            pdf.text('Page ' + i + ' of ' + totalPages, pageWidth - 20, pageHeight - 10, { align: 'right' });
        }
    }

    /**
     * Generate PDF content as HTML (fallback method)
     * @param {Object} session - Session object
     * @param {Object} config - Configuration
     * @returns {string} - HTML content for printing
     */
    static async generatePDFContent(session, config) {
        const timestamp = new Date().toLocaleString();
        const sessionDuration = this.getSessionDuration(session);
        
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
                    @media print {
                        body { margin: 0; padding: 15px; }
                        .image-grid { grid-template-columns: repeat(2, 1fr); }
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
                    <p><strong>Total Questions:</strong> ${session.conversationHistory.length}</p>
                    <p><strong>Images Generated:</strong> ${session.imageGallery.length}</p>
                    <p><strong>Session Duration:</strong> ${sessionDuration}</p>
                    <p><strong>MCP Features:</strong> Context Memory, Tool Chaining</p>
                </div>
        `;

        // Add conversation history
        if (session.conversationHistory.length > 0) {
            htmlContent += `<h2>Conversation History</h2>`;
            
            const conversationsToShow = config.maxConversations || session.conversationHistory.length;
            for (let i = 0; i < Math.min(conversationsToShow, session.conversationHistory.length); i++) {
                const entry = session.conversationHistory[i];
                htmlContent += `
                    <div class="conversation-item">
                        <div><strong>Question ${i + 1}:</strong> ${entry.question}</div>
                        <div style="margin-top: 10px;"><strong>Response:</strong> ${this.formatResponseForPDF(entry.response)}</div>
                        <div style="margin-top: 10px; color: #666; font-size: 0.9em;">${entry.timestamp}</div>
                    </div>
                `;
            }
        }

        // Add images section
        if (config.includeImages && session.imageGallery.length > 0) {
            htmlContent += `
                <h2>Generated Images</h2>
                <div class="image-grid">
            `;
            
            session.imageGallery.forEach((image, index) => {
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
     * @param {string} htmlContent - HTML content to print
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

    /**
     * Clean text for PDF generation to avoid encoding issues
     * @param {string} text - Text to clean
     * @returns {string} - Cleaned text safe for PDF
     */
    static cleanTextForPDF(text) {
        if (!text || typeof text !== 'string') return '';
        
        return text
            // Convert <li> to bullet points
            .replace(/<li[^>]*>/gi, '\n* ')
            // Remove </li>
            .replace(/<\/li>/gi, '')
            // Remove <ul> and </ul>
            .replace(/<ul[^>]*>/gi, '')
            .replace(/<\/ul>/gi, '')
            // Convert <br> and <br/> to newlines
            .replace(/<br\s*\/?>/gi, '\n')
            // Remove all other HTML tags
            .replace(/<[^>]*>/g, '')
            // Decode HTML entities
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&')
            .replace(/&quot;/g, '"')
            .replace(/&#39;/g, "'")
            .replace(/&nbsp;/g, ' ')
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
     * Format response text for PDF display
     * @param {string} response - AI response text
     * @returns {string} - Cleaned response for PDF
     */
    static formatResponseForPDF(response) {
        if (!response || typeof response !== 'string') return '';
        
        // Clean up response for PDF - remove HTML and excessive formatting but preserve content
        let cleanedResponse = this.cleanTextForPDF(response);
        
        // Additional cleaning for common formatting patterns
        cleanedResponse = cleanedResponse
            .replace(/\*\*/g, '') // Remove bold markers
            .replace(/\*/g, '') // Remove bullet markers
            .replace(/\n/g, ' ') // Replace newlines with spaces
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim();
        
        // Limit length for PDF readability
        const maxLength = 800; // Increased from 500 for better content preservation
        return cleanedResponse.length > maxLength 
            ? cleanedResponse.substring(0, maxLength) + '...' 
            : cleanedResponse;
    }

    /**
     * Get session duration for display
     * @param {Object} session - Session object
     * @returns {string} - Formatted session duration
     */
    static getSessionDuration(session) {
        if (!session || session.conversationHistory.length === 0) {
            return 'No activity';
        }
        
        const firstTime = session.conversationHistory[0].timestamp;
        const lastTime = session.conversationHistory[session.conversationHistory.length - 1].timestamp;
        
        return `${firstTime} - ${lastTime}`;
    }

    /**
     * Validate session object for PDF generation
     * @param {Object} session - Session object to validate
     * @returns {boolean} - Whether session is valid
     */
    static validateSession(session) {
        if (!session) return false;
        if (!Array.isArray(session.conversationHistory)) return false;
        if (!Array.isArray(session.imageGallery)) return false;
        return session.conversationHistory.length > 0 || session.imageGallery.length > 0;
    }

    /**
     * Get PDF generation statistics
     * @param {Object} session - Session object
     * @returns {Object} - Statistics about what will be included in PDF
     */
    static getPDFStats(session, options = {}) {
        if (!this.validateSession(session)) {
            return { valid: false, error: 'Invalid session data' };
        }

        const stats = {
            valid: true,
            conversations: session.conversationHistory.length,
            images: session.imageGallery.length,
            estimatedPages: 1, // Header + summary
            features: []
        };

        // Estimate pages based on content
        if (session.conversationHistory.length > 0) {
            stats.estimatedPages += Math.ceil(session.conversationHistory.length / 3); // ~3 conversations per page
            stats.features.push('Conversation History');
        }

        if (options.includeImages !== false && session.imageGallery.length > 0) {
            stats.estimatedPages += Math.ceil(session.imageGallery.length / 2); // ~2 images per page
            stats.features.push('Embedded Images');
        }

        // Estimate file size (rough)
        const baseSize = 50; // KB for text content
        const imageSize = session.imageGallery.length * 100; // ~100KB per image
        stats.estimatedSizeKB = baseSize + (options.includeImages !== false ? imageSize : 0);

        return stats;
    }
}

// Export for global use
if (typeof window !== 'undefined') {
    window.MCPPDFExport = MCPPDFExport;
}

// Also export for ES6 module usage
// export { MCPPDFExport };