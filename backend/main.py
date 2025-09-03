from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
import uuid
from game_engine import OthelloGame
from ai_engine import OthelloAI

app = FastAPI(title="Othello Game API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vue.js 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 게임 인스턴스 저장소 (실제 프로덕션에서는 DB 사용)
games = {}
ai_engine = OthelloAI()

class MoveRequest(BaseModel):
    row: int
    col: int

class GameState(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[Tuple[int, int]]
    game_over: bool
    winner: Optional[int]
    black_count: int
    white_count: int
    pass_count: int

@app.get("/api/game/new")
async def new_game():
    """새 게임 시작"""
    game_id = str(uuid.uuid4())
    game = OthelloGame()
    games[game_id] = game
    return {"game_id": game_id, "state": game.get_state()}

@app.get("/api/game/{game_id}/state")
async def get_game_state(game_id: str):
    """게임 상태 조회"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    return game.get_state()

@app.post("/api/game/{game_id}/move")
async def make_move(game_id: str, move: MoveRequest):
    """플레이어 착수"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    if not game.is_valid_move(move.row, move.col):
        raise HTTPException(status_code=400, detail="Invalid move")
    
    game.make_move(move.row, move.col)
    return game.get_state()

@app.post("/api/game/{game_id}/ai-move")
async def ai_move(game_id: str):
    """AI 착수"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    if game.is_game_over():
        raise HTTPException(status_code=400, detail="Game is over")
    
    # AI가 현재 플레이어인 경우에만 착수
    if game.current_player == 2:  # AI는 백돌(2)
        best_move = ai_engine.get_best_move(game)
        if best_move:
            game.make_move(best_move[0], best_move[1])
        else:
            # AI가 둘 수 있는 수가 없으면 패스
            game.pass_turn()
    
    return game.get_state()

@app.get("/api/game/{game_id}/valid-moves")
async def get_valid_moves(game_id: str):
    """유효한 수 조회"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    return {"valid_moves": game.get_valid_moves()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
