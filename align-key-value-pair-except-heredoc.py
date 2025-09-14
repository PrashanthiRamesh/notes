import re

def align_equals_skip_heredoc(content: str) -> str:
    """
    Aligns the '=' signs for key-value pairs, but skips lines inside heredocs.
    """
    lines = content.splitlines()
    formatted_lines = []
    block = []
    max_key_length = 0
    inside_heredoc = False
    heredoc_delimiter = None

    # Regex to detect key = value pairs (ignoring leading/trailing spaces)
    kv_pattern = re.compile(r'^(\s*)(\w+)\s*=\s*(.*)$')
    heredoc_pattern = re.compile(r'<<-?([A-Z0-9_]+)')

    for line in lines:
        stripped = line.strip()

        # Track start/end of heredocs
        if inside_heredoc:
            formatted_lines.append(line)
            if stripped == heredoc_delimiter:
                inside_heredoc = False
                heredoc_delimiter = None
            continue

        # Check if line contains a heredoc start
        heredoc_match = heredoc_pattern.search(line)
        if heredoc_match:
            inside_heredoc = True
            heredoc_delimiter = heredoc_match.group(1)
            # Add current line and flush any key-value block
            if block:
                for b in block:
                    indent, key, value = b.groups()
                    spaces = ' ' * (max_key_length - len(key))
                    formatted_lines.append(f"{indent}{key}{spaces} = {value}")
                block = []
                max_key_length = 0
            formatted_lines.append(line)
            continue

        # Handle normal key-value lines
        kv_match = kv_pattern.match(line)
        if kv_match:
            block.append(kv_match)
            key_len = len(kv_match.group(2))
            if key_len > max_key_length:
                max_key_length = key_len
        else:
            # Flush current block
            if block:
                for b in block:
                    indent, key, value = b.groups()
                    spaces = ' ' * (max_key_length - len(key))
                    formatted_lines.append(f"{indent}{key}{spaces} = {value}")
                block = []
                max_key_length = 0
            formatted_lines.append(line)

    # Flush remaining block
    if block:
        for b in block:
            indent, key, value = b.groups()
            spaces = ' ' * (max_key_length - len(key))
            formatted_lines.append(f"{indent}{key}{spaces} = {value}")

    return "\n".join(formatted_lines)


# Example usage
if __name__ == "__main__":
    example_tf = """
resource "example_resource" "test" {
  name = "example"
  query = <<QUERY
SELECT * FROM table;
another_line = "inside heredoc"
QUERY
  display_name = "Example Resource"
  severity = "high"
  other_property = "value"
}
"""
    print(align_equals_skip_heredoc(example_tf))