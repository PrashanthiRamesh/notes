import re

def reorder_resource_properties(content: str) -> str:
    """
    Reorders properties in Terraform resource blocks.
    
    Args:
        content: The Terraform file content.
    
    Returns:
        Modified content with properties reordered.
    """
    # Define the preferred order
    preferred_order = ["display_name", "description", "name", "severity", "tactics", "query"]

    lines = content.splitlines()
    output = []
    inside_resource = False
    resource_lines = []
    brace_count = 0

    for line in lines:
        stripped = line.strip()

        # Detect start of resource block
        if re.match(r'resource\s+".*"\s+".*"\s*{', stripped):
            inside_resource = True
            resource_lines = [line]
            brace_count = line.count("{") - line.count("}")
            continue

        if inside_resource:
            resource_lines.append(line)
            brace_count += line.count("{") - line.count("}")
            
            # End of resource block
            if brace_count == 0:
                # Reorder properties inside the block
                reordered_lines = []
                other_lines = []

                # Collect property blocks
                i = 1  # skip first line (resource declaration)
                while i < len(resource_lines) - 1:  # skip last line (closing brace)
                    l = resource_lines[i]
                    prop_match = re.match(r'\s*(\w+)\s*=', l)
                    if prop_match:
                        prop_name = prop_match.group(1)
                        # Capture multi-line heredoc or block
                        block_lines = [l]
                        i += 1
                        if "<<-" in l or "<<" in l:  # heredoc
                            delimiter = re.search(r'<<-?([A-Z0-9_]+)', l).group(1)
                            while i < len(resource_lines) - 1:
                                block_lines.append(resource_lines[i])
                                if resource_lines[i].strip() == delimiter:
                                    i += 1
                                    break
                                i += 1
                        # Save in order dict
                        if prop_name in preferred_order:
                            reordered_lines.append((preferred_order.index(prop_name), block_lines))
                        else:
                            other_lines.append(block_lines)
                    else:
                        other_lines.append([l])
                        i += 1

                # Sort by preferred order and flatten
                reordered_lines.sort(key=lambda x: x[0])
                flat_lines = []
                for _, lines_block in reordered_lines:
                    flat_lines.extend(lines_block)
                for lines_block in other_lines:
                    flat_lines.extend(lines_block)

                # Append resource declaration and closing brace
                output.append(resource_lines[0])
                output.extend(flat_lines)
                output.append(resource_lines[-1])

                inside_resource = False
            continue

        # Outside resource, just append
        output.append(line)

    return "\n".join(output)

# Example usage
if __name__ == "__main__":
    example_content = """
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
    print(reorder_resource_properties(example_content))