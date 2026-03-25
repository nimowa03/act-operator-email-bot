from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from casts.base_graph import BaseGraph
from casts.email_bot.modules.nodes import DraftEmailNode, ReviewEmailNode, SendEmailNode
from casts.email_bot.modules.state import InputState, OutputState, State


class EmailBotGraph(BaseGraph):

    def __init__(self) -> None:
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        builder = StateGraph(
            self.state, input_schema=self.input, output_schema=self.output
        )

        # 노드 등록
        builder.add_node("draft_email", DraftEmailNode())
        builder.add_node("review_email", ReviewEmailNode())
        builder.add_node("send_email", SendEmailNode())

        # 흐름: 초안 작성 → 사용자 승인(HITL) → 이메일 전송
        builder.add_edge(START, "draft_email")
        builder.add_edge("draft_email", "review_email")
        builder.add_edge("review_email", "send_email")
        builder.add_edge("send_email", END)

        # Checkpointer: HITL interrupt 후 재개를 위해 필수
        graph = builder.compile(checkpointer=InMemorySaver())
        graph.name = self.name
        return graph


email_bot_graph = EmailBotGraph()
