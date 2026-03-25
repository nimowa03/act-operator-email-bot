"""HITL 이메일 봇 라이브 시연 스크립트.

사용법:
    uv run python demo.py                                  # 대화형
    uv run python demo.py "김팀장에게 회의록 보내줘"         # 요청 직접 전달
"""
from __future__ import annotations

import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from langgraph.types import Command

from casts.email_bot.graph import email_bot_graph

console = Console()


def check_env() -> bool:
    keys = {
        "OPENAI_API_KEY": "OpenAI API 키",
        "GMAIL_ADDRESS": "Gmail 주소",
        "GMAIL_APP_PASSWORD": "Gmail 앱 비밀번호",
        "LANGSMITH_API_KEY": "LangSmith API 키",
    }
    t = Table(title="환경 변수 점검", box=box.ROUNDED, show_lines=False)
    t.add_column("항목", style="bold")
    t.add_column("상태", justify="center")
    ok = True
    for k, label in keys.items():
        if os.environ.get(k):
            t.add_row(label, "[green]✅ 설정됨[/]")
        else:
            t.add_row(label, "[red]❌ 없음[/]")
            ok = False
    console.print(t)
    console.print()
    return ok


def get_query() -> str:
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
    else:
        q = console.input("[bold cyan]어떤 이메일을 보낼까요?[/] → ")
    console.print()
    console.print(Panel(q, title="[bold]사용자 요청[/]", border_style="cyan", padding=(0, 2)))
    console.print()
    return q


def show_draft(values: dict) -> None:
    t = Table(box=box.HEAVY_EDGE, show_header=False, padding=(0, 2))
    t.add_column("", style="bold", width=8)
    t.add_column("")
    t.add_row("[yellow]수신자[/]", values.get("email_to", ""))
    t.add_row("[yellow]제목[/]", values.get("email_subject", ""))
    t.add_row("[yellow]본문[/]", values.get("email_body", ""))
    console.print(Panel(
        t,
        title="[bold yellow]📝 AI가 작성한 이메일 초안[/]",
        border_style="yellow",
        padding=(1, 1),
    ))


def show_interrupt() -> None:
    console.print()
    console.print(Panel(
        "[bold yellow]⏸️  그래프 실행이 멈췄습니다![/]\n\n"
        "[dim]ReviewEmailNode 안의[/] [bold]interrupt()[/] [dim]함수가 호출되었습니다.[/]\n"
        "[dim]사람이 승인할 때까지 이메일은 전송되지 않습니다.[/]",
        title="[bold yellow]Human-in-the-Loop[/]",
        border_style="yellow",
        padding=(1, 2),
    ))
    console.print()


def get_approval() -> str:
    return console.input("[bold yellow]이 이메일을 승인하시겠습니까?[/] [green]yes[/] / [red]no[/] → ")


def show_result(result_text: str, approved: bool) -> None:
    console.print()
    if approved and "완료" in result_text:
        console.print(Panel(
            f"[bold green]✅ {result_text}[/]\n\n[dim]Gmail 받은편지함을 확인하세요![/]",
            title="[bold green]전송 성공[/]",
            border_style="green",
            padding=(1, 2),
        ))
    elif not approved:
        console.print(Panel(
            "[bold yellow]📭 이메일 전송이 취소되었습니다.[/]",
            title="[bold yellow]전송 취소[/]",
            border_style="yellow",
            padding=(1, 2),
        ))
    else:
        console.print(Panel(
            f"[bold red]❌ {result_text}[/]",
            title="[bold red]오류[/]",
            border_style="red",
            padding=(1, 2),
        ))


def show_next_steps() -> None:
    console.print()
    console.print(Panel(
        "[bold]다음 확인 사항:[/]\n\n"
        "  1. 📧  Gmail 받은편지함에서 이메일 도착 확인\n"
        "  2. 📊  [link=https://smith.langchain.com]smith.langchain.com[/link] → email-bot 프로젝트 → 최신 Trace 확인\n"
        "  3. 🖥️  [dim]uv run langgraph dev[/dim] → LangGraph Studio에서 그래프 시각화",
        title="[bold cyan]What's Next[/]",
        border_style="cyan",
        padding=(1, 2),
    ))


def main() -> None:
    console.clear()
    console.print(Panel(
        "[bold]Act Operator — HITL 이메일 봇 시연[/]\n"
        "[dim]Human-in-the-Loop: AI가 판단하고, 사람이 최종 결정한다[/]",
        border_style="bright_cyan",
        padding=(1, 3),
    ))
    console.print()

    if not check_env():
        console.print("[bold red].env 파일에 필요한 환경 변수가 없습니다.[/]")
        sys.exit(1)

    query = get_query()

    graph = email_bot_graph()
    thread_id = f"demo-{int(time.time())}"
    config = {"configurable": {"thread_id": thread_id}}

    # Step 1: 이메일 초안 작성 → interrupt에서 멈춤
    with console.status("[bold cyan]AI가 이메일을 작성하고 있습니다...", spinner="dots"):
        graph.invoke({"query": query}, config=config)

    state = graph.get_state(config)
    values = state.values

    show_draft(values)
    show_interrupt()

    decision = get_approval()
    approved = decision.lower() in ("yes", "y", "승인", "확인")

    # Step 2: resume → 전송 또는 취소
    with console.status("[bold cyan]처리 중...", spinner="dots"):
        result = graph.invoke(Command(resume=decision), config=config)

    result_text = result.get("result", "알 수 없는 결과")
    show_result(result_text, approved)
    show_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]시연이 취소되었습니다.[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]오류 발생: {e}[/]")
        sys.exit(1)
