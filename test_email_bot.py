"""이메일 봇 전체 흐름 테스트: 초안 작성 → HITL 승인 → 실제 전송"""
from dotenv import load_dotenv
load_dotenv()

from langgraph.types import Command
from casts.email_bot.graph import email_bot_graph

# 그래프를 한 번만 컴파일 (InMemorySaver 공유)
graph = email_bot_graph()
config = {"configurable": {"thread_id": "demo-1"}}

# === Step 1: 이메일 작성 요청 → review_email에서 interrupt ===
print("=" * 50)
print("Step 1: 이메일 작성 요청")
print("=" * 50)

result = graph.invoke(
    {"query": "nimowa03@gmail.com 에게 테스트 이메일을 보내줘. 내용은 Act Operator 이메일 봇 HITL 시연 테스트입니다."},
    config=config,
)

# interrupt 상태 확인
state = graph.get_state(config)
print(f"다음 노드: {state.next}")
if state.tasks:
    for task in state.tasks:
        if hasattr(task, "interrupts") and task.interrupts:
            for intr in task.interrupts:
                print(f"\n{intr.value}")

# === Step 2: 사용자 승인 → 이메일 실제 전송 ===
print("\n" + "=" * 50)
print("Step 2: 사용자가 'yes' 입력 → 이메일 전송")
print("=" * 50)

result = graph.invoke(Command(resume="yes"), config=config)
print(f"\n최종 결과: {result['result']}")
