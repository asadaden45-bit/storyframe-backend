def generate_story(prompt: str, style: str = "default") -> str:
    if style == "dark":
        return f"In a dark world, {prompt}. The ending was uncertain."

    if style == "kids":
        return f"Once upon a time, {prompt}. Everyone smiled and felt safe."

    return f"Once upon a time, {prompt}. And they lived happily ever after."
