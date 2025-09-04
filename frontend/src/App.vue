<template>
  <div id="app">
    <div class="game-container">
      <div class="game-board">
        <div
          v-for="(row, rowIndex) in board"
          :key="rowIndex"
          class="row"
        >
          <div
            v-for="(cell, colIndex) in row"
            :key="colIndex"
            class="cell"
            :class="{ 
              'valid-move': isValidMove(rowIndex, colIndex),
              'last-move': isLastMove(rowIndex, colIndex)
            }"
            @click="makeMove(rowIndex, colIndex)"
          >
            <div
              v-if="cell === 1"
              class="stone black"
            ></div>
            <div
              v-else-if="cell === 2"
              class="stone white"
            ></div>
            <div
              v-if="isLastMove(rowIndex, colIndex)"
              class="last-move-indicator"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <div class="game-info">
      <h1 class="game-title">OTHELLO</h1>
      
      <div class="score-panel">
        <div class="score-label">SCORE</div>
        <div class="score-display">
          <div class="score-item black">
            <div class="score-stone black"></div>
            <span>{{ blackCount }}</span>
          </div>
          <div class="score-item white">
            <div class="score-stone white"></div>
            <span>{{ whiteCount }}</span>
          </div>
        </div>
      </div>

      <div class="current-player" :class="{ 'ai-thinking': isAiThinking }">
        {{ currentPlayerText }}
      </div>

      <div class="game-controls">
        <button
          class="game-button button-new-game"
          @click="showModeSelectionModal"
          :disabled="isAiThinking"
        >
          NEW GAME
        </button>
        <button
          v-if="gameMode === 'human_vs_ai'"
          class="game-button button-ai-move"
          @click="requestAiMove"
          :disabled="isAiThinking || currentPlayer !== aiPlayer || gameOver"
        >
          AI MOVE
        </button>
        <button
          class="game-button button-pass"
          @click="passTurn"
          :disabled="!canPass || isAiThinking || gameOver"
        >
          PASS TURN
        </button>
        <button
          class="game-button button-undo"
          @click="undoMove"
          :disabled="!canUndo || isAiThinking"
        >
          UNDO MOVE
        </button>
      </div>

      <div class="game-status">
        <div class="valid-moves">
          Valid Moves: {{ validMoves.length }}
        </div>
        <div v-if="passCount > 0" class="pass-info">
          Pass Count: {{ passCount }}
        </div>
        <div v-if="lastMove" class="last-move-info">
          Last Move: {{ formatMove(lastMove) }}
        </div>
        <div class="instruction">
          {{ instructionText }}
        </div>
        <div v-if="statusMessage" class="status-message">
          {{ statusMessage }}
        </div>
        <div v-if="lastAction === 'pass'" class="pass-notification">
          ⚠️ Last action was a pass
        </div>
      </div>
    </div>

    <!-- 게임 모드 선택 모달 -->
    <div v-if="showModeSelection" class="modal-overlay" @click="closeModeSelection">
      <div class="modal-content" @click.stop>
        <h2>게임 모드 선택</h2>
        <p class="selection-description">어떤 모드로 플레이하시겠습니까?</p>
        <div class="mode-selection">
          <button class="mode-option" @click="selectMode('human_vs_ai')">
            <div class="mode-icon">🤖</div>
            <h3>AI 대전</h3>
            <p>인공지능과 대결합니다</p>
          </button>
          <button class="mode-option" @click="selectMode('human_vs_human')">
            <div class="mode-icon">👥</div>
            <h3>2인용 대전</h3>
            <p>친구와 함께 플레이합니다</p>
          </button>
        </div>
        <div class="modal-actions">
          <button class="game-button button-close" @click="closeModeSelection">
            닫기
          </button>
        </div>
      </div>
    </div>

    <!-- 플레이어 선택 모달 (AI 모드에서만) -->
    <div v-if="showPlayerSelection" class="modal-overlay" @click="closePlayerSelection">
      <div class="modal-content" @click.stop>
        <h2>색깔 선택</h2>
        <p class="selection-description">어떤 색의 돌로 플레이하시겠습니까?</p>
        <div class="player-selection">
          <button class="player-option black-option" @click="selectPlayer(1)">
            <div class="stone black large"></div>
            <span>흑돌 (먼저 시작)</span>
          </button>
          <button class="player-option white-option" @click="selectPlayer(2)">
            <div class="stone white large"></div>
            <span>백돌 (나중에 시작)</span>
          </button>
        </div>
        <p class="selection-hint">흑돌이 먼저 시작하며, AI는 반대 색을 사용합니다.</p>
        <div class="modal-actions">
          <button class="game-button button-close" @click="closePlayerSelection">
            닫기
          </button>
        </div>
      </div>
    </div>

    <!-- 게임 종료 모달 -->
    <div v-if="showGameOverModal" class="modal-overlay" @click="closeGameOverModal">
      <div class="modal-content" @click.stop>
        <h2>게임 종료!</h2>
        <div class="final-score">
          <div class="score-item black">
            <div class="score-stone black"></div>
            <span>흑돌: {{ blackCount }}</span>
          </div>
          <div class="score-item white">
            <div class="score-stone white"></div>
            <span>백돌: {{ whiteCount }}</span>
          </div>
        </div>
        <div class="winner-message">
          <p v-if="winner === 1">🎉 흑돌이 승리했습니다!</p>
          <p v-else-if="winner === 2">🎉 백돌이 승리했습니다!</p>
          <p v-else>🤝 무승부입니다!</p>
        </div>
        <button class="game-button button-new-game" @click="showModeSelectionModal(); closeGameOverModal()">
          새 게임 시작
        </button>
        <button class="game-button button-close" @click="closeGameOverModal">
          닫기
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      gameId: null,
      board: Array(8).fill().map(() => Array(8).fill(0)),
      currentPlayer: 1,
      validMoves: [],
      gameOver: false,
      winner: null,
      blackCount: 2,
      whiteCount: 2,
      passCount: 0,
      isAiThinking: false,
      statusMessage: '',
      canPass: false,
      canUndo: false,
      showGameOverModal: false,
      showModeSelection: true,
      showPlayerSelection: false,
      gameMode: 'human_vs_ai', // 'human_vs_ai' 또는 'human_vs_human'
      humanPlayer: 1, // 1: 흑돌, 2: 백돌
      aiPlayer: 2,
      player1Name: 'Player 1',
      player2Name: 'Player 2',
      lastAction: 'move',
      lastMove: null
    }
  },
  computed: {
    currentPlayerText() {
      if (this.isAiThinking) {
        return 'AI IS THINKING...'
      }
      if (this.gameOver) {
        if (this.winner === 1) return 'BLACK WINS!'
        if (this.winner === 2) return 'WHITE WINS!'
        return 'DRAW!'
      }
      
      if (this.gameMode === 'human_vs_human') {
        const playerName = this.currentPlayer === 1 ? this.player1Name : this.player2Name
        const stoneColor = this.currentPlayer === 1 ? 'BLACK' : 'WHITE'
        return `${playerName} (${stoneColor})`
      } else {
        // AI 모드
        if (this.currentPlayer === this.humanPlayer) {
          return this.currentPlayer === 1 ? "YOUR TURN (BLACK)" : "YOUR TURN (WHITE)"
        } else {
          return this.currentPlayer === 1 ? "AI TURN (BLACK)" : "AI TURN (WHITE)"
        }
      }
    },
    instructionText() {
      if (this.gameOver) {
        return 'Game Over'
      }
      if (this.validMoves.length === 0) {
        return 'No valid moves - pass turn'
      }
      return 'Click a valid move to play'
    }
  },
  watch: {
    gameOver(newVal) {
      if (newVal) {
        this.showGameOverModal = true
      }
    }
  },
  async mounted() {
    // 게임 시작은 사용자가 모드를 선택한 후에
  },
  methods: {
    selectMode(mode) {
      this.gameMode = mode
      this.showModeSelection = false
      
      if (mode === 'human_vs_ai') {
        // AI 모드: 색깔 선택 필요
        this.showPlayerSelection = true
      } else {
        // 2인용 모드: 바로 게임 시작
        this.startNewGame()
      }
    },
    
    closeModeSelection() {
      this.showModeSelection = false
    },
    
    async startNewGame() {
      try {
        const requestData = {
          mode: this.gameMode
        }
        
        if (this.gameMode === 'human_vs_ai') {
          requestData.human_color = this.humanPlayer
        } else {
          requestData.player1_name = this.player1Name
          requestData.player2_name = this.player2Name
        }
        
        const response = await axios.post('/api/game/new', requestData)
        this.gameId = response.data.game_id
        this.updateGameState(response.data.state)
        
        // 모달 닫기
        this.showPlayerSelection = false
        
        // AI가 먼저 시작하는 경우 자동으로 AI 수 요청
        this.$nextTick(() => {
          if (this.gameMode === 'human_vs_ai' && this.currentPlayer === this.aiPlayer && !this.gameOver) {
            setTimeout(() => this.requestAiMove(), 1000)
          }
        })
      } catch (error) {
        console.error('Failed to start new game:', error)
        // 에러 발생 시 모달 다시 표시
        if (this.gameMode === 'human_vs_ai') {
          this.showPlayerSelection = true
        } else {
          this.showModeSelection = true
        }
      }
    },
    
    selectPlayer(player) {
      this.humanPlayer = player
      this.aiPlayer = player === 1 ? 2 : 1
      this.startNewGame()
    },
    
    showModeSelectionModal() {
      this.showModeSelection = true
    },
    
    showPlayerSelectionModal() {
      this.showPlayerSelection = true
    },
    
    closePlayerSelection() {
      // 플레이어 선택 모달 닫기
      this.showPlayerSelection = false
    },
    
    async makeMove(row, col) {
      if (this.isAiThinking || this.gameOver || !this.isValidMove(row, col)) {
        return
      }

      try {
        const moveData = {
          row,
          col
        }
        
        // 2인용 모드에서 현재 플레이어 정보 추가
        if (this.gameMode === 'human_vs_human') {
          moveData.player = this.currentPlayer
        }
        
        const response = await axios.post(`/api/game/${this.gameId}/move`, moveData)
        this.updateGameState(response.data)
        
        // AI 차례인 경우 자동으로 AI 수 요청
        if (this.gameMode === 'human_vs_ai' && this.currentPlayer === this.aiPlayer && !this.gameOver) {
          setTimeout(() => this.requestAiMove(), 500)
        }
      } catch (error) {
        console.error('Failed to make move:', error)
      }
    },
    
    async requestAiMove() {
      if (this.isAiThinking || this.gameMode !== 'human_vs_ai' || this.currentPlayer !== this.aiPlayer || this.gameOver) {
        return
      }

      this.isAiThinking = true
      
      try {
        const response = await axios.post(`/api/game/${this.gameId}/ai-move`)
        this.updateGameState(response.data)
      } catch (error) {
        console.error('Failed to get AI move:', error)
      } finally {
        this.isAiThinking = false
      }
    },
    
    updateGameState(state) {
      this.board = state.board
      this.currentPlayer = state.current_player
      this.validMoves = state.valid_moves
      this.gameOver = state.game_over
      this.winner = state.winner
      this.blackCount = state.black_count
      this.whiteCount = state.white_count
      this.passCount = state.pass_count
      this.statusMessage = state.status_message || ''
      this.canPass = state.can_pass || false
      this.canUndo = state.can_undo || false
      this.lastAction = state.last_action || 'move'
      this.lastMove = state.last_move || null
      
      // 디버깅용 로그
      console.log('Game State Updated:', {
        canUndo: this.canUndo,
        historyLength: state.history_length,
        gameOver: this.gameOver,
        isAiThinking: this.isAiThinking
      })
      
      // 게임 모드 정보 업데이트
      if (state.mode) {
        this.gameMode = state.mode
      }
      if (state.player1_name) {
        this.player1Name = state.player1_name
      }
      if (state.player2_name) {
        this.player2Name = state.player2_name
      }
      
      // AI 모드에서만 플레이어 정보 업데이트
      if (state.human_player && state.mode === 'human_vs_ai') {
        this.humanPlayer = state.human_player
        this.aiPlayer = state.ai_player
      }
    },
    
    isValidMove(row, col) {
      return this.validMoves.some(move => move[0] === row && move[1] === col)
    },
    
    isLastMove(row, col) {
      return this.lastMove && this.lastMove[0] === row && this.lastMove[1] === col
    },
    
    formatMove(move) {
      if (!move) return ''
      const [row, col] = move
      const colLetter = String.fromCharCode(65 + col) // A, B, C, ...
      const rowNumber = row + 1 // 1-based row number
      return `${colLetter}${rowNumber}`
    },
    
    async passTurn() {
      if (!this.canPass || this.isAiThinking || this.gameOver) {
        return
      }

      try {
        const response = await axios.post(`/api/game/${this.gameId}/pass`)
        this.updateGameState(response.data)
        
        // AI 차례인 경우 자동으로 AI 수 요청
        if (this.gameMode === 'human_vs_ai' && this.currentPlayer === this.aiPlayer && !this.gameOver) {
          setTimeout(() => this.requestAiMove(), 500)
        }
      } catch (error) {
        console.error('Failed to pass turn:', error)
      }
    },
    
    async undoMove() {
      console.log('undoMove called:', {
        canUndo: this.canUndo,
        isAiThinking: this.isAiThinking,
        gameOver: this.gameOver,
        gameId: this.gameId
      })
      
      if (!this.canUndo || this.isAiThinking) {
        console.log('undoMove blocked by conditions')
        return
      }

      try {
        console.log('Sending undo request...')
        const response = await axios.post(`/api/game/${this.gameId}/undo`)
        console.log('Undo response:', response.data)
        this.updateGameState(response.data)
      } catch (error) {
        console.error('Failed to undo move:', error)
      }
    },
    
    closeGameOverModal() {
      this.showGameOverModal = false
    }
  }
}
</script>

<style scoped>
.row {
  display: contents;
}
</style>
