好的，收到产品需求文档。作为架构师 Agent，我将基于“极简”、“开箱即玩”、“纯核心玩法”的原则，设计一套最小可运行的软件架构。

---

### 架构设计方案：极简俄罗斯方块 (MVP)

#### 1. 技术选型

- **运行环境**：**纯浏览器（Web）**。这是实现“零启动成本”、“即开即玩”的最佳选择，无需安装，跨平台（PC/手机/平板）。
- **核心语言**：**HTML5 + CSS3 + 原生 JavaScript (ES6+)**
    - **HTML**：负责游戏页面的基本结构。
    - **CSS3**：负责界面样式、布局和响应式适配。
    - **JavaScript**：负责所有游戏逻辑、渲染和交互控制。
- **渲染方式**：**Canvas 2D API**。HTML5 Canvas 是轻量级、高性能的游戏渲染方案，非常适合 2D 网格游戏的实时绘制，且无需任何外部依赖。
- **模块化**：**ES6 Modules**。利用 `<script type="module">` 实现代码的模块化组织，使代码结构清晰，易于维护和测试。
- **事件驱动**：**原生 DOM 事件 + 自定义事件**。用于处理键盘和触摸输入。无需引入第三方框架或库。

**技术选型理由**：零依赖、极简、跨平台、学习成本低，完全符合 MVP “快”、“纯” 的定位。

#### 2. 项目目录结构

```
tetris-mvp/
├── index.html          # 游戏入口页面，是唯一的用户界面。
├── style.css           # 页面样式和布局。
├── js/
│   ├── main.js         # 应用初始化入口，启动游戏主循环。
│   ├── game-core.js    # 核心游戏逻辑模块（棋盘、方块、碰撞检测、消行、分数、状态管理）。
│   ├── renderer.js     # Canvas 渲染模块（绘制游戏区域、方块、预览、分数、游戏结束画面）。
│   ├── input-handler.js # 输入控制模块（键盘事件和触摸事件监听与映射）。
│   └── sound-manager.js # 音效管理模块（预加载并播放简单音效，支持开/关）。
└── assets/
    └── sound/          # 存放音效文件（可选，可使用 Web Audio API 合成简单音效以避免外部文件）
        ├── move.wav
        ├── rotate.wav
        ├── clear.wav
        └── gameover.wav
```

#### 3. 每个文件的作用

- **`index.html`**：游戏的主入口。
    - 引入 `style.css` 和所有 JS 模块（通过 `<script type="module" src="js/main.js"></script>`）。
    - 定义游戏界面 HTML 结构：一个用于渲染游戏区域的 `<canvas>` 元素、显示分数的 `<div>`、显示下一个方块的 `<canvas>` 元素、音效开关按钮等。
- **`style.css`**：负责页面的所有样式。
    - 游戏页面整体布局（居中、响应式）。
    - 游戏区域、预览区域的边框、背景色。
    - 分数显示、按钮的样式。
    - 游戏结束提示覆盖层的样式。
    - 触摸控制按钮（如果采用虚拟按钮方式）的样式。
- **`main.js`**：应用的**启动器**。
    - 引入 `GameCore`、`Renderer`、`InputHandler`、`SoundManager` 四个核心模块。
    - 实例化它们，并建立模块间的通信（依赖注入）。
    - 启动游戏主循环（`requestAnimationFrame` 驱动）。
    - 监听 `InputHandler` 的事件，调用 `GameCore` 的对应方法（如 `moveLeft()`, `moveRight()`, `rotate()`, `hardDrop()`）。
    - 监听 `GameCore` 的状态变化（如分数更新、游戏结束），调用 `Renderer` 更新画面。
- **`game-core.js`**：游戏**逻辑引擎**，不依赖 UI。
    - 定义 **`Board`** 类：管理 10x20 的游戏网格状态（二维数组），提供设置、获取、消除整行、检查碰撞、判断游戏结束的方法。
    - 定义 **`Tetromino`** 类：封装七种方块的形状、颜色、旋转状态（使用矩阵表示），提供获取当前形状、旋转后形状、下一个方块的方法。
    - 定义 **`GameCore`** 类：整合 `Board` 和 `Tetromino`。
        - **状态**：当前方块、下一个方块、当前分数、游戏是否运行。
        - **核心逻辑**：`tick()` (定时下落)、`moveLeft/Right/Down`、`rotate`、`hardDrop`、`lockPiece` (锁定方块)、`clearLines`、`spawnNext` (生成方块)、`gameOver` 检测。
        - 使用 `EventTarget` 或简单回调函数，当有状态变化时通知外部（如 `onScoreChange`, `onGameOver`, `onGridUpdate`）。
- **`renderer.js`**：**纯视图层**。
    - 接收 `GameCore` 的状态（棋盘网格、当前方块、下一个方块、分数）和 DOM 中的 Canvas 元素引用。
    - 实现 `render()` 方法，在每一帧调用 `requestAnimationFrame` 循环渲染。
    - **绘制内容**：
        - 清空 Canvas。
        - 绘制网格背景。
        - 绘制已锁定在棋盘上的方块。
        - 绘制当前正在下落的方块。
        - 绘制“下一个方块”预览。
        - 绘制分数。
        - 如果游戏结束，绘制“Game Over”覆盖层。
        - 实现行消除的闪烁动画（简单的逐帧动画逻辑）。
- **`input-handler.js`**：**交互控制层**。
    - 初始化键盘事件监听：`keydown`（下移、快速下落）、`keyup`（左、右、旋转）。防止长按导致的意外连续触发。
    - 初始化触摸事件监听：
        - **方案A（推荐）**：监听整个游戏区域的触摸屏手势（滑动方向 = 移动，点击 = 旋转，长按或快速滑动下 = 快速下落）。
        - **方案B**：在页面底部渲染虚拟按钮（左、右、旋转、下），监听其 `touchstart` 事件。
    - 将原始输入事件统一转换成游戏逻辑可识别的指令列表（如 `'MOVE_LEFT'`, `'ROTATE'`）。
    - 暴露 `getCommands()` 或通过事件 `emit('input', command)` 供 `main.js` 消费。
- **`sound-manager.js`**：**音效控制器**。
    - **方案一（简单）**：使用 `<audio>` 元素预加载 `assets/sound/` 下的音效文件，提供 `play('move')`, `stop()` 等方法。
    - **方案二（更轻量）**：使用 **Web Audio API** 生成简单的合成音效（如一个短促的方波或噪声）。无需外部音频文件，符合“极简”理念。
    - 提供一个开关方法（`toggle()`) 来控制音效的播放与静音。

#### 4. 核心模块说明

- **状态管理**：**所有游戏状态统一放在 `GameCore` 中**。`Renderer` 和 `InputHandler` 不存储状态，只负责读取和消费。这是典型的 **单向数据流**，避免状态混乱。
- **方块逻辑**：方块形状用二维布尔数组表示，旋转通过矩阵转置和轴对称实现。碰撞检测是 `GameCore` 中最关键的性能点，通过检查方块矩阵与棋盘网格的坐标交集实现。
- **游戏循环**：由 `main.js` 中的 `requestAnimationFrame` 驱动。每次循环：
    1.  `InputHandler` 获取最新输入指令。
    2.  `GameCore` 根据指令更新逻辑状态。
    3.  `Renderer` 读取最新状态并绘制。
- **事件驱动**：`InputHandler` 和 `GameCore` 通过发布-订阅模式通信。`GameCore` 不直接操作 DOM 或 Canvas，它只发射事件（如 `scoreUpdated`, `gameOver`, `pieceLocked`）。`Renderer` 和 `SoundManager` 订阅这些事件来执行对应操作。这样，逻辑和视图完全解耦。

#### 5. 开发顺序

建议按以下顺序，确保每一步都可运行、可验证：

1.  **基础环境搭建**：
    - 创建 `index.html`、`style.css`、`js/main.js`。
    - 在 `index.html` 中放置一个 `canvas` 元素并固定宽高（如 300x600）。
    - 在 `main.js` 中使用 `console.log('Game Start')` 验证模块加载成功。

2.  **核心游戏逻辑 `GameCore`**：
    - 实现 `Board` 类：一个 10x20 的网格数组，包含 `setCell(x, y)`、`isLineFull(y)`、`clearLine(y)` 方法。
    - 实现 `Tetromino` 类：定义七种方块的形状和旋转矩阵。
    - 实现 `GameCore` 类：
        - 生成第一个方块并放置在棋盘顶部中央。
        - 实现 `tick()` 方法：让当前方块向下移动一行。
        - 实现碰撞检测（向下、左右、旋转）。
        - 实现锁定方块（将方块数据写入 `Board`）。
        - **此时 `GameCore` 应能在控制台打印出棋盘状态**。

3.  **基础渲染 `Renderer`**：
    - 实现 `render()` 方法，将 `GameCore` 的棋盘网格和当前方块绘制在 Canvas 上。
    - 实现绘制网格线（可选，增强视觉效果）。
    - **此时，可以在浏览器中看到方块开始下落，并停在棋盘边界**。

4.  **输入控制 `InputHandler`**：
    - 实现键盘事件监听，映射到 `GameCore` 的 `moveLeft()`, `moveRight()`, `moveDown()`, `rotate()`。
    - 确保触摸屏幕的初始滑动或点击产生正确指令。
    - **此时，可以通过键盘/触摸控制方块左右移动、旋转、加速下落**。

5.  **完成核心玩法循环**：
    - 完善 `GameCore` 的 `clearLines()` 逻辑（检测并消除满行，更新分数）。
    - 实现 `spawnNext()` 方法：当一个方块被锁定时，生成下一个方块，并将“下一个方块”推送给 `Renderer`。
    - 实现游戏结束逻辑。
    - **此时，一个完整的可玩循环已经形成**。

6.  **界面与交互优化**：
    - 在 `index.html` 中添加分数显示、下一个方块预览的 Canvas 或 `<div>`。
    - 在 `Renderer` 中绘制这些元素。
    - 添加音效开关按钮（UI）和音效控制模块。
    - 实现行消除动画（简单的闪烁或渐变）。
    - 实现适配不同屏幕尺寸的响应式布局（使用 `vh/vw`、 `rem` 或 max-width）。

7.  **最后收尾**：
    - 测试并修复所有边界情况（如旋转卡墙、超快速按键、触摸误触）。
    - 确认音效开关正常工作。
    - 确认“Game Over”后按任意键可重新开始。