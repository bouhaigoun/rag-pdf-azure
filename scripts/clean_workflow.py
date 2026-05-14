import json
import sys
from pathlib import Path

FORBIDDEN_KEYS = {"updatedAt", "createdAt", "id", "isArchived", "description"}

input_path = Path("workflow_n8n.json")
output_path = Path("workflow_import.json")

if not input_path.exists():
    print(f"Error: {input_path} not found", file=sys.stderr)
    sys.exit(1)

with input_path.open(encoding="utf-8") as f:
    workflow = json.load(f)

for key in FORBIDDEN_KEYS:
    workflow.pop(key, None)

with output_path.open("w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"Cleaned workflow saved to {output_path}")
