import tiktoken

def get_token_count(text: str, model: str) -> int:
    model = model.lower()

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

if __name__ == "__main__":
    content = "Hello world!"

    # 测试 OpenAI
    print(f"GPT-4o: {get_token_count(content, 'gpt-4o')}")

    # 测试 Claude
    print(f"Claude-3: {get_token_count(content, 'claude-3-opus-20240229')}")
