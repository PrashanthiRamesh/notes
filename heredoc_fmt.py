import re
from pathlib import Path


def convert_to_indented_heredoc(content: str) -> str:
    """
    Replace standard heredocs (<<DELIM) with indented heredoc (<<-DELIM) in the given content.
    """
    return re.sub(r"<<([A-Z0-9_]+)", r"<<-\1", content)

def align_heredoc_closing_delimited(content: str) -> str:
    """
    Aligns the closing delimited of heredocs to the same indent as the key
    """
    lines = content.splitlines()
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        heredoc_match = re.search(r'(\s*\w+\s*=\s*<<-?)([A-Z0-9_]+)', line)
        if heredoc_match:
            key_indent = re.match(r'(\s*)', line).group(1)
            delimiter = heredoc_match.group(2)
            output.append(line)
            i += 1
            heredoc_content = []
            while i < len(lines):
                current_line = lines[i]
                if(current_line.strip() == delimiter):
                    break
                heredoc_content.append(current_line)
                i += 1
            output.extend(heredoc_content)
            output.append(f"{key_indent}{delimiter}")
        else:
            output.append(line)
        i += 1
    return "\n".join(output) 
