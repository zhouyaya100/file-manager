// 主应用脚本

// 工具提示初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有 Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 初始化所有 popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 自动隐藏 alert
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // 确认对话框
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});

// 显示加载状态
function showLoading(message) {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">${message || '加载中...'}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

// 隐藏加载状态
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container') || createNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 150);
    }, 3000);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;';
    document.body.appendChild(container);
    return container;
}

// API 请求封装
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        // 检查响应内容类型，如果是 HTML 说明未登录被重定向
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
            window.location.href = '/login';
            throw new Error('未登录，请重新登录');
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 获取文件图标
function getFileIcon(filename, isFolder) {
    if (isFolder) return 'bi-folder-fill';
    
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'pdf': 'bi-file-pdf-fill',
        'doc': 'bi-file-word-fill',
        'docx': 'bi-file-word-fill',
        'xls': 'bi-file-excel-fill',
        'xlsx': 'bi-file-excel-fill',
        'ppt': 'bi-file-powerpoint-fill',
        'pptx': 'bi-file-powerpoint-fill',
        'jpg': 'bi-file-image-fill',
        'jpeg': 'bi-file-image-fill',
        'png': 'bi-file-image-fill',
        'gif': 'bi-file-image-fill',
        'mp3': 'bi-file-music-fill',
        'wav': 'bi-file-music-fill',
        'mp4': 'bi-file-play-fill',
        'avi': 'bi-file-play-fill',
        'zip': 'bi-file-zip-fill',
        'rar': 'bi-file-zip-fill',
        'txt': 'bi-file-text-fill',
        'md': 'bi-file-text-fill',
        'json': 'bi-file-code-fill',
        'js': 'bi-file-code-fill',
        'py': 'bi-file-code-fill',
        'html': 'bi-file-code-fill',
        'css': 'bi-file-code-fill'
    };
    
    return iconMap[ext] || 'bi-file-earmark-fill';
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('已复制到剪贴板', 'success');
        return true;
    } catch (err) {
        console.error('复制失败:', err);
        showNotification('复制失败', 'danger');
        return false;
    }
}
