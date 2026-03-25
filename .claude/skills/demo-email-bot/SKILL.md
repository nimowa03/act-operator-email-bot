---
name: demo-email-bot
description: "HITL 이메일 봇 라이브 시연을 오케스트레이션합니다. '/demo', '시연 시작', '@demo-email-bot'으로 트리거."
version: "2026.03.25"
author: charlee
allowed-tools:
  - Bash(uv run python *)
  - Bash(open *)
  - Bash(cd *)
  - Read
  - AskUserQuestion
---

# HITL 이메일 봇 시연 스킬

이 스킬은 10~15분 발표에서 HITL 이메일 봇의 **슬라이드 설명 + 라이브 시연 + LangSmith 추적**을 한 호흡으로 진행합니다.

## 언제 사용하나

- 라이브 발표/시연을 할 때
- Human-in-the-Loop 패턴을 보여줄 때
- LangGraph Studio나 LangSmith를 시연할 때

## 언제 사용하지 않나

- 코드 구현 → `@developing-cast` 사용
- 테스트 작성 → `@testing-cast` 사용
- 아키텍처 설계 → `@architecting-act` 사용

---

## 모드 감지

사용자 요청에 따라 모드를 결정합니다:

| 키워드 | 모드 | 설명 |
|---|---|---|
| "슬라이드", "발표 시작" | 슬라이드만 | 브라우저에서 발표자료 열기 |
| "/demo", "시연", "데모" | 시연만 | 터미널에서 이메일 봇 실행 |
| "/demo full", "전체 시연" | 전체 | 슬라이드 → 시연 → LangSmith |

---

## 사전 점검

어떤 모드든 시작 전에 확인합니다:

1. `.env` 파일 존재 여부 확인 (값은 표시하지 않음)
2. 그래프 import 테스트:
   ```bash
   cd /Users/charlee/Desktop/email-assistant && uv run python -c "from casts.email_bot.graph import email_bot_graph; print('OK')"
   ```
3. 문제가 있으면 해결 방법을 안내합니다.

---

## 슬라이드 모드

슬라이드를 브라우저에서 엽니다:

```bash
open https://nimowa03.github.io/act-operator-email-bot/
```

### 슬라이드 가이드 (12장)

| 슬라이드 | 제목 | 시간 | 발표 포인트 |
|---|---|---|---|
| 1 | 타이틀 | 15초 | "오늘은 AI가 이메일을 보내기 전에 사람에게 물어보는 시스템을 만들어봅니다" |
| 2 | AI 에이전트란 | 40초 | "일반 챗봇은 답만 하지만, AI 에이전트는 실제로 행동합니다" |
| 3 | 문제 제기 | 40초 | "근데 마음대로 행동하면 위험하죠. 잘못된 이메일이 나가면 되돌릴 수 없습니다" |
| 4 | LangGraph | 40초 | "이런 AI 워크플로우를 설계하는 도구가 LangGraph입니다" |
| 5 | Act Operator | 40초 | "이 프로젝트 구조를 명령어 하나로 생성해주는 게 Act Operator입니다" |
| 6 | HITL 개념 | 60초 | "핵심은 여기입니다. AI가 초안을 쓰고 멈추고 사람이 결정합니다" |
| 7 | 파일 구조 | 30초 | "파일 5개로 구성됩니다. 이제 실제로 돌려봅시다" |
| 8 | 시연 예고 | — | **여기서 터미널로 전환** |
| 9-10 | Studio/LangSmith | — | 시연 후 보여줌 |
| 11 | 활용 사례 | 40초 | "이메일 외에도 결제, DB, 고객 응대 등에 활용 가능합니다" |
| 12 | 마무리 | 20초 | "AI가 판단하고, 사람이 최종 결정합니다" |

슬라이드 7번까지 설명한 후, AskUserQuestion으로 물어봅니다:

> "슬라이드 설명이 끝났습니다. 터미널에서 라이브 시연을 시작할까요?"

---

## 시연 모드

### Step 1: 이메일 요청 받기

AskUserQuestion으로 물어봅니다:

> "어떤 이메일을 보낼까요? 자연어로 설명해주세요. (예: 'makegrowth101@gmail.com에게 프로젝트 진행 상황 메일 보내줘')"

### Step 2: demo.py 실행

```bash
cd /Users/charlee/Desktop/email-assistant && uv run python demo.py "<사용자 요청>"
```

이 스크립트가 자동으로 처리하는 것:
1. 환경 변수 점검 (테이블 표시)
2. AI가 이메일 초안 작성 (스피너 표시)
3. 초안을 시각적으로 표시 (노란색 패널)
4. **"⏸️ 그래프 실행이 멈췄습니다!"** 배너 표시
5. 발표자에게 승인/거부 입력 요청
6. 승인 시 실제 Gmail 전송
7. 다음 단계 안내

### Step 3: 후속 안내

시연 완료 후 발표자에게 안내합니다:

1. **Gmail 확인**: "Gmail 탭을 열어서 이메일이 도착했는지 보여주세요"
2. **LangSmith** (선택):
   - 브라우저에서 https://smith.langchain.com 열기
   - email-bot 프로젝트 → 최신 Trace 클릭
   - 3개 노드(초안/승인/전송)의 입출력 데이터 보여주기
3. **LangGraph Studio** (선택):
   - `uv run langgraph dev` 실행 후 localhost에서 그래프 시각화

---

## 전체 모드

1. 슬라이드 모드 실행
2. 슬라이드 7번 후 시연 모드로 전환
3. 시연 완료 후 슬라이드 11~12번으로 마무리 안내

---

## 문제 해결

| 증상 | 해결 |
|---|---|
| ModuleNotFoundError | `uv sync` 실행 |
| Gmail 인증 실패 | .env의 GMAIL_APP_PASSWORD가 앱 비밀번호(16자리)인지 확인 |
| LangSmith에 trace 안 뜸 | .env에 LANGSMITH_TRACING=true 확인 |
| OpenAI 오류 | OPENAI_API_KEY 유효성 및 크레딧 확인 |
