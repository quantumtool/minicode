# 明天中午12点吃饭提醒 Web 应用 - 最小可运行代码

## 文件结构

```
reminder-app/
├── index.html
├── css/
│   └── style.css
└── js/
    ├── app.js
    ├── timer.js
    ├── notification.js
    ├── ui.js
    └── utils.js
```

## 代码实现

### index.html

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>吃饭提醒</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="card">
        <h1>🍚 吃饭提醒</h1>
        <div class="time-display">
            <label>提醒时间</label>
            <span id="target-time">--</span>
        </div>
        <div class="input-group">
            <label for="message">提醒内容</label>
            <input type="text" id="message" value="该吃饭啦！" maxlength="50">
        </div>
        <div class="button-group">
            <button id="set-btn" class="btn primary">设置提醒</button>
            <button id="cancel-btn" class="btn secondary" disabled>取消提醒</button>
        </div>
        <div id="countdown" class="countdown">--:--:--</div>
        <div id="status" class="status"></div>
    </div>

    <!-- 页面弹窗（默认隐藏） -->
    <div id="popup-overlay" class="popup-overlay hidden">
        <div class="popup-content">
            <p id="popup-message"></p>
            <button id="popup-close" class="btn primary">知道了</button>
        </div>
    </div>

    <script type="module" src="js/app.js"></script>
</body>
</html>
```

### css/style.css

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #f5f5f5;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
}

.card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    padding: 30px 24px;
    max-width: 400px;
    width: 100%;
    text-align: center;
}

h1 {
    font-size: 1.6rem;
    margin-bottom: 20px;
    color: #333;
}

.time-display {
    margin-bottom: 16px;
    font-size: 1rem;
}

.time-display label {
    display: block;
    color: #666;
    margin-bottom: 4px;
}

#target-time {
    font-size: 1.3rem;
    font-weight: bold;
    color: #222;
}

.input-group {
    margin-bottom: 20px;
    text-align: left;
}

.input-group label {
    display: block;
    margin-bottom: 6px;
    color: #555;
    font-size: 0.95rem;
}

#message {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 1rem;
    outline: none;
    transition: border 0.2s;
}

#message:focus {
    border-color: #4caf50;
}

.button-group {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}

.btn {
    flex: 1;
    padding: 12px 0;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.1s;
    min-height: 48px; /* 移动端触控友好 */
}

.btn:active {
    transform: scale(0.97);
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn.primary {
    background: #4caf50;
    color: white;
}

.btn.primary:hover:not(:disabled) {
    opacity: 0.9;
}

.btn.secondary {
    background: #f44336;
    color: white;
}

.btn.secondary:hover:not(:disabled) {
    opacity: 0.9;
}

.countdown {
    font-size: 2rem;
    font-family: "Courier New", monospace;
    letter-spacing: 2px;
    color: #333;
    margin-bottom: 16px;
    padding: 10px 0;
    background: #fafafa;
    border-radius: 8px;
}

.status {
    font-size: 0.95rem;
    min-height: 1.5rem;
    color: #666;
}

/* 页面弹窗样式 */
.popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999;
}

.popup-overlay.hidden {
    display: none;
}

.popup-content {
    background: white;
    border-radius: 16px;
    padding: 32px 24px;
    max-width: 320px;
    width: 90%;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.popup-content p {
    font-size: 1.2rem;
    margin-bottom: 20px;
    color: #333;
}

/* 移动端适配 */
@media (max-width: 480px) {
    .card {
        padding: 20px 16px;
    }

    .countdown {
        font-size: 1.6rem;
    }

    .btn {
        font-size: 0.95rem;
    }
}
```

### js/utils.js

```javascript
/**
 * 工具函数模块
 * 提供计算明天中午、格式化时间、生成音效等功能
 */

/**
 * 获取明天中午12:00的 Date 对象（基于本地时区）
 * 例：当前 2025-04-01 14:30 → 2025-04-02 12:00:00
 */
export function getTomorrowNoon() {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(now.getDate() + 1);
    tomorrow.setHours(12, 0, 0, 0);
    return tomorrow;
}

/**
 * 将剩余毫秒数格式化为 HH:MM:SS
 * @param {number} ms - 剩余毫秒数（非负）
 * @returns {string} 格式如 "01:30:45"
 */
export function formatRemaining(ms) {
    if (ms <= 0) return "00:00:00";
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    return [hours, minutes, seconds].map(v => String(v).padStart(2, '0')).join(':');
}

/**
 * 使用 Web Audio API 播放一个 440Hz 的正弦波音效，持续指定时长
 * @param {number} duration - 持续时间（毫秒），默认 1000
 * @returns {AudioContext} 返回当前 AudioContext，可在外部停止
 */
export function playBeep(duration = 1000) {
    // 需要用户交互后调用才能成功
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(440, audioCtx.currentTime);
    gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
    // 淡出，避免突然结束产生咔嗒声
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration / 1000);
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + duration / 1000);
    return audioCtx;
}
```

### js/timer.js

```javascript
/**
 * 计时器模块
 * 管理用于触发提醒的 setTimeout 和用于更新倒计时的 setInterval
 */
export const Timer = {
    timeoutId: null,     // setTimeout 句柄
    intervalId: null,    // setInterval 句柄
    targetTime: null,    // 目标时间戳
    onTrigger: null,     // 提醒触发回调
    onTick: null,        // 每秒更新回调

    /**
     * 设置定时器
     * @param {number} targetTimestamp - 目标时间的毫秒时间戳
     * @param {Function} triggerCallback - 触发提醒时调用的函数
     * @param {Function} tickCallback - 每秒更新倒计时，参数为剩余毫秒数
     */
    setTimer(targetTimestamp, triggerCallback, tickCallback) {
        this.cancelTimer(); // 先清除之前设置的定时器
        this.targetTime = targetTimestamp;
        this.onTrigger = triggerCallback;
        this.onTick = tickCallback;

        const checkAndUpdate = () => {
            const remaining = this.getRemaining();
            if (remaining <= 0) {
                // 时间到，触发提醒
                this.cancelTimer();
                if (this.onTrigger) this.onTrigger();
                if (this.onTick) this.onTick(0);
            } else {
                if (this.onTick) this.onTick(remaining);
            }
        };

        // 每秒更新倒计时
        this.intervalId = setInterval(checkAndUpdate, 1000);

        // 计算第一次触发时间（精确到毫秒，但使用checkAndUpdate每1秒也会检查）
        const remaining = this.getRemaining();
        if (remaining <= 0) {
            // 如果当前时间已超过目标，立即触发
            this.cancelTimer();
            if (this.onTrigger) this.onTrigger();
            if (this.onTick) this.onTick(0);
        } else {
            // 使用 setTimeout 确保即使在页面休眠后也能触发（多数浏览器允许延迟）
            this.timeoutId = setTimeout(() => {
                this.cancelTimer();
                if (this.onTrigger) this.onTrigger();
                if (this.onTick) this.onTick(0);
            }, remaining);

            // 立即调用一次 tick 更新界面
            if (this.onTick) this.onTick(remaining);
        }
    },

    /**
     * 取消定时器，重置状态
     */
    cancelTimer() {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = null;
        }
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.targetTime = null;
        this.onTrigger = null;
        this.onTick = null;
    },

    /**
     * 返回当前剩余毫秒数（可能为负，但外部应判断）
     * @returns {number}
     */
    getRemaining() {
        if (!this.targetTime) return 0;
        return this.targetTime - Date.now();
    },

    /**
     * 判断是否有正在运行的定时器
     * @returns {boolean}
     */
    isActive() {
        return this.timeoutId !== null || this.intervalId !== null;
    }
};
```

### js/notification.js

```javascript
/**
 * 通知模块
 * 处理系统通知（Notification API）的请求和发送
 */
export const Notifier = {
    /**
     * 检查浏览器是否支持 Notification API
     * @returns {boolean}
     */
    isSupported() {
        return 'Notification' in window;
    },

    /**
     * 请求通知权限
     * @returns {Promise<string>} 'granted' | 'denied' | 'default'
     */
    async requestPermission() {
        if (!this.isSupported()) return 'denied';
        try {
            const permission = await Notification.requestPermission();
            return permission;
        } catch (e) {
            // 旧式回调处理
            return new Promise((resolve) => {
                Notification.requestPermission((perm) => resolve(perm));
            });
        }
    },

    /**
     * 如果拥有通知权限，则发送系统通知
     * @param {string} title - 通知标题
     * @param {string} body - 通知正文
     * @returns {boolean} 是否成功发送系统通知
     */
    sendNotification(title, body) {
        if (this.isSupported() && Notification.permission === 'granted') {
            try {
                new Notification(title, { body });
                return true;
            } catch (e) {
                console.warn('发送系统通知失败', e);
                return false;
            }
        }
        return false;
    }
};
```

### js/ui.js

```javascript
/**
 * UI模块
 * 管理所有DOM元素引用和操作
 */
export const UI = {
    elements: {},

    /**
     * 初始化UI模块，获取DOM引用并返回自身
     * @returns {this}
     */
    init() {
        this.elements = {
            targetTime: document.getElementById('target-time'),
            messageInput: document.getElementById('message'),
            setBtn: document.getElementById('set-btn'),
            cancelBtn: document.getElementById('cancel-btn'),
            countdown: document.getElementById('countdown'),
            status: document.getElementById('status'),
            popupOverlay: document.getElementById('popup-overlay'),
            popupMessage: document.getElementById('popup-message'),
            popupClose: document.getElementById('popup-close'),
        };
        return this;
    },

    /**
     * 更新显示目标时间
     * @param {string} timeString - 格式如 "2025-04-02 12:00"
     */
    updateTargetTime(timeString) {
        this.elements.targetTime.textContent = timeString;
    },

    /**
     * 更新倒计时显示
     * @param {string} timeString - 格式如 "01:30:45"
     */
    updateCountdown(timeString) {
        this.elements.countdown.textContent = timeString;
    },

    /**
     * 显示状态信息（成功/失败/提示）
     * @param {string} message - 文字内容
     * @param {boolean} isSuccess - 是否为成功（绿色），否则为提示/错误（红色/黄色）
     */
    showStatus(message, isSuccess = true) {
        this.elements.status.textContent = message;
        this.elements.status.style.color = isSuccess ? '#4caf50' : '#e65100';
    },

    /**
     * 弹出页面内通知弹窗
     * @param {string} message - 弹窗显示的文字
     * @param {Function} [onClose] - 关闭弹窗后的回调
     */
    showPagePopup(message, onClose) {
        this.elements.popupMessage.textContent = message;
        this.elements.popupOverlay.classList.remove('hidden');
        // 移除之前绑定的关闭事件
        const closeHandler = () => {
            this.hidePagePopup();
            if (onClose) onClose();
        };
        this.elements.popupClose.onclick = closeHandler;
    },

    /**
     * 隐藏弹窗
     */
    hidePagePopup() {
        this.elements.popupOverlay.classList.add('hidden');
    },

    /**
     * 重置UI到初始状态：清除倒计时、启用设置按钮、禁用取消按钮、清空状态
     */
    resetUI() {
        this.updateCountdown('--:--:--');
        this.elements.setBtn.disabled = false;
        this.elements.cancelBtn.disabled = true;
        this.showStatus('', true);
        this.hidePagePopup();
    },

    /**
     * 设置提醒按钮点击事件绑定
     * @param {Function} callback
     */
    onSetClick(callback) {
        this.elements.setBtn.addEventListener('click', callback);
    },

    /**
     * 取消提醒按钮点击事件绑定
     * @param {Function} callback
     */
    onCancelClick(callback) {
        this.elements.cancelBtn.addEventListener('click', callback);
    },

    /**
     * 获取当前输入的提醒内容，若为空则返回默认文字
     * @returns {string}
     */
    getMessage() {
        const text = this.elements.messageInput.value.trim();
        return text || '该吃饭啦！';
    }
};
```

### js/app.js

```javascript
/**
 * 应用主入口
 * 协调各模块，实现完整的提醒流程
 */
import { Timer } from './timer.js';
import { Notifier } from './notification.js';
import { UI } from './ui.js';
import { getTomorrowNoon, formatRemaining, playBeep } from './utils.js';

// DOM 完全加载后初始化
document.addEventListener('DOMContentLoaded', () => {
    UI.init();

    // 显示默认目标时间
    const tomorrowNoon = getTomorrowNoon();
    const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
    UI.updateTargetTime(tomorrowNoon.toLocaleString(undefined, options));

    let usePageFallback = false; // 标记是否无法使用系统通知

    // 设置提醒按钮处理
    UI.onSetClick(async () => {
        // 禁用设置按钮防止重复点击
        UI.elements.setBtn.disabled = true;

        // 检查通知支持情况
        if (Notifier.isSupported()) {
            const permission = await Notifier.requestPermission();
            if (permission !== 'granted') {
                usePageFallback = true;
                UI.showStatus('⚠️ 通知被拒绝，将使用页面弹窗', false);
            } else {
                usePageFallback = false;
                UI.showStatus('✅ 提醒已设置', true);
            }
        } else {
            usePageFallback = true;
            UI.showStatus('⚠️ 浏览器不支持系统通知，将使用页面弹窗', false);
        }

        // 启用取消按钮
        UI.elements.cancelBtn.disabled = false;

        // 获取提醒内容
        const message = UI.getMessage();

        // 设置定时器
        const targetTS = tomorrowNoon.getTime();
        Timer.setTimer(
            targetTS,
            // 触发提醒回调
            () => {
                // 尝试发送系统通知
                const sent = Notifier.sendNotification('吃饭提醒', message);
                if (!sent) {
                    // 页面弹窗 + 音效
                    UI.showPagePopup(`⏰ 吃饭提醒：${message}`, () => {
                        // 关闭弹窗后可选择性停止音效
                    });
                    playBeep(1000);
                }
                // 触发后重置UI（取消定时器已在timer内部调用cancelTimer并回调onTrigger）
                UI.resetUI();
                UI.showStatus('🕐 提醒已触发', true);
            },
            // 每秒更新倒计时
            (remainingMs) => {
                UI.updateCountdown(formatRemaining(remainingMs));
            }
        );
    });

    // 取消提醒按钮处理
    UI.onCancelClick(() => {
        Timer.cancelTimer();
        UI.resetUI();
        UI.showStatus('提醒已取消', false);
        usePageFallback = false;
    });

    // 初始状态：确保弹窗隐藏
    UI.hidePagePopup();
});
```

## 运行说明

1. **直接打开**：将上述文件按目录结构放置后，直接用浏览器打开 `index.html` 即可运行。  
2. **本地服务器**（推荐）：如使用 VSCode 的 Live Server 插件，或 Python 启动简易服务器：
   ```bash
   # Python 3
   python -m http.server 8080
   ```
   然后访问 `http://localhost:8080`。  
3. **移动端测试**：可使用手机浏览器访问同一局域网下的地址（需确保本地服务器局域网可用）。

### 注意事项
- 由于使用了 ES Module (`type="module"`)，**必须通过 HTTP 协议访问**，不能直接双击 `index.html` 使用 `file://` 协议（浏览器会禁止跨域请求模块脚本）。  
- 如果无法使用服务器，也可将 `app.js` 改为普通 `<script>` 内联方式，但本实现为了模块化清晰，推荐使用简单静态服务器。

### 功能测试
- 默认时间显示为“明天 12:00”（根据你当前时区）。  
- 修改提醒内容文本框（默认“该吃饭啦！”）。  
- 点击“设置提醒”，倒计时开始，按钮状态切换。  
- 到达时间后，若授予过通知权限，弹出系统通知；否则页面弹窗 + 1秒音效。  
- 点击“取消提醒”可随时撤销，界面重置。

---

所有代码合计约 230 行 JavaScript，满足 MVP 最小可运行要求，结构清晰，方便后续扩展。