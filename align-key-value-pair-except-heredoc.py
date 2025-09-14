import re

def align_equals_skip_heredoc_content(content: str) -> str:
    """
    Aligns '=' signs for key-value pairs, but does not modify heredoc content.
    Only the key line (e.g., query = <<EOT) is aligned.
    """
    lines = content.splitlines()
    formatted_lines = []
    block = []
    max_key_length = 0
    inside_heredoc = False
    heredoc_delimiter = ""

    # Regex for key = value pairs
    kv_pattern = re.compile(r'^(\s*)(\w+)\s*=\s*(.*)$')

    for line in lines:
        stripped = line.strip()

        # Detect start of heredoc
        if not inside_heredoc:
            kv_match = kv_pattern.match(line)
            if kv_match:
                key, value = kv_match.group(2), kv_match.group(3)
                indent = kv_match.group(1)

                # Check if this is a heredoc
                heredoc_match = re.match(r'<<-?([A-Z0-9_]+)', value)
                if heredoc_match:
                    # Align this line only
                    max_key_length = len(key)
                    spaces = ' ' * (max_key_length - len(key))
                    formatted_lines.append(f"{indent}{key}{spaces} = {value}")
                    # Start skipping heredoc content
                    inside_heredoc = True
                    heredoc_delimiter = heredoc_match.group(1)
                    continue
                else:
                    # Collect block to align consecutive key-value pairs (non-heredoc)
                    block.append((indent, key, value))
                    if len(key) > max_key_length:
                        max_key_length = len(key)
                    continue
            else:
                # Flush block if exists
                if block:
                    for b in block:
                        indent, key, value = b
                        spaces = ' ' * (max_key_length - len(key))
                        formatted_lines.append(f"{indent}{key}{spaces} = {value}")
                    block = []
                    max_key_length = 0
                formatted_lines.append(line)
        else:
            # Inside heredoc, just append lines until closing delimiter
            formatted_lines.append(line)
            if stripped == heredoc_delimiter:
                inside_heredoc = False
                heredoc_delimiter = ""

    # Flush any remaining block
    if block:
        for b in block:
            indent, key, value = b
            spaces = ' ' * (max_key_length - len(key))
            formatted_lines.append(f"{indent}{key}{spaces} = {value}")

    return "\n".join(formatted_lines)


# Example usage
if __name__ == "__main__":
    example_tf = """
resource "example_resource" "test" {
  name = "example"
  query = <<QUERY
SELECT *
FROM table
WHERE id = 1;
QUERY
  display_name = "Example Resource"
  severity = "high"
  other_property = "value"
}
"""
    print(align_equals_skip_heredoc_content(example_tf))