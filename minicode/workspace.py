import os
import re
from datetime import datetime
from minicode.config import OUTPUT_DIR


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5]+", "_", text)
    return text[:30].strip("_") or "minicode_project"


def save_project_result(idea: str, prd: str, architecture: str, code: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = f"{timestamp}_{slugify(idea)}"
    project_path = os.path.join(OUTPUT_DIR, project_name)

    os.makedirs(project_path, exist_ok=True)

    with open(os.path.join(project_path, "idea.txt"), "w", encoding="utf-8") as f:
        f.write(idea)

    with open(os.path.join(project_path, "prd.md"), "w", encoding="utf-8") as f:
        f.write(prd)

    with open(os.path.join(project_path, "architecture.md"), "w", encoding="utf-8") as f:
        f.write(architecture)

    with open(os.path.join(project_path, "generated_code.md"), "w", encoding="utf-8") as f:
        f.write(code)

    return project_path