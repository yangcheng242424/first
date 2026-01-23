// 全局变量
let lineCount = 1;
let undoStack = [];
let redoStack = [];
let maxUndoStackSize = 50;

// DOM元素
const codeEditor = document.getElementById('codeEditor');
const lineNumbers = document.getElementById('lineNumbers');
const charCount = document.getElementById('charCount');
const languageSelect = document.getElementById('languageSelect');
const consoleOutput = document.getElementById('console');
const clearConsoleBtn = document.getElementById('clearConsole');
const runBtn = document.getElementById('runBtn');
const saveBtn = document.getElementById('saveBtn');
const formatBtn = document.getElementById('formatBtn');
const actionBtns = document.querySelectorAll('.action-btn');
const modal = document.getElementById('modal');
const modalBody = document.getElementById('modalBody');
const modalClose = document.querySelector('.modal-close');
const toast = document.getElementById('toast');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeEditor();
    setupEventListeners();
    loadSavedCode();
    updateLineNumbers();
    logToConsole('系统已就绪', 'success');
    logToConsole('欢迎使用手机端Cursor控制演示！', 'info');
});

// 初始化编辑器
function initializeEditor() {
    // 设置初始代码示例
    const sampleCode = `// 欢迎使用手机端Cursor控制演示
function greet(name) {
    return \`你好, \${name}! 欢迎使用Cursor手机端编程。\`;
}

// 示例：使用AI助手生成代码
const message = greet('开发者');
console.log(message);

// 提示：点击右上角按钮可以运行、保存或格式化代码`;
    
    codeEditor.value = sampleCode;
    updateLineNumbers();
    updateCharCount();
    saveToHistory();
}

// 设置事件监听器
function setupEventListeners() {
    // 代码编辑器事件
    codeEditor.addEventListener('input', handleCodeInput);
    codeEditor.addEventListener('scroll', syncScroll);
    codeEditor.addEventListener('keydown', handleKeyDown);
    
    // 工具栏按钮
    runBtn.addEventListener('click', runCode);
    saveBtn.addEventListener('click', saveCode);
    formatBtn.addEventListener('click', formatCode);
    
    // 语言选择
    languageSelect.addEventListener('change', handleLanguageChange);
    
    // 控制台
    clearConsoleBtn.addEventListener('click', clearConsole);
    
    // 快捷操作按钮
    actionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            handleQuickAction(action);
        });
    });
    
    // 模态框
    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // 手势支持
    setupGestureSupport();
    
    // 防止页面滚动时的意外操作
    preventAccidentalScroll();
}

// 处理代码输入
function handleCodeInput() {
    updateLineNumbers();
    updateCharCount();
    saveToHistory();
}

// 更新行号
function updateLineNumbers() {
    const lines = codeEditor.value.split('\n');
    lineCount = lines.length;
    lineNumbers.innerHTML = lines.map((_, i) => i + 1).join('<br>');
}

// 更新字符计数
function updateCharCount() {
    const count = codeEditor.value.length;
    charCount.textContent = count.toLocaleString();
}

// 同步滚动
function syncScroll() {
    lineNumbers.scrollTop = codeEditor.scrollTop;
}

// 处理键盘事件
function handleKeyDown(e) {
    // Tab键插入4个空格
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = codeEditor.selectionStart;
        const end = codeEditor.selectionEnd;
        const value = codeEditor.value;
        codeEditor.value = value.substring(0, start) + '    ' + value.substring(end);
        codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
        updateLineNumbers();
        updateCharCount();
    }
    
    // Ctrl/Cmd + S 保存
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveCode();
    }
    
    // Ctrl/Cmd + Enter 运行
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        runCode();
    }
}

// 运行代码
function runCode() {
    const code = codeEditor.value;
    const language = languageSelect.value;
    
    logToConsole(`正在运行 ${language} 代码...`, 'info');
    
    // 模拟代码执行
    setTimeout(() => {
        try {
            if (language === 'javascript') {
                // 简单的JavaScript执行模拟
                const result = executeJavaScript(code);
                logToConsole('执行成功！', 'success');
                if (result) {
                    logToConsole(`输出: ${result}`, 'info');
                }
            } else {
                logToConsole(`[模拟] ${language} 代码执行完成`, 'success');
                logToConsole('提示：这是演示版本，实际执行需要后端支持', 'warning');
            }
        } catch (error) {
            logToConsole(`错误: ${error.message}`, 'error');
        }
    }, 500);
    
    showToast('代码运行中...');
}

// 执行JavaScript代码（简单模拟）
function executeJavaScript(code) {
    // 仅用于演示，实际应用中需要更安全的执行环境
    try {
        // 提取console.log调用
        const logMatches = code.match(/console\.log\([^)]+\)/g);
        if (logMatches) {
            logMatches.forEach(match => {
                const content = match.replace(/console\.log\(|\)/g, '').trim();
                logToConsole(`输出: ${content}`, 'info');
            });
        }
        
        // 检查是否有函数调用
        if (code.includes('greet(')) {
            return '你好, 开发者! 欢迎使用Cursor手机端编程。';
        }
        
        return null;
    } catch (error) {
        throw new Error('代码执行失败');
    }
}

// 保存代码
function saveCode() {
    const code = codeEditor.value;
    const language = languageSelect.value;
    
    // 保存到本地存储
    localStorage.setItem('savedCode', code);
    localStorage.setItem('savedLanguage', language);
    
    logToConsole('代码已保存到本地存储', 'success');
    showToast('保存成功！');
}

// 加载保存的代码
function loadSavedCode() {
    const savedCode = localStorage.getItem('savedCode');
    const savedLanguage = localStorage.getItem('savedLanguage');
    
    if (savedCode) {
        codeEditor.value = savedCode;
        updateLineNumbers();
        updateCharCount();
    }
    
    if (savedLanguage) {
        languageSelect.value = savedLanguage;
    }
}

// 格式化代码
function formatCode() {
    const code = codeEditor.value;
    const language = languageSelect.value;
    
    logToConsole('正在格式化代码...', 'info');
    
    // 简单的格式化（实际应用中需要使用专业的格式化工具）
    let formatted = code;
    
    if (language === 'javascript' || language === 'python') {
        // 基本的缩进整理
        formatted = formatIndentation(code);
    }
    
    codeEditor.value = formatted;
    updateLineNumbers();
    updateCharCount();
    saveToHistory();
    
    logToConsole('代码格式化完成', 'success');
    showToast('格式化完成！');
}

// 简单的缩进格式化
function formatIndentation(code) {
    const lines = code.split('\n');
    let indentLevel = 0;
    const indentSize = 4;
    
    return lines.map(line => {
        const trimmed = line.trim();
        if (!trimmed) return '';
        
        // 减少缩进
        if (trimmed.startsWith('}') || trimmed.startsWith(']') || trimmed.startsWith(')')) {
            indentLevel = Math.max(0, indentLevel - 1);
        }
        
        const indented = ' '.repeat(indentLevel * indentSize) + trimmed;
        
        // 增加缩进
        if (trimmed.endsWith('{') || trimmed.endsWith('[') || trimmed.endsWith('(')) {
            indentLevel++;
        }
        
        return indented;
    }).join('\n');
}

// 处理语言切换
function handleLanguageChange() {
    const language = languageSelect.value;
    logToConsole(`已切换到 ${language}`, 'info');
    showToast(`语言: ${language}`);
}

// 处理快捷操作
function handleQuickAction(action) {
    switch (action) {
        case 'voice':
            showVoiceInput();
            break;
        case 'ai':
            showAIAssistant();
            break;
        case 'search':
            showCodeSearch();
            break;
        case 'git':
            showGitOperations();
            break;
        case 'terminal':
            showTerminal();
            break;
        case 'files':
            showFileManager();
            break;
        default:
            showToast('功能开发中...');
    }
}

// 显示语音输入
function showVoiceInput() {
    const content = `
        <h3>🎤 语音输入</h3>
        <p>在手机上使用语音输入可以大大提高编程效率：</p>
        <ul style="margin: 15px 0; padding-left: 20px;">
            <li>点击输入框，使用系统语音输入</li>
            <li>说出代码关键词，系统会自动补全</li>
            <li>支持中英文混合输入</li>
        </ul>
        <button onclick="startVoiceInput()" style="background: var(--primary-color); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 10px;">
            开始语音输入
        </button>
    `;
    showModal(content);
}

// 开始语音输入
function startVoiceInput() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new Recognition();
        recognition.lang = 'zh-CN';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const cursorPos = codeEditor.selectionStart;
            const value = codeEditor.value;
            codeEditor.value = value.substring(0, cursorPos) + transcript + value.substring(cursorPos);
            codeEditor.selectionStart = codeEditor.selectionEnd = cursorPos + transcript.length;
            updateLineNumbers();
            updateCharCount();
            showToast('语音输入完成');
        };
        
        recognition.onerror = () => {
            showToast('语音识别不可用，请使用键盘输入');
        };
        
        recognition.start();
        showToast('正在监听语音...');
    } else {
        showToast('您的浏览器不支持语音识别');
    }
    closeModal();
}

// 显示AI助手
function showAIAssistant() {
    const content = `
        <h3>🤖 AI助手</h3>
        <p>Cursor的AI助手可以帮助你：</p>
        <ul style="margin: 15px 0; padding-left: 20px;">
            <li>生成代码片段</li>
            <li>解释代码功能</li>
            <li>修复代码错误</li>
            <li>优化代码性能</li>
        </ul>
        <textarea id="aiPrompt" placeholder="描述你想要的功能..." style="width: 100%; min-height: 100px; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; margin: 10px 0; font-family: inherit;"></textarea>
        <button onclick="generateCode()" style="background: var(--primary-color); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%;">
            生成代码
        </button>
    `;
    showModal(content);
}

// 生成代码
function generateCode() {
    const prompt = document.getElementById('aiPrompt')?.value || '';
    if (!prompt) {
        showToast('请输入你的需求');
        return;
    }
    
    // 模拟AI生成代码
    const generatedCode = `// AI生成的代码：${prompt}
function ${prompt.toLowerCase().replace(/\s+/g, '_')}() {
    // TODO: 实现功能
    console.log('功能已生成');
}`;
    
    codeEditor.value += '\n\n' + generatedCode;
    updateLineNumbers();
    updateCharCount();
    closeModal();
    showToast('代码已生成！');
    logToConsole('AI助手已生成代码', 'success');
}

// 显示代码搜索
function showCodeSearch() {
    const content = `
        <h3>🔍 代码搜索</h3>
        <input type="text" id="searchInput" placeholder="输入搜索关键词..." style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; margin: 10px 0;">
        <button onclick="searchCode()" style="background: var(--primary-color); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%;">
            搜索
        </button>
        <div id="searchResults" style="margin-top: 15px;"></div>
    `;
    showModal(content);
}

// 搜索代码
function searchCode() {
    const query = document.getElementById('searchInput')?.value || '';
    if (!query) {
        showToast('请输入搜索关键词');
        return;
    }
    
    const code = codeEditor.value;
    const lines = code.split('\n');
    const results = [];
    
    lines.forEach((line, index) => {
        if (line.toLowerCase().includes(query.toLowerCase())) {
            results.push({ line: index + 1, content: line.trim() });
        }
    });
    
    const resultsDiv = document.getElementById('searchResults');
    if (results.length > 0) {
        resultsDiv.innerHTML = `<p style="margin-bottom: 10px;"><strong>找到 ${results.length} 个结果：</strong></p>` +
            results.map(r => `<div style="padding: 8px; background: var(--bg-color); border-radius: 6px; margin-bottom: 5px; font-size: 12px;">
                <strong>第 ${r.line} 行:</strong> ${r.content.substring(0, 50)}${r.content.length > 50 ? '...' : ''}
            </div>`).join('');
    } else {
        resultsDiv.innerHTML = '<p style="color: var(--text-secondary);">未找到匹配结果</p>';
    }
}

// 显示Git操作
function showGitOperations() {
    const content = `
        <h3>📦 Git操作</h3>
        <p>在手机上管理Git仓库：</p>
        <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
            <button onclick="gitCommand('status')" style="background: var(--primary-color); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer;">
                📊 Git Status
            </button>
            <button onclick="gitCommand('add')" style="background: var(--success-color); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer;">
                ➕ Git Add
            </button>
            <button onclick="gitCommand('commit')" style="background: var(--secondary-color); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer;">
                💾 Git Commit
            </button>
            <button onclick="gitCommand('push')" style="background: var(--warning-color); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer;">
                ⬆️ Git Push
            </button>
        </div>
    `;
    showModal(content);
}

// Git命令
function gitCommand(cmd) {
    logToConsole(`执行: git ${cmd}`, 'info');
    showToast(`Git ${cmd} 执行中...`);
    closeModal();
    
    // 模拟Git操作
    setTimeout(() => {
        logToConsole(`[模拟] git ${cmd} 执行完成`, 'success');
        showToast(`Git ${cmd} 完成`);
    }, 1000);
}

// 显示终端
function showTerminal() {
    const content = `
        <h3>💻 终端</h3>
        <p>在手机上使用终端命令：</p>
        <input type="text" id="terminalInput" placeholder="输入命令..." style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 8px; margin: 10px 0; font-family: monospace;">
        <button onclick="executeTerminalCommand()" style="background: var(--primary-color); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; width: 100%;">
            执行
        </button>
        <div id="terminalOutput" style="margin-top: 15px; padding: 10px; background: #1E1E1E; color: #D4D4D4; border-radius: 8px; font-family: monospace; font-size: 12px; min-height: 100px; max-height: 200px; overflow-y: auto;"></div>
    `;
    showModal(content);
}

// 执行终端命令
function executeTerminalCommand() {
    const command = document.getElementById('terminalInput')?.value || '';
    if (!command) {
        showToast('请输入命令');
        return;
    }
    
    const outputDiv = document.getElementById('terminalOutput');
    outputDiv.innerHTML += `<div style="color: #4EC9B0;">$ ${command}</div>`;
    
    // 模拟命令执行
    setTimeout(() => {
        const output = `[模拟] 命令 "${command}" 执行完成\n`;
        outputDiv.innerHTML += `<div style="color: #D4D4D4;">${output}</div>`;
        outputDiv.scrollTop = outputDiv.scrollHeight;
    }, 500);
}

// 显示文件管理器
function showFileManager() {
    const content = `
        <h3>📁 文件管理</h3>
        <p>管理项目文件：</p>
        <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 15px;">
            <button onclick="fileOperation('new')" style="background: var(--success-color); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer;">
                ➕ 新建文件
            </button>
            <button onclick="fileOperation('open')" style="background: var(--primary-color); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer;">
                📂 打开文件
            </button>
            <button onclick="fileOperation('save')" style="background: var(--secondary-color); color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer;">
                💾 保存文件
            </button>
        </div>
    `;
    showModal(content);
}

// 文件操作
function fileOperation(op) {
    logToConsole(`文件操作: ${op}`, 'info');
    showToast(`执行 ${op} 操作...`);
    closeModal();
}

// 显示模态框
function showModal(content) {
    modalBody.innerHTML = content;
    modal.classList.add('show');
}

// 关闭模态框
function closeModal() {
    modal.classList.remove('show');
}

// 显示提示消息
function showToast(message, duration = 2000) {
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

// 记录到控制台
function logToConsole(message, type = 'info') {
    const line = document.createElement('div');
    line.className = `console-line ${type}`;
    const timestamp = new Date().toLocaleTimeString();
    line.textContent = `[${timestamp}] ${message}`;
    consoleOutput.appendChild(line);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

// 清空控制台
function clearConsole() {
    consoleOutput.innerHTML = '';
    logToConsole('控制台已清空', 'info');
}

// 设置手势支持
function setupGestureSupport() {
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    
    // 左右滑动撤销/重做
    document.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    });
    
    document.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    });
    
    function handleSwipe() {
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        
        // 水平滑动（左右）
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
            if (deltaX > 0) {
                // 右滑 - 重做
                redo();
            } else {
                // 左滑 - 撤销
                undo();
            }
        }
    }
    
    // 双击选中单词
    let lastClickTime = 0;
    codeEditor.addEventListener('click', (e) => {
        const currentTime = Date.now();
        if (currentTime - lastClickTime < 300) {
            // 双击
            selectWord(e);
        }
        lastClickTime = currentTime;
    });
}

// 选中单词
function selectWord(e) {
    const text = codeEditor.value;
    const cursorPos = codeEditor.selectionStart;
    
    let start = cursorPos;
    let end = cursorPos;
    
    // 向前查找单词边界
    while (start > 0 && /\w/.test(text[start - 1])) {
        start--;
    }
    
    // 向后查找单词边界
    while (end < text.length && /\w/.test(text[end])) {
        end++;
    }
    
    codeEditor.setSelectionRange(start, end);
}

// 撤销/重做功能
function saveToHistory() {
    const currentCode = codeEditor.value;
    if (undoStack.length === 0 || undoStack[undoStack.length - 1] !== currentCode) {
        undoStack.push(currentCode);
        if (undoStack.length > maxUndoStackSize) {
            undoStack.shift();
        }
        redoStack = []; // 清空重做栈
    }
}

function undo() {
    if (undoStack.length > 1) {
        redoStack.push(undoStack.pop());
        codeEditor.value = undoStack[undoStack.length - 1];
        updateLineNumbers();
        updateCharCount();
        showToast('已撤销');
    }
}

function redo() {
    if (redoStack.length > 0) {
        const code = redoStack.pop();
        undoStack.push(code);
        codeEditor.value = code;
        updateLineNumbers();
        updateCharCount();
        showToast('已重做');
    }
}

// 防止意外滚动
function preventAccidentalScroll() {
    let lastTouchY = 0;
    let isScrolling = false;
    
    document.addEventListener('touchstart', (e) => {
        lastTouchY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchmove', (e) => {
        const currentY = e.touches[0].clientY;
        const deltaY = Math.abs(currentY - lastTouchY);
        
        if (deltaY > 10) {
            isScrolling = true;
        }
    });
    
    document.addEventListener('touchend', () => {
        setTimeout(() => {
            isScrolling = false;
        }, 100);
    });
}

// 导出函数供HTML调用
window.startVoiceInput = startVoiceInput;
window.generateCode = generateCode;
window.searchCode = searchCode;
window.gitCommand = gitCommand;
window.executeTerminalCommand = executeTerminalCommand;
window.fileOperation = fileOperation;
