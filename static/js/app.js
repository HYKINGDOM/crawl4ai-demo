// 全局变量
let loadingModal;
let previewModal;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化模态框
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
    
    // 绑定表单提交事件
    document.getElementById('crawl-form').addEventListener('submit', handleCrawlSubmit);
    
    // 加载历史记录
    loadHistory();
    
    // 设置定时刷新历史记录（每30秒）
    setInterval(loadHistory, 30000);
});

// 处理爬取表单提交
async function handleCrawlSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const url = formData.get('url');
    const contentSource = formData.get('content_source');
    
    // 获取选中的AI模式
    const aiModes = [];
    const checkboxes = document.querySelectorAll('input[name="ai_modes"]:checked');
    checkboxes.forEach(checkbox => {
        aiModes.push(checkbox.value);
    });
    
    // 验证表单
    if (!url) {
        showAlert('请输入有效的URL', 'danger');
        return;
    }
    
    if (aiModes.length === 0) {
        showAlert('请至少选择一种AI分析模式', 'warning');
        return;
    }
    
    // 显示加载模态框
    loadingModal.show();
    
    try {
        // 构建请求数据
        const requestData = {
            url: url,
            content_source: contentSource,
            ai_modes: aiModes,
            save_files: true
        };
        
        // 发送POST请求
        const response = await fetch('/crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        // 隐藏加载模态框
        loadingModal.hide();
        
        if (result.success) {
            // 显示成功结果
            displayResult(result);
            showAlert('爬取和分析完成！', 'success');
            
            // 刷新历史记录
            setTimeout(loadHistory, 1000);
        } else {
            // 显示错误信息
            showAlert(`处理失败: ${result.error}`, 'danger');
        }
        
    } catch (error) {
        // 隐藏加载模态框
        loadingModal.hide();
        console.error('请求失败:', error);
        showAlert(`请求失败: ${error.message}`, 'danger');
    }
}

// 显示处理结果
function displayResult(result) {
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');
    
    let html = `
        <div class="result-item fade-in">
            <h5><i class="fas fa-globe me-2"></i>爬取信息</h5>
            <p><strong>URL:</strong> <a href="${result.url}" target="_blank">${result.url}</a></p>
            <p><strong>时间:</strong> ${formatTimestamp(result.timestamp)}</p>
            <p><strong>内容长度:</strong> ${result.markdown_content ? result.markdown_content.length : 0} 字符</p>
        </div>
    `;
    
    // 显示AI分析结果
    if (result.ai_results) {
        for (const [mode, aiResult] of Object.entries(result.ai_results)) {
            if (aiResult.success) {
                html += `
                    <div class="result-item fade-in">
                        <h5><i class="fas fa-robot me-2"></i>AI分析 - ${getModeName(mode)}</h5>
                        <div class="result-content">
                            ${aiResult.content ? aiResult.content.substring(0, 500) + '...' : '无内容'}
                        </div>
                    </div>
                `;
            }
        }
    }
    
    // 显示存储信息
    if (result.storage_info && result.storage_info.minio_files) {
        html += `
            <div class="result-item fade-in">
                <h5><i class="fas fa-cloud me-2"></i>文件存储</h5>
                <p><strong>数据库记录ID:</strong> ${result.storage_info.database_id}</p>
                <p><strong>文件数量:</strong> ${result.storage_info.total_files}</p>
                <div class="file-list">
        `;
        
        result.storage_info.minio_files.forEach(file => {
            html += `
                <a href="#" class="file-badge ${file.type}" onclick="previewFile('${file.url}', '${file.filename}', '${file.type}')">
                    <i class="fas fa-file me-1"></i>${file.filename}
                </a>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    resultContent.innerHTML = html;
    resultSection.style.display = 'block';
    
    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// 加载历史记录
async function loadHistory() {
    const historyContent = document.getElementById('history-content');
    
    try {
        const response = await fetch('/history');
        const data = await response.json();
        
        if (data.success && data.tasks && data.tasks.length > 0) {
            let html = '';
            
            data.tasks.forEach(task => {
                html += `
                    <div class="history-item fade-in">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="mb-1">
                                <a href="${task.url}" target="_blank" class="text-decoration-none">
                                    ${task.url.length > 60 ? task.url.substring(0, 60) + '...' : task.url}
                                </a>
                            </h6>
                            <span class="status-badge status-${task.status}">${getStatusName(task.status)}</span>
                        </div>
                        
                        <div class="history-meta mb-2">
                            <i class="fas fa-clock me-1"></i>${formatTimestamp(task.created_at)}
                            <span class="ms-3">
                                <i class="fas fa-cog me-1"></i>${task.content_source}
                            </span>
                            <span class="ms-3">
                                <i class="fas fa-file me-1"></i>${task.files ? task.files.length : 0} 个文件
                            </span>
                        </div>
                        
                        ${task.files && task.files.length > 0 ? `
                            <div class="file-list">
                                ${task.files.map(file => `
                                    <a href="#" class="file-badge ${file.file_type}" 
                                       onclick="previewFile('${file.minio_url}', '${file.filename}', '${file.file_type}')">
                                        <i class="fas fa-file me-1"></i>${file.filename}
                                    </a>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            historyContent.innerHTML = html;
        } else {
            historyContent.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-inbox fa-3x mb-3"></i>
                    <p>暂无历史记录</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('加载历史记录失败:', error);
        historyContent.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <p>加载历史记录失败</p>
            </div>
        `;
    }
}

// 预览文件
async function previewFile(url, filename, fileType) {
    const previewModalTitle = document.getElementById('previewModalTitle');
    const previewContent = document.getElementById('preview-content');
    const downloadLink = document.getElementById('download-link');
    
    // 设置模态框标题和下载链接
    previewModalTitle.textContent = `预览: ${filename}`;
    downloadLink.href = url;
    
    // 显示加载状态
    previewContent.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p>正在加载文件内容...</p>
        </div>
    `;
    
    // 显示模态框
    previewModal.show();
    
    try {
        // 获取文件内容
        const response = await fetch(`/preview?url=${encodeURIComponent(url)}`);
        const data = await response.json();
        
        if (data.success) {
            // 根据文件类型显示内容
            if (fileType.includes('json')) {
                previewContent.innerHTML = `
                    <pre><code>${JSON.stringify(JSON.parse(data.content), null, 2)}</code></pre>
                `;
            } else {
                // Markdown文件，转换为HTML显示
                previewContent.innerHTML = `
                    <div class="preview-content">
                        ${markdownToHtml(data.content)}
                    </div>
                `;
            }
        } else {
            previewContent.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <p>无法加载文件内容: ${data.error}</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('预览文件失败:', error);
        previewContent.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                <p>预览失败: ${error.message}</p>
            </div>
        `;
    }
}

// 简单的Markdown转HTML函数
function markdownToHtml(markdown) {
    return markdown
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        .replace(/!\[([^\]]*)\]\(([^\)]*)\)/gim, '<img alt="$1" src="$2" class="img-fluid" />')
        .replace(/\[([^\]]*)\]\(([^\)]*)\)/gim, '<a href="$2">$1</a>')
        .replace(/\n$/gim, '<br />');
}

// 显示提示信息
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 在页面顶部插入提示
    const container = document.querySelector('.container');
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = alertHtml;
    container.insertBefore(tempDiv.firstElementChild, container.firstElementChild);
    
    // 5秒后自动移除
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// 格式化时间戳
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 获取模式中文名称
function getModeName(mode) {
    const modeNames = {
        'structured_data': '结构化数据',
        'content_summary': '内容摘要',
        'key_points': '关键要点'
    };
    return modeNames[mode] || mode;
}

// 获取状态中文名称
function getStatusName(status) {
    const statusNames = {
        'completed': '已完成',
        'processing': '处理中',
        'failed': '失败'
    };
    return statusNames[status] || status;
}