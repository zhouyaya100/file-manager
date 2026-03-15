// 文件管理脚本

let currentPath = null;  // 初始为 null，等用户选择目录
let selectedItems = [];

// 上传相关文件
let selectedFiles = [];  // 存储待上传的文件

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 不自动加载文件，等用户选择目录后再加载
    setupEventListeners();
    initUploadArea();
    
    // 如果有保存的上次路径，可以恢复（可选功能）
    // const savedPath = localStorage.getItem('fileManagerLastPath');
    // if (savedPath) {
    //     currentPath = savedPath;
    //     loadFiles(currentPath);
    // }
});

// 设置事件监听
function setupEventListeners() {
    // 目录卡片点击（目录选择器）
    document.querySelectorAll('.directory-card').forEach(card => {
        card.addEventListener('click', handleDirectorySelect);
    });
    
    // 上传按钮（已在 HTML 中通过 onclick 调用 showUploadModal）
    
    // 文件上传 - 事件在 HTML 中通过 onchange 绑定，这里不需要重复绑定
    // const fileInput = document.getElementById('file-input');
    // if (fileInput) {
    //     fileInput.addEventListener('change', handleFileUpload);
    // }
    
    // 上传区域点击事件在 showUploadModal 中绑定（因为 innerHTML 会被重置）
    
    // 新建文件夹
    const newFolderBtn = document.getElementById('new-folder-btn');
    if (newFolderBtn) {
        newFolderBtn.addEventListener('click', showCreateFolderModal);
    }
    
    // 面包屑导航点击
    document.querySelectorAll('.breadcrumb-item-link').forEach(item => {
        item.addEventListener('click', handleBreadcrumbClick);
    });
    
    // 拖放上传
    const dropZone = document.getElementById('file-list-container') || document.body;
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // 搜索框
    const searchInput = document.getElementById('file-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // 全选复选框
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', handleSelectAll);
    }
}

// 处理目录选择（目录选择器中的卡片点击）
function handleDirectorySelect(e) {
    const card = e.currentTarget;
    const path = card.dataset.path;
    const name = card.dataset.name;
    const permission = card.dataset.permission;
    
    if (!path) return;
    
    // 隐藏目录选择器，显示文件浏览器
    const directorySelector = document.getElementById('directory-selector');
    const fileBrowser = document.getElementById('file-browser');
    
    if (directorySelector) directorySelector.style.display = 'none';
    if (fileBrowser) fileBrowser.style.display = 'block';
    
    // 设置当前路径并加载文件
    currentPath = path;
    loadFiles(currentPath);
    
    // 更新页面标题
    const pageTitle = document.querySelector('.page-header h2');
    if (pageTitle) {
        pageTitle.textContent = `📁 ${name}`;
    }
    
    showNotification(`已进入目录：${name}（${permission === 'write' ? '读写' : '只读'}）`, 'success');
}

// 返回上层目录
function goBack() {
    if (!currentPath || currentPath === '/' || currentPath === '') {
        showNotification('已经在根目录了', 'info');
        return;
    }
    
    // 统一使用反斜杠处理 Windows 路径
    let path = currentPath;
    
    // 移除末尾的反斜杠（如果有）
    if (path.endsWith('\\')) {
        path = path.slice(0, -1);
    }
    
    // 检查是否是根目录（如 D:\ 或 C:\）
    if (/^[A-Za-z]:\\$/.test(path) || path === '\\\\' || path === '/') {
        showNotification('已经在根目录了', 'info');
        return;
    }
    
    // 找到最后一个反斜杠的位置
    const lastSlashIndex = path.lastIndexOf('\\');
    
    if (lastSlashIndex <= 0) {
        // 如果没有找到反斜杠，尝试正斜杠
        const lastForwardSlashIndex = path.lastIndexOf('/');
        if (lastForwardSlashIndex <= 0) {
            showNotification('已经在根目录了', 'info');
            return;
        }
        currentPath = path.substring(0, lastForwardSlashIndex);
    } else {
        currentPath = path.substring(0, lastSlashIndex);
    }
    
    loadFiles(currentPath);
}

// 刷新文件列表
function refreshFiles() {
    if (currentPath) {
        loadFiles(currentPath);
        showNotification('已刷新', 'success');
    }
}

// 加载文件列表
async function loadFiles(path) {
    currentPath = path || '/';
    
    try {
        showLoading('加载文件...');
        
        // 使用 URLSearchParams 正确处理路径编码
        const params = new URLSearchParams({ path: currentPath });
        const response = await fetch(`/api/files/list?${params.toString()}`);
        
        // 检查响应内容类型，如果是 HTML 说明未登录被重定向
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('text/html')) {
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            const items = data.data.items || [];
            renderFileList(items);
            updateBreadcrumb(data.data.current_path || currentPath);
            // 在前端计算统计信息
            const stats = {
                total_files: items.filter(i => !i.is_directory).length,
                total_folders: items.filter(i => i.is_directory).length,
                total_size: items.filter(i => !i.is_directory).reduce((sum, i) => sum + (i.size || 0), 0)
            };
            updateStats(stats);
        } else {
            const errorMsg = data.error || '未知错误，请检查权限设置';
            showNotification('加载失败：' + errorMsg, 'danger');
            console.error('API 返回错误:', data);
        }
    } catch (error) {
        console.error('加载文件失败:', error);
        showNotification('加载失败：' + (error.message || '网络错误'), 'danger');
    } finally {
        hideLoading();
    }
}

// 渲染文件列表
function renderFileList(files) {
    const container = document.getElementById('file-list');
    if (!container) return;
    
    if (files.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-folder-open"></i>
                <p class="mt-3">此目录为空</p>
                <p class="text-muted small">上传文件或创建新文件夹</p>
            </div>
        `;
        return;
    }
    
    // 先显示文件夹，再显示文件
    const folders = files.filter(f => f.is_directory);
    const fileList = files.filter(f => !f.is_directory);
    
    let html = '';
    
    // 文件夹
    folders.forEach(file => {
        html += createFileRowHtml(file, true);
    });
    
    // 文件
    fileList.forEach(file => {
        html += createFileRowHtml(file, false);
    });
    
    container.innerHTML = html;
    
    // 绑定点击事件
    container.querySelectorAll('.file-row').forEach(row => {
        row.addEventListener('click', handleFileRowClick);
        row.addEventListener('dblclick', handleFileRowDblClick);
        row.addEventListener('contextmenu', handleContextMenu);
    });
}

// 创建文件行 HTML（表格布局）
function createFileRowHtml(file, isFolder) {
    const icon = getFileIcon(file.name, file.is_directory);
    const iconClass = getFileIconClass(file.name, file.is_directory);
    const size = file.is_directory ? '-' : formatFileSize(file.size);
    const date = formatDate(file.modified);
    
    return `
        <tr class="file-row" data-path="${file.path}" data-name="${file.name}" data-is-folder="${file.is_directory}">
            <td class="text-center">
                <input type="checkbox" class="file-select" value="${file.path}">
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="file-icon-wrapper ${iconClass} me-3">
                        <i class="bi ${icon}"></i>
                    </div>
                    <span class="file-name-cell">${escapeHtml(file.name)}</span>
                </div>
            </td>
            <td class="text-end text-muted" style="font-family: 'Consolas', monospace;">${size}</td>
            <td class="text-end text-muted">${date}</td>
            <td class="text-center">
                <div class="action-buttons">
                    ${file.is_directory ? `
                        <button class="btn btn-outline-light" onclick="event.stopPropagation(); loadFiles('${escapeHtml(file.path)}')" title="打开">
                            <i class="bi bi-folder2-open"></i>
                        </button>
                    ` : `
                        <button class="btn btn-outline-light" onclick="event.stopPropagation(); downloadFile('${escapeHtml(file.path)}')" title="下载">
                            <i class="bi bi-download"></i>
                        </button>
                    `}
                    <button class="btn btn-outline-primary" onclick="event.stopPropagation(); renameItem('${escapeHtml(file.path)}', '${escapeHtml(file.name)}')" title="重命名">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="event.stopPropagation(); deleteItem('${escapeHtml(file.path)}', '${escapeHtml(file.name)}')" title="删除">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

// 获取文件图标样式类
function getFileIconClass(filename, isFolder) {
    if (isFolder) return 'folder';
    
    const ext = filename.split('.').pop().toLowerCase();
    const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'];
    const videoExts = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv'];
    const audioExts = ['mp3', 'wav', 'flac', 'aac', 'ogg'];
    const archiveExts = ['zip', 'rar', '7z', 'tar', 'gz'];
    const codeExts = ['js', 'ts', 'py', 'java', 'cpp', 'c', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'vue', 'react', 'html', 'css', 'scss', 'json', 'xml', 'md'];
    
    if (imageExts.includes(ext)) return 'image';
    if (videoExts.includes(ext)) return 'video';
    if (audioExts.includes(ext)) return 'audio';
    if (archiveExts.includes(ext)) return 'archive';
    if (codeExts.includes(ext)) return 'code';
    return 'file';
}

// 处理文件行点击
function handleFileRowClick(e) {
    if (e.target.type === 'checkbox') return;
    if (e.target.closest('.btn-group')) return;
    
    const checkbox = this.querySelector('.file-select');
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        updateSelectedItems();
    }
}

// 处理文件行双击（文件夹打开，文件下载）
function handleFileRowDblClick(e) {
    const isFolder = this.dataset.isFolder === 'true';
    const path = this.dataset.path;
    
    if (isFolder) {
        loadFiles(path);
    } else {
        downloadFile(path);
    }
}

// 处理面包屑点击
function handleBreadcrumbClick(e) {
    e.preventDefault();
    const path = this.dataset.path;
    loadFiles(path);
}

// 更新面包屑导航
function updateBreadcrumb(path) {
    const container = document.getElementById('breadcrumb-list');
    if (!container) return;
    
    const parts = path.split('/').filter(p => p);
    let html = '<li class="breadcrumb-item"><a href="#" class="breadcrumb-item-link" data-path="/">首页</a></li>';
    
    let currentPath = '';
    parts.forEach((part, index) => {
        currentPath += '/' + part;
        if (index === parts.length - 1) {
            html += `<li class="breadcrumb-item active">${escapeHtml(part)}</li>`;
        } else {
            html += `<li class="breadcrumb-item"><a href="#" class="breadcrumb-item-link" data-path="${currentPath}">${escapeHtml(part)}</a></li>`;
        }
    });
    
    container.innerHTML = html;
    
    // 重新绑定点击事件
    container.querySelectorAll('.breadcrumb-item-link').forEach(item => {
        item.addEventListener('click', handleBreadcrumbClick);
    });
}

// 更新统计信息
function updateStats(stats) {
    const totalFilesEl = document.getElementById('stat-total-files');
    const totalFoldersEl = document.getElementById('stat-total-folders');
    const totalSizeEl = document.getElementById('stat-total-size');
    
    if (totalFilesEl) totalFilesEl.textContent = stats?.total_files || 0;
    if (totalFoldersEl) totalFoldersEl.textContent = stats?.total_folders || 0;
    if (totalSizeEl) totalSizeEl.textContent = formatFileSize(stats?.total_size || 0);
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// 获取文件类型图标
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'];
    const videoExts = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv'];
    const audioExts = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma'];
    const docExts = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'];
    const codeExts = ['js', 'ts', 'py', 'java', 'cpp', 'c', 'h', 'html', 'css', 'json', 'xml', 'md'];
    
    if (imageExts.includes(ext)) return {icon: 'bi-image', class: 'image'};
    if (videoExts.includes(ext)) return {icon: 'bi-camera-video', class: 'video'};
    if (audioExts.includes(ext)) return {icon: 'bi-music-note-beamed', class: 'audio'};
    if (docExts.includes(ext)) return {icon: 'bi-file-earmark-text'};
    if (codeExts.includes(ext)) return {icon: 'bi-file-code'};
    if (ext === 'zip' || ext === 'rar' || ext === '7z') return {icon: 'bi-file-zip'};
    return {icon: 'bi-file-earmark'};
}

// 最大文件大小限制（1GB）
const MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024; // 1GB

// 添加文件到上传列表
function handleFileUpload(e) {
    const files = e.target?.files;
    if (!files || !files.length) {
        return;
    }
    
    // 检查每个文件的大小
    let oversizedFiles = [];
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (file.size > MAX_FILE_SIZE) {
            oversizedFiles.push({
                name: file.name,
                size: file.size
            });
        } else {
            selectedFiles.push(file);
        }
    }
    
    // 如果有文件超过限制，显示提示
    if (oversizedFiles.length > 0) {
        let message = '';
        if (oversizedFiles.length === 1) {
            message = `文件 "${oversizedFiles[0].name}" 大小为 ${formatFileSize(oversizedFiles[0].size)}，超过 1GB 限制`;
        } else {
            message = `${oversizedFiles.length} 个文件超过 1GB 限制，已自动跳过`;
        }
        showNotification(message, 'warning');
    }
    
    // 更新文件列表显示
    updateFileList();
    
    // 清空 input，允许重复选择同一文件
    e.target.value = '';
    
    // 启用上传按钮
    if (selectedFiles.length > 0) {
        document.getElementById('upload-confirm-btn').disabled = false;
    }
}

// 更新文件列表显示
function updateFileList() {
    const listContainer = document.getElementById('file-list-container');
    const fileList = document.getElementById('selected-file-list');
    const fileCount = document.getElementById('file-count');
    const fileTotalSize = document.getElementById('file-total-size');
    
    if (selectedFiles.length === 0) {
        listContainer.style.display = 'none';
        document.getElementById('upload-confirm-btn').disabled = true;
        return;
    }
    
    listContainer.style.display = 'block';
    
    let html = '';
    let totalSize = 0;
    
    selectedFiles.forEach((file, index) => {
        totalSize += file.size;
        const iconInfo = getFileIcon(file.name);
        
        html += `
            <div class="file-item">
                <div class="file-item-icon ${iconInfo.class || ''}">
                    <i class="bi ${iconInfo.icon}"></i>
                </div>
                <div class="file-item-info">
                    <div class="file-item-name" title="${escapeHtml(file.name)}">${escapeHtml(file.name)}</div>
                    <div class="file-item-size">${formatFileSize(file.size)}</div>
                </div>
                <button class="btn btn-sm btn-link text-danger file-item-remove" onclick="removeFile(${index})">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
        `;
    });
    
    fileList.innerHTML = html;
    fileCount.textContent = selectedFiles.length;
    fileTotalSize.textContent = formatFileSize(totalSize);
}

// 移除单个文件
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
    
    if (selectedFiles.length === 0) {
        document.getElementById('upload-confirm-btn').disabled = true;
    }
}

// 清空所有文件
function clearSelectedFiles() {
    selectedFiles = [];
    updateFileList();
    document.getElementById('file-input').value = '';
}

// 开始上传
async function startUpload() {
    if (selectedFiles.length === 0) {
        showNotification('请先选择要上传的文件', 'warning');
        return;
    }
    
    // 隐藏拖拽区域，显示进度条
    document.getElementById('upload-area').style.display = 'none';
    document.getElementById('upload-progress').style.display = 'block';
    document.getElementById('upload-cancel-btn').disabled = true;
    document.getElementById('upload-add-btn').disabled = true;
    
    const progressBar = document.getElementById('upload-progress-bar');
    const uploadStatus = document.getElementById('upload-status');
    
    // 计算总文件大小
    let totalSize = 0;
    for (let i = 0; i < selectedFiles.length; i++) {
        totalSize += selectedFiles[i].size;
    }
    
    try {
        const formData = new FormData();
        for (let i = 0; i < selectedFiles.length; i++) {
            formData.append('file', selectedFiles[i]);
        }
        formData.append('path', currentPath || '/');
        
        // 使用 XMLHttpRequest 来跟踪上传进度
        const xhr = new XMLHttpRequest();
        
        // 记录开始时间和进度
        let startTime = null;
        let lastLoaded = 0;
        let lastUpdateTime = null;
        let lastSpeed = 0;
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressBar.style.width = percentComplete + '%';
                
                const currentTime = new Date().getTime();
                
                if (!startTime) {
                    startTime = currentTime;
                    lastUpdateTime = currentTime;
                    lastLoaded = e.loaded;
                }
                
                // 计算平均速度（从开始到现在）
                const timeDiff = (currentTime - startTime) / 1000; // 秒
                const avgSpeed = timeDiff > 0 ? e.loaded / timeDiff : 0;
                
                // 计算瞬时速度（每 0.5 秒更新）
                const timeSinceLastUpdate = (currentTime - lastUpdateTime) / 1000;
                if (timeSinceLastUpdate >= 0.5 && lastUpdateTime !== null) {
                    const loadedDiff = e.loaded - lastLoaded;
                    lastSpeed = loadedDiff / timeSinceLastUpdate;
                    lastLoaded = e.loaded;
                    lastUpdateTime = currentTime;
                }
                
                // 使用瞬时速度，如果没有则用平均速度
                const speed = lastSpeed > 0 ? lastSpeed : avgSpeed;
                
                // 计算剩余时间
                let remainingTime = '';
                if (speed > 0 && percentComplete < 100) {
                    const remainingBytes = e.total - e.loaded;
                    const remainingSeconds = Math.ceil(remainingBytes / speed);
                    if (remainingSeconds > 60) {
                        remainingTime = ` 剩余${Math.floor(remainingSeconds / 60)}分${remainingSeconds % 60}秒`;
                    } else if (remainingSeconds > 0) {
                        remainingTime = ` 剩余${remainingSeconds}秒`;
                    }
                }
                
                // 显示进度信息
                let statusText = `上传中... ${percentComplete.toFixed(1)}%`;
                if (speed > 0) {
                    statusText += ` | ${formatFileSize(speed)}/s`;
                }
                if (remainingTime) {
                    statusText += remainingTime;
                }
                
                uploadStatus.textContent = statusText;
            }
        });
        
        xhr.addEventListener('load', () => {
            console.log('[Upload] Load event fired, status:', xhr.status);
            console.log('[Upload] Response:', xhr.responseText);
            
            if (xhr.status === 200) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    console.log('[Upload] Parsed response:', data);
                    
                    if (data.success) {
                        progressBar.classList.remove('progress-bar-animated');
                        progressBar.classList.add('bg-success');
                        uploadStatus.textContent = `✓ 成功上传 ${selectedFiles.length} 个文件`;
                        
                        // 设置超时，防止卡住
                        let modalClosed = false;
                        
                        const closeTimeout = setTimeout(() => {
                            if (!modalClosed) {
                                console.warn('[Upload] Timeout closing modal, forcing close');
                                forceCloseModal();
                            }
                        }, 3000);
                        
                        setTimeout(() => {
                            console.log('[Upload] Reloading files and closing modal');
                            // 只在有当前路径时才刷新文件列表
                            if (currentPath) {
                                loadFiles(currentPath);
                            }
                            
                            const modal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
                            if (modal) {
                                modal.hide();
                                modalClosed = true;
                            } else {
                                forceCloseModal();
                            }
                            
                            resetUploadModal();
                            clearTimeout(closeTimeout);
                        }, 1000);
                        
                        function forceCloseModal() {
                            document.getElementById('uploadModal').style.display = 'none';
                            document.body.classList.remove('modal-open');
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) backdrop.remove();
                        }
                    } else {
                        handleError(data.error || '上传失败');
                    }
                } catch (e) {
                    console.error('[Upload] Parse error:', e);
                    handleError('服务器响应解析失败：' + e.message);
                }
            } else {
                handleError(`HTTP ${xhr.status}: ${xhr.statusText}`);
            }
        });
        
        xhr.addEventListener('error', () => {
            console.error('[Upload] XHR error event fired');
            handleError('网络错误，请检查连接');
        });
        
        xhr.addEventListener('abort', () => {
            console.log('[Upload] Upload aborted');
            uploadStatus.textContent = '✗ 已取消';
            setTimeout(() => {
                resetUploadModal();
            }, 1000);
        });
        
        // 辅助函数：处理错误
        function handleError(message) {
            console.error('[Upload] Error:', message);
            progressBar.classList.remove('progress-bar-animated');
            progressBar.classList.add('bg-danger');
            uploadStatus.textContent = '✗ ' + message;
            showNotification('上传失败：' + message, 'danger');
            
            setTimeout(() => {
                resetUploadModal();
            }, 2000);
        }
        
        xhr.open('POST', '/api/files/upload');
        xhr.send(formData);
        
    } catch (error) {
        console.error('上传失败:', error);
        showNotification('上传失败：' + error.message, 'danger');
        progressBar.classList.remove('progress-bar-animated');
        progressBar.classList.add('bg-danger');
        uploadStatus.textContent = '✗ 上传失败';
        
        setTimeout(() => {
            resetUploadModal();
        }, 2000);
    }
}

// 重置上传模态框
function resetUploadModal() {
    selectedFiles = [];
    document.getElementById('upload-area').style.display = 'block';
    document.getElementById('upload-progress').style.display = 'none';
    document.getElementById('upload-cancel-btn').disabled = false;
    document.getElementById('upload-add-btn').disabled = false;
    document.getElementById('upload-progress-bar').style.width = '0%';
    document.getElementById('upload-progress-bar').className = 'progress-bar progress-bar-striped progress-bar-animated';
    document.getElementById('file-list-container').style.display = 'none';
    document.getElementById('upload-confirm-btn').disabled = true;
    document.getElementById('file-input').value = '';
}

// 下载文件
function downloadFile(path) {
    window.location.href = `/api/files/download?path=${encodeURIComponent(path)}`;
}

// 显示新建文件夹模态框（已在 HTML 中通过 onclick 调用 showNewFolderModal）

// 创建文件夹
async function createNewFolder() {
    const nameInput = document.getElementById('new-folder-name');
    const name = nameInput.value.trim();
    
    if (!name) {
        alert('请输入文件夹名称');
        return;
    }
    
    try {
        const response = await fetch('/api/files/mkdir', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                path: currentPath,
                name: name
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('newFolderModal')).hide();
            nameInput.value = '';
            showNotification('文件夹创建成功', 'success');
            loadFiles(currentPath);
        } else {
            showNotification('创建失败：' + data.error, 'danger');
        }
    } catch (error) {
        console.error('创建失败:', error);
        showNotification('创建失败：' + error.message, 'danger');
    }
}

// 重命名
async function renameItem(path, oldName) {
    const newName = prompt('请输入新名称:', oldName);
    if (!newName || newName === oldName) return;
    
    try {
        const response = await fetch('/api/files/rename', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                path: path,
                new_name: newName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('重命名成功', 'success');
            loadFiles(currentPath);
        } else {
            showNotification('重命名失败：' + data.error, 'danger');
        }
    } catch (error) {
        console.error('重命名失败:', error);
        showNotification('重命名失败：' + error.message, 'danger');
    }
}

// 删除
async function deleteItem(path, name) {
    if (!confirm(`确定要删除 "${name}" 吗？此操作不可恢复！`)) return;
    
    try {
        const response = await fetch('/api/files/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: path})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('删除成功', 'success');
            loadFiles(currentPath);
        } else {
            showNotification('删除失败：' + data.error, 'danger');
        }
    } catch (error) {
        console.error('删除失败:', error);
        showNotification('删除失败：' + error.message, 'danger');
    }
}

// 拖放处理
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (!files || !files.length) {
        console.warn('[WARN] No files in drop event');
        return;
    }
    
    handleFileUpload({target: {files: files}});
}

// 搜索处理
function handleSearch(e) {
    const query = e.target.value.toLowerCase();
    const items = document.querySelectorAll('.file-item');
    
    items.forEach(item => {
        const name = item.dataset.name.toLowerCase();
        if (name.includes(query)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// 全选处理
function handleSelectAll(e) {
    const checkboxes = document.querySelectorAll('.file-select');
    checkboxes.forEach(cb => {
        cb.checked = e.target.checked;
    });
    updateSelectedItems();
}

// 更新选中项
function updateSelectedItems() {
    const checkboxes = document.querySelectorAll('.file-select:checked');
    selectedItems = Array.from(checkboxes).map(cb => cb.value);
    
    const batchActions = document.getElementById('batch-actions');
    if (batchActions) {
        batchActions.style.display = selectedItems.length > 0 ? '' : 'none';
    }
}

// 批量删除
async function batchDelete() {
    if (selectedItems.length === 0) return;
    
    if (!confirm(`确定要删除选中的 ${selectedItems.length} 项吗？此操作不可恢复！`)) return;
    
    try {
        const response = await fetch('/api/files/batch-delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({paths: selectedItems})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`成功删除 ${data.deleted.length} 项`, 'success');
            selectedItems = [];
            loadFiles(currentPath);
        } else {
            showNotification('删除失败：' + data.error, 'danger');
        }
    } catch (error) {
        console.error('批量删除失败:', error);
        showNotification('删除失败：' + error.message, 'danger');
    }
}

// 右键菜单
function handleContextMenu(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // 这里可以添加自定义右键菜单逻辑
    console.log('右键点击:', this.dataset.path);
}

// HTML 转义（包括反斜杠，防止在 onclick 属性中被解释为转义字符）
function escapeHtml(text) {
    if (!text) return '';
    // 先转义 HTML 特殊字符
    const div = document.createElement('div');
    div.textContent = text;
    let html = div.innerHTML;
    // 再转义反斜杠，防止在 onclick 属性中被解释为转义字符
    html = html.replace(/\\/g, '\\\\');
    return html;
}

// 显示上传模态框
function showUploadModal() {
    const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
    modal.show();
}

// 初始化上传区域点击事件（页面加载时调用一次）
function initUploadArea() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', (e) => {
            // 如果点击的是按钮区域，不触发文件选择
            if (e.target.closest('button')) return;
            fileInput.click();
        });
        
        // 绑定文件选择变化事件
        fileInput.addEventListener('change', handleFileUpload);
    }
}

// 显示新建文件夹模态框
function showNewFolderModal() {
    const modal = new bootstrap.Modal(document.getElementById('newFolderModal'));
    modal.show();
}

// 拖放事件处理
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    const uploadArea = document.getElementById('upload-area');
    if (uploadArea) {
        uploadArea.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
    }
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    const uploadArea = document.getElementById('upload-area');
    if (uploadArea) {
        uploadArea.style.backgroundColor = '';
    }
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    const uploadArea = document.getElementById('upload-area');
    if (uploadArea) {
        uploadArea.style.backgroundColor = '';
    }
    
    const files = e.dataTransfer.files;
    if (!files || !files.length) {
        console.warn('[WARN] No files in upload area drop event');
        return;
    }
    
    // 检查每个文件的大小
    let oversizedFiles = [];
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (file.size > MAX_FILE_SIZE) {
            oversizedFiles.push({
                name: file.name,
                size: file.size
            });
        } else {
            selectedFiles.push(file);
        }
    }
    
    // 如果有文件超过限制，显示提示
    if (oversizedFiles.length > 0) {
        let message = '';
        if (oversizedFiles.length === 1) {
            message = `文件 "${oversizedFiles[0].name}" 大小为 ${formatFileSize(oversizedFiles[0].size)}，超过 1GB 限制`;
        } else {
            message = `${oversizedFiles.length} 个文件超过 1GB 限制，已自动跳过`;
        }
        showNotification(message, 'warning');
    }
    
    // 更新文件列表显示
    updateFileList();
    
    // 启用上传按钮
    if (selectedFiles.length > 0) {
        document.getElementById('upload-confirm-btn').disabled = false;
    }
}

