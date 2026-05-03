## 俄罗斯方块小游戏 - 技术架构与开发方案

### 一、技术选型

- **前端框架**：无（纯原生Web技术栈，零依赖）
- **渲染**：**Canvas 2D API**（性能好，像素级控制，适合方块类游戏）
- **语言**：HTML5 + CSS3 + **JavaScript (ES6+)**
- **音效**：**Web Audio API** 合成简单音效（无需外部音频文件，体积最小）
- **模块化**：ES6 `export/import`（现代浏览器均支持，便于维护）
- **开发工具**：任意文本编辑器 + 浏览器直接运行（无构建步骤）

### 二、项目目录结构

```
tetris/
├── index.html                # 入口页面：包含画布、UI元素、引入JS模块
├── css/
│   └── style.css             # 全局样式：布局、按钮、字体、颜色主题
├── js/
│   ├── main.js               # 应用入口：初始化各模块，启动游戏循环
│   ├── constants.js          # 配置常量：棋盘尺寸、方块形状、颜色、速度参数、计分规则
│   ├── board.js              # 棋盘数据模型：二维数组存储固定方块，碰撞检测，消行逻辑
│   ├── piece.js              # 当前方块对象：形状、位置、旋转、移动、克隆
│   ├── game.js               # 游戏核心控制器：状态机（playing/paused/over），游戏循环，难度递增
│   ├── renderer.js           # 渲染引擎：绘制棋盘、方块、预览、分数、覆盖层
│   ├── input.js              # 键盘事件管理：绑定/解绑事件，映射操作
│   ├── audio.js              # 音效发生器：Web Audio API 生成消行/结束音效
│   └── utils.js              # 工具函数：随机数、深拷贝、矩阵旋转等
```

### 三、每个文件的作用

| 文件 | 职责 |
|------|------|
| `index.html` | 提供页面骨架，包含 Canvas、分数显示区、预览区、暂停/重启按钮；通过 `<script type="module">` 加载 `main.js` |
| `style.css` | 定义整体布局（居中、网格背景）、按钮样式、字体、颜色，确保1024×768以上显示完整 |
| `constants.js` | 导出所有不可变配置，如棋盘列数10、行数20、单元格尺寸30px、7种方块形状矩阵、颜色映射、初始下落间隔800ms、每10行加速100ms（最低100ms）、消行分数 {1:100, 2:300, 3:500, 4:800} |
| `board.js` | 导出 `Board` 类：`grid` 二维数组（0表示空，1-7对应颜色ID）；方法 `isValidPosition()`, `lockPiece()`, `clearFullRows()`, `isGameOver()`, `reset()` |
| `piece.js` | 导出 `Piece` 类：属性 `shape`, `x`, `y`, `colorId`；方法 `rotate()`, `moveLeft()`, `moveRight()`, `moveDown()`, `clone()`，基于当前形状矩阵和坐标 |
| `game.js` | 导出 `Game` 类：持有 Board、当前 Piece、下一个 Piece、分数、速度、行数计数器；运行 `requestAnimationFrame` 循环；处理方块下落、碰撞、消行、难度升级；暴露 `start()`, `pause()`, `restart()`, `handleAction()` 接口 |
| `renderer.js` | 导出 `Renderer` 类：接收 Canvas 上下文；绘制网格线、已固定方块、当前方块（含幽灵块显示？MVP可暂不）、下一个预览、分数文本、暂停/结束覆盖层；每帧调用一次 |
| `input.js` | 导出 `InputHandler` 类：监听 `keydown` 事件，将方向键、空格、P键映射到 Game 的方法；提供 `bind()` 和 `unbind()` |
| `audio.js` | 导出 `AudioManager` 类：使用 Web Audio API 创建 `OscillatorNode`；提供 `playLineClear()`（短促上升音）、`playGameOver()`（低沉下降音）；默认静音可外部控制 |
| `utils.js` | 提供 `randomPieceType()`, `deepCopyArray()`, `rotateMatrix()` 等通用函数 |

### 四、核心模块说明

#### 4.1 游戏循环（Game 类）
- 基于 `requestAnimationFrame` + 时间累积实现帧率无关下落。
- 每帧调用 `update(deltaTime)`：累计下落时间，达到当前速度间隔时尝试下落，若无法下落则锁定当前方块到 Board，生成新 Piece，判断游戏结束。
- 锁定后调用 `Board.clearFullRows()`，更新分数，检查是否达到难度升级条件（每消除10行）。
- 管理游戏状态枚举：`'idle'`, `'playing'`, `'paused'`, `'over'`。

#### 4.2 碰撞检测（Board 类）
- `isValidPosition(piece, offsetX, offsetY, newShape?)`：检查指定方块（可带偏移和旋转）的所有非空格子是否在棋盘边界内且不与已固定格子重叠。
- 移动、旋转、硬降前先调用该方法，只有合法才执行。

#### 4.3 输入处理（InputHandler 类）
- 键盘映射：
  - `ArrowLeft` → `game.movePiece(-1, 0)`
  - `ArrowRight` → `game.movePiece(1, 0)`
  - `ArrowUp` → `game.rotatePiece()`
  - `ArrowDown` → `game.softDrop()`
  - `Space` → `game.hardDrop()`
  - `p` / `P` → `game.togglePause()`
- 使用 `event.preventDefault()` 防止页面滚动。

#### 4.4 渲染（Renderer 类）
- 绘制顺序：背景网格 → 已固定方块 → 当前方块 → 预览方块 → 分数文字 → 状态覆盖层。
- 预览方块绘制在右上角专用区域（画布额外区域或单独 Canvas）。
- 游戏结束时绘制半透明遮罩 + 得分弹窗。

#### 4.5 音效（AudioManager 类）
- 消行时触发 `playLineClear()`：短促正弦波（频率 440Hz → 880Hz，时长 80ms）。
- 游戏结束时触发 `playGameOver()`：低频三角波（频率 200Hz → 100Hz，时长 300ms）。
- 默认输出音量 0.3；可通过设置 `audioManager.muted = true` 静音（无UI控制，MVP不做）。

### 五、开发顺序（分步迭代）

| 阶段 | 任务 | 验证点 |
|------|------|--------|
| **1. 渲染骨架** | 创建 `index.html` + `style.css`，放置 Canvas 和 UI 元素，实现静态下棋界面 | 页面居中，显示10×20网格 |
| **2. 数据模型** | 实现 `constants.js`，`board.js`，`piece.js`，`utils.js`；编写单元测试（手动控制台输出） | 棋盘格子正确、方块形状矩阵清晰、碰撞检测可用 |
| **3. 核心逻辑** | 实现 `game.js`：游戏循环、下落、碰撞、锁定、消行、计分、难度递增 | 方块自动下落，满行消除并加分 |
| **4. 键盘控制** | 实现 `input.js`，绑定所有按键，实现移动、旋转、加速、硬降、暂停 | 方块响应操作流畅，无延迟 |
| **5. 完整渲染** | 完善 `renderer.js`：绘制当前方块、预览、分数、暂停/结束覆盖层 | 下一个方块正确，分数实时更新，暂停时画面冻结 |
| **6. 音效&打磨** | 实现 `audio.js`，加入消行和结束音效；修复边界条件（如旋转卡墙） | 音效播放正常，操作手感丝滑 |
| **7. 集成测试** | 确保所有验收标准达标，浏览器兼容（Chrome/Edge/Firefox），调整UI细节 | 符合需求文档全部验收项 |

整个开发过程中所有文件均可直接通过浏览器访问 `index.html` 运行，无需任何构建工具或服务器。