# 오델로(리버시) 게임 프로젝트 명세서

## 프로젝트 개요
8x8 보드에서 진행되는 오델로 게임을 웹 애플리케이션으로 구현합니다. 2인용 모드와 AI 대전 모드를 지원하며, 높은 수준의 AI를 내장합니다.

## 기술 스택
- **백엔드**: Python (FastAPI 또는 Flask)
- **프론트엔드**: Vue.js 3 + Composition API
- **AI 엔진**: Python (minimax 알고리즘 + 알파베타 가지치기)
- **통신**: REST API 또는 WebSocket

## 핵심 기능 요구사항

### 1. 게임 엔진 (백엔드)
#### 1.1 게임 로직
- 8x8 보드 상태 관리
- 유효한 수 계산 알고리즘
- 돌 뒤집기 로직 구현
- 게임 종료 조건 판정
- 승부 결과 계산

#### 1.2 게임 상태 관리
```python
# 게임 상태 예시 구조
{
    "board": [[0, 0, 0, ...], ...],  # 0: 빈칸, 1: 흑돌, 2: 백돌
    "current_player": 1,             # 1: 흑돌 차례, 2: 백돌 차례
    "valid_moves": [(2, 3), (3, 2), ...],  # 유효한 수 목록
    "game_over": false,
    "winner": null,                  # null, 1, 2, "draw"
    "black_count": 2,
    "white_count": 2,
    "pass_count": 0                  # 연속 패스 횟수
}
```

#### 1.3 API 엔드포인트
- `GET /api/game/new` - 새 게임 시작
- `GET /api/game/{game_id}/state` - 게임 상태 조회
- `POST /api/game/{game_id}/move` - 플레이어 착수
- `POST /api/game/{game_id}/ai-move` - AI 착수 요청
- `GET /api/game/{game_id}/valid-moves` - 유효한 수 조회

### 2. AI 엔진
#### 2.1 AI 성능 요구사항
- **최소 탐색 깊이**: 8-10수 이상
- **응답 시간**: 3초 이내
- **강도**: 중급자 이상 수준 (승률 70% 이상)

#### 2.2 AI 알고리즘
- **기본 알고리즘**: Minimax with Alpha-Beta Pruning
- **평가 함수 요소**:
  - 안정돌(Stable discs) 가중치: 높음
  - 모서리 점유 가중치: 높음
  - 이동성(Mobility) 가중치: 중간
  - 돌 개수 가중치: 낮음 (게임 후반에서 증가)

#### 2.3 AI 난이도 설정 (선택사항)
- Easy: 탐색 깊이 4-6, 단순한 평가함수
- Normal: 탐색 깊이 6-8, 균형잡힌 평가함수
- Hard: 탐색 깊이 8-10+, 고급 평가함수

### 3. 프론트엔드 (Vue.js)
#### 3.1 화면 구성
- **메인 화면**: 게임 모드 선택 (2인용 vs AI 대전)
- **게임 화면**: 8x8 보드, 게임 정보 표시
- **결과 화면**: 승부 결과, 재시작 옵션

#### 3.2 게임 보드 UI
- 8x8 그리드 형태의 보드
- 클릭 가능한 유효한 수 하이라이트
- 돌 애니메이션 (놓기, 뒤집기)
- 현재 차례 표시
- 돌 개수 실시간 표시

#### 3.3 사용자 경험
- 유효하지 않은 수 클릭 시 에러 메시지
- AI 사고 시간 동안 로딩 표시
- 게임 진행 상황을 명확하게 표시
- 반응형 디자인 (모바일 지원)

## 구현 우선순위

### Phase 1: 핵심 게임 엔진
1. 보드 상태 관리 클래스 구현
2. 유효한 수 계산 알고리즘
3. 돌 뒤집기 로직
4. 게임 종료 조건 판정

### Phase 2: API 서버
1. FastAPI/Flask 서버 설정
2. 게임 상태 관리 API 구현
3. CORS 설정 및 에러 핸들링

### Phase 3: 기본 AI
1. Minimax 알고리즘 구현
2. 기본 평가 함수 작성
3. AI 착수 API 연동

### Phase 4: 프론트엔드
1. Vue.js 프로젝트 설정
2. 게임 보드 컴포넌트 구현
3. API 연동 및 상태 관리

### Phase 5: AI 개선
1. Alpha-Beta 가지치기 적용
2. 고급 평가 함수 구현
3. 성능 최적화

## 테스트 요구사항
- 게임 로직 단위 테스트 (유효한 수, 돌 뒤집기 등)
- AI 성능 테스트 (응답 시간, 승률)
- 엣지 케이스 테스트 (연속 패스, 보드 가득참 등)

## 품질 기준
### 기능성
- [ ] 모든 오델로 규칙이 정확하게 구현되어야 함
- [ ] AI가 불법적인 수를 두지 않아야 함
- [ ] 게임이 중간에 멈추거나 에러가 발생하지 않아야 함

### 성능
- [ ] AI 응답 시간 3초 이내
- [ ] 프론트엔드 반응 속도 1초 이내
- [ ] 동시에 여러 게임 세션 지원

### 사용성
- [ ] 직관적인 UI/UX
- [ ] 명확한 게임 상태 표시
- [ ] 모바일에서도 사용 가능

## 개발 환경 설정
### 백엔드
```bash
# 가상환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install fastapi uvicorn numpy
```

### 프론트엔드
```bash
# Vue.js 프로젝트 생성
npm create vue@latest othello-frontend
cd othello-frontend
npm install
npm install axios  # API 통신용
```

## 참고 자료 (AI 개발 중심)
### 오델로 AI 개발 필수 자료
- **Logistello**: 역대 최강 오델로 엔진 논문
- **Edax**: 현재 최강급 오픈소스 엔진 [GitHub](https://github.com/abulmo/edax-reversi)
- **NTest**: 엔진 성능 테스트 도구
- **Thor Database**: 전문가 게임 기보 데이터베이스

### 알고리즘 참고 자료
- [Minimax with Alpha-Beta Pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
- [Negamax Algorithm](https://en.wikipedia.org/wiki/Negamax)
- [Transposition Table](https://www.chessprogramming.org/Transposition_Table)
- [Move Ordering](https://www.chessprogramming.org/Move_Ordering)

### 평가함수 연구 자료
- **Stability Analysis**: Rosenbloom's stability calculation
- **Mobility Evaluation**: Current vs Potential mobility
- **Corner Strategy**: Corner-adjacent square evaluation
- **Parity Theory**: Odd-even move analysis

### 기술 자료
- [Bitboard Techniques](https://www.chessprogramming.org/Bitboards)
- [Zobrist Hashing](https://www.chessprogramming.org/Zobrist_Hashing)
- [Iterative Deepening](https://www.chessprogramming.org/Iterative_Deepening)

### Figma MCP 활용 가이드
- **Figma MCP 서버**: Claude Desktop과 Figma 연동
- **디자인 토큰**: Figma에서 CSS 변수 자동 추출
- **컴포넌트 생성**: Figma 컴포넌트를 Vue 컴포넌트로 변환
- **자산 추출**: 아이콘, 이미지 등 자동 export
- **일관성 보장**: 디자인 시스템 기반 코드 생성

### Figma 디자인 가이드라인
- **보드 그리드**: 8x8 균등 분할, 클릭 영역 명확 구분
- **돌 디자인**: 심플하고 대비가 명확한 흑/백 디자인
- **상태 표시**: 미니멀한 정보 표시 (돌 개수, 차례 등)
- **하이라이트**: 유효한 수 표시를 위한 시각적 피드백
- **컬러 팔레트**: 고대비, 접근성 고려한 색상 선택

## 성능 벤치마킹 계획
### 테스트 대상
1. **Edax (Level 21)**: 현재 최강급 엔진
2. **NTest 표준 포지션**: 널리 사용되는 테스트 셋
3. **FFO 테스트**: 종반 완전탐색 테스트
4. **실제 전문가**: 가능하다면 고수와 실전

### 성능 목표
- **Edax Level 15 이상**: 최소 목표
- **NTest 95% 이상**: 표준 포지션 정답률
- **FFO Perfect**: 종반 완전탐색 모든 문제 정답