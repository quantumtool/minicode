```file:index.html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
  <title>极简俄罗斯方块</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div id="game-container">
    <div id="info-panel">
      <div id="score-label">得分</div>
      <div id="score">0</div>
      <div id="next-label">下一个</div>
      <canvas id="next-canvas" width="120" height="120"></canvas>
      <button id="sound-toggle" title="音效开关">🔊</button>
    </div>
    <canvas id="game-canvas" width="300" height="600"></canvas>
    <div id="controls">
      <button class="ctrl-btn" id="btn-left">◀</button>
      <button class="ctrl-btn" id="btn-rotate">↻</button>
      <button class="ctrl-btn" id="btn-right">▶</button>
      <button class="ctrl-btn" id="btn-down">▼</button>
    </div>
    <div id="game-over-overlay" style="display:none;">
      <h1>Game Over</h1>
      <p>得分：<span id="final-score">0</span></p>
      <p id="restart-hint">按空格键或点击重新开始</p>
    </div>
  </div>
  <script type="module" src="js/main.js"></script>
</body>
</html>
```

```file:style.css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  user-select: none;
}

body {
  background: #1a1a2e;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Segoe UI', sans-serif;
  touch-action: manipulation;
}

#game-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  align-items: flex-start;
  padding: 20px;
  background: #16213e;
  border-radius: 16px;
  box-shadow: 0 0 40px rgba(0,0,0,0.5);
}

#game-canvas {
  border: 2px solid #0f3460;
  background: #0f0f23;
  border-radius: 4px;
  touch-action: none;
}

#info-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  min-width: 120px;
}

#score-label, #next-label {
  color: #e94560;
  font-weight: bold;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

#score {
  color: #ffffff;
  font-size: 2rem;
  font-weight: bold;
}

#next-canvas {
  background: #0f0f23;
  border: 2px solid #0f3460;
  border-radius: 4px;
}

#sound-toggle {
  background: none;
  border: 2px solid #0f3460;
  color: #e94560;
  font-size: 1.5rem;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px;
}

#sound-toggle:active {
  transform: scale(0.95);
}

#controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
  max-width: 300px;
  margin-top: 10px;
}

.ctrl-btn {
  background: #0f3460;
  color: white;
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: manipulation;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  transition: background 0.1s;
}

.ctrl-btn:active {
  background: #e94560;
}

#game-over-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 100;
}

#game-over-overlay h1 {
  font-size: 3rem;
  color: #e94560;
  margin-bottom: 20px;
}

#game-over-overlay p {
  font-size: 1.5rem;
  margin: 10px 0;
}

#restart-hint {
  color: #aaaaaa;
  font-size: 1rem;
}

@media (max-width: 600px) {
  #game-container {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }
  #game-canvas {
    width: 280px;
    height: 560px;
  }
  .ctrl-btn {
    width: 50px;
    height: 50px;
  }
}
```

```file:js/game-core.js
// 游戏核心逻辑
export class GameCore {
  static COLS = 10;
  static ROWS = 20;
  static TETROMINOES = {
    I: { shape: [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]], color: '#00f0f0' },
    O: { shape: [[1,1],[1,1]], color: '#f0f000' },
    T: { shape: [[0,1,0],[1,1,1],[0,0,0]], color: '#a000f0' },
    S: { shape: [[0,1,1],[1,1,0],[0,0,0]], color: '#00f000' },
    Z: { shape: [[1,1,0],[0,1,1],[0,0,0]], color: '#f00000' },
    J: { shape: [[1,0,0],[1,1,1],[0,0,0]], color: '#0000f0' },
    L: { shape: [[0,0,1],[1,1,1],[0,0,0]], color: '#f0a000' }
  };
  static KEYS = Object.keys(GameCore.TETROMINOES);

  constructor() {
    this.board = Array.from({ length: GameCore.ROWS }, () => Array(GameCore.COLS).fill(0));
    this.score = 0;
    this.gameOver = false;
    this.currentPiece = null;
    this.nextPiece = null;
    this.flashLines = []; // 即将消除的行号，用于闪烁动画
    this.flashTimer = 0;
    this.onScoreChange = null; // 回调
    this.onGameOver = null;
    this.onGridUpdate = null;  // 每帧通知渲染
    this.onSpawn = null;       // 新方块出现时通知
    this._initPieces();
  }

  _initPieces() {
    this.nextPiece = this._randomPiece();
    this._spawnNewPiece();
  }

  _randomPiece() {
    const key = GameCore.KEYS[Math.floor(Math.random() * GameCore.KEYS.length)];
    const def = GameCore.TETROMINOES[key];
    return {
      type: key,
      shape: def.shape.map(row => row.slice()), // 深拷贝
      color: def.color,
      x: 3,
      y: 0
    };
  }

  _spawnNewPiece() {
    this.currentPiece = this.nextPiece;
    this.nextPiece = this._randomPiece();
    this.currentPiece.x = 3;
    this.currentPiece.y = 0;
    // 检查是否游戏结束
    if (this._collision(this.currentPiece.shape, this.currentPiece.x, this.currentPiece.y)) {
      this.gameOver = true;
      if (this.onGameOver) this.onGameOver(this.score);
    } else {
      if (this.onSpawn) this.onSpawn(this.currentPiece, this.nextPiece);
    }
  }

  _collision(shape, offsetX, offsetY) {
    for (let row = 0; row < shape.length; row++) {
      for (let col = 0; col < shape[0].length; col++) {
        if (shape[row][col] !== 0) {
          const boardX = offsetX + col;
          const boardY = offsetY + row;
          if (boardX < 0 || boardX >= GameCore.COLS || boardY >= GameCore.ROWS || boardY < 0) return true;
          if (boardY >= 0 && this.board[boardY][boardX] !== 0) return true;
        }
      }
    }
    return false;
  }

  _lockPiece() {
    const piece = this.currentPiece;
    for (let row = 0; row < piece.shape.length; row++) {
      for (let col = 0; col < piece.shape[0].length; col++) {
        if (piece.shape[row][col] !== 0) {
          const boardX = piece.x + col;
          const boardY = piece.y + row;
          if (boardY >= 0 && boardY < GameCore.ROWS && boardX >= 0 && boardX < GameCore.COLS) {
            this.board[boardY][boardX] = piece.color;
          }
        }
      }
    }
    // 清除满行并开始闪烁动画
    this._checkLines();
  }

  _checkLines() {
    const fullLines = [];
    for (let row = 0; row < GameCore.ROWS; row++) {
      if (this.board[row].every(cell => cell !== 0)) {
        fullLines.push(row);
      }
    }
    if (fullLines.length > 0) {
      this.flashLines = fullLines;
      this.flashTimer = 10; // 闪烁帧数
      // 暂时不消除，等待动画完成后再消除
      // 在渲染循环中检测 flashTimer 归零后执行消除
    } else {
      this._afterClear();
    }
  }

  _afterClear() {
    // 实际消除行
    if (this.flashLines.length > 0) {
      const lines = this.flashLines.sort((a,b) => b-a);
      for (const line of lines) {
        this.board.splice(line, 1);
        this.board.unshift(Array(GameCore.COLS).fill(0));
      }
      // 计分
      this.score += this.flashLines.length * 100;
      if (this.onScoreChange) this.onScoreChange(this.score);
      this.flashLines = [];
    }
    // 生成下一个方块
    this._spawnNewPiece();
  }

  tick() {
    if (this.gameOver) return;
    // 处理闪烁动画
    if (this.flashTimer > 0) {
      this.flashTimer--;
      if (this.flashTimer === 0) {
        this._afterClear();
      }
      return; // 闪烁期间不移动
    }
    // 向下移动
    if (!this._moveDown()) {
      this._lockPiece();
    }
  }

  _moveDown() {
    if (this._collision(this.currentPiece.shape, this.currentPiece.x, this.currentPiece.y + 1)) {
      return false;
    }
    this.currentPiece.y++;
    return true;
  }

  moveLeft() {
    if (this.gameOver || this.flashTimer > 0) return;
    if (!this._collision(this.currentPiece.shape, this.currentPiece.x - 1, this.currentPiece.y)) {
      this.currentPiece.x--;
    }
  }

  moveRight() {
    if (this.gameOver || this.flashTimer > 0) return;
    if (!this._collision(this.currentPiece.shape, this.currentPiece.x + 1, this.currentPiece.y)) {
      this.currentPiece.x++;
    }
  }

  rotate() {
    if (this.gameOver || this.flashTimer > 0) return;
    const shape = this.currentPiece.shape;
    const rotated = shape[0].map((_, idx) => shape.map(row => row[idx]).reverse());
    if (!this._collision(rotated, this.currentPiece.x, this.currentPiece.y)) {
      this.currentPiece.shape = rotated;
    } else {
      // 可以尝试踢墙（简单处理：不踢）
    }
  }

  hardDrop() {
    if (this.gameOver || this.flashTimer > 0) return;
    while (this._moveDown()) { /* 空 */ }
    this._lockPiece();
  }

  reset() {
    this.board = Array.from({ length: GameCore.ROWS }, () => Array(GameCore.COLS).fill(0));
    this.score = 0;
    this.gameOver = false;
    this.flashLines = [];
    this.flashTimer = 0;
    this._initPieces();
    if (this.onScoreChange) this.onScoreChange(0);
  }
}
```

```file:js/renderer.js
// 渲染模块
export class Renderer {
  constructor(gameCanvas, nextCanvas) {
    this.gameCtx = gameCanvas.getContext('2d');
    this.nextCtx = nextCanvas.getContext('2d');
    this.gameCanvas = gameCanvas;
    this.nextCanvas = nextCanvas;
    this.blockSize = gameCanvas.width / 10;
    this.nextBlockSize = nextCanvas.width / 4; // 预览最大4x4
  }

  render(gameCore) {
    this._drawBoard(gameCore);
    this._drawCurrentPiece(gameCore);
    this._drawNextPiece(gameCore);
    this._drawScore(gameCore);
    this._drawFlashLines(gameCore);
  }

  _drawBoard(core) {
    const ctx = this.gameCtx;
    ctx.fillStyle = '#0f0f23';
    ctx.fillRect(0, 0, this.gameCanvas.width, this.gameCanvas.height);
    // 网格线
    ctx.strokeStyle = '#1c1c3a';
    ctx.lineWidth = 0.5;
    for (let col = 1; col < GameCore.COLS; col++) {
      ctx.beginPath();
      ctx.moveTo(col * this.blockSize, 0);
      ctx.lineTo(col * this.blockSize, this.gameCanvas.height);
      ctx.stroke();
    }
    for (let row = 1; row < GameCore.ROWS; row++) {
      ctx.beginPath();
      ctx.moveTo(0, row * this.blockSize);
      ctx.lineTo(this.gameCanvas.width, row * this.blockSize);
      ctx.stroke();
    }
    // 已固定的方块
    for (let row = 0; row < GameCore.ROWS; row++) {
      for (let col = 0; col < GameCore.COLS; col++) {
        if (core.board[row][col] !== 0) {
          ctx.fillStyle = core.board[row][col];
          ctx.fillRect(col * this.blockSize, row * this.blockSize, this.blockSize - 1, this.blockSize - 1);
        }
      }
    }
  }

  _drawCurrentPiece(core) {
    if (!core.currentPiece || core.gameOver) return;
    const piece = core.currentPiece;
    const ctx = this.gameCtx;
    ctx.fillStyle = piece.color;
    for (let row = 0; row < piece.shape.length; row++) {
      for (let col = 0; col < piece.shape[0].length; col++) {
        if (piece.shape[row][col] !== 0) {
          const x = (piece.x + col) * this.blockSize;
          const y = (piece.y + row) * this.blockSize;
          ctx.fillRect(x, y, this.blockSize - 1, this.blockSize - 1);
        }
      }
    }
  }

  _drawNextPiece(core) {
    const ctx = this.nextCtx;
    ctx.fillStyle = '#0f0f23';
    ctx.fillRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);
    if (!core.nextPiece) return;
    const piece = core.nextPiece;
    ctx.fillStyle = piece.color;
    const shapeRows = piece.shape.length;
    const shapeCols = piece.shape[0].length;
    const offsetX = (4 - shapeCols) / 2; // 居中
    const offsetY = (4 - shapeRows) / 2;
    for (let row = 0; row < shapeRows; row++) {
      for (let col = 0; col < shapeCols; col++) {
        if (piece.shape[row][col] !== 0) {
          const x = (col + offsetX) * this.nextBlockSize;
          const y = (row + offsetY) * this.nextBlockSize;
          ctx.fillRect(x, y, this.nextBlockSize - 1, this.nextBlockSize - 1);
        }
      }
    }
  }

  _drawScore(core) {
    const scoreEl = document.getElementById('score');
    scoreEl.textContent = core.score;
  }

  _drawFlashLines(core) {
    if (core.flashLines.length === 0) return;
    const ctx = this.gameCtx;
    const flashColor = (core.flashTimer % 2 === 0) ? '#ffffff' : '#ffcc00';
    ctx.fillStyle = flashColor;
    for (const row of core.flashLines) {
      ctx.fillRect(0, row * this.blockSize, this.gameCanvas.width, this.blockSize);
    }
  }
}
```

```file:js/input-handler.js
// 输入处理模块
export class InputHandler {
  constructor(gameCore, renderer) {
    this.core = gameCore;
    this.renderer = renderer;
    this._setupKeyboard();
    this._setupTouchControls();
    this._setupGameOverRestart();
  }

  _setupKeyboard() {
    document.addEventListener('keydown', (e) => {
      if (e.repeat && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
        // 重复只处理移动，旋转和下落不重复
        // 但实际上需要处理重复移动
      }
      switch (e.key) {
        case 'ArrowLeft':
          this.core.moveLeft();
          break;
        case 'ArrowRight':
          this.core.moveRight();
          break;
        case 'ArrowDown':
          this.core._moveDown(); // 加速下落
          break;
        case 'ArrowUp':
          this.core.rotate();
          break;
        case ' ':
          e.preventDefault();
          if (this.core.gameOver) {
            this.core.reset();
          } else {
            this.core.hardDrop();
          }
          break;
      }
    });
  }

  _setupTouchControls() {
    const btnLeft = document.getElementById('btn-left');
    const btnRight = document.getElementById('btn-right');
    const btnRotate = document.getElementById('btn-rotate');
    const btnDown = document.getElementById('btn-down');

    const pressHandler = (action) => {
      if (this.core.gameOver) return;
      action();
    };

    btnLeft.addEventListener('click', () => pressHandler(() => this.core.moveLeft()));
    btnRight.addEventListener('click', () => pressHandler(() => this.core.moveRight()));
    btnRotate.addEventListener('click', () => pressHandler(() => this.core.rotate()));
    btnDown.addEventListener('click', () => pressHandler(() => this.core._moveDown()));
    // 长按快速下落处理？简单起见只点击一次移动一步
  }

  _setupGameOverRestart() {
    const overlay = document.getElementById('game-over-overlay');
    // 点击 overlay 重新开始
    overlay.addEventListener('click', () => {
      if (this.core.gameOver) {
        this.core.reset();
        overlay.style.display = 'none';
      }
    });
    // 空格键重新开始（已在键盘处理中）
  }
}
```

```file:js/sound-manager.js
// 音效管理器（使用 Web Audio API 合成简单音效）
export class SoundManager {
  constructor() {
    this.ctx = null;
    this.enabled = true;
    this._initAudioContext();
    this._setupToggleButton();
  }

  _initAudioContext() {
    try {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    } catch(e) {
      this.enabled = false;
    }
  }

  _playTone(frequency, duration, type = 'square') {
    if (!this.ctx || !this.enabled) return;
    // 如果 AudioContext 是 suspended，先恢复
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    const oscillator = this.ctx.createOscillator();
    const gainNode = this.ctx.createGain();
    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, this.ctx.currentTime);
    gainNode.gain.setValueAtTime(0.3, this.ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + duration);
    oscillator.connect(gainNode);
    gainNode.connect(this.ctx.destination);
    oscillator.start(this.ctx.currentTime);
    oscillator.stop(this.ctx.currentTime + duration);
  }

  playMove() {
    this._playTone(200, 0.05);
  }

  playRotate() {
    this._playTone(300, 0.08);
  }

  playDrop() {
    this._playTone(150, 0.1, 'sawtooth');
  }

  playClear() {
    this._playTone(400, 0.15);
    this._playTone(500, 0.15);
  }

  playGameOver() {
    this._playTone(100, 0.3, 'sawtooth');
  }

  toggle() {
    this.enabled = !this.enabled;
    const btn = document.getElementById('sound-toggle');
    btn.textContent = this.enabled ? '🔊' : '🔇';
  }

  _setupToggleButton() {
    const btn = document.getElementById('sound-toggle');
    btn.addEventListener('click', () => this.toggle());
  }
}
```

```file:js/main.js
// 应用入口
import { GameCore } from './game-core.js';
import { Renderer } from './renderer.js';
import { InputHandler } from './input-handler.js';
import { SoundManager } from './sound-manager.js';

// 获取 DOM 元素
const gameCanvas = document.getElementById('game-canvas');
const nextCanvas = document.getElementById('next-canvas');

// 初始化核心模块
const gameCore = new GameCore();
const renderer = new Renderer(gameCanvas, nextCanvas);
const inputHandler = new InputHandler(gameCore, renderer);
const soundManager = new SoundManager();

// 关联音效
gameCore.onScoreChange = (score) => {
  soundManager.playClear();
  document.getElementById('score').textContent = score;
};
gameCore.onGameOver = (score) => {
  soundManager.playGameOver();
  document.getElementById('final-score').textContent = score;
  document.getElementById('game-over-overlay').style.display = 'flex';
};

gameCore.onSpawn = (current, next) => {
  // 可以播放 spawn 音效（可选）
};

// 游戏主循环
let lastTick = 0;
const tickInterval = 500; // 毫秒

function gameLoop(timestamp) {
  if (!lastTick) lastTick = timestamp;
  const delta = timestamp - lastTick;
  if (delta >= tickInterval && !gameCore.gameOver && gameCore.flashTimer === 0) {
    gameCore.tick();
    lastTick = timestamp;
  } else if (gameCore.flashTimer > 0) {
    gameCore.tick(); // 处理闪烁动画
  }
  renderer.render(gameCore);
  requestAnimationFrame(gameLoop);
}

// 开始游戏
requestAnimationFrame(gameLoop);
```

```file:README.md
# 极简俄罗斯方块 (Tetris MVP)

一款“开箱即玩”的极简俄罗斯方块游戏，使用纯浏览器技术（HTML5 + CSS3 + JavaScript）实现，零依赖。

## 运行方法

### 方式一：本地 HTTP 服务器（推荐）
1. 将本项目文件夹放在任意目录。
2. 打开终端，进入该目录。
3. 运行 `python -m http.server 8000`（需要安装 Python）。
4. 在浏览器中访问 `http://localhost:8000`。

### 方式二：直接打开文件（可能不支持 ES6 模块）
部分浏览器（如 Chrome）不允许 `file://` 协议加载 ES6 模块。如果无法运行，请使用方法一。

## 操作说明
- **键盘控制**：
  - 方向键左/右：左右移动
  - 方向键上：旋转方块
  - 方向键下：加速下落
  - 空格键：硬降（直接落底）/ 游戏结束后重新开始
- **触摸控制**：
  - 点击屏幕下方的按钮：左移、右移、旋转、下移
  - 点击“Game Over”画面或按空格键重新开始

## 项目结构
```
tetris-mvp/
├── index.html          # 主页面
├── style.css           # 样式
├── js/
│   ├── main.js         # 入口，游戏主循环
│   ├── game-core.js    # 游戏核心逻辑
│   ├── renderer.js     # Canvas 渲染
│   ├── input-handler.js# 输入控制（键盘 + 触摸按钮）
│   └── sound-manager.js# 音效管理（Web Audio API）
└── README.md
```

## 核心功能
- 经典七种方块随机生成
- 10x20 标准网格
- 键盘 + 触摸控制
- 行消除计分
- 下一个方块预览
- 游戏结束提示与重开
- 简单合成音效（可开关）

## 技术栈
- 原生 ES6 模块
- Canvas 2D 渲染
- Web Audio API 音效合成
- 响应式布局

## 许可
MIT
```