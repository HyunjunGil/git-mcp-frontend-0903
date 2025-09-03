# 오델로 게임 추가 기능 명세서

## 추가 기능 개요
기존 AI 대전 모드에 더해 4가지 핵심 기능을 추가하여 완전한 오델로 게임을 구현합니다.

## 1. 2인용 대전 모드 (사람 vs 사람)

### 1.1 게임 모드 선택
```python
# 게임 모드 enum
class GameMode(Enum):
    HUMAN_VS_HUMAN = "human_vs_human"
    HUMAN_VS_AI = "human_vs_ai"

# 게임 상태에 모드 추가
{
    "game_mode": "human_vs_human",
    "player1_name": "Player 1",  # 흑돌 플레이어
    "player2_name": "Player 2",  # 백돌 플레이어
    "current_player": 1,         # 1: 흑돌, 2: 백돌
    # ... 기존 게임 상태
}
```

### 1.2 2인용 모드 특징
- **턴 관리**: 흑돌(Player 1) → 백돌(Player 2) 순서로 번갈아가며 진행
- **입력 처리**: 두 플레이어 모두 마우스 클릭으로 착수
- **AI 비활성화**: AI 엔진 호출 없이 순수 사람 대 사람
- **게임 규칙**: AI 모드와 동일한 오델로 규칙 적용

### 1.3 API 엔드포인트 (2인용)
- `POST /api/game/new` - body에 `{"mode": "human_vs_human"}` 추가
- `POST /api/game/{game_id}/move` - 현재 플레이어의 착수 처리
- `GET /api/game/{game_id}/current-player` - 현재 차례 플레이어 확인

## 2. AI 대전 시 색깔 선택 기능

### 2.1 게임 시작 시 색깔 선택
```python
# AI 모드 게임 생성 시
{
    "mode": "human_vs_ai",
    "human_color": 1,    # 1: 흑돌(선수), 2: 백돌(후수)
    "ai_color": 2,       # human_color의 반대
    "first_move": 1      # 항상 흑돌이 먼저 (오델로 규칙)
}
```

### 2.2 선택 로직
- **사용자 선택**: 게임 시작 전 흑돌/백돌 선택
- **AI 자동 배정**: 사용자가 선택하지 않은 색으로 자동 설정
- **선수 결정**: 흑돌이 항상 먼저 시작 (오델로 규칙)
- **턴 순서**: 
  - 사용자가 흑돌 선택 → 사용자 먼저 시작
  - 사용자가 백돌 선택 → AI 먼저 시작

### 2.3 UI 구현
- **색깔 선택 화면**: 게임 시작 전 모달 또는 선택 버튼
- **시각적 표현**: 흑돌(●) / 백돌(○) 명확히 구분
- **선수 안내**: "흑돌은 먼저 시작합니다" 메시지 표시

## 3. 패스(Pass) 기능 구현

### 3.1 패스 조건 판정
```python
def has_valid_moves(board, player):
    """현재 플레이어가 둘 수 있는 유효한 수가 있는지 확인"""
    valid_moves = get_valid_moves(board, player)
    return len(valid_moves) > 0

def should_pass(board, player):
    """패스해야 하는지 판정"""
    return not has_valid_moves(board, player)
```

### 3.2 패스 처리 로직
- **자동 패스**: 유효한 수가 없으면 강제로 패스
- **패스 알림**: "둘 곳이 없어서 차례를 넘깁니다" 메시지 표시
- **턴 넘김**: 상대방에게 차례 이동
- **패스 카운트**: 연속 패스 횟수 추적 (게임 종료 판정용)

### 3.3 패스 상태 관리
```python
{
    "board": [[0, 0, 0, ...], ...],
    "current_player": 1,
    "valid_moves": [],           # 빈 배열 = 패스 상황
    "last_action": "pass",       # "move" 또는 "pass"
    "pass_count": 1,             # 연속 패스 횟수
    "pass_player": 1,            # 패스한 플레이어
    "game_over": false
}
```

### 3.4 패스 시나리오별 처리
- **사람 플레이어 패스**: 자동으로 상대방(AI 또는 상대 플레이어)에게 턴 이동
- **AI 플레이어 패스**: AI가 패스 상황을 인식하고 턴 넘김
- **UI 표시**: "Player 1 패스 - 유효한 수가 없습니다" 알림

## 4. 게임 종료 조건

### 4.1 종료 조건 판정
```python
def check_game_over(board, pass_count):
    """게임 종료 조건 확인"""
    # 1. 연속 2번 패스 (양쪽 모두 둘 곳이 없음)
    if pass_count >= 2:
        return True, "both_pass"
    
    # 2. 보드가 가득 참
    if is_board_full(board):
        return True, "board_full"
    
    # 3. 한쪽 돌이 모두 사라짐
    black_count = count_stones(board, 1)
    white_count = count_stones(board, 2)
    
    if black_count == 0:
        return True, "no_black_stones"
    if white_count == 0:
        return True, "no_white_stones"
    
    return False, None
```

### 4.2 승부 결정
```python
def determine_winner(board):
    """최종 승자 결정"""
    black_count = count_stones(board, 1)
    white_count = count_stones(board, 2)
    
    if black_count > white_count:
        return {"winner": 1, "black_count": black_count, "white_count": white_count}
    elif white_count > black_count:
        return {"winner": 2, "black_count": black_count, "white_count": white_count}
    else:
        return {"winner": "draw", "black_count": black_count, "white_count": white_count}
```

### 4.3 게임 종료 처리
- **즉시 종료**: 종료 조건 만족 시 게임 상태를 `game_over: true`로 변경
- **결과 계산**: 보드의 돌 개수를 세어 승부 결정
- **결과 표시**: 승자, 각 색깔별 돌 개수, 종료 사유 표시

## API 명세 변경사항

### 게임 생성 API 확장
```python
POST /api/game/new
{
    "mode": "human_vs_human" | "human_vs_ai",
    "human_color": 1 | 2,  # AI 모드에서만 사용
    "player1_name": "Player 1",  # 2인용 모드에서만 사용
    "player2_name": "Player 2"   # 2인용 모드에서만 사용
}

Response:
{
    "game_id": "uuid",
    "mode": "human_vs_human",
    "current_player": 1,
    "board": [[0, 0, ...], ...],
    "valid_moves": [(2, 3), (3, 2), ...],
    "black_count": 2,
    "white_count": 2
}
```

### 착수 API 확장
```python
POST /api/game/{game_id}/move
{
    "row": 2,
    "col": 3,
    "player": 1  # 2인용 모드에서 현재 플레이어 검증용
}

Response:
{
    "success": true,
    "board": [[0, 0, ...], ...],
    "current_player": 2,
    "valid_moves": [(1, 2), ...],
    "last_action": "move",
    "pass_count": 0,
    "black_count": 4,
    "white_count": 1,
    "game_over": false,
    "winner": null
}
```

### 패스 처리 API
```python
GET /api/game/{game_id}/check-pass
Response:
{
    "should_pass": true,
    "current_player": 1,
    "valid_moves": []
}

POST /api/game/{game_id}/pass
Response:
{
    "success": true,
    "current_player": 2,  # 턴이 넘어감
    "pass_count": 1,
    "last_action": "pass",
    "game_over": false
}
```

## 프론트엔드 UI 변경사항

### 1. 게임 모드 선택 화면
- 2인용 대전과 AI 대전 선택 버튼
- 각 모드별 설명 제공
- 선택 후 해당 모드 설정 화면으로 이동

### 2. AI 대전 색깔 선택 화면
- 흑돌(선수)와 백돌(후수) 선택 버튼
- "흑돌은 먼저 시작합니다" 안내 메시지
- 선택 후 게임 시작

### 3. 게임 상태 표시 강화
- 현재 차례 플레이어 명확히 표시
- 자동 패스 상황 알림 메시지
- 게임 종료 시 결과 화면
- 돌 개수 실시간 업데이트

### 4. 자동 패스 처리 UI
- 패스 상황 감지 시 자동으로 알림 표시
- 1-2초 후 자동으로 턴 넘김
- 연속 패스 상황 별도 표시
- 사용자 액션 없이 시스템이 처리

## 구현 우선순위

### Phase 1: 패스 기능 구현
1. 유효한 수 판정 로직 구현
2. 패스 조건 체크 함수
3. 게임 종료 조건 판정
4. API 엔드포인트 추가

### Phase 2: 2인용 모드 구현  
1. 게임 모드 관리 시스템
2. 턴 관리 로직 수정
3. 2인용 모드 API 구현
4. UI 모드 선택 화면

### Phase 3: AI 색깔 선택 구현
1. 게임 생성 시 색깔 선택 로직
2. AI 모드 초기화 수정
3. 색깔 선택 UI 구현
4. 턴 순서 관리

### Phase 4: UI 통합 및 테스트
1. 모든 모드 통합 테스트
2. 패스 상황 UI 개선
3. 게임 종료 화면 구현
4. 사용자 경험 최적화

## 테스트 케이스

### 패스 기능 테스트
- [ ] 유효한 수가 없을 때 자동 패스
- [ ] 연속 2번 패스 시 게임 종료
- [ ] 패스 후 턴 정상 이동
- [ ] 패스 알림 메시지 표시

### 2인용 모드 테스트
- [ ] 플레이어 간 턴 교체
- [ ] 게임 규칙 정확한 적용
- [ ] 승부 결정 정확성

### AI 색깔 선택 테스트
- [ ] 사용자 선택에 따른 AI 색깔 자동 배정
- [ ] 선수(흑돌) 먼저 시작 규칙
- [ ] 색깔별 턴 순서 정확성

### 게임 종료 테스트
- [ ] 양쪽 모두 패스 시 종료
- [ ] 보드 가득 참 시 종료
- [ ] 한쪽 돌 모두 사라짐 시 종료
- [ ] 승부 결정 정확성