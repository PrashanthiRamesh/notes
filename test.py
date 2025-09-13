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

    # Normalize spacing similar to terraform fmt
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

    # Reorder properties inside resources
    def reorder_block(match):
        block = match.group(0)
        lines = block.splitlines()

        # Separate resource header and body
        header = lines[0]
        body = lines[1:-1]
        footer = lines[-1]

        # Extract properties
        props = {}
        other_props = []
        for line in body:
            stripped = line.strip()
            if "=" in stripped:
                key = stripped.split("=")[0].strip()
                props[key] = line
            else:
                other_props.append(line)

        # Reorder according to PROPERTY_ORDER
        ordered_lines = []
        for key in PROPERTY_ORDER:
            if key in props:
                ordered_lines.append(props[key])

        # Add remaining properties not in PROPERTY_ORDER
        for k, v in props.items():
            if k not in PROPERTY_ORDER:
                ordered_lines.append(v)

        ordered_lines.extend(other_props)

        # Rebuild block
        return "\n".join([header] + ["  " + l.strip() for l in ordered_lines] + [footer])

    # Apply reordering only inside resource blocks
    resource_pattern = re.compile(r'resource\s+".+?"\s+".+?"\s*{[^}]*}', re.DOTALL)
    formatted_text = resource_pattern.sub(reorder_block, formatted_text)

    # Save or overwrite
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