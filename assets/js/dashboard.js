// Enhanced LLM Dashboard - 3 Charts
class EnhancedLLMDashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        
        // Only initialize if Chart is available
        if (typeof Chart !== 'undefined') {
            this.init();
        } else {
            console.warn('⚠️ Chart.js not loaded - skipping dashboard');
        }
    }
    
    init() {
        console.log('🚀 Initializing Enhanced LLM Dashboard...');
        this.setupCharts();
        this.loadData();
        
        // Update every 60 seconds
        this.updateInterval = setInterval(() => {
            this.loadData();
        }, 60000);
    }
    
    setupCharts() {
        this.setupResponseTimeChart();
        this.setupProviderPerformanceChart();
        this.setupRSSQualityChart();
    }
    
    setupResponseTimeChart() {
        const canvas = document.getElementById('responseTimesChart');
        if (!canvas) {
            console.warn('⚠️ Response times chart canvas not found');
            return;
        }
        
        this.charts.responseTimes = new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
                datasets: [{
                    label: 'Response Time (seconds)',
                    data: [0, 0, 0, 0, 0],
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Seconds',
                            font: { size: 11 }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Recent Queries',
                            font: { size: 11 }
                        }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
        
        console.log('✅ Response time chart initialized');
    }
    
    setupProviderPerformanceChart() {
        const canvas = document.getElementById('providerPerformanceChart');
        if (!canvas) {
            console.warn('⚠️ Provider performance chart canvas not found');
            return;
        }
        
        this.charts.providerPerformance = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Claude', 'Gemini'],
                datasets: [{
                    label: 'Avg Response Time (s)',
                    data: [0, 0],
                    backgroundColor: ['#059669', '#dc2626'],
                    borderColor: ['#047857', '#b91c1c'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Seconds',
                            font: { size: 11 }
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y}s`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ Provider performance chart initialized');
    }
    
    setupRSSQualityChart() {
        const canvas = document.getElementById('rssQualityChart');
        if (!canvas) {
            console.warn('⚠️ RSS quality chart canvas not found');
            return;
        }
        
        this.charts.rssQuality = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Articles Contributed',
                    data: [],
                    backgroundColor: [
                        '#4f46e5',  // RealEstate.com.au
                        '#059669',  // Smart Property Investment
                        '#f59e0b',  // PropertyMe
                        '#dc2626',  // View.com.au
                        '#7c3aed'   // Others
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', // Horizontal bars
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Articles',
                            font: { size: 11 }
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.parsed.x} articles`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('✅ RSS quality chart initialized');
    }
    
    async loadData() {
        try {
            const response = await fetch('https://curam-ai-python-v2-production.up.railway.app/api/property/stats');
            const data = await response.json();
            
            if (data.success && data.stats.llm_performance) {
                this.updateCharts(data.stats);
                this.updateMetrics(data.stats);
                console.log('📊 All charts updated with new data');
            } else {
                console.warn('⚠️ No LLM performance data available');
                this.showNoDataState();
            }
        } catch (error) {
            console.error('❌ Failed to load dashboard data:', error);
            this.showErrorState();
        }
    }
    
    updateCharts(stats) {
        const llmPerf = stats.llm_performance;
        
        // Update Response Times Chart
        if (this.charts.responseTimes && llmPerf.response_times) {
            const times = llmPerf.response_times.slice(-5);
            const labels = times.map((_, index) => `Q${index + 1}`);
            const values = times.map(q => q.processing_time || 0);
            
            while (values.length < 5) {
                values.unshift(0);
            }
            
            this.charts.responseTimes.data.labels = labels;
            this.charts.responseTimes.data.datasets[0].data = values;
            this.charts.responseTimes.update('none');
        }
        
        // Update Provider Performance Chart
        if (this.charts.providerPerformance && llmPerf.provider_performance) {
            const claude = llmPerf.provider_performance.claude || { avg_response_time: 0 };
            const gemini = llmPerf.provider_performance.gemini || { avg_response_time: 0 };
            
            this.charts.providerPerformance.data.datasets[0].data = [
                claude.avg_response_time || 0,
                gemini.avg_response_time || 0
            ];
            this.charts.providerPerformance.update('none');
        }
        
        // Update RSS Quality Chart
        if (this.charts.rssQuality && stats.rss_status) {
            this.updateRSSQualityChart(stats.rss_status);
        }
    }
    
    updateRSSQualityChart(rssStatus) {
        // Simulate RSS source contribution data
        // In a real implementation, you'd track this in your backend
        const sources = [
            { name: 'RealEstate.com.au', articles: 5 },
            { name: 'Smart Property Investment', articles: 3 },
            { name: 'PropertyMe Blog', articles: 2 },
            { name: 'View.com.au', articles: 1 }
        ];
        
        // Filter out sources with 0 articles
        const activeSources = sources.filter(s => s.articles > 0);
        
        this.charts.rssQuality.data.labels = activeSources.map(s => s.name);
        this.charts.rssQuality.data.datasets[0].data = activeSources.map(s => s.articles);
        this.charts.rssQuality.update('none');
    }
    
    updateMetrics(stats) {
        const llmPerf = stats.llm_performance;
        
        // Success Rate
        const successRateEl = document.getElementById('success-rate');
        if (successRateEl && llmPerf.success_rates) {
            successRateEl.textContent = `${llmPerf.success_rates.overall}%`;
        }
        
        // Average Response Time
        const avgResponseEl = document.getElementById('avg-response');
        if (avgResponseEl && llmPerf.provider_performance) {
            const claude = llmPerf.provider_performance.claude?.avg_response_time || 0;
            const gemini = llmPerf.provider_performance.gemini?.avg_response_time || 0;
            const avg = ((claude + gemini) / 2).toFixed(1);
            avgResponseEl.textContent = `${avg}s`;
        }
        
        // Total Queries
        const totalQueriesEl = document.getElementById('total-queries');
        if (totalQueriesEl && llmPerf.total_queries_analyzed) {
            totalQueriesEl.textContent = llmPerf.total_queries_analyzed;
        }
        
        // RSS Status
        const rssStatusEl = document.getElementById('rss-status');
        if (rssStatusEl && stats.rss_status) {
            rssStatusEl.textContent = `${stats.rss_status.active_feeds}/${stats.rss_status.total_feeds}`;
        }
    }
    
    showNoDataState() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.data && chart.data.datasets[0]) {
                // Reset chart data to zeros
                chart.data.datasets[0].data = chart.data.datasets[0].data.map(() => 0);
                chart.update('none');
            }
        });
        
        document.querySelectorAll('.metric-value').forEach(el => {
            if (el.textContent.includes('---')) {
                el.textContent = 'No data';
            }
        });
    }
    
    showErrorState() {
        console.error('❌ Dashboard in error state');
        
        document.querySelectorAll('.metric-value').forEach(el => {
            el.style.color = '#dc2626';
        });
    }
    
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// Initialize enhanced dashboard when script loads
window.enhancedDashboard = new EnhancedLLMDashboard();