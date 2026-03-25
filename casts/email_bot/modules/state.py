from langgraph.graph import MessagesState
from typing_extensions import TypedDict


class InputState(TypedDict):
    query: str


class OutputState(TypedDict):
    result: str


class State(MessagesState):
    query: str
    result: str
    email_to: str
    email_subject: str
    email_body: str
    email_approved: bool
