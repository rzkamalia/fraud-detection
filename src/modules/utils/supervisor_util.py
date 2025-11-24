from langchain_core.documents import Document


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


def format_pdf_search_results(responses: list[Document]) -> str:
    """Format the PDF search responses for inclusion in the prompt.

    Args:
        responses (list[Document]): List of search results from the PDF tool.
    Returns:
        str: Formatted PDF search results.
    """
    if not responses:
        return "No relevant information found in the PDF contents."

    formatted_results = ""
    for result in responses:
        content = result.page_content
        formatted_results += f"{content}\n"

    return formatted_results