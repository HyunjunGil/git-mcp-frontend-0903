"""
오델로 게임 엔진
8x8 보드에서 진행되는 오델로 게임의 핵심 로직을 구현
"""

from typing import List, Tuple, Optional
import copy

class OthelloGame:
    def __init__(self, mode="human_vs_ai", human_player=1, player1_name="Player 1", player2_name="Player 2"):
        # 8x8 보드 초기화 (0: 빈칸, 1: 흑돌, 2: 백돌)
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        
        # 초기 돌 배치 (중앙 4칸)
        self.board[3][3] = 2  # 백돌
        self.board[3][4] = 1  # 흑돌
        self.board[4][3] = 1  # 흑돌
        self.board[4][4] = 2  # 백돌
        
        self.current_player = 1  # 1: 흑돌, 2: 백돌
        self.mode = mode  # "human_vs_ai" 또는 "human_vs_human"
        self.human_player = human_player  # AI 모드에서만 사용 (1: 흑돌, 2: 백돌)
        self.ai_player = 2 if human_player == 1 else 1  # AI 모드에서만 사용
        self.player1_name = player1_name  # 2인용 모드에서만 사용
        self.player2_name = player2_name  # 2인용 모드에서만 사용
        self.game_over = False
        self.winner = None
        self.pass_count = 0  # 연속 패스 횟수
        self.last_move = None  # 마지막 수 위치 (row, col)
        
        # 게임 히스토리 - 각 수에 대한 상태 저장
        self.history = []
        self._save_initial_state()
        
        # 8방향 벡터 (상, 하, 좌, 우, 대각선)
        self.directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
    
    def _save_initial_state(self):
        """초기 게임 상태를 히스토리에 저장"""
        state = {
            'board': copy.deepcopy(self.board),
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'pass_count': self.pass_count,
            'last_move': self.last_move,
            'move_type': 'initial'
        }
        self.history.append(state)
    
    def _save_state(self, move_type='move', move_position=None):
        """현재 게임 상태를 히스토리에 저장"""
        state = {
            'board': copy.deepcopy(self.board),
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'pass_count': self.pass_count,
            'last_move': self.last_move,
            'move_type': move_type,
            'move_position': move_position
        }
        self.history.append(state)
        print(f"State saved: {move_type}, history length now: {len(self.history)}")
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """보드 범위 내의 유효한 위치인지 확인"""
        return 0 <= row < 8 and 0 <= col < 8
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """해당 위치에 착수할 수 있는지 확인"""
        if not self.is_valid_position(row, col) or self.board[row][col] != 0:
            return False
        
        # 8방향으로 상대방 돌을 뒤집을 수 있는지 확인
        for dr, dc in self.directions:
            if self._can_flip_in_direction(row, col, dr, dc):
                return True
        
        return False
    
    def _can_flip_in_direction(self, row: int, col: int, dr: int, dc: int) -> bool:
        """특정 방향으로 상대방 돌을 뒤집을 수 있는지 확인"""
        opponent = 2 if self.current_player == 1 else 1
        r, c = row + dr, col + dc
        found_opponent = False
        
        # 연속된 상대방 돌 찾기
        while self.is_valid_position(r, c) and self.board[r][c] == opponent:
            found_opponent = True
            r, c = r + dr, c + dc
        
        # 상대방 돌이 있고, 그 끝에 자신의 돌이 있으면 뒤집기 가능
        return found_opponent and self.is_valid_position(r, c) and self.board[r][c] == self.current_player
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """현재 플레이어가 둘 수 있는 유효한 수들의 리스트 반환"""
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col):
                    valid_moves.append((row, col))
        return valid_moves
    
    def make_move(self, row: int, col: int) -> bool:
        """착수하고 상대방 돌 뒤집기"""
        if not self.is_valid_move(row, col):
            return False
        
        # 돌 놓기
        self.board[row][col] = self.current_player
        
        # 마지막 수 위치 저장
        self.last_move = (row, col)
        
        # 8방향으로 상대방 돌 뒤집기
        for dr, dc in self.directions:
            self._flip_in_direction(row, col, dr, dc)
        
        # 패스 카운트 리셋
        self.pass_count = 0
        
        # 다음 플레이어로 변경
        self.current_player = 2 if self.current_player == 1 else 1
        
        # 게임 종료 조건 확인
        self._check_game_over()
        
        # 상태를 히스토리에 저장
        self._save_state('move', (row, col))
        
        return True
    
    def _flip_in_direction(self, row: int, col: int, dr: int, dc: int):
        """특정 방향으로 상대방 돌 뒤집기"""
        if not self._can_flip_in_direction(row, col, dr, dc):
            return
        
        opponent = 2 if self.current_player == 1 else 1
        r, c = row + dr, col + dc
        
        # 연속된 상대방 돌들을 뒤집기
        while self.is_valid_position(r, c) and self.board[r][c] == opponent:
            self.board[r][c] = self.current_player
            r, c = r + dr, c + dc
    
    def pass_turn(self):
        """차례 패스"""
        self.pass_count += 1
        self.last_move = None  # 패스 시 마지막 수 위치 초기화
        self.current_player = 2 if self.current_player == 1 else 1
        self._check_game_over()
        
        # 상태를 히스토리에 저장
        self._save_state('pass')
    
    def _check_game_over(self):
        """게임 종료 조건 확인"""
        # 1. 보드가 가득 찬 경우
        if self._is_board_full():
            self.game_over = True
            self._determine_winner()
            return
        
        # 2. 한쪽 돌이 모두 사라진 경우
        black_count = self.get_black_count()
        white_count = self.get_white_count()
        if black_count == 0 or white_count == 0:
            self.game_over = True
            self._determine_winner()
            return
        
        # 3. 연속 2번 패스 (양쪽 모두 둘 곳이 없음)
        if self.pass_count >= 2:
            self.game_over = True
            self._determine_winner()
            return
        
        # 4. 현재 플레이어가 둘 수 있는 수가 없는 경우
        if not self.get_valid_moves():
            # 상대방도 둘 수 있는 수가 없는지 확인
            opponent = 2 if self.current_player == 1 else 1
            original_player = self.current_player
            
            # 상대방 차례로 변경하여 유효한 수 확인
            self.current_player = opponent
            opponent_has_moves = len(self.get_valid_moves()) > 0
            self.current_player = original_player
            
            if not opponent_has_moves:
                # 둘 다 둘 수 없으면 게임 종료
                self.game_over = True
                self._determine_winner()
                return
            else:
                # 현재 플레이어만 둘 수 없으면 패스
                self.pass_turn()
                return
    
    def _is_board_full(self) -> bool:
        """보드가 가득 찼는지 확인"""
        return all(self.board[row][col] != 0 for row in range(8) for col in range(8))
    
    def _determine_winner(self):
        """승자 결정"""
        black_count = sum(1 for row in self.board for cell in row if cell == 1)
        white_count = sum(1 for row in self.board for cell in row if cell == 2)
        
        if black_count > white_count:
            self.winner = 1  # 흑돌 승리
        elif white_count > black_count:
            self.winner = 2  # 백돌 승리
        else:
            self.winner = 0  # 무승부
    
    def get_black_count(self) -> int:
        """흑돌 개수 반환"""
        return sum(1 for row in self.board for cell in row if cell == 1)
    
    def get_white_count(self) -> int:
        """백돌 개수 반환"""
        return sum(1 for row in self.board for cell in row if cell == 2)
    
    def is_game_over(self) -> bool:
        """게임 종료 여부 반환"""
        return self.game_over
    
    def get_state(self) -> dict:
        """게임 상태 반환"""
        valid_moves = self.get_valid_moves()
        
        # 게임 상태 메시지 생성
        status_message = ""
        last_action = "move"  # 기본값
        
        if self.game_over:
            if self.winner == 1:
                status_message = "게임 종료! 흑돌이 승리했습니다!"
            elif self.winner == 2:
                status_message = "게임 종료! 백돌이 승리했습니다!"
            else:
                status_message = "게임 종료! 무승부입니다!"
        elif len(valid_moves) == 0:
            status_message = f"{'흑돌' if self.current_player == 1 else '백돌'}이 둘 수 있는 수가 없습니다. 턴을 패스합니다."
            last_action = "pass"
        else:
            player_type = "사용자" if self.current_player == self.human_player else "AI"
            stone_color = "흑돌" if self.current_player == 1 else "백돌"
            status_message = f"{player_type} ({stone_color})의 차례입니다."
        
        return {
            "board": self.board,
            "current_player": self.current_player,
            "valid_moves": valid_moves,
            "game_over": self.game_over,
            "winner": self.winner,
            "black_count": self.get_black_count(),
            "white_count": self.get_white_count(),
            "pass_count": self.pass_count,
            "status_message": status_message,
            "can_pass": len(valid_moves) == 0 and not self.game_over,
            "can_undo": self.can_undo(),
            "history_length": self.get_history_length(),
            "mode": self.mode,
            "player1_name": self.player1_name,
            "player2_name": self.player2_name,
            "human_player": self.human_player if self.mode == "human_vs_ai" else None,
            "ai_player": self.ai_player if self.mode == "human_vs_ai" else None,
            "last_action": last_action,
            "last_move": self.last_move
        }
    
    def can_undo(self) -> bool:
        """되돌리기가 가능한지 확인 (초기 상태가 아닌 경우)"""
        result = len(self.history) > 1
        print(f"can_undo: history length = {len(self.history)}, result = {result}")
        return result
    
    def undo_move(self) -> bool:
        """한 수 되돌리기"""
        if not self.can_undo():
            return False
        
        # 현재 상태 제거
        self.history.pop()
        
        # 이전 상태로 복원
        previous_state = self.history[-1]
        self.board = copy.deepcopy(previous_state['board'])
        self.current_player = previous_state['current_player']
        self.game_over = previous_state['game_over']
        self.winner = previous_state['winner']
        self.pass_count = previous_state['pass_count']
        self.last_move = previous_state['last_move']
        
        return True
    
    def get_history_length(self) -> int:
        """히스토리 길이 반환"""
        return len(self.history)
    
    def copy(self):
        """게임 상태 복사 (AI에서 사용)"""
        new_game = OthelloGame(self.mode, self.human_player, self.player1_name, self.player2_name)
        new_game.board = copy.deepcopy(self.board)
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.pass_count = self.pass_count
        new_game.last_move = self.last_move
        new_game.history = copy.deepcopy(self.history)
        return new_game
