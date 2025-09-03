"""
오델로 AI 엔진
Minimax 알고리즘과 Alpha-Beta 가지치기를 사용한 강력한 AI
"""

import math
import time
from typing import List, Tuple, Optional
from game_engine import OthelloGame

class OthelloAI:
    def __init__(self, max_depth: int = 8, time_limit: float = 5.0):
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.start_time = None
        
        # 평가 함수 가중치 (더 정교한 전략)
        self.weights = {
            'corner': 1000,      # 모서리 점유
            'corner_adjacent': -200,  # 모서리 인접 (매우 위험)
            'edge': 80,          # 가장자리
            'mobility': 15,      # 이동성
            'stability': 30,     # 안정성
            'disc_count': 1,     # 돌 개수 (게임 후반에서 증가)
            'parity': 5,         # 패리티 (게임 후반)
            'frontier': -10,     # 프론티어 (위험한 위치)
            'internal': 20,      # 내부 안정성
            'potential_mobility': 8  # 잠재적 이동성
        }
        
        # 안정돌 판정을 위한 패턴
        self.stable_patterns = self._init_stable_patterns()
        
        # 성능 최적화를 위한 캐시
        self.evaluation_cache = {}
        self.move_ordering_cache = {}
    
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
        """최적의 수 반환 (적응적 깊이 조절)"""
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # 시간 제한 시작
        self.start_time = time.time()
        
        # 캐시 초기화 (새로운 게임 상태마다)
        self.evaluation_cache.clear()
        self.move_ordering_cache.clear()
        
        # 게임 단계별 적응적 깊이 조절
        total_discs = game.get_black_count() + game.get_white_count()
        
        if total_discs < 20:  # 게임 초반
            depth = min(self.max_depth - 2, 6)
        elif total_discs < 40:  # 게임 중반
            depth = self.max_depth - 1
        elif total_discs < 55:  # 게임 후반
            depth = self.max_depth
        else:  # 게임 말기
            depth = self.max_depth + 1
        
        # 수가 적으면 더 깊이 탐색
        if len(valid_moves) <= 3:
            depth = min(depth + 2, 10)
        elif len(valid_moves) <= 6:
            depth = min(depth + 1, 9)
        
        return self._minimax_with_alpha_beta(game, depth)
    
    def _minimax_with_alpha_beta(self, game: OthelloGame, depth: int) -> Optional[Tuple[int, int]]:
        """Alpha-Beta 가지치기를 사용한 Minimax 알고리즘"""
        best_move = None
        best_score = -math.inf
        
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        # 수 정렬 (좋은 수부터 탐색하여 가지치기 효과 증대)
        sorted_moves = self._order_moves(game, valid_moves)
        
        for move in sorted_moves:
            # 시간 제한 확인 (전역 시간 체크)
            if self._is_time_up():
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
        """Minimax 알고리즘 (Alpha-Beta 가지치기 포함, 성능 최적화)"""
        # 시간 제한 확인
        if self._is_time_up():
            return self._evaluate_position(game)
        
        # 종료 조건
        if depth == 0 or game.is_game_over():
            return self._evaluate_position(game)
        
        valid_moves = game.get_valid_moves()
        
        # 수가 없으면 패스
        if not valid_moves:
            new_game = game.copy()
            new_game.pass_turn()
            return self._minimax(new_game, depth - 1, alpha, beta, not maximizing)
        
        # 수 정렬 (가지치기 효과 증대)
        if depth > 2:  # 깊은 탐색에서만 정렬 (성능 최적화)
            valid_moves = self._order_moves(game, valid_moves)
        
        if maximizing:
            max_eval = -math.inf
            for move in valid_moves:
                # 시간 제한 확인
                if self._is_time_up():
                    break
                    
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
                # 시간 제한 확인
                if self._is_time_up():
                    break
                    
                new_game = game.copy()
                new_game.make_move(move[0], move[1])
                eval_score = self._minimax(new_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha 가지치기
            return min_eval
    
    def _order_moves(self, game: OthelloGame, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """수 정렬 (더 정교한 우선순위)"""
        def move_priority(move):
            priority = 0
            row, col = move
            
            # 모서리 수는 최우선
            if move in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                priority += 1000
            
            # 모서리 인접 수는 매우 위험
            corner_adjacent = [
                (0, 1), (0, 6), (1, 0), (1, 1), (1, 6), (1, 7),
                (6, 0), (6, 1), (6, 6), (6, 7), (7, 1), (7, 6)
            ]
            if move in corner_adjacent:
                priority -= 200
            
            # 가장자리 수는 좋은 우선순위
            if row in [0, 7] or col in [0, 7]:
                priority += 80
            
            # 내부 안정성 (2,2 ~ 5,5 영역)
            if 2 <= row <= 5 and 2 <= col <= 5:
                priority += 20
            
            # 프론티어 위치는 위험 (빈 칸과 인접한 위치)
            if self._is_frontier_position(game, row, col):
                priority -= 10
            
            # 잠재적 이동성 (상대방의 이동성을 줄이는 수)
            potential_mobility = self._calculate_potential_mobility(game, move)
            priority += potential_mobility * 5
            
            return priority
        
        return sorted(moves, key=move_priority, reverse=True)
    
    def _is_time_up(self) -> bool:
        """시간 제한 확인"""
        if self.start_time is None:
            return False
        return time.time() - self.start_time > self.time_limit
    
    def _is_frontier_position(self, game: OthelloGame, row: int, col: int) -> bool:
        """프론티어 위치인지 확인 (빈 칸과 인접한 위치)"""
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if game.board[new_row][new_col] == 0:  # 빈 칸과 인접
                    return True
        return False
    
    def _calculate_potential_mobility(self, game: OthelloGame, move: Tuple[int, int]) -> int:
        """잠재적 이동성 계산 (상대방의 이동성을 줄이는 정도)"""
        # 수를 두기 전 상대방의 이동성
        opponent = 1 if game.current_player == 2 else 2
        original_player = game.current_player
        
        game.current_player = opponent
        original_mobility = len(game.get_valid_moves())
        
        # 수를 두고 난 후 상대방의 이동성
        new_game = game.copy()
        new_game.make_move(move[0], move[1])
        new_game.current_player = opponent
        new_mobility = len(new_game.get_valid_moves())
        
        game.current_player = original_player
        
        return original_mobility - new_mobility
    
    def _evaluate_position(self, game: OthelloGame) -> float:
        """포지션 평가 (더 정교한 전략)"""
        if game.is_game_over():
            if game.winner == 2:  # AI(백돌) 승리
                return 10000
            elif game.winner == 1:  # 플레이어(흑돌) 승리
                return -10000
            else:  # 무승부
                return 0
        
        score = 0
        total_discs = game.get_black_count() + game.get_white_count()
        
        # 각 위치별 점수 계산
        for row in range(8):
            for col in range(8):
                if game.board[row][col] == 2:  # AI 돌
                    score += self._get_position_value(game, row, col, True)
                elif game.board[row][col] == 1:  # 플레이어 돌
                    score -= self._get_position_value(game, row, col, False)
        
        # 이동성 평가
        ai_moves = len(game.get_valid_moves())
        original_player = game.current_player
        game.current_player = 1  # 플레이어 차례로 변경
        player_moves = len(game.get_valid_moves())
        game.current_player = original_player  # 원래 플레이어로 복원
        
        mobility_diff = ai_moves - player_moves
        score += mobility_diff * self.weights['mobility']
        
        # 잠재적 이동성 평가
        potential_mobility_diff = self._calculate_potential_mobility_difference(game)
        score += potential_mobility_diff * self.weights['potential_mobility']
        
        # 프론티어 평가 (위험한 위치에 있는 돌들)
        frontier_diff = self._calculate_frontier_difference(game)
        score += frontier_diff * self.weights['frontier']
        
        # 내부 안정성 평가
        internal_diff = self._calculate_internal_difference(game)
        score += internal_diff * self.weights['internal']
        
        # 게임 단계별 가중치 조정
        if total_discs > 50:  # 게임 후반
            # 패리티 (남은 수의 홀짝성)
            parity = (64 - total_discs) % 2
            if parity == 0:  # AI가 마지막에 둘 차례
                score += self.weights['parity']
            else:
                score -= self.weights['parity']
            
            # 돌 개수 가중치 증가
            disc_diff = game.get_white_count() - game.get_black_count()
            score += disc_diff * self.weights['disc_count'] * 3
        
        return score
    
    def _calculate_potential_mobility_difference(self, game: OthelloGame) -> int:
        """잠재적 이동성 차이 계산"""
        ai_potential = self._count_potential_moves(game, 2)  # AI의 잠재적 이동성
        player_potential = self._count_potential_moves(game, 1)  # 플레이어의 잠재적 이동성
        return ai_potential - player_potential
    
    def _count_potential_moves(self, game: OthelloGame, player: int) -> int:
        """특정 플레이어의 잠재적 이동성 계산"""
        potential_moves = 0
        original_player = game.current_player
        
        for row in range(8):
            for col in range(8):
                if game.board[row][col] == 0:  # 빈 칸
                    # 이 위치에 둘 수 있는지 확인
                    game.current_player = player
                    if game.is_valid_move(row, col):
                        potential_moves += 1
        
        game.current_player = original_player
        return potential_moves
    
    def _calculate_frontier_difference(self, game: OthelloGame) -> int:
        """프론티어 돌 개수 차이 계산"""
        ai_frontier = 0
        player_frontier = 0
        
        for row in range(8):
            for col in range(8):
                if game.board[row][col] != 0:  # 돌이 있는 위치
                    if self._is_frontier_position(game, row, col):
                        if game.board[row][col] == 2:  # AI 돌
                            ai_frontier += 1
                        else:  # 플레이어 돌
                            player_frontier += 1
        
        return player_frontier - ai_frontier  # 프론티어는 적을수록 좋음
    
    def _calculate_internal_difference(self, game: OthelloGame) -> int:
        """내부 안정 돌 개수 차이 계산"""
        ai_internal = 0
        player_internal = 0
        
        for row in range(2, 6):  # 내부 영역 (2,2 ~ 5,5)
            for col in range(2, 6):
                if game.board[row][col] != 0:
                    if not self._is_frontier_position(game, row, col):  # 프론티어가 아닌 내부 돌
                        if game.board[row][col] == 2:  # AI 돌
                            ai_internal += 1
                        else:  # 플레이어 돌
                            player_internal += 1
        
        return ai_internal - player_internal
    
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
