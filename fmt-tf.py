import re
import sys
from pathlib import Path

# Desired property order
PROPERTY_ORDER = ["display_name", "description", "name", "severity", "tactics"]

def format_terraform_file(input_file: str, output_file: str = None):
    path = Path(input_file)
    if not path.exists():
        print(f"File not found: {input_file}")
        return

    text = path.read_text()

    # --- Step 1: Normalize spacing like terraform fmt ---
    formatted = []
    indent_level = 0

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.endswith("}"):
            indent_level -= 1

        if stripped:
            formatted.append("  " * indent_level + stripped)
        else:
            formatted.append("")

        if stripped.endswith("{"):
            indent_level += 1

    formatted_text = "\n".join(formatted)

    # --- Step 2: Fix heredoc delimiters (<<WORD -> <<-WORD) ---
    formatted_text = re.sub(r'(<<)([A-Z][A-Za-z0-9_]*)', r'\1-\2', formatted_text)

    # --- Step 3: Indent heredoc bodies ---
    def indent_heredoc(match):
        full = match.group(0)
        start = match.group(1)
        tag = match.group(2)
        body = match.group(3)
        end = match.group(4)

        # detect base indent from the line with "<<-TAG"
        base_indent = " " * (len(start) - len(start.lstrip()))
        content_indent = base_indent + "  "  # indent heredoc body by +2 spaces

        # indent each non-empty line
        indented_body = "\n".join(
            content_indent + line if line.strip() else line
            for line in body.splitlines()
        )

        return f"{start}{tag}\n{indented_body}\n{base_indent}{end}"

    heredoc_pattern = re.compile(r"(^\s*.*<<-?)([A-Za-z0-9_]+)\n(.*?\n)(\s*\2)", re.DOTALL | re.MULTILINE)
    formatted_text = heredoc_pattern.sub(indent_heredoc, formatted_text)

    # --- Step 4: Reorder properties inside resources ---
    def reorder_block(match):
        block = match.group(0)
        lines = block.splitlines()

        header = lines[0]
        body = lines[1:-1]
        footer = lines[-1]

        props = {}
        other_props = []
        for line in body:
            stripped = line.strip()
            if "=" in stripped and not stripped.startswith("#"):
                key = stripped.split("=")[0].strip()
                props[key] = line
            else:
                other_props.append(line)

        ordered_lines = []
        for key in PROPERTY_ORDER:
            if key in props:
                ordered_lines.append(props[key])

        for k, v in props.items():
            if k not in PROPERTY_ORDER:
                ordered_lines.append(v)

        ordered_lines.extend(other_props)

        return "\n".join([header] + ["  " + l.strip() for l in ordered_lines] + [footer])

    resource_pattern = re.compile(r'resource\s+".+?"\s+".+?"\s*{[^}]*}', re.DOTALL)
    formatted_text = resource_pattern.sub(reorder_block, formatted_text)

    # --- Step 5: Save result ---
    if output_file:
        Path(output_file).write_text(formatted_text)
    else:
        path.write_text(formatted_text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tf_fmt.py <file.tf> [output.tf]")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        format_terraform_file(input_file, output_file)