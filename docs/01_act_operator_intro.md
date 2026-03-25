---
title: "1차시 - Act Operator와 AI 에이전트 자동화"
description: "Act Operator가 무엇이고, 왜 명령어 4개로 프로덕션 AI 워크플로우를 만들 수 있는지 이해한다."
order: 1
duration: "3분"
animation_sequence:
  - fade_in: hero_title
  - slide_up: problem_statement
  - morph: four_commands_table
  - zoom_in: act_vs_cast_diagram
  - fade_in: checklist
---

# Act Operator와 AI 에이전트 자동화

## 🎯 Topic

> **핵심 키워드**: `스캐폴딩(Scaffolding)`, `LangGraph 프로젝트 자동 생성`

AI 에이전트를 만들 때, 코드를 밑바닥부터 짜는 대신
**명령어 4개**로 프로덕션 수준의 프로젝트 구조를 자동 생성하는 도구.

---

## 💡 Concept

### 문제: AI 에이전트 개발의 현실

```
"챗봇 하나 만들려고 했는데..."

├── 폴더 구조는 어떻게 잡지?
├── 상태 관리는? 메모리는?
├── 도구(Tool) 연동은 어디에 넣지?
├── 테스트는 어떻게 하지?
└── 팀원이 코드를 이해할 수 있을까?
```

> 매번 처음부터 설계하면 **구조가 제각각**이고, **유지보수가 어렵다.**

### 해결: Act Operator

Act Operator는 **건축의 설계도면**과 같다.

```
건축가가 집을 지을 때           개발자가 AI 에이전트를 만들 때
─────────────────────         ─────────────────────────────
설계도면 → 골조 → 인테리어     act new → 코드 구현 → 배포
         ↑                            ↑
    표준화된 구조                Act Operator가 생성하는 구조
```

### 명령어 4개로 끝나는 워크플로우

| 순서 | 명령어 | 역할 |
|:---:|---|---|
| 1 | `act new` | 프로젝트 뼈대 생성 (폴더 + 모듈 + AI 스킬) |
| 2 | `uv sync` | 의존성 설치 및 가상환경 동기화 |
| 3 | `act cast` | 새 워크플로우(Cast) 추가 |
| 4 | `langgraph dev` | 개발 서버 실행 + 시각적 디버깅 |

### Act와 Cast — 핵심 구조

```
🎬 Act = 영화 한 편 (전체 프로젝트, 모노레포)
   🎭 Cast = 배우 (개별 워크플로우, 독립 패키지)

예시:
   Act: "고객 서비스 시스템"
   ├── Cast 1: 챗봇
   ├── Cast 2: 이메일 자동화 봇     ← 오늘 만들 것
   └── Cast 3: 티켓 분류기
```

---

## 🚀 Example

### `act new` 한 번으로 생성되는 프로젝트 구조

```bash
uvx --from act-operator act new
# → Act 이름: email-assistant
# → Cast 이름: email-bot
```

```
email-assistant/               ← Act (모노레포)
├── casts/
│   └── email_bot/             ← Cast (워크플로우)
│       ├── graph.py           ← 🟠 그래프 조립 (진입점)
│       └── modules/
│           ├── state.py       ← 🔵 상태 스키마
│           ├── nodes.py       ← 🔵 비즈니스 로직
│           ├── tools.py       ← ⚫ 외부 도구 (이메일 전송 등)
│           ├── middlewares.py  ← ⚫ 안전장치 (HITL, PII 등)
│           └── ...
├── langgraph.json             ← LangGraph 등록
└── .env                       ← API 키 설정
```

> **핵심 3파일**: `state.py` → `nodes.py` → `graph.py` 만 있으면 동작한다.

---

## ✅ Checklist

- [ ] Act Operator가 "코드를 짜주는 도구"가 아니라 "구조를 생성하는 도구"임을 이해했는가?
- [ ] Act(모노레포)와 Cast(개별 워크플로우)의 차이를 설명할 수 있는가?
- [ ] 명령어 4개(`act new`, `uv sync`, `act cast`, `langgraph dev`)의 역할을 구분할 수 있는가?
- [ ] 생성된 폴더 구조에서 `state.py`, `nodes.py`, `graph.py`의 역할을 알고 있는가?
