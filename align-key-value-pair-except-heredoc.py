import re

def align_key_value_pairs(content: str) -> str:
    """
    Align '=' signs for key-value pairs in Terraform content.
    Does not modify anything inside heredoc content.
    """
    lines = content.splitlines()
    output = []
    block = []
    max_key_length = 0
    inside_heredoc = False
    heredoc_delimiter = ""

    kv_pattern = re.compile(r'^(\s*)(\w+)\s*=\s*(.*)$')

    for line in lines:
        stripped = line.strip()

        # Detect start or end of heredoc
        if inside_heredoc:
            output.append(line)
            if stripped == heredoc_delimiter:
                inside_heredoc = False
                heredoc_delimiter = ""
            continue

        # Match key=value
        kv_match = kv_pattern.match(line)
        if kv_match:
            indent, key, value = kv_match.groups()

            # Check for heredoc
            heredoc_match = re.match(r'<<-?([A-Z0-9_]+)', value)
            if heredoc_match:
                # Flush previous block
                if block:
                    for b in block:
                        i_indent, i_key, i_value = b
                        spaces = ' ' * (max_key_length - len(i_key))
                        output.append(f"{i_indent}{i_key}{spaces} = {i_value}")
                    block = []
                    max_key_length = 0

                # Add the heredoc declaration line aligned
                output.append(f"{indent}{key} = {value}")
                inside_heredoc = True
                heredoc_delimiter = heredoc_match.group(1)
            else:
                # Collect block of key-value pairs
                block.append((indent, key, value))
                if len(key) > max_key_length:
                    max_key_length = len(key)
        else:
            # Flush previous block
            if block:
                for b in block:
                    i_indent, i_key, i_value = b
                    spaces = ' ' * (max_key_length - len(i_key))
                    output.append(f"{i_indent}{i_key}{spaces} = {i_value}")
                block = []
                max_key_length = 0
            output.append(line)

    # Flush remaining block
    if block:
        for b in block:
            i_indent, i_key, i_value = b
            spaces = ' ' * (max_key_length - len(i_key))
            output.append(f"{i_indent}{i_key}{spaces} = {i_value}")

    return "\n".join(output)


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
    print(align_key_value_pairs(example_tf))