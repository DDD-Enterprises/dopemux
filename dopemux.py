"""dopemux automation helper
Allows specifying a custom data location via the ``DOPMUX_DATA_ROOT``
environment variable. Default is ``/mnt/data``.
"""

import os
from pathlib import Path

# Define basic shell script templates for each tool in the automation suite

tool_scripts = {
    "context_archive": """#!/bin/bash
# 🗃️ Auto-archive memory and logs
ARCHIVE_DIR="dev/archives"
mkdir -p "$ARCHIVE_DIR"

TS=$(date +%Y-%m-%d_%H%M)
cp dev/memory.md "$ARCHIVE_DIR/memory_$TS.md"
cp dev/logs/devlog_latest.md "$ARCHIVE_DIR/devlog_$TS.md" 2>/dev/null || true
echo "🧠 Archived memory and devlog to $ARCHIVE_DIR/"
""",

    "dirtycommit": """#!/bin/bash
# 🧼 Git commit + memory enforcement

if [[ -z "$1" ]]; then
  echo "❌ Commit message required."
  exit 1
fi

git add dev/memory.md dev/prompts/ dev/logs/
git commit -m "🧠 $1"
TS=$(date +%Y-%m-%d_%H%M)
git tag -a export-$TS -m "Context snapshot"
echo "✅ Dirty commit complete with tag export-$TS"
""",

    "alias_inspector": """#!/bin/bash
# 🧪 Checks for risky or overused aliases

ALIASES=(gb st sl g)

for a in "${ALIASES[@]}"; do
  if grep -q "alias $a=" ~/.zshrc ~/.bashrc 2>/dev/null; then
    echo "⚠️ Alias '$a' already in use. Choose something filthier."
  fi
done
""",

    "project_bootstrap": """#!/bin/bash
# 🚀 New repo bootstrapper

mkdir -p dev/prompts dev/logs dev/specs .copilot
touch dev/memory.md dev/logs/devlog_latest.md
cp ../template/context_dom_dev.md dev/prompts/context_dom_dev.md 2>/dev/null || echo "# Default prompt" > dev/prompts/context_dom_dev.md
echo "CONTEXT_MODE=dev" > .contextrc
echo "✅ Project bootstrapped."
""",

    "autopaste": """#!/bin/bash
# 📋 Copies export to clipboard (macOS only)

./dev/export.sh > /tmp/dom_context.txt
pbcopy < /tmp/dom_context.txt && echo "✅ Copied to clipboard." || echo "⚠️ Clipboard copy failed."
""",

    "session_summarizer": """#!/bin/bash
# 📆 Summarizes latest devlog session

echo "📝 Session Summary:"
tail -n 15 dev/logs/devlog_latest.md
""",

    "tui_expansion": """#!/bin/bash
# 🧠 Placeholder: Extend TUI with log/memory view toggle
echo "🚧 TUI Expansion not yet implemented. (TUI hooks coming soon)"
""",

    "design_dump": """#!/bin/bash
# 📄 Dumps all .specs for LLM reload
cat dev/specs/*.md > dev/logs/full_specs_dump.md
echo "🧬 Dumped design specs to dev/logs/full_specs_dump.md"
"""
}

# Write all automation tools to their script files
data_root = Path(os.environ.get("DOPMUX_DATA_ROOT", "/mnt/data"))
script_dir = data_root / "dev" / "tools"
script_dir.mkdir(parents=True, exist_ok=True)

for name, content in tool_scripts.items():
    script_path = script_dir / f"{name}.sh"
    script_path.write_text(content)
    script_path.chmod(0o755)

# List all generated tool paths
[str(p) for p in script_dir.glob("*.sh")]
