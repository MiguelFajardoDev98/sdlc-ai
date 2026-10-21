"""Validates the runtime-neutral Antigravity harness contract."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "ANTIGRAVITY.md",
    "AGENTS.md",
    "docs/constitution.md",
    "MEMORY.md",
    ".opencode/agents/coordinator.md",
    ".opencode/commands/feature.md",
    ".opencode/commands/status.md",
    ".opencode/commands/approve-spec.md",
)


def main() -> None:
    """Raises an error when the operational harness contract is incomplete."""
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"Missing harness files: {', '.join(missing)}")

    for config_path in (ROOT / ".opencode/agents").glob("*.json"):
        json.loads(config_path.read_text(encoding="utf-8"))

    contract = (ROOT / "ANTIGRAVITY.md").read_text(encoding="utf-8")
    for state in ("WAITING_APPROVAL", "ARCHITECTING", "QA_REPAIR", "COMPLETED"):
        if state not in contract:
            raise SystemExit(f"Missing state in ANTIGRAVITY.md: {state}")

    print("Antigravity harness contract: valid")


if __name__ == "__main__":
    main()
