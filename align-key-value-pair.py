import re

def align_equals(content: str) -> str:
    """
    Aligns the '=' signs for all simple key-value pairs in the content.
    Does not change indentation or other formatting.
    """
    lines = content.splitlines()
    formatted_lines = []
    block = []
    max_key_length = 0

    # Regex to detect key = value pairs (ignoring leading/trailing spaces)
    kv_pattern = re.compile(r'^(\s*)(\w+)\s*=\s*(.*)$')

    for line in lines:
        kv_match = kv_pattern.match(line)
        if kv_match:
            # Add line to current block
            block.append(kv_match)
            key_len = len(kv_match.group(2))
            if key_len > max_key_length:
                max_key_length = key_len
        else:
            # Flush current block if exists
            if block:
                for b in block:
                    indent, key, value = b.groups()
                    # Align '=' using max key length
                    spaces = ' ' * (max_key_length - len(key))
                    formatted_lines.append(f"{indent}{key}{spaces} = {value}")
                block = []
                max_key_length = 0
            formatted_lines.append(line)

    # Flush any remaining block
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
QUERY
  display_name = "Example Resource"
  severity = "high"
  other_property = "value"
}
"""
    print(align_equals(example_tf))