---
title: "2차시 - Human-in-the-Loop 이메일 봇의 작동 원리"
description: "AI가 행동하기 전에 사람이 승인하는 HITL 패턴의 원리와, 이메일 봇에서의 구체적인 구현 구조를 이해한다."
order: 2
duration: "5분"
animation_sequence:
  - fade_in: hero_title
  - typewriter: problem_scenario
  - step_by_step: hitl_flow_diagram
  - morph: interrupt_resume_cycle
  - code_highlight: node_by_node
  - slide_up: module_mapping_table
  - fade_in: checklist
---

# Human-in-the-Loop 이메일 봇의 작동 원리

## 🎯 Topic

> **핵심 키워드**: `Human-in-the-Loop (HITL)`, `interrupt / resume`, `Checkpointer`

AI 에이전트가 **민감한 행동(이메일 전송)을 실행하기 전에**,
반드시 사람의 승인을 받도록 강제하는 안전장치 패턴.

---

## 💡 Concept

### 왜 HITL이 필요한가?

```
시나리오: AI 비서에게 "김팀장에게 회의록 보내줘"라고 요청

❌ HITL 없이                        ✅ HITL 적용
────────────────                   ────────────────
AI가 즉시 전송                      AI가 초안 작성
  ↓                                  ↓
잘못된 주소로 발송됨                 ⏸️ "이 내용으로 보낼까요?"
  ↓                                  ↓
기밀 정보 유출 🚨                   사람이 확인 후 승인 ✅
  ↓                                  ↓
되돌릴 수 없음                      안전하게 전송됨
```

> **HITL의 본질**: AI는 **판단**하고, 사람은 **최종 결정**한다.

### 핵심 메커니즘: `interrupt()` → 중단 → `resume` → 재개

HITL은 LangGraph의 **interrupt/resume** 메커니즘으로 구현된다.

```
             ┌─────────────────────────────────────────┐
             │           그래프 실행 흐름               │
             │                                         │
  입력 ──▶  │  [draft_email] ──▶ [review_email] ──▶ [send_email]  ──▶ 완료
             │                        │                │
             │                   interrupt()           │
             │                   ⏸️ 실행 중단          │
             │                        │                │
             └────────────────────────┼────────────────┘
                                      │
                              사용자 결정 대기
                                      │
                         ┌────────────┼────────────┐
                         │            │            │
                      "yes"        "edit"        "no"
                     승인 ✅      수정 ✏️       거부 ❌
                         │            │            │
                      resume       resume       resume
                         │            │            │
                    이메일 전송   수정 후 전송   전송 취소
```

### 왜 Checkpointer가 필수인가?

```
interrupt()로 그래프가 중단되면:
  → 현재 상태(이메일 초안, 수신자, 제목...)를 어딘가에 저장해야 함
  → resume할 때 저장된 상태에서 이어서 실행해야 함

Checkpointer = 게임의 "세이브 포인트" 💾
  → InMemorySaver: 메모리에 저장 (개발/시연용)
  → PostgresSaver: DB에 저장 (프로덕션용)
```

---

## 🚀 Example

### 이메일 봇의 3개 노드 — 각각의 역할

#### 노드 1: `DraftEmailNode` — AI가 이메일 초안 작성

```python
class DraftEmailNode(BaseNode):
    """사용자 요청 → OpenAI가 이메일 초안 생성"""

    def execute(self, state):
        # 사용자의 자연어 요청을 LLM에 전달
        messages = [
            SystemMessage(content="당신은 이메일 작성 전문 비서입니다."),
            HumanMessage(content=state["query"]),
        ]
        response = self.model.invoke(messages)

        # LLM 응답에서 수신자, 제목, 본문을 파싱
        return {
            "email_to": "추출된 이메일 주소",
            "email_subject": "추출된 제목",
            "email_body": "추출된 본문",
        }
```

#### 노드 2: `ReviewEmailNode` — ⏸️ HITL 중단 지점

```python
class ReviewEmailNode(BaseNode):
    """이메일 전송 전 사용자 승인을 요청하는 노드"""

    def execute(self, state):
        review_info = (
            f"수신자: {state['email_to']}\n"
            f"제목: {state['email_subject']}\n"
            f"본문:\n{state['email_body']}\n"
            f"승인하려면 'yes', 거부하려면 'no'"
        )

        # ⭐ 여기서 그래프 실행이 멈춘다
        decision = interrupt(review_info)

        # 사용자가 resume하면 여기부터 이어서 실행
        if decision == "yes":
            return {"messages": [AIMessage("승인됨")]}
        else:
            return {"messages": [AIMessage("거부됨")]}
```

> `interrupt(review_info)` — 이 한 줄이 HITL의 핵심이다.
> 그래프 실행을 **완전히 멈추고**, 사용자의 입력을 기다린다.

#### 노드 3: `SendEmailNode` — 실제 Gmail 전송

```python
class SendEmailNode(BaseNode):
    """승인된 이메일을 Gmail SMTP로 전송"""

    def execute(self, state):
        result = send_email_via_gmail(
            to=state["email_to"],
            subject=state["email_subject"],
            body=state["email_body"],
        )
        return {"result": result}
```

### 그래프 조립 — `graph.py`

```python
# 노드 등록
builder.add_node("draft_email", DraftEmailNode())
builder.add_node("review_email", ReviewEmailNode())   # ← HITL 지점
builder.add_node("send_email", SendEmailNode())

# 흐름 연결: 초안 → 승인 → 전송
builder.add_edge(START, "draft_email")
builder.add_edge("draft_email", "review_email")
builder.add_edge("review_email", "send_email")
builder.add_edge("send_email", END)

# ⭐ Checkpointer 필수 — interrupt/resume을 위한 상태 저장
graph = builder.compile(checkpointer=InMemorySaver())
```

### 모듈 ↔ 역할 매핑

| 파일 | 역할 | 핵심 코드 |
|---|---|---|
| `state.py` | 이메일 데이터 스키마 정의 | `email_to`, `email_subject`, `email_body` |
| `nodes.py` | 3개 노드 (초안/승인/전송) | `DraftEmailNode`, `ReviewEmailNode`, `SendEmailNode` |
| `tools.py` | Gmail SMTP 전송 함수 | `send_email_via_gmail()` |
| `models.py` | OpenAI GPT-4o-mini 설정 | `ChatOpenAI(model="gpt-4o-mini")` |
| `graph.py` | 노드 연결 + Checkpointer | `builder.compile(checkpointer=InMemorySaver())` |

---

## ✅ Checklist

- [ ] HITL이 "AI의 행동 전에 사람이 승인하는 패턴"임을 한 문장으로 설명할 수 있는가?
- [ ] `interrupt()`가 그래프 실행을 멈추고, `resume`으로 재개되는 흐름을 이해하는가?
- [ ] Checkpointer가 왜 필수인지 (중단된 상태를 저장해야 재개 가능) 설명할 수 있는가?
- [ ] 3개 노드(`DraftEmail` → `ReviewEmail` → `SendEmail`)의 역할을 구분할 수 있는가?
- [ ] `review_email` 노드 안의 `interrupt()` 한 줄이 HITL의 핵심임을 이해하는가?
