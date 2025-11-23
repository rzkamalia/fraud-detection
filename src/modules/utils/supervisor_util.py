def format_conversation_history(messages: list) -> str:
    """Format the conversation history from a list of messages.

    Args:
        messages (list): List of messages in the conversation.

    Returns:
        str: Formatted conversation history.
    """
    return "\n".join(
        f"""{message["role"]}: {message["content"]}""" for message in messages
    ) if messages else ""