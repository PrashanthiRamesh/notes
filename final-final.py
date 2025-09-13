import re
import sys
from pathlib import Path

# Desired property order
PROPERTY_ORDER = ["display_name", "description", "name", "severity", "tactics", "query"]

def format_terraform_file(input_file: str, output_file: str = None):
    path = Path(input_file)
    if not path.exists():
        print(f"File not found: {input_file}")
        return

    text = path.read_text()

    # --- Step 1: Process each resource block ---
    def process_resource(match):
        block = match.group(0)
        lines = block.splitlines()

        header = lines[0]  # resource "type" "name" {
        footer = lines[-1]  # closing }

        body = lines[1:-1]  # everything in between

        top_level_props = {}
        other_lines = []

        i = 0
        while i < len(body):
            line = body[i]
            stripped = line.strip()

            # Detect top-level key=value (non-nested)
            if "=" in stripped and not stripped.startswith("#") and not re.match(r'\s+\S', line):
                key = stripped.split("=")[0].strip()

                # Handle query heredoc specially
                if key == "query" and re.search(r'<<-?[A-Za-z0-9_]+', line):
                    heredoc_tag = re.search(r'<<-?([A-Za-z0-9_]+)', line).group(1)
                    heredoc_lines = []
                    i += 1
                    while i < len(body) and not body[i].strip() == heredoc_tag:
                        heredoc_lines.append(body[i])
                        i += 1
                    heredoc_lines.append(body[i])  # closing tag

                    # Indent heredoc content by 2 spaces relative to property line
                    indent = "  "
                    indented_heredoc = [line]  # the `query = <<-TAG` line itself
                    for l in heredoc_lines[0:-1]:
                        if l.strip():
                            indented_heredoc.append(indent + l)
                        else:
                            indented_heredoc.append(l)
                    indented_heredoc.append(heredoc_lines[-1])  # closing tag

                    top_level_props[key] = "\n".join(indented_heredoc)
                else:
                    top_level_props[key] = line
            else:
                other_lines.append(line)
            i += 1

        # Reorder top-level properties
        ordered_lines = []
        for key in PROPERTY_ORDER:
            if key in top_level_props:
                ordered_lines.append(top_level_props[key])
        for k, v in top_level_props.items():
            if k not in PROPERTY_ORDER:
                ordered_lines.append(v)

        # Combine with other lines (nested blocks, comments)
        final_body = ordered_lines + other_lines

        return "\n".join([header] + final_body + [footer])

    resource_pattern = re.compile(r'resource\s+".+?"\s+".+?"\s*{[^}]*}', re.DOTALL)
    text = resource_pattern.sub(process_resource, text)

    # --- Step 2: Add '-' to all heredocs (including query if not already) ---
    text = re.sub(r'(<<)([A-Za-z0-9_]+)', r'\1-\2', text)

    # --- Step 3: Save result ---
    if output_file:
        Path(output_file).write_text(text)
    else:
        path.write_text(text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tf_fmt.py <file.tf> [output.tf]")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        format_terraform_file(input_file, output_file)