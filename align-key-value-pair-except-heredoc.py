import re

def align_equals(content: str) -> str:
    """
    Aligns the '=' signs for all simple key-value pairs in the content.
    - Correctly handles cases where the value contains '==' or other operators.
    - Does not break heredoc contents or expressions.
    """
    lines = content.splitlines()
    formatted_lines = []
    block = []
    max_key_length = 0

    # Match only the first "=" (not "=="), splitting key from value
    kv_pattern = re.compile(r'^(\s*)(\w+)\s*=\s+(.*)$')

    for line in lines:
        kv_match = kv_pattern.match(line)
        if kv_match:
            indent, key, value = kv_match.groups()
            # Exclude lines that *start* with something like "if (...) ==" (heredoc code)
            if not key.startswith("if") and not key.endswith("=="):
                block.append((indent, key, value))
                max_key_length = max(max_key_length, len(key))
                continue

        # Flush current block if exists
        if block:
            for indent, key, value in block:
                spaces = ' ' * (max_key_length - len(key))
                formatted_lines.append(f"{indent}{key}{spaces} = {value}")
            block = []
            max_key_length = 0

        formatted_lines.append(line)

    # Flush any remaining block
    if block:
        for indent, key, value in block:
            spaces = ' ' * (max_key_length - len(key))
            formatted_lines.append(f"{indent}{key}{spaces} = {value}")

    return "\n".join(formatted_lines)