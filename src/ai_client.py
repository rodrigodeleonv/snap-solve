from .config import config
from .screenshot import to_base64


def analyze(png_bytes: bytes) -> str:
    """Send a screenshot to the configured AI provider and return the response."""
    if config.provider == "openai":
        return _openai(png_bytes)
    if config.provider == "groq":
        return _groq(png_bytes)
    return _claude(png_bytes)


def _claude(png_bytes: bytes) -> str:
    import anthropic
    from anthropic.types import TextBlock

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.model,
        max_tokens=config.MAX_TOKENS,
        system=config.SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": to_base64(png_bytes),
                        },
                    },
                    {
                        "type": "text",
                        "text": "Please analyze this screenshot and provide your response.",
                    },
                ],
            }
        ],
    )
    block = message.content[0]
    if not isinstance(block, TextBlock):
        raise ValueError(f"Unexpected response block type from Claude: {type(block)}")
    return block.text


def _openai(png_bytes: bytes) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    b64 = to_base64(png_bytes)
    response = client.chat.completions.create(
        model=config.model,
        max_tokens=config.MAX_TOKENS,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                    {
                        "type": "text",
                        "text": "Please analyze this screenshot and provide your response.",
                    },
                ],
            },
        ],
    )
    return response.choices[0].message.content or ""


def _groq(png_bytes: bytes) -> str:
    from groq import Groq

    client = Groq(api_key=config.GROQ_API_KEY)
    b64 = to_base64(png_bytes)
    response = client.chat.completions.create(
        model=config.model,
        max_tokens=config.MAX_TOKENS,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                    {
                        "type": "text",
                        "text": "Please analyze this screenshot and provide your response.",
                    },
                ],
            },
        ],
    )
    return response.choices[0].message.content or ""
