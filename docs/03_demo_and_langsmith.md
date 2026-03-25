---
title: "3차시 - 라이브 시연: 이메일 전송과 LangSmith 추적"
description: "이메일 봇의 실제 실행 과정을 시연하고, LangSmith에서 에이전트의 모든 행동을 추적하는 방법을 배운다."
order: 3
duration: "5~7분"
animation_sequence:
  - fade_in: hero_title
  - step_by_step: demo_terminal_output
  - highlight: interrupt_moment
  - celebration: email_sent
  - transition: langsmith_dashboard
  - zoom_in: trace_detail
  - slide_up: use_cases
  - fade_in: checklist
---

# 라이브 시연: 이메일 전송과 LangSmith 추적

## 🎯 Topic

> **핵심 키워드**: `실행 흐름 시연`, `LangSmith Trace`, `관측 가능성(Observability)`

실제로 이메일이 전송되는 과정을 단계별로 확인하고,
LangSmith에서 에이전트의 **모든 판단 과정을 추적**하는 방법.

---

## 💡 Concept

### 시연의 두 가지 축

```
축 1: 터미널 (실행)                축 2: LangSmith (관측)
──────────────────                ──────────────────────
코드가 실제로 돌아가는 모습        각 노드의 입출력을 시각적으로 추적
"무엇이 일어나는가"               "왜, 어떻게 일어났는가"
```

### LangSmith란?

> LangSmith = AI 에이전트의 **블랙박스 레코더** 🛫

비행기에 블랙박스가 있듯이, AI 에이전트에도 모든 행동을 기록하는 장치가 필요하다.

```
에이전트가 실행될 때 자동으로 기록되는 것들:

📍 Trace (전체 실행 흐름)
├── 🔵 draft_email 노드
│   ├── 입력: "김팀장에게 회의록 보내줘"
│   ├── LLM 호출: GPT-4o-mini에 보낸 프롬프트
│   ├── LLM 응답: 생성된 이메일 초안 전문
│   └── 출력: {email_to, email_subject, email_body}
│
├── 🟡 review_email 노드
│   ├── interrupt 발생! ⏸️
│   ├── 사용자 결정 대기...
│   └── resume("yes") → 승인
│
└── 🟢 send_email 노드
    ├── Gmail SMTP 연결
    └── 전송 완료 ✅
```

### `.env` 설정 3줄이면 자동 추적

```bash
LANGSMITH_TRACING=true              # 추적 ON
LANGSMITH_PROJECT=email-bot         # 프로젝트 이름
LANGSMITH_API_KEY=lsv2_pt_xxx...   # API 키
```

> 코드를 한 줄도 수정하지 않아도, `.env` 설정만으로 모든 실행이 LangSmith에 기록된다.

---

## 🚀 Example

### 시연 Step 1: 이메일 작성 요청 → HITL 중단

```python
graph = email_bot_graph()
config = {"configurable": {"thread_id": "demo-1"}}

# 사용자 요청 전달
result = graph.invoke(
    {"query": "makegrowth101@gmail.com에게 테스트 이메일 보내줘"},
    config=config,
)
```

**터미널 출력:**

```
=== 이메일 승인 요청 ===
수신자: makegrowth101@gmail.com
제목: 테스트 이메일
본문:
안녕하세요,
테스트 이메일을 보내드립니다.
감사합니다.
========================
승인하려면 'yes', 거부하려면 'no'를 입력하세요.
```

> ⏸️ **여기서 그래프가 멈춘다.** `review_email` 노드의 `interrupt()`가 실행됨.
> 사용자가 결정할 때까지 **영원히 기다린다.**

### 시연 Step 2: 승인 → 실제 이메일 전송

```python
from langgraph.types import Command

# 사용자가 "yes" 입력 → 그래프 재개
result = graph.invoke(Command(resume="yes"), config=config)
```

**터미널 출력:**

```
최종 결과: 이메일 전송 완료: makegrowth101@gmail.com
```

> ✅ **실제로 Gmail에 이메일이 도착한다.** 받은편지함에서 확인 가능.

### 시연 Step 3: LangSmith에서 Trace 확인

**smith.langchain.com → email-bot 프로젝트 → 최신 Trace 클릭**

```
Trace 상세 화면에서 확인할 수 있는 것:

┌─────────────────────────────────────────────┐
│ 📍 Run: EmailBotGraph                       │
│ Duration: 3.2s                              │
│                                             │
│ ├── draft_email (1.8s)                      │
│ │   ├── ChatOpenAI                          │
│ │   │   ├── Input:  시스템 프롬프트 + 사용자 요청│
│ │   │   ├── Output: 이메일 초안 전문         │
│ │   │   ├── Tokens: 입력 180 / 출력 95      │
│ │   │   └── Cost:   $0.0002                 │
│ │   └── State Update: email_to, subject...  │
│ │                                           │
│ ├── review_email (대기시간)                  │
│ │   ├── ⏸️ Interrupt 발생                   │
│ │   └── ▶️ Resume: "yes"                    │
│ │                                           │
│ └── send_email (0.4s)                       │
│     └── Result: "이메일 전송 완료"           │
└─────────────────────────────────────────────┘
```

> 각 노드를 클릭하면 **입력값, LLM 프롬프트, 응답, 토큰 사용량, 비용**까지 전부 볼 수 있다.

### 이 기술로 뭘 할 수 있는가?

| 활용 사례 | HITL 적용 지점 | 비즈니스 가치 |
|---|---|---|
| **이메일 자동화** | 전송 전 승인 | 오발송 방지, 컴플라이언스 |
| **결제 처리 봇** | 10만원 이상 결제 시 승인 | 금융 사고 예방 |
| **DB 수정 봇** | DELETE/UPDATE 쿼리 전 승인 | 데이터 손실 방지 |
| **고객 응대 봇** | 민감한 답변 전 검토 | 브랜드 리스크 관리 |
| **보고서 발송 봇** | 주간 보고서 검토 후 발송 | 품질 보증 |
| **채용 알림 봇** | 합격/불합격 통보 전 승인 | HR 실수 방지 |

> **공통 원칙**: AI가 판단하고, 사람이 최종 결정한다.
> 자동화의 **효율성**과 사람의 **판단력**을 결합하는 것이 HITL의 핵심 가치.

---

## ✅ Checklist

- [ ] 이메일 봇 시연에서 "어디서 멈추고, 어디서 이어지는지" 흐름을 설명할 수 있는가?
- [ ] `interrupt()`로 멈춘 그래프를 `Command(resume="yes")`로 재개하는 코드를 이해하는가?
- [ ] LangSmith에서 Trace를 열어 각 노드의 입출력을 확인하는 방법을 아는가?
- [ ] `.env` 설정 3줄만으로 추적이 활성화됨을 설명할 수 있는가?
- [ ] HITL 패턴을 이메일 외의 다른 사례(결제, DB, 고객 응대)에 적용할 수 있는 아이디어가 있는가?
