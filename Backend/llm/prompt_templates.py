from typing import List, Dict


def get_finance_prompt(messages: List[Dict[str, str]]) -> str:
    """
    Format messages into the prompt template expected by finance-chat

    Expected format:
    [INST] <<SYS>>
    You are a financial expert. You are helpful and harmless.
    <</SYS>>

    {user_input} [/INST]
    """
    system_message = "You are a financial expert assistant named Fenny. You provide accurate, helpful information about finance, investing, and financial documents. Be concise and professional."

    # Start with system message
    prompt = f"[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n"

    # Process messages
    for i, msg in enumerate(messages):
        if msg["role"] == "user":
            # User message
            prompt += f"{msg['content']} [/INST]\n"
        elif msg["role"] == "assistant":
            # Assistant response
            prompt += f"{msg['content']}\n"
            # Add separator for next user message if not last message
            if i < len(messages) - 1:
                prompt += "<s>[INST] "

    return prompt
