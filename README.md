# 오델로(리버시) 게임

8x8 보드에서 진행되는 오델로 게임을 웹 애플리케이션으로 구현한 프로젝트입니다. 2인용 모드와 AI 대전 모드를 지원하며, 강력한 AI 엔진을 내장하고 있습니다.

## 🎮 게임 특징

- **완전한 오델로 규칙 구현**: 모든 오델로 게임 규칙이 정확하게 구현됨
- **강력한 AI**: Minimax 알고리즘 + Alpha-Beta 가지치기로 구현된 고수준 AI
- **아름다운 UI**: Figma 디자인 시스템 기반의 모던한 인터페이스
- **반응형 디자인**: 데스크톱과 모바일 모두 지원

## 🛠 기술 스택

- **백엔드**: Python (FastAPI)
- **프론트엔드**: Vue.js 3 + Composition API
- **AI 엔진**: Minimax + Alpha-Beta Pruning
- **디자인**: Figma MCP 연동

## 🚀 설치 및 실행

### 백엔드 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

백엔드 서버가 `http://localhost:8000`에서 실행됩니다.

### 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

프론트엔드가 `http://localhost:5173`에서 실행됩니다.

## 🎯 게임 방법

1. **게임 시작**: "NEW GAME" 버튼을 클릭하여 새 게임을 시작합니다.
2. **착수**: 유효한 위치(녹색으로 하이라이트)를 클릭하여 돌을 놓습니다.
3. **AI 대전**: "AI MOVE" 버튼을 클릭하여 AI의 수를 요청할 수 있습니다.
4. **승리 조건**: 게임이 끝났을 때 더 많은 돌을 가진 플레이어가 승리합니다.

## 🤖 AI 엔진 특징

- **탐색 깊이**: 8-10수 이상
- **응답 시간**: 3초 이내
- **평가 함수**: 
  - 모서리 점유 (가중치: 1000)
  - 안정돌 분석 (가중치: 20)
  - 이동성 평가 (가중치: 10)
  - 모서리 인접 회피 (가중치: -100)

## 📁 프로젝트 구조

```
├── backend/
│   ├── main.py          # FastAPI 서버
│   ├── game_engine.py   # 게임 로직
│   ├── ai_engine.py     # AI 엔진
│   └── requirements.txt # Python 의존성
├── frontend/
│   ├── src/
│   │   ├── App.vue      # 메인 컴포넌트
│   │   ├── main.js      # Vue 앱 진입점
│   │   └── style.css    # 스타일시트
│   ├── package.json     # Node.js 의존성
│   └── vite.config.js   # Vite 설정
└── README.md
```

## 🎨 디자인 시스템

Figma MCP를 통해 구현된 디자인 시스템:
- **컬러 팔레트**: 고대비, 접근성 고려
- **타이포그래피**: 명확한 계층 구조
- **컴포넌트**: 재사용 가능한 UI 요소들
- **반응형**: 모든 디바이스 지원

## 🔧 API 엔드포인트

- `GET /api/game/new` - 새 게임 시작
- `GET /api/game/{game_id}/state` - 게임 상태 조회
- `POST /api/game/{game_id}/move` - 플레이어 착수
- `POST /api/game/{game_id}/ai-move` - AI 착수 요청
- `GET /api/game/{game_id}/valid-moves` - 유효한 수 조회

## 🏆 성능 목표

- **AI 응답 시간**: 3초 이내
- **프론트엔드 반응 속도**: 1초 이내
- **AI 강도**: 중급자 이상 수준 (승률 70% 이상)

## 📝 라이선스

MIT License
