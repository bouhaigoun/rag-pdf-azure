import json
import sys
from pathlib import Path

# Only these keys are accepted by POST /api/v1/workflows
ALLOWED_KEYS = {"name", "nodes", "connections", "settings", "staticData", "pinData", "tags"}

input_path = Path("workflow_n8n.json")
output_path = Path("workflow_import.json")

if not input_path.exists():
    print(f"Error: {input_path} not found", file=sys.stderr)
    sys.exit(1)

with input_path.open(encoding="utf-8") as f:
    workflow = json.load(f)

workflow = {
    k: v for k, v in workflow.items()
    if k in ALLOWED_KEYS and v is not None and v != [] and v != {}
}

with output_path.open("w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"Cleaned workflow saved to {output_path}")
