class CSVQAMaker {
    constructor() {
        this.baseURL = 'http://localhost:5000';
        this.selectedFile = null;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.fileUploadArea = document.getElementById('fileUploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.questionInput = document.getElementById('questionInput');
        this.submitBtn = document.getElementById('submitBtn');
        this.loading = document.getElementById('loading');
        this.loadingTitle = document.getElementById('loadingTitle');
        this.loadingSubtitle = document.getElementById('loadingSubtitle');
        this.loadingStatus = document.getElementById('loadingStatus');
        this.loadingTimer = document.getElementById('loadingTimer');
        this.progressFill = document.getElementById('progressFill');
        this.step1 = document.getElementById('step1');
        this.step2 = document.getElementById('step2');
        this.step3 = document.getElementById('step3');
        this.step4 = document.getElementById('step4');
        this.responseSection = document.getElementById('responseSection');
        this.responseTitle = document.getElementById('responseTitle');
        this.responseContent = document.getElementById('responseContent');
        this.responseHeader = document.getElementById('responseHeader');
        this.responseStatus = document.getElementById('responseStatus');
        this.responseTimestamp = document.getElementById('responseTimestamp');
        this.responseMeta = document.getElementById('responseMeta');
        this.responseAnswer = document.getElementById('responseAnswer');
        this.responseActions = document.getElementById('responseActions');
        this.copyBtn = document.getElementById('copyBtn');
        this.clearBtn = document.getElementById('clearBtn');
    }

    attachEventListeners() {
        // File upload area click
        this.fileUploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Drag and drop events
        this.fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.fileUploadArea.classList.add('dragover');
        });

        this.fileUploadArea.addEventListener('dragleave', () => {
            this.fileUploadArea.classList.remove('dragover');
        });

        this.fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.fileUploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) {
                this.handleFileSelect(file);
            }
        });

        // Question input change
        this.questionInput.addEventListener('input', () => {
            this.updateSubmitButton();
        });

        // Submit button click
        this.submitBtn.addEventListener('click', () => {
            this.submitQuestion();
        });

        // Enter key in question input
        this.questionInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.submitQuestion();
            }
        });

        // Copy button click
        this.copyBtn.addEventListener('click', () => {
            this.copyResponseToClipboard();
        });

        // Clear button click
        this.clearBtn.addEventListener('click', () => {
            this.clearResponse();
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.csv')) {
            this.showError('Please select a CSV file.');
            return;
        }

        // Validate file size (16MB)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('File size exceeds 16MB limit.');
            return;
        }

        this.selectedFile = file;
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.fileInfo.classList.add('show');
        this.updateSubmitButton();
        this.hideResponse();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    updateSubmitButton() {
        const hasFile = this.selectedFile !== null;
        const hasQuestion = this.questionInput.value.trim() !== '';
        this.submitBtn.disabled = !hasFile || !hasQuestion;
    }

    async submitQuestion() {
        if (!this.selectedFile || !this.questionInput.value.trim()) {
            return;
        }

        const startTime = Date.now();

        try {
            this.showLoadingWithProgress();
            this.hideResponse();

            // Step 1: Upload
            this.updateLoadingStep(1, 'Uploading file...', 20);
            await this.delay(500); // Simulate upload time

            // Step 2: Process
            this.updateLoadingStep(2, 'Processing CSV data...', 40);
            
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            formData.append('question', this.questionInput.value.trim());

            await this.delay(300); // Brief pause for UX

            // Step 3: Analyze
            this.updateLoadingStep(3, 'AI is analyzing your data...', 60);

            const response = await fetch(`${this.baseURL}/chat`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            // Step 4: Complete
            this.updateLoadingStep(4, 'Finalizing results...', 90);
            await this.delay(300);

            const processingTime = Date.now() - startTime;

            if (response.ok && result.success) {
                this.updateLoadingStep(4, 'Analysis complete!', 100, true);
                await this.delay(500);
                this.showSuccess(result, processingTime);
            } else {
                this.showError(result.error || 'An error occurred while processing your request.', response.status, processingTime);
            }
        } catch (error) {
            console.error('Fetch Error Details:', error);
            console.error('Error name:', error.name);
            console.error('Error message:', error.message);
            const processingTime = Date.now() - startTime;
            
            let errorMessage = 'Unable to connect to the server. ';
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                errorMessage += 'This might be a CORS issue. Try serving the HTML file via HTTP server instead of opening directly.';
            } else {
                errorMessage += `Error: ${error.message}. Please make sure the backend is running on localhost:5000.`;
            }
            
            this.showError(errorMessage, null, processingTime);
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        this.loading.classList.add('show');
        this.submitBtn.disabled = true;
    }

    showLoadingWithProgress() {
        this.loading.classList.add('show');
        this.submitBtn.disabled = true;
        
        // Reset all steps
        [this.step1, this.step2, this.step3, this.step4].forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        // Reset progress
        this.progressFill.classList.add('indeterminate');
        this.progressFill.style.width = '0%';
        
        // Reset timer
        this.startTime = Date.now();
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            this.loadingTimer.textContent = `Processing time: ${elapsed}s`;
        }, 1000);
        
        // Initial status
        this.loadingStatus.textContent = 'Preparing analysis...';
    }

    updateLoadingStep(stepNumber, statusText, progress = 0, isComplete = false) {
        // Update status text
        this.loadingStatus.textContent = statusText;
        
        // Update progress bar
        this.progressFill.classList.remove('indeterminate');
        this.progressFill.style.width = `${progress}%`;
        
        // Update step indicators
        const steps = [this.step1, this.step2, this.step3, this.step4];
        
        steps.forEach((step, index) => {
            const stepNum = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNum < stepNumber) {
                step.classList.add('completed');
            } else if (stepNum === stepNumber) {
                if (isComplete) {
                    step.classList.add('completed');
                } else {
                    step.classList.add('active');
                }
            }
        });
        
        // Update title based on step
        const stepTitles = [
            '📤 Uploading File',
            '⚙️ Processing Data',
            '🤖 AI Analysis',
            '✅ Finalizing Results'
        ];
        
        if (stepNumber <= stepTitles.length) {
            this.loadingTitle.textContent = stepTitles[stepNumber - 1];
        }
    }

    hideLoading() {
        this.loading.classList.remove('show');
        this.updateSubmitButton();
        
        // Clear timer
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        // Reset loading elements
        this.loadingTitle.textContent = '🚀 Processing Your Request';
        this.loadingSubtitle.textContent = 'Please wait while we analyze your data';
        this.loadingStatus.textContent = 'Preparing analysis...';
        this.progressFill.classList.add('indeterminate');
        this.progressFill.style.width = '0%';
        
        // Reset steps
        [this.step1, this.step2, this.step3, this.step4].forEach(step => {
            step.classList.remove('active', 'completed');
        });
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    showSuccess(result, processingTime) {
        const timestamp = new Date().toLocaleString();
        
        // Update title and status
        this.responseTitle.textContent = '✅ Analysis Complete';
        this.responseStatus.innerHTML = '✅ Success';
        this.responseStatus.className = 'response-status success';
        this.responseTimestamp.textContent = `Completed at ${timestamp}`;
        
        // Build meta information
        this.responseMeta.innerHTML = `
            <div class="meta-item">
                <span class="meta-label">Question:</span>
                <span class="meta-value">${this.escapeHtml(result.question)}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">File:</span>
                <span class="meta-value">${this.selectedFile.name}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Data Size:</span>
                <span class="meta-value">${result.csv_rows || 'unknown'} rows, ${(result.csv_columns && result.csv_columns.length) || 0} columns</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Processing Time:</span>
                <span class="meta-value">${(processingTime / 1000).toFixed(2)}s</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Columns:</span>
                <span class="meta-value">${(result.csv_columns && result.csv_columns.join) ? result.csv_columns.join(', ') : 'Not available'}</span>
            </div>
        `;
        
        this.responseAnswer.innerHTML = this.parseMarkdownToHTML(result.answer);
        this.responseContent.className = 'response-content success';
        this.responseSection.classList.add('show');
    }

    showError(message, statusCode = null, processingTime = 0) {
        const timestamp = new Date().toLocaleString();
        
        // Update title and status
        this.responseTitle.textContent = '❌ Analysis Failed';
        this.responseStatus.innerHTML = '❌ Error';
        this.responseStatus.className = 'response-status error';
        this.responseTimestamp.textContent = `Failed at ${timestamp}`;
        
        // Build error meta information
        let metaContent = `
            <div class="meta-item">
                <span class="meta-label">Error Type:</span>
                <span class="meta-value">${statusCode ? `HTTP ${statusCode}` : 'Connection Error'}</span>
            </div>
        `;
        
        if (this.selectedFile) {
            metaContent += `
                <div class="meta-item">
                    <span class="meta-label">File:</span>
                    <span class="meta-value">${this.selectedFile.name}</span>
                </div>
            `;
        }
        
        if (this.questionInput.value.trim()) {
            metaContent += `
                <div class="meta-item">
                    <span class="meta-label">Question:</span>
                    <span class="meta-value">${this.escapeHtml(this.questionInput.value.trim())}</span>
                </div>
            `;
        }
        
        metaContent += `
            <div class="meta-item">
                <span class="meta-label">Processing Time:</span>
                <span class="meta-value">${(processingTime / 1000).toFixed(2)}s</span>
            </div>
        `;
        
        this.responseMeta.innerHTML = metaContent;
        this.responseAnswer.innerHTML = this.escapeHtml(message);
        this.responseContent.className = 'response-content error';
        this.responseSection.classList.add('show');
    }

    hideResponse() {
        this.responseSection.classList.remove('show');
    }

    clearResponse() {
        this.hideResponse();
        this.responseMeta.innerHTML = '';
        this.responseAnswer.textContent = '';
        this.responseStatus.innerHTML = '';
        this.responseTimestamp.textContent = '';
    }

    async copyResponseToClipboard() {
        try {
            const question = this.questionInput.value.trim();
            const answer = this.responseAnswer.textContent;
            const timestamp = new Date().toLocaleString();
            
            const textToCopy = `CSV Q&A Analysis - ${timestamp}\n\nQuestion: ${question}\n\nAnswer:\n${answer}`;
            
            await navigator.clipboard.writeText(textToCopy);
            
            // Visual feedback
            const originalText = this.copyBtn.textContent;
            this.copyBtn.textContent = '✅ Copied!';
            this.copyBtn.style.backgroundColor = '#28a745';
            
            setTimeout(() => {
                this.copyBtn.textContent = originalText;
                this.copyBtn.style.backgroundColor = '#667eea';
            }, 2000);
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            // Fallback for older browsers
            this.fallbackCopyToClipboard();
        }
    }

    fallbackCopyToClipboard() {
        const question = this.questionInput.value.trim();
        const answer = this.responseAnswer.textContent;
        const timestamp = new Date().toLocaleString();
        
        const textToCopy = `CSV Q&A Analysis - ${timestamp}\n\nQuestion: ${question}\n\nAnswer:\n${answer}`;
        
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            // Visual feedback
            const originalText = this.copyBtn.textContent;
            this.copyBtn.textContent = '✅ Copied!';
            setTimeout(() => {
                this.copyBtn.textContent = originalText;
            }, 2000);
        } catch (error) {
            console.error('Fallback copy failed:', error);
        }
        
        document.body.removeChild(textArea);
    }

    parseMarkdownToHTML(markdown) {
        if (!markdown) return '';
        
        let html = markdown;
        
        // Headers
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');
        
        // Italic
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        html = html.replace(/_(.*?)_/g, '<em>$1</em>');
        
        // Code blocks
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Inline code
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Lists
        html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
        html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
        html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');
        
        // Wrap consecutive list items in ul tags
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        html = html.replace(/<\/li>\s*<li>/g, '</li><li>');
        
        // Tables (basic support)
        const lines = html.split('\n');
        let inTable = false;
        let processedLines = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            if (line.includes('|') && line.split('|').length > 2) {
                if (!inTable) {
                    processedLines.push('<table class="markdown-table">');
                    inTable = true;
                }
                
                const cells = line.split('|').filter(cell => cell.trim() !== '');
                const isHeader = i === 0 || (i > 0 && lines[i-1].includes('---'));
                const tag = isHeader ? 'th' : 'td';
                
                if (!line.includes('---')) {
                    const row = cells.map(cell => `<${tag}>${cell.trim()}</${tag}>`).join('');
                    processedLines.push(`<tr>${row}</tr>`);
                }
            } else {
                if (inTable) {
                    processedLines.push('</table>');
                    inTable = false;
                }
                processedLines.push(line);
            }
        }
        
        if (inTable) {
            processedLines.push('</table>');
        }
        
        html = processedLines.join('\n');
        
        // Line breaks
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        
        // Wrap in paragraphs
        if (!html.startsWith('<')) {
            html = '<p>' + html + '</p>';
        }
        
        return html;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CSVQAMaker();
});

// Add smooth horizontal scrolling with mouse wheel
document.addEventListener('DOMContentLoaded', function() {
    const scrollableElements = document.querySelectorAll('.response-content, .response-answer, .markdown-table-container');
    
    scrollableElements.forEach(element => {
        element.addEventListener('wheel', function(e) {
            if (e.shiftKey) {
                e.preventDefault();
                this.scrollLeft += e.deltaY;
            }
        });
    });
});