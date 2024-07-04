import anthropic
import logs


def chat_completion(
        system_prompt: str,
        prompt: str,
        model: str,
):
    logs.debug(f"Starting chat completion using {model}")
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ]
            }
        ],
    )
    logs.debug("Finished chat completion")
    return message.content


def tool_completion(
        system_prompt: str,
        prompt: str,
        model: str,
        tools: list[dict],
        tool_override: str = "",
):
    logs.debug("Starting tool completion")
    client = anthropic.Anthropic()

    if tool_override == "any":
        tool_choice = {"type": "any"}
    elif tool_override:
        tool_choice = {"type": "tool", "name": tool_override}
    else:
        tool_choice = {"type": "auto"}

    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ]
            }
        ],
        tools=tools,
        tool_choice=tool_choice,
    )
    if message.stop_reason == "tool_use":
        for response in message.content:
            if response.type == "tool_use":
                logs.debug(f"Tool completion finished with {response.input}")
                return response.input
    else:
        logs.debug(f"Tool completion finished without tool use: {message.content[0].text}")
        return message.content[0].text
