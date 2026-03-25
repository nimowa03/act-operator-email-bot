def route_after_review(state):
    """사용자 승인 결과에 따라 라우팅합니다."""
    if state.get("email_approved"):
        return "send_email"
    return "draft_email"
