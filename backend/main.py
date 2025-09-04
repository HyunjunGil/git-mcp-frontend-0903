from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
from enum import Enum
import uuid
from game_engine import OthelloGame
from ai_engine import OthelloAI

class GameMode(str, Enum):
    HUMAN_VS_HUMAN = "human_vs_human"
    HUMAN_VS_AI = "human_vs_ai"

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
    player: Optional[int] = None  # 2인용 모드에서 현재 플레이어 검증용

class NewGameRequest(BaseModel):
    mode: GameMode
    human_color: Optional[int] = None  # AI 모드에서만 사용 (1: 흑돌, 2: 백돌)
    player1_name: Optional[str] = "Player 1"  # 2인용 모드에서만 사용
    player2_name: Optional[str] = "Player 2"  # 2인용 모드에서만 사용

class GameState(BaseModel):
    board: List[List[int]]
    current_player: int
    valid_moves: List[Tuple[int, int]]
    game_over: bool
    winner: Optional[int]
    black_count: int
    white_count: int
    pass_count: int
    mode: Optional[str] = None
    player1_name: Optional[str] = None
    player2_name: Optional[str] = None
    last_action: Optional[str] = None
    last_move: Optional[Tuple[int, int]] = None

@app.post("/api/game/new")
async def new_game(request: NewGameRequest):
    """새 게임 시작"""
    game_id = str(uuid.uuid4())
    
    # 모드별 게임 생성
    if request.mode == GameMode.HUMAN_VS_AI:
        # AI 모드: 색깔 선택이 필요
        human_color = request.human_color or 1  # 기본값: 흑돌
        game = OthelloGame(
            mode="human_vs_ai",
            human_player=human_color,
            player1_name="Player",
            player2_name="AI"
        )
    else:
        # 2인용 모드
        game = OthelloGame(
            mode="human_vs_human",
            human_player=1,  # 2인용 모드에서는 사용되지 않음
            player1_name=request.player1_name or "Player 1",
            player2_name=request.player2_name or "Player 2"
        )
    
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
    
    # 2인용 모드에서 플레이어 검증
    if game.mode == "human_vs_human" and move.player is not None:
        if move.player != game.current_player:
            raise HTTPException(status_code=400, detail="Not your turn")
    
    if not game.is_valid_move(move.row, move.col):
        raise HTTPException(status_code=400, detail="Invalid move")
    
    game.make_move(move.row, move.col)
    return game.get_state()

@app.post("/api/game/{game_id}/ai-move")
async def ai_move(game_id: str):
    """AI 착수 (AI 모드에서만 사용)"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    # AI 모드가 아닌 경우 에러
    if game.mode != "human_vs_ai":
        raise HTTPException(status_code=400, detail="AI move is only available in AI mode")
    
    if game.is_game_over():
        raise HTTPException(status_code=400, detail="Game is over")
    
    # AI가 현재 플레이어인 경우에만 착수
    if game.current_player == game.ai_player:
        import time
        start_time = time.time()
        best_move = ai_engine.get_best_move(game)
        end_time = time.time()
        
        print(f"AI thinking time: {end_time - start_time:.2f} seconds")
        
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

@app.get("/api/game/{game_id}/check-pass")
async def check_pass(game_id: str):
    """패스 필요 여부 확인"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    valid_moves = game.get_valid_moves()
    should_pass = len(valid_moves) == 0 and not game.is_game_over()
    
    return {
        "should_pass": should_pass,
        "current_player": game.current_player,
        "valid_moves": valid_moves
    }

@app.post("/api/game/{game_id}/pass")
async def pass_turn(game_id: str):
    """차례 패스"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    if game.is_game_over():
        raise HTTPException(status_code=400, detail="Game is over")
    
    # 유효한 수가 있는 경우 패스 불가
    if game.get_valid_moves():
        raise HTTPException(status_code=400, detail="Cannot pass when valid moves are available")
    
    game.pass_turn()
    return game.get_state()

@app.get("/api/game/{game_id}/current-player")
async def get_current_player(game_id: str):
    """현재 차례 플레이어 확인"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    return {
        "current_player": game.current_player,
        "mode": game.mode,
        "player1_name": game.player1_name,
        "player2_name": game.player2_name
    }

@app.post("/api/game/{game_id}/undo")
async def undo_move(game_id: str):
    """한 수 되돌리기"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    if not game.can_undo():
        raise HTTPException(status_code=400, detail="Cannot undo - no moves to undo")
    
    if game.is_game_over():
        raise HTTPException(status_code=400, detail="Cannot undo - game is over")
    
    success = game.undo_move()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to undo move")
    
    return game.get_state()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
