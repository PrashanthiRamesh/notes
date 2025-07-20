import re

# Order of keys based on Sentinel GUI
DESIRED_KEY_ORDER = [
    "for_each",
    "name",
    "display_name",
    "description",
    "log_analytics_workspace_id",
    "severity",
    "tactics",
    "query_frequency",
    "query_period",
    "query",
    "enabled",
    "suppression_duration",
    "suppression_enabled",
    "trigger_operator",
    "trigger_threshold"
]

def add_dash_to_heredocs(text: str) -> str:
    return re.sub(r'(<<)([A-Z]+)', r'\1-\2', text)

def indent_heredoc_closers(lines):
    result = []
    heredoc_indent = None
    heredoc_tag = None
    inside_heredoc = False

    heredoc_start_pattern = re.compile(r'^(\s*[a-zA-Z0-9_]+\s*=\s*<<-?)([A-Z]+)')

    for line in lines:
        if not inside_heredoc:
            match = heredoc_start_pattern.search(line)
            if match:
                heredoc_tag = match.group(2)
                heredoc_indent = re.match(r'^(\s*)', line).group(1)
                inside_heredoc = True
            result.append(line)
        else:
            if line.strip() == heredoc_tag:
                result.append(f"{heredoc_indent}{heredoc_tag}")  # indent closing tag
                inside_heredoc = False
                heredoc_tag = None
                heredoc_indent = None
            else:
                result.append(line)
    return result

def format_block(block: str) -> str:
    lines = block.splitlines()
    kv_pattern = re.compile(r'^(\s*)([a-zA-Z0-9_]+)\s*=\s*(.*)$')

    kv_lines = {}
    other_lines = []

    for line in lines:
        match = kv_pattern.match(line)
        if match:
            indent, key, value = match.groups()
            kv_lines[key] = (indent, key, value.strip())
        else:
            other_lines.append(line)

    max_key_len = max((len(k) for k in kv_lines), default=0)
    formatted_lines = []

    for key in DESIRED_KEY_ORDER:
        if key in kv_lines:
            indent, k, v = kv_lines[key]
            padding = ' ' * (max_key_len - len(k))
            formatted_lines.append(f"{indent}{k}{padding} = {v}")

    for key in kv_lines:
        if key not in DESIRED_KEY_ORDER:
            indent, k, v = kv_lines[key]
            padding = ' ' * (max_key_len - len(k))
            formatted_lines.append(f"{indent}{k}{padding} = {v}")

    formatted_lines.extend(other_lines)

    # Apply indentation fix to heredoc closers
    formatted_lines = indent_heredoc_closers(formatted_lines)

    return '\n'.join(formatted_lines)

def format_tf_file(filepath: str):
    with open(filepath, 'r') as f:
        content = f.read()

    updated = add_dash_to_heredocs(content)
    blocks = re.split(r'(?<=})\n', updated)
    formatted_blocks = [format_block(block) for block in blocks]
    formatted_content = '\n'.join(formatted_blocks)

    with open(filepath, 'w') as f:
        f.write(formatted_content)

    print("✅ Heredoc dash, GUI key order, and heredoc closing indentation updated.")

if __name__ == "__main__":
    format_tf_file("sentinel.tf")
