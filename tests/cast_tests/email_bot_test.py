"""Test the Email Bot graph.

Official document URL:
    https://docs.langchain.com/oss/python/langgraph/test"""

from __future__ import annotations

from casts.email_bot.graph import email_bot_graph


def test_graph_produces_message() -> None:
    graph = email_bot_graph()

    # 최소 상태로 그래프 실행
    result = graph.invoke({"query": "I'm joining Act"})

    # SampleNode가 message 키를 생성하는지 확인
    assert "messages" in result
    assert result["messages"] == "Welcome to the Act!"
