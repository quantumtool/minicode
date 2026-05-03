根据产品需求文档，设计一个最小可运行的Web应用架构，专注于极简、单次提醒、纯前端实现。以下是详细方案。

---

## 1. 技术选型

| 层级 | 技术 | 理由 |
|------|------|------|
| **UI** | HTML5 + CSS3 | 原生语义化标签、Flexbox/Grid实现移动端适配；无需构建工具，加载即用 |
| **样式** | 纯CSS（单文件） | 卡片式布局、平滑动画、媒体查询，无外部框架依赖，体积最小 |
| **交互逻辑** | 原生JavaScript（ES6+） | 模块化（ES Modules）管理功能块，无需打包工具，浏览器原生支持 |
| **通知** | Notification API + Web Audio API | 系统通知（支持则使用） + 页面弹窗+音效回退（符合MVP要求） |
| **定时器** | setTimeout（配合Date.now()） | 单次提醒无需复杂调度，setTimeout精度满足秒级误差 |
| **持久化** | 无（内存变量） | MVP不要求关闭页面后持久化，关闭即失效 |

**不选框架**：Vue/React 会增加初始加载成本和复杂度，MVP只需一个页面，原生三件套已足够，且更易被开发者快速理解和修改。

---

## 2. 项目目录结构

```
reminder-app/
├── index.html              # 主页面：卡片布局、引用CSS和JS模块
├── css/
│   └── style.css           # 所有样式：卡片、按钮、倒计时、弹窗、响应式
└── js/
    ├── app.js              # 入口文件：初始化、绑定事件、协调模块
    ├── timer.js            # 倒计时模块：计算剩余时间、启动/停止setInterval
    ├── notification.js     # 通知模块：请求权限、触发系统通知或页面回退（弹窗+音效）
    ├── ui.js               # UI更新模块：设置/取消状态、倒计时显示、提示信息、弹窗控制
    └── utils.js            # 工具函数：计算明天12:00时间戳、格式化时间、生成beep音效
```

> 音效采用Web Audio API在`utils.js`中生成，无需额外音频文件。

---

## 3. 每个文件的作用

### `index.html`
- 渲染卡片式界面：包含提醒内容输入框、默认时间展示（只读）、“设置提醒”按钮、“取消提醒”按钮、倒计时显示区、状态提示区。
- 以`<script type="module" src="js/app.js">`加载主入口，保证模块化。
- 移动端viewport设置、图标占位等。

### `css/style.css`
- 卡片居中，最大宽度400px，背景柔光颜色（如#f5f5f5），阴影圆角。
- 按钮样式（绿色/红色），输入框，倒计时大号字体（等宽字体），弹窗遮罩+居中内容。
- 媒体查询：`@media (max-width: 480px)` 适配小屏，按钮高度≥44px，字体适当放大。
- 简单过渡动画（比如弹窗淡入、按钮点击反馈）。

### `js/utils.js`
- **`getTomorrowNoon()`**：基于本地时区，返回明天12:00的`Date`对象。
  - 逻辑：`new Date()` + 1天，setHours(12,0,0,0)，注意跨月问题（利用Date自动处理）。
- **`formatRemaining(ms)`**：将剩余毫秒转化为`HH:MM:SS`字符串。
- **`playBeep(duration = 1000)`**：使用`AudioContext`生成440Hz正弦波，持续1秒，自动播放（需用户交互后）。返回`stop`函数以便取消（非必须）。
- **`showPageAlert(message, isError = false)`**：在页面内创建一个临时弹窗（覆盖层+居中文字+“知道了”按钮），或直接修改现有弹窗元素（由`ui.js`管理）。

### `js/timer.js`
- **导出类或函数集合**（推荐导出对象`Timer`）
- **属性**：`timeoutId`（setTimeout句柄）、`intervalId`（setInterval句柄）、`targetTime`（时间戳）、`callback`（触发提醒的回调）。
- **方法**：
  - `setTimer(targetTimestamp, onTrigger)`：计算剩余时间，若≤0立即触发，否则启动setTimeout；同时启动setInterval每秒更新UI（由调用者传入回调更新倒计时）。
  - `cancelTimer()`：清除两计时器，重置相关属性。
  - `getRemaining()`：返回当前剩余毫秒数。

### `js/notification.js`
- **导出对象`Notifier`**
- **`requestPermission()`**：调用`Notification.requestPermission()`，返回promise状态（granted/denied/default）。
- **`sendNotification(title, body)`**：如果权限为granted，创建`new Notification(title, {body})`；否则返回false，由调用方触发页面回退。
- **`isSupported()`**：检查`window.Notification`是否存在。

### `js/ui.js`
- **导出对象`UI`**，管理界面所有DOM元素引用（不直接在全局查找，避免耦合）。
- **方法**：
  - `init()`：获取各元素引用（文本框、按钮、倒计时显示区、状态提示区、时间显示区域等），返回自身。
  - `updateCountdown(timeString)`：更新倒计时显示。
  - `showStatus(message, isSuccess)`：设置状态提示区样式（绿色/红色）并显示文字。
  - `showPagePopup(message, onCloseCallback)`：显示页面内弹窗（可能包含音效触发），点击关闭后回调。
  - `hidePagePopup()`：隐藏弹窗。
  - `resetUI()`：恢复初始状态：倒计时清空、按钮可用、状态清空。
  - `onSetClick(callback)`、`onCancelClick(callback)`：绑定事件（解耦事件处理与DOM）。

### `js/app.js`
- **核心协调者**：
  1. 导入`Timer`、`Notifier`、`UI`、`utils`。
  2. `UI.init()`后，获取明天12:00时间并展示在界面（只读）。
  3. 绑定设置按钮点击事件：
     - 检查通知支持情况，若支持且未授权则请求权限。
     - 获取用户输入的提醒内容（若为空则使用默认“该吃饭啦！”）。
     - 调用`Timer.setTimer()`，传入明天noon时间戳和`onTrigger`回调。
     - `onTrigger`回调：先尝试`Notifier.sendNotification`，若失败则`UI.showPagePopup` + `utils.playBeep`。
     - 启动倒计时更新：`Timer`内部的interval每秒调用`UI.updateCountdown`。
     - 显示“✅ 提醒已设置”状态，根据通知权限情况附加提示。
  4. 绑定取消按钮点击事件：
     - `Timer.cancelTimer()`，`UI.resetUI()`，显示“提醒已取消”。
  5. 页面关闭/刷新无需特殊处理（不持久化）。

---

## 4. 核心模块说明

### 定时与倒计时模块（timer.js）
- 使用两个定时器：一个`setTimeout`用于触发提醒，一个`setInterval`（每秒）用于更新UI剩余时间。
- 计算剩余时间时，每次获取当前时间戳与`targetTime`比较，精准避免累积误差。
- 取消时同时清除两个定时器，并将状态置为未设置。

### 通知与回退机制（notification.js + utils.js）
- 策略：  
  1. 点击设置时，若`Notification.permission`为`granted`，直接登记。  
  2. 若为`default`，先请求权限，等待结果（promise）。  
  3. 若最终权限为`denied`或浏览器不支持，则标记为“使用页面回退”。  
  4. 触发时：系统通知优先，否则页面弹窗+音效。
- 页面弹窗设计：一个固定定位的遮罩层，内含提醒文字和关闭按钮，音效通过`AudioContext`播放1秒。

### UI状态管理（ui.js）
- 不依赖框架的响应式，采用直接DOM操作。提供清晰的方法接口，便于后续扩展（如增加自定义时间选择器）。
- 状态反馈分为三种：成功（绿色）、提示（黄色）、取消（灰色）。
- 倒计时显示区防止文字闪烁，使用`innerText`替换，CSS加`transition: none`。

---

## 5. 开发顺序

| 步骤 | 内容 | 产出 |
|------|------|------|
| 1 | 创建`index.html`基础骨架：卡片、输入框、按钮、状态区、倒计时区、隐藏的弹窗层 | 静态HTML |
| 2 | 编写`css/style.css`：响应式卡片、按钮样式、弹窗样式、状态颜色 | 基础UI |
| 3 | 实现`js/utils.js`：`getTomorrowNoon`、`formatRemaining`、`playBeep` | 工具函数 |
| 4 | 实现`js/timer.js`：Timer对象的setTimer、cancelTimer、getRemaining | 定时核心 |
| 5 | 实现`js/notification.js`：权限请求、发送系统通知、检查支持 | 通知模块 |
| 6 | 实现`js/ui.js`：DOM元素管理、更新倒计时、状态提示、弹窗控制 | UI模块 |
| 7 | 实现`js/app.js`：整合所有模块，绑定事件，协调完整流程 | 可运行应用 |
| 8 | 测试验收：五个场景、Safari回退、移动端适配、时间准确性 | 满足验收标准 |

**说明**：步骤3-6可并行开发，但建议按顺序以降低集成风险。所有模块通过ES Module导入导出，无需构建工具，直接使用`type="module"`运行。

---

## 附加说明

- **扩展性保留**：架构已预留自定义日期接口：只需在UI增加时间选择器，修改`utils.getTomorrowNoon`为获取用户选择的时间，其余模块无需大改。重复提醒可通过增加`setInterval`循环触发，但MVP不做。
- **无后端依赖**：整个应用可部署在任意静态托管（GitHub Pages、Netlify、Vercel），文件名和目录结构符合常规Web服务器规则。
- **代码量估计**：每个JS文件约30-80行，总计300行以内，轻量可维护。