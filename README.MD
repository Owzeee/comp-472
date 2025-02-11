<h1 align="center">Mini Chess</h1>

## Overview

Mini Chess is a simplified chess game played on a 5×5 board. It supports human-vs-human gameplay, enforces legal moves for each piece, and logs all moves and game events to a trace file.

<p align="center">
  <a href="#game-specifications">Specifications</a> •
  <a href="#usage">Usage</a> •
  <a href="#current-features">Current Features</a> •
  <a href="#future-implementations">Future</a> •
  <a href="#requirements">Requirements</a>
</p>

## 🎮 Game Specifications

### 📋 Board Configuration
- 5x5 board

#### ♟️ Pieces & Movement
- King (K): One square any direction 
- Queen (Q): Any squares horizontal/vertical/diagonal
- Bishop (B): Any squares diagonal
- Knight (N): L-shape (2+1)
- Pawn (p): 
  - Forward one square
  - Captures diagonally
  - Auto-promotes to Queen at opposite end

### 🏆 Win Conditions
- Capture opponent's king
- Draw:
  - 10 turns without captures
  - 100 total turns reached

## 🚀 Usage

### ⚙️ Execution
```bash
python MiniChessSkeletonCode.py
```
### 🎮 Commands
* Move: `<from> <to>` (e.g., `B2 B3`)
* Exit: `exit`

### 📤 Output
* File: `gameTrace-false-<timeout>-<maxTurns>.txt`
* Contents:
   * Game parameters
   * Move history
   * Captures
   * Outcome

### Current Features (Demo 1)
* Human vs Human gameplay
* Move validation
* Piece movement rules
* Capture handling
* Pawn promotion
* Draw conditions
* Game trace generation
* Error handling

### 🔮 Future Implementations (Demo 2+)

#### 🤖 AI Opponent
* Minimax algorithm
* Alpha-beta pruning
* Multiple heuristics (e0, e1, e2)

#### 🎲 Game Modes
* Human vs AI (H-AI)
* AI vs Human (AI-H)
* AI vs AI (AI-AI)

#### Enhanced Statistics
* States explored
* Average branching factor
* Search tree depth metrics

#### Performance Metrics
* Time per move
* Memory usage
* Node expansion rate

### Requirements
* Python 3.x

### Development Status
* [x] Demo 1: Manual Game (H-H)
* [ ] Demo 2: AI Implementation
* [ ] Tournament Version
* [ ] Final Release


### Group: COMP472-Monarchs
* Ruturajsinh Vihol: 40154693
* Omar Zaari: 40194212
* Leiticia Taleb : 40225167
