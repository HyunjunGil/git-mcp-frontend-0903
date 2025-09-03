"""
오델로 AI 엔진
Minimax 알고리즘과 Alpha-Beta 가지치기를 사용한 강력한 AI
"""

import math
import time
from typing import List, Tuple, Optional
from game_engine import OthelloGame

class OthelloAI:
    def __init__(self, max_depth: int = 6, time_limit: float = 4.0):
        self.max_depth = max_depth
        self.time_limit = time_limit
        
        # 평가 함수 가중치
        self.weights = {
            'corner': 1000,      # 모서리 점유
            'corner_adjacent': -100,  # 모서리 인접 (위험)
            'edge': 50,          # 가장자리
            'mobility': 10,      # 이동성
            'stability': 20,     # 안정성
            'disc_count': 1      # 돌 개수 (게임 후반에서 증가)
        }
        
        # 안정돌 판정을 위한 패턴
        self.stable_patterns = self._init_stable_patterns()
    
    def _init_stable_patterns(self) -> List[List[Tuple[int, int]]]:
        """안정돌 패턴 초기화"""
        patterns = []
        
        # 모서리에서 시작하는 안정돌 패턴들
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        
        for corner in corners:
            # 모서리에서 가로/세로로 연속된 돌들
            for direction in [(0, 1), (1, 0)]:
                pattern = [corner]
                for i in range(1, 8):
                    next_pos = (corner[0] + direction[0] * i, corner[1] + direction[1] * i)
                    if 0 <= next_pos[0] < 8 and 0 <= next_pos[1] < 8:
                        pattern.append(next_pos)
                patterns.append(pattern)
        
        return patterns
    
    def get_best_move(self, game: OthelloGame) -> Optional[Tuple[int, int]]:
        """최적의 수 반환"""
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # 수가 적으면 완전탐색 (하지만 시간 제한은 유지)
        if len(valid_moves) <= 4:
            return self._minimax_with_alpha_beta(game, self.max_depth + 1)
        
        # 일반적인 경우
        return self._minimax_with_alpha_beta(game, self.max_depth)
    
    def _minimax_with_alpha_beta(self, game: OthelloGame, depth: int) -> Optional[Tuple[int, int]]:
        """Alpha-Beta 가지치기를 사용한 Minimax 알고리즘"""
        start_time = time.time()
        best_move = None
        best_score = -math.inf
        
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # 수 정렬 (좋은 수부터 탐색하여 가지치기 효과 증대)
        sorted_moves = self._order_moves(game, valid_moves)
        
        for move in sorted_moves:
            # 시간 제한 확인 (더 엄격하게)
            if time.time() - start_time > self.time_limit * 0.8:  # 80% 시간에 도달하면 중단
                break
            
            # 수 시뮬레이션
            new_game = game.copy()
            new_game.make_move(move[0], move[1])
            
            # Minimax 점수 계산
            score = self._minimax(new_game, depth - 1, -math.inf, math.inf, False)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _minimax(self, game: OthelloGame, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """Minimax 알고리즘 (Alpha-Beta 가지치기 포함)"""
        # 종료 조건
        if depth == 0 or game.is_game_over():
            return self._evaluate_position(game)
        
        valid_moves = game.get_valid_moves()
        
        if maximizing:
            max_eval = -math.inf
            for move in valid_moves:
                new_game = game.copy()
                new_game.make_move(move[0], move[1])
                eval_score = self._minimax(new_game, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta 가지치기
            return max_eval
        else:
            min_eval = math.inf
            for move in valid_moves:
                new_game = game.copy()
                new_game.make_move(move[0], move[1])
                eval_score = self._minimax(new_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha 가지치기
            return min_eval
    
    def _order_moves(self, game: OthelloGame, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """수 정렬 (좋은 수부터 탐색)"""
        def move_priority(move):
            priority = 0
            
            # 모서리 수는 최우선
            if move in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                priority += 1000
            
            # 모서리 인접 수는 피하기
            corner_adjacent = [
                (0, 1), (0, 6), (1, 0), (1, 1), (1, 6), (1, 7),
                (6, 0), (6, 1), (6, 6), (6, 7), (7, 1), (7, 6)
            ]
            if move in corner_adjacent:
                priority -= 100
            
            # 가장자리 수는 중간 우선순위
            if move[0] in [0, 7] or move[1] in [0, 7]:
                priority += 50
            
            return priority
        
        return sorted(moves, key=move_priority, reverse=True)
    
    def _evaluate_position(self, game: OthelloGame) -> float:
        """포지션 평가"""
        if game.is_game_over():
            if game.winner == 2:  # AI(백돌) 승리
                return 10000
            elif game.winner == 1:  # 플레이어(흑돌) 승리
                return -10000
            else:  # 무승부
                return 0
        
        score = 0
        
        # 각 위치별 점수 계산
        for row in range(8):
            for col in range(8):
                if game.board[row][col] == 2:  # AI 돌
                    score += self._get_position_value(game, row, col, True)
                elif game.board[row][col] == 1:  # 플레이어 돌
                    score -= self._get_position_value(game, row, col, False)
        
        # 이동성 평가
        ai_moves = len(game.get_valid_moves())
        game.current_player = 1  # 플레이어 차례로 변경
        player_moves = len(game.get_valid_moves())
        game.current_player = 2  # AI 차례로 복원
        
        mobility_diff = ai_moves - player_moves
        score += mobility_diff * self.weights['mobility']
        
        # 게임 후반 돌 개수 가중치 증가
        total_discs = game.get_black_count() + game.get_white_count()
        if total_discs > 50:  # 게임 후반
            disc_diff = game.get_white_count() - game.get_black_count()
            score += disc_diff * self.weights['disc_count'] * 2
        
        return score
    
    def _get_position_value(self, game: OthelloGame, row: int, col: int, is_ai: bool) -> float:
        """특정 위치의 가치 계산"""
        value = 0
        
        # 모서리 점유
        if (row, col) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            value += self.weights['corner']
        
        # 모서리 인접 (위험)
        corner_adjacent = [
            (0, 1), (0, 6), (1, 0), (1, 1), (1, 6), (1, 7),
            (6, 0), (6, 1), (6, 6), (6, 7), (7, 1), (7, 6)
        ]
        if (row, col) in corner_adjacent:
            value += self.weights['corner_adjacent']
        
        # 가장자리
        if row in [0, 7] or col in [0, 7]:
            value += self.weights['edge']
        
        # 안정성 평가
        if self._is_stable(game, row, col):
            value += self.weights['stability']
        
        return value
    
    def _is_stable(self, game: OthelloGame, row: int, col: int) -> bool:
        """돌의 안정성 판정"""
        # 모서리는 항상 안정
        if (row, col) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            return True
        
        # 모서리에서 연속된 돌들은 안정
        for pattern in self.stable_patterns:
            if (row, col) in pattern:
                # 패턴의 모든 돌이 같은 색인지 확인
                player = game.board[row][col]
                is_stable = True
                for r, c in pattern:
                    if game.board[r][c] != player:
                        is_stable = False
                        break
                if is_stable:
                    return True
        
        return False
