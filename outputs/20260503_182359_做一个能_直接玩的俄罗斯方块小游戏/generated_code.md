以下是生成的最小可运行版本俄罗斯方块代码。所有文件均采用纯原生 Web 技术栈，无任何外部依赖，直接通过浏览器打开 `index.html` 即可运行（建议使用本地服务器以避免模块加载的 CORS 限制）。

---

## 运行说明

1. 将以下所有文件按照目录结构保存：
   ```
   tetris/
    ├── index.html
    ├── css/
    │   └── style.css
    └── js/
        ├── main.js
        ├── constants.js
        ├── board.js
        ├── piece.js
        ├── game.js
        ├── renderer.js
        ├── input.js
        ├── audio.js
        └── utils.js
   ```
2. 使用任意本地静态服务器（如 VS Code 的 Live Server、Python 的 `http.server`）或直接打开 `index.html`（部分浏览器可能因安全策略限制 ES6 模块对 `file://` 的访问，推荐使用 Live Server）。
3. 游戏自动开始，使用键盘控制：
   - `←`/`→`：左右移动
   - `↑`：旋转
   - `↓`：加速下落
   - `空格`：直接落底
   - `P`：暂停/继续
4. 游戏结束后点击“重新开始”按钮或按回车键即可重玩。

---

## 文件清单

### `index.html`
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>俄罗斯方块 - MVP</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div id="game-container">
        <div id="game-board">
            <canvas id="board-canvas" width="300" height="600"></canvas>
        </div>
        <div id="side-panel">
            <div id="info">
                <div>分数: <span id="score">0</span></div>
                <div>等级: <span id="level">1</span></div>
                <div>行数: <span id="lines">0</span></div>
            </div>
            <div id="next-piece">
                <div>下一个:</div>
                <canvas id="preview-canvas" width="120" height="120"></canvas>
            </div>
            <div id="controls">
                <button id="pause-btn">暂停</button>
                <button id="restart-btn">重新开始</button>
            </div>
        </div>
    </div>
    <div id="overlay" class="hidden">
        <div id="game-over-box">
            <h2>游戏结束</h2>
            <p>得分: <span id="final-score">0</span></p>
            <button id="restart-overlay-btn">重新开始</button>
        </div>
    </div>
    <script type="module" src="js/main.js"></script>
</body>
</html>
```

### `css/style.css`
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background: #1a1a2e;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #fff;
}

#game-container {
    display: flex;
    gap: 20px;
    padding: 20px;
    background: #16213e;
    border-radius: 8px;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
}

#game-board {
    border: 2px solid #0f3460;
    background: #111;
}

#board-canvas {
    display: block;
}

#side-panel {
    width: 150px;
}

#info {
    margin-bottom: 20px;
    font-size: 18px;
    line-height: 1.8;
}

#info span {
    font-weight: bold;
    color: #e94560;
}

#next-piece {
    margin-bottom: 20px;
}

#next-piece div {
    font-size: 16px;
    margin-bottom: 5px;
}

#preview-canvas {
    background: #111;
    border: 1px solid #0f3460;
}

#controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

button {
    padding: 10px;
    font-size: 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    background: #e94560;
    color: #fff;
    transition: background 0.2s;
}

button:hover {
    background: #c23152;
}

#overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10;
}

#overlay.hidden {
    display: none;
}

#game-over-box {
    background: #16213e;
    padding: 40px;
    border-radius: 10px;
    text-align: center;
}

#game-over-box h2 {
    margin-bottom: 20px;
    font-size: 28px;
}

#game-over-box p {
    font-size: 20px;
    margin-bottom: 20px;
}
```

### `js/constants.js`
```javascript
// 棋盘尺寸
export const COLS = 10;
export const ROWS = 20;
export const BLOCK_SIZE = 30; // 像素

// 方块形状矩阵 (4x4)
export const SHAPES = [
    // I
    [
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0]
    ],
    // O
    [
        [1,1],
        [1,1]
    ],
    // T
    [
        [0,1,0],
        [1,1,1],
        [0,0,0]
    ],
    // S
    [
        [0,1,1],
        [1,1,0],
        [0,0,0]
    ],
    // Z
    [
        [1,1,0],
        [0,1,1],
        [0,0,0]
    ],
    // L
    [
        [1,0,0],
        [1,1,1],
        [0,0,0]
    ],
    // J
    [
        [0,0,1],
        [1,1,1],
        [0,0,0]
    ]
];

// 颜色 (索引 1-7)
export const COLORS = [
    null,           // 0: 空
    '#00f0f0',      // I 青色
    '#f0f000',      // O 黄色
    '#a000f0',      // T 紫色
    '#00f000',      // S 绿色
    '#f00000',      // Z 红色
    '#f0a000',      // L 橙色
    '#0000f0'       // J 蓝色
];

// 初始下落间隔 (毫秒)
export const INITIAL_DROP_INTERVAL = 800;
// 每消除10行减少的毫秒数
export const LEVEL_DECREASE = 100;
// 最小下落间隔
export const MIN_DROP_INTERVAL = 100;

// 计分规则：消除行数 => 分数
export const SCORE_TABLE = {
    1: 100,
    2: 300,
    3: 500,
    4: 800
};

// 每个等级的消除行数阈值
export const LINES_PER_LEVEL = 10;
```

### `js/utils.js`
```javascript
// 生成随机方块类型 (0~6)
export function randomPieceType() {
    return Math.floor(Math.random() * 7);
}

// 深拷贝二维数组
export function deepCopyArray(arr) {
    return arr.map(row => [...row]);
}

// 顺时针旋转矩阵
export function rotateMatrix(matrix) {
    const rows = matrix.length;
    const cols = matrix[0].length;
    const result = [];
    for (let c = 0; c < cols; c++) {
        result[c] = [];
        for (let r = rows - 1; r >= 0; r--) {
            result[c].push(matrix[r][c]);
        }
    }
    return result;
}
```

### `js/board.js`
```javascript
import { COLS, ROWS } from './constants.js';
import { deepCopyArray } from './utils.js';

export class Board {
    constructor() {
        this.grid = this.createEmptyGrid();
    }

    createEmptyGrid() {
        return Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    }

    reset() {
        this.grid = this.createEmptyGrid();
    }

    // 检查方块是否可以在指定位置放置（offsetX, offsetY 和可选的形状）
    isValidPosition(piece, offsetX = 0, offsetY = 0, shape = null) {
        const matrix = shape || piece.shape;
        for (let r = 0; r < matrix.length; r++) {
            for (let c = 0; c < matrix[r].length; c++) {
                if (matrix[r][c] !== 0) {
                    const newX = piece.x + c + offsetX;
                    const newY = piece.y + r + offsetY;
                    if (newX < 0 || newX >= COLS || newY >= ROWS || newY < 0) return false;
                    if (newY >= 0 && this.grid[newY][newX] !== 0) return false;
                }
            }
        }
        return true;
    }

    // 将方块固定到棋盘
    lockPiece(piece) {
        const matrix = piece.shape;
        for (let r = 0; r < matrix.length; r++) {
            for (let c = 0; c < matrix[r].length; c++) {
                if (matrix[r][c] !== 0) {
                    const y = piece.y + r;
                    const x = piece.x + c;
                    if (y >= 0 && y < ROWS && x >= 0 && x < COLS) {
                        this.grid[y][x] = piece.colorId;
                    }
                }
            }
        }
    }

    // 消除满行，返回消除的行数
    clearFullRows() {
        let cleared = 0;
        for (let row = ROWS - 1; row >= 0; ) {
            if (this.grid[row].every(cell => cell !== 0)) {
                this.grid.splice(row, 1);
                this.grid.unshift(Array(COLS).fill(0));
                cleared++;
                // 继续检查同一行(原下一行)
            } else {
                row--;
            }
        }
        return cleared;
    }

    // 检查是否游戏结束（第一行有方块）
    isGameOver() {
        return this.grid[0].some(cell => cell !== 0);
    }

    // 获取当前棋盘状态（供渲染使用）
    getGrid() {
        return this.grid;
    }
}
```

### `js/piece.js`
```javascript
import { SHAPES } from './constants.js';
import { deepCopyArray, rotateMatrix } from './utils.js';

export class Piece {
    constructor(typeId, x, y) {
        this.typeId = typeId;          // 0-6
        this.shape = deepCopyArray(SHAPES[typeId]);
        this.x = x;
        this.y = y;
        this.colorId = typeId + 1;     // 颜色索引 1-7
    }

    // 生成旋转后的形状（不修改自身）
    rotatedShape() {
        return rotateMatrix(this.shape);
    }

    clone() {
        const p = new Piece(this.typeId, this.x, this.y);
        p.shape = deepCopyArray(this.shape);
        p.colorId = this.colorId;
        return p;
    }
}
```

### `js/game.js`
```javascript
import { Board } from './board.js';
import { Piece } from './piece.js';
import { COLS, INITIAL_DROP_INTERVAL, LEVEL_DECREASE, MIN_DROP_INTERVAL, 
         SCORE_TABLE, LINES_PER_LEVEL } from './constants.js';
import { randomPieceType, deepCopyArray } from './utils.js';

export class Game {
    constructor() {
        this.board = new Board();
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.dropInterval = INITIAL_DROP_INTERVAL;
        this.state = 'idle';       // idle | playing | paused | over
        this.currentPiece = null;
        this.nextPiece = null;

        // 用于 requestAnimationFrame 累加时间
        this.lastTime = 0;

        // 音效管理器（将由 main 注入）
        this.audioManager = null;
    }

    // 初始化新游戏
    start() {
        this.board.reset();
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.dropInterval = INITIAL_DROP_INTERVAL;
        this.state = 'playing';
        this.currentPiece = this.createRandomPiece();
        this.nextPiece = this.createRandomPiece();
        // 将 currentPiece 放在棋盘顶部中间
        this.currentPiece.x = Math.floor((COLS - this.currentPiece.shape[0].length) / 2);
        this.currentPiece.y = 0;
        this.lastTime = performance.now();
    }

    createRandomPiece() {
        return new Piece(randomPieceType());
    }

    // 生成下一个方块
    spawnNext() {
        this.currentPiece = this.nextPiece;
        this.currentPiece.x = Math.floor((COLS - this.currentPiece.shape[0].length) / 2);
        this.currentPiece.y = 0;
        this.nextPiece = this.createRandomPiece();

        // 生成即碰撞则 game over
        if (!this.board.isValidPosition(this.currentPiece, 0, 0)) {
            this.state = 'over';
            if (this.audioManager) this.audioManager.playGameOver();
        }
    }

    // 移动方块
    movePiece(dx, dy) {
        if (this.state !== 'playing') return;
        if (this.board.isValidPosition(this.currentPiece, dx, dy)) {
            this.currentPiece.x += dx;
            this.currentPiece.y += dy;
        }
    }

    // 旋转方块
    rotatePiece() {
        if (this.state !== 'playing') return;
        const newShape = this.currentPiece.rotatedShape();
        // 尝试旋转，若不合法则尝试 wall kick（简单的左/右微移）
        if (this.board.isValidPosition(this.currentPiece, 0, 0, newShape)) {
            this.currentPiece.shape = newShape;
        } else if (this.board.isValidPosition(this.currentPiece, -1, 0, newShape)) {
            this.currentPiece.shape = newShape;
            this.currentPiece.x -= 1;
        } else if (this.board.isValidPosition(this.currentPiece, 1, 0, newShape)) {
            this.currentPiece.shape = newShape;
            this.currentPiece.x += 1;
        }
    }

    // 软降 (加速下落)
    softDrop() {
        if (this.state !== 'playing') return;
        if (this.board.isValidPosition(this.currentPiece, 0, 1)) {
            this.currentPiece.y += 1;
        }
    }

    // 硬降 (落到底)
    hardDrop() {
        if (this.state !== 'playing') return;
        while (this.board.isValidPosition(this.currentPiece, 0, 1)) {
            this.currentPiece.y += 1;
        }
        this.lockAndSpawn();
    }

    // 锁定当前方块并生成下一个
    lockAndSpawn() {
        this.board.lockPiece(this.currentPiece);
        const cleared = this.board.clearFullRows();
        if (cleared > 0) {
            this.lines += cleared;
            this.score += (SCORE_TABLE[cleared] || 0);
            if (this.audioManager) this.audioManager.playLineClear();
            // 升级
            const neededLines = this.level * LINES_PER_LEVEL;
            if (this.lines >= neededLines) {
                this.level++;
                this.dropInterval = Math.max(INITIAL_DROP_INTERVAL - (this.level - 1) * LEVEL_DECREASE, MIN_DROP_INTERVAL);
            }
        }
        // 检查游戏结束: 锁定后是否溢出到顶部
        if (this.board.isGameOver()) {
            this.state = 'over';
            if (this.audioManager) this.audioManager.playGameOver();
            return;
        }
        this.spawnNext();
    }

    // 暂停切换
    togglePause() {
        if (this.state === 'playing') {
            this.state = 'paused';
        } else if (this.state === 'paused') {
            this.state = 'playing';
            this.lastTime = performance.now(); // 重置时间防止瞬间下落
        }
    }

    // 重新开始
    restart() {
        this.start();
    }

    // 主更新循环 (每帧调用)
    update(time) {
        if (this.state !== 'playing') return;

        const delta = time - this.lastTime;
        this.lastTime = time;

        if (delta >= this.dropInterval) {
            // 下落一格
            if (this.board.isValidPosition(this.currentPiece, 0, 1)) {
                this.currentPiece.y += 1;
            } else {
                this.lockAndSpawn();
            }
            this.lastTime = time;
        }
    }
}
```

### `js/renderer.js`
```javascript
import { COLS, ROWS, BLOCK_SIZE, COLORS } from './constants.js';

export class Renderer {
    constructor(canvas, previewCanvas) {
        this.ctx = canvas.getContext('2d');
        this.previewCtx = previewCanvas.getContext('2d');
    }

    // 绘制整个场景
    render(game) {
        const board = game.board;
        const currentPiece = game.currentPiece;
        const nextPiece = game.nextPiece;
        const score = game.score;
        const level = game.level;
        const lines = game.lines;
        const state = game.state;

        // 更新 HTML 中显示的分数、等级、行数
        document.getElementById('score').textContent = score;
        document.getElementById('level').textContent = level;
        document.getElementById('lines').textContent = lines;

        // 绘制游戏板
        this.drawBoard(board, currentPiece, state);

        // 绘制预览
        this.drawPreview(nextPiece);

        // 处理覆盖层（暂停/结束）
        if (state === 'over') {
            document.getElementById('overlay').classList.remove('hidden');
            document.getElementById('final-score').textContent = score;
        } else {
            document.getElementById('overlay').classList.add('hidden');
        }
    }

    drawBoard(board, currentPiece, state) {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, COLS * BLOCK_SIZE, ROWS * BLOCK_SIZE);

        // 绘制已固定的方块
        const grid = board.getGrid();
        for (let row = 0; row < ROWS; row++) {
            for (let col = 0; col < COLS; col++) {
                const colorId = grid[row][col];
                if (colorId !== 0) {
                    ctx.fillStyle = COLORS[colorId];
                    ctx.fillRect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                    ctx.strokeStyle = '#000';
                    ctx.strokeRect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                }
            }
        }

        // 绘制当前方块
        if (currentPiece && state === 'playing') {
            const matrix = currentPiece.shape;
            for (let r = 0; r < matrix.length; r++) {
                for (let c = 0; c < matrix[r].length; c++) {
                    if (matrix[r][c] !== 0) {
                        const x = (currentPiece.x + c) * BLOCK_SIZE;
                        const y = (currentPiece.y + r) * BLOCK_SIZE;
                        ctx.fillStyle = COLORS[currentPiece.colorId];
                        ctx.fillRect(x, y, BLOCK_SIZE, BLOCK_SIZE);
                        ctx.strokeStyle = '#000';
                        ctx.strokeRect(x, y, BLOCK_SIZE, BLOCK_SIZE);
                    }
                }
            }
        }

        // 绘制网格线
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        for (let i = 0; i <= COLS; i++) {
            ctx.beginPath();
            ctx.moveTo(i * BLOCK_SIZE, 0);
            ctx.lineTo(i * BLOCK_SIZE, ROWS * BLOCK_SIZE);
            ctx.stroke();
        }
        for (let i = 0; i <= ROWS; i++) {
            ctx.beginPath();
            ctx.moveTo(0, i * BLOCK_SIZE);
            ctx.lineTo(COLS * BLOCK_SIZE, i * BLOCK_SIZE);
            ctx.stroke();
        }
    }

    drawPreview(piece) {
        const ctx = this.previewCtx;
        ctx.clearRect(0, 0, 120, 120);
        if (!piece) return;

        const matrix = piece.shape;
        const blockSize = 25; // 预览格子大小
        const offsetX = (120 - matrix[0].length * blockSize) / 2;
        const offsetY = (120 - matrix.length * blockSize) / 2;

        for (let r = 0; r < matrix.length; r++) {
            for (let c = 0; c < matrix[r].length; c++) {
                if (matrix[r][c] !== 0) {
                    ctx.fillStyle = COLORS[piece.colorId];
                    ctx.fillRect(offsetX + c * blockSize, offsetY + r * blockSize, blockSize, blockSize);
                    ctx.strokeStyle = '#000';
                    ctx.strokeRect(offsetX + c * blockSize, offsetY + r * blockSize, blockSize, blockSize);
                }
            }
        }
    }
}
```

### `js/input.js`
```javascript
export class InputHandler {
    constructor(game) {
        this.game = game;
        this.handleKeyDown = this.handleKeyDown.bind(this);
    }

    bind() {
        document.addEventListener('keydown', this.handleKeyDown);
    }

    unbind() {
        document.removeEventListener('keydown', this.handleKeyDown);
    }

    handleKeyDown(e) {
        const game = this.game;
        if (e.repeat && (e.key === 'ArrowDown')) {
            // 忽略长按重复的加速下落（保留方向键重复用于移动）
            // 为简化，允许重复加速
        }

        switch (e.key) {
            case 'ArrowLeft':
                game.movePiece(-1, 0);
                e.preventDefault();
                break;
            case 'ArrowRight':
                game.movePiece(1, 0);
                e.preventDefault();
                break;
            case 'ArrowUp':
                game.rotatePiece();
                e.preventDefault();
                break;
            case 'ArrowDown':
                game.softDrop();
                e.preventDefault();
                break;
            case ' ':
                game.hardDrop();
                e.preventDefault();
                break;
            case 'p':
            case 'P':
                game.togglePause();
                e.preventDefault();
                break;
            case 'Enter':
                if (game.state === 'over') {
                    game.restart();
                    e.preventDefault();
                }
                break;
            default:
                break;
        }
    }
}
```

### `js/audio.js`
```javascript
export class AudioManager {
    constructor() {
        this.ctx = null;
        this.muted = false; // 默认不静音
    }

    _getContext() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
        return this.ctx;
    }

    // 消行音效：短促上升音
    playLineClear() {
        if (this.muted) return;
        try {
            const ctx = this._getContext();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(440, ctx.currentTime);
            osc.frequency.linearRampToValueAtTime(880, ctx.currentTime + 0.08);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.08);
        } catch (e) {
            // 静默失败
        }
    }

    // 游戏结束音效：低沉下降音
    playGameOver() {
        if (this.muted) return;
        try {
            const ctx = this._getContext();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(200, ctx.currentTime);
            osc.frequency.linearRampToValueAtTime(80, ctx.currentTime + 0.3);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.3);
        } catch (e) {
            // 静默失败
        }
    }
}
```

### `js/main.js`
```javascript
import { Game } from './game.js';
import { Renderer } from './renderer.js';
import { InputHandler } from './input.js';
import { AudioManager } from './audio.js';

// 获取 Canvas
const boardCanvas = document.getElementById('board-canvas');
const previewCanvas = document.getElementById('preview-canvas');

// 初始化各模块
const game = new Game();
const renderer = new Renderer(boardCanvas, previewCanvas);
const input = new InputHandler(game);
const audio = new AudioManager();

// 注入音频管理器
game.audioManager = audio;

// 绑定键盘事件
input.bind();

// 绑定按钮事件
document.getElementById('pause-btn').addEventListener('click', () => {
    game.togglePause();
    // 更新按钮文本
    document.getElementById('pause-btn').textContent = 
        game.state === 'paused' ? '继续' : '暂停';
});

const restartFn = () => {
    game.restart();
    document.getElementById('pause-btn').textContent = '暂停';
};

document.getElementById('restart-btn').addEventListener('click', restartFn);
document.getElementById('restart-overlay-btn').addEventListener('click', restartFn);

// 自动开始游戏
game.start();

// 游戏循环
function gameLoop(time) {
    game.update(time);
    renderer.render(game);
    requestAnimationFrame(gameLoop);
}

requestAnimationFrame(gameLoop);
```

---

## 功能概览

- **核心玩法**：10×20 标准棋盘，7 种方块随机出现，自动下落。
- **键盘控制**：方向键移动/旋转，空格硬降，P 键暂停。
- **计分与等级**：消行得分（1行100，2行300，3行500，4行800），每消除10行提升等级，下落速度加快。
- **下一个预览**：右上角显示即将出现的方块形状。
- **游戏状态**：开始/暂停/结束，结束后显示得分并可通过按钮或回车键重新开始。
- **音效**：消行时播放上升音，游戏结束时播放下降音（默认开启，无静音开关）。

所有代码均符合 MVP 需求，无多余功能，可直接运行。如遇到模块加载问题，请使用本地服务器。