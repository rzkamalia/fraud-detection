def format_conversation_history(messages: list) -> str:
    """Format the conversation history from a list of messages.

    Args:
        messages (list): List of messages in the conversation.

    Returns:
        str: Formatted conversation history.
    """
    formatted = []
    for msg in messages:
        if msg.content and msg.__class__.__name__ in ["HumanMessage", "AIMessage"]:
            role = "## User" if msg.__class__.__name__ == "HumanMessage" else "## AI Assistant"
            formatted.append(f"{role}\n{msg.content}")

    return "\n".join(formatted)
