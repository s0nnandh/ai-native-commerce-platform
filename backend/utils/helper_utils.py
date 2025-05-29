from itertools import zip_longest

def get_message_summary(
        user_messages: list[str],
        ai_messages: list[str] | None = None
):
    messages_summary_parts = []
    for user_msg, ai_msg in zip_longest(user_messages, ai_messages or [], fillvalue=""):
        if user_msg:
            messages_summary_parts.append(f"User: {user_msg}")
        if ai_msg:
            messages_summary_parts.append(f"Assistant: {ai_msg}")

    return "\n".join(messages_summary_parts)