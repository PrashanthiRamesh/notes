import subprocess
import tempfile
from pathlib import Path


def terraform_fmt(content: str) -> str:
    """
    Takes Terraform code as a string, formats it using `terraform fmt`, and returns the formatted version.
    This is preferred for formatting a terraform file for the following reasons:
      1. avoid inconsistent styles by following the tf official standardized formatting + benefit from additional formatting like
         - Normalizes indentation (2 spaces per block)
         - aligns = signs in key-value pair [custom script atm is designed to handle only this case for the moment]
         - fixes spaces around braces, lists and maps
         - normalizes heredocs and keeps indentation consistent
         - removes trailing spaces
      2. to handle all edge cases correctly
      3. future-proof- when tf introduces breaking changes or new syntax in future updates `terraform fmt` will be adapted implicitely
      4. the custom scripts needs constant maintanance
      5. its risky to use a custom script on prod files as it might make unintentional alterations 
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile = Path(tmpdir) / "temp.tf"

        tmpfile.write_text(content, encoding="utf-8")
        subprocess.run(
            ["terraform", "fmt", str(tmpfile)], check=True, capture_output=True
        )

        formatted = tmpfile.read_text(encoding="utf-8")

    return formatted
