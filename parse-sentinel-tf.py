import re
from pathlib import Path

def add_dash_to_heredocs(text: str) -> str:
    # Replace <<WORD with <<-WORD (only at assignment points)
    return re.sub(r'(<<)([A-Z]+)', r'\1-\2', text)

def format_block(block: str) -> str:
    lines = block.splitlines()
    formatted_lines = []
    kv_pattern = re.compile(r'^(\s*)([a-zA-Z0-9_]+)\s*=\s*(.*)$')

    # Find max key length for alignment
    max_key_len = 0
    for line in lines:
        match = kv_pattern.match(line)
        if match:
            key = match.group(2)
            max_key_len = max(max_key_len, len(key))

    for line in lines:
        match = kv_pattern.match(line)
        if match:
            indent, key, value = match.groups()
            padding = ' ' * (max_key_len - len(key))
            formatted_lines.append(f"{indent}{key}{padding} = {value.strip()}")
        else:
            formatted_lines.append(line)
    return '\n'.join(formatted_lines)

def format_tf_file(filepath: str):
    with open(filepath, 'r') as f:
        content = f.read()

    # Step 1: Add dash to heredocs
    updated = add_dash_to_heredocs(content)

    # Step 2: Format key = value pairs in each Terraform block
    blocks = re.split(r'(?<=})\n', updated)  # split by resource blocks
    formatted_blocks = [format_block(block) for block in blocks]
    formatted_content = '\n'.join(formatted_blocks)

    with open(filepath, 'w') as f:
        f.write(formatted_content)

    print("✅ Updated heredocs and formatted key-value pairs.")

if __name__ == "__main__":
    format_tf_file("sentinel.tf")
