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
            :class="{ 'valid-move': isValidMove(rowIndex, colIndex) }"
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
          @click="startNewGame"
          :disabled="isAiThinking"
        >
          NEW GAME
        </button>
        <button
          class="game-button button-ai-move"
          @click="requestAiMove"
          :disabled="isAiThinking || currentPlayer !== 2 || gameOver"
        >
          AI MOVE
        </button>
      </div>

      <div class="game-status">
        <div class="valid-moves">
          Valid Moves: {{ validMoves.length }}
        </div>
        <div class="instruction">
          {{ instructionText }}
        </div>
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
      isAiThinking: false
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
      return this.currentPlayer === 1 ? "BLACK'S TURN" : "WHITE'S TURN"
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
  async mounted() {
    await this.startNewGame()
  },
  methods: {
    async startNewGame() {
      try {
        const response = await axios.get('/api/game/new')
        this.gameId = response.data.game_id
        this.updateGameState(response.data.state)
      } catch (error) {
        console.error('Failed to start new game:', error)
      }
    },
    
    async makeMove(row, col) {
      if (this.isAiThinking || this.gameOver || !this.isValidMove(row, col)) {
        return
      }

      try {
        const response = await axios.post(`/api/game/${this.gameId}/move`, {
          row,
          col
        })
        this.updateGameState(response.data)
        
        // AI 차례인 경우 자동으로 AI 수 요청
        if (this.currentPlayer === 2 && !this.gameOver) {
          setTimeout(() => this.requestAiMove(), 500)
        }
      } catch (error) {
        console.error('Failed to make move:', error)
      }
    },
    
    async requestAiMove() {
      if (this.isAiThinking || this.currentPlayer !== 2 || this.gameOver) {
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
    },
    
    isValidMove(row, col) {
      return this.validMoves.some(move => move[0] === row && move[1] === col)
    }
  }
}
</script>

<style scoped>
.row {
  display: contents;
}
</style>
