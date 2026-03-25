import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt

from casts.base_node import BaseNode
from casts.email_bot.modules.models import get_chat_model
from casts.email_bot.modules.prompts import SYSTEM_PROMPT
from casts.email_bot.modules.tools import send_email_via_gmail


class DraftEmailNode(BaseNode):
    """사용자 요청을 받아 이메일 초안을 작성하는 노드."""

    def __init__(self):
        super().__init__()
        self.model = get_chat_model()

    def execute(self, state):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=state["query"]),
        ]
        response = self.model.invoke(messages)
        content = response.content

        email_to = "unknown@example.com"
        email_subject = "제목 없음"
        email_body = content

        to_match = re.search(r"수신자:\s*(.+)", content)
        if to_match:
            email_to = to_match.group(1).strip()

        subj_match = re.search(r"제목:\s*(.+)", content)
        if subj_match:
            email_subject = subj_match.group(1).strip()

        body_match = re.search(r"본문:\s*\n([\s\S]+)", content)
        if body_match:
            email_body = body_match.group(1).strip()

        return {
            "messages": [AIMessage(content=content)],
            "email_to": email_to,
            "email_subject": email_subject,
            "email_body": email_body,
            "result": content,
        }


class ReviewEmailNode(BaseNode):
    """Human-in-the-Loop: 이메일 전송 전 사용자 승인을 요청하는 노드."""

    def __init__(self):
        super().__init__()

    def execute(self, state):
        review_info = (
            f"=== 이메일 승인 요청 ===\n"
            f"수신자: {state['email_to']}\n"
            f"제목: {state['email_subject']}\n"
            f"본문:\n{state['email_body']}\n"
            f"========================\n"
            f"승인하려면 'yes', 거부하려면 'no'를 입력하세요."
        )

        # interrupt()로 그래프 실행을 중단하고 사용자 입력을 기다립니다
        decision = interrupt(review_info)

        if decision.lower() in ("yes", "y", "승인", "확인"):
            return {"messages": [AIMessage(content="사용자가 이메일 전송을 승인했습니다.")]}
        else:
            return {
                "messages": [AIMessage(content=f"사용자가 이메일 전송을 거부했습니다. 사유: {decision}")],
                "result": f"이메일 전송이 거부되었습니다. 사유: {decision}",
            }


class SendEmailNode(BaseNode):
    """승인된 이메일을 실제로 Gmail로 전송하는 노드."""

    def __init__(self):
        super().__init__()

    def execute(self, state):
        # 마지막 메시지가 거부였으면 전송하지 않음
        last_msg = state["messages"][-1]
        if "거부" in last_msg.content:
            return {"result": "이메일 전송이 취소되었습니다."}

        try:
            result = send_email_via_gmail(
                to=state["email_to"],
                subject=state["email_subject"],
                body=state["email_body"],
            )
            return {
                "messages": [AIMessage(content=result)],
                "result": result,
            }
        except Exception as e:
            error_msg = f"이메일 전송 실패: {e}"
            return {
                "messages": [AIMessage(content=error_msg)],
                "result": error_msg,
            }
