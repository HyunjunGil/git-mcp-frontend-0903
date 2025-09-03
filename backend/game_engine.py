"""
오델로 게임 엔진
8x8 보드에서 진행되는 오델로 게임의 핵심 로직을 구현
"""

from typing import List, Tuple, Optional
import copy

class OthelloGame:
    def __init__(self):
        # 8x8 보드 초기화 (0: 빈칸, 1: 흑돌, 2: 백돌)
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        
        # 초기 돌 배치 (중앙 4칸)
        self.board[3][3] = 2  # 백돌
        self.board[3][4] = 1  # 흑돌
        self.board[4][3] = 1  # 흑돌
        self.board[4][4] = 2  # 백돌
        
        self.current_player = 1  # 1: 흑돌, 2: 백돌
        self.game_over = False
        self.winner = None
        self.pass_count = 0  # 연속 패스 횟수
        
        # 8방향 벡터 (상, 하, 좌, 우, 대각선)
        self.directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
    
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
        
        # 8방향으로 상대방 돌 뒤집기
        for dr, dc in self.directions:
            self._flip_in_direction(row, col, dr, dc)
        
        # 패스 카운트 리셋
        self.pass_count = 0
        
        # 다음 플레이어로 변경
        self.current_player = 2 if self.current_player == 1 else 1
        
        # 게임 종료 조건 확인
        self._check_game_over()
        
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
        self.current_player = 2 if self.current_player == 1 else 1
        self._check_game_over()
    
    def _check_game_over(self):
        """게임 종료 조건 확인"""
        # 보드가 가득 찬 경우
        if all(self.board[row][col] != 0 for row in range(8) for col in range(8)):
            self.game_over = True
            self._determine_winner()
            return
        
        # 연속으로 2번 패스한 경우
        if self.pass_count >= 2:
            self.game_over = True
            self._determine_winner()
            return
        
        # 현재 플레이어가 둘 수 있는 수가 없는 경우
        if not self.get_valid_moves():
            self.pass_turn()
    
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
        return {
            "board": self.board,
            "current_player": self.current_player,
            "valid_moves": self.get_valid_moves(),
            "game_over": self.game_over,
            "winner": self.winner,
            "black_count": self.get_black_count(),
            "white_count": self.get_white_count(),
            "pass_count": self.pass_count
        }
    
    def copy(self):
        """게임 상태 복사 (AI에서 사용)"""
        new_game = OthelloGame()
        new_game.board = copy.deepcopy(self.board)
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.pass_count = self.pass_count
        return new_game
