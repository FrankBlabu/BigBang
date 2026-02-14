#!/usr/bin/env bash
#
# audit.sh - Scan local repositories for AI coding agent artifacts
#
# Usage: ./audit.sh [repo_path ...]
#
# This script discovers and inventories:
# - .github/copilot-instructions.md
# - .github/prompts/*.prompt.md
# - .copilot/ directory
# - LEARNINGS.md
# - AGENTS.md, CLAUDE.md
#

set -euo pipefail

# Default repos if none provided (assumes BigBang is in ~/Projects/)
DEFAULT_REPOS=(
    "$HOME/Projects/BigBang"
    "$HOME/Projects/Pulsar"
    "$HOME/Projects/ParabelLab"
    "$HOME/Projects/ProjectZ"
    "$HOME/Projects/backend"
)

REPOS=("${@:-${DEFAULT_REPOS[@]}}")

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  BigBang Artifact Audit                                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

for repo in "${REPOS[@]}"; do
    if [ ! -d "$repo" ]; then
        echo "⊗ $(basename "$repo") — SKIPPED (directory not found)"
        continue
    fi
    
    echo "═══ $(basename "$repo") ════════════════════════════════════════"
    
    # Check for copilot-instructions
    if [ -f "$repo/.github/copilot-instructions.md" ]; then
        lines=$(wc -l < "$repo/.github/copilot-instructions.md")
        echo "  ✓ copilot-instructions.md: YES ($lines lines)"
    else
        echo "  ✗ copilot-instructions.md: NO"
    fi
    
    # Check for .copilot directory
    if [ -d "$repo/.copilot" ]; then
        count=$(find "$repo/.copilot" -type f 2>/dev/null | wc -l)
        echo "  ✓ .copilot/ directory: YES ($count files)"
    else
        echo "  ✗ .copilot/ directory: NO"
    fi
    
    # Check for prompt files
    if [ -d "$repo/.github/prompts" ]; then
        count=$(find "$repo/.github/prompts" -name "*.prompt.md" 2>/dev/null | wc -l)
        if [ "$count" -gt 0 ]; then
            echo "  ✓ prompt files: $count"
            # List them
            find "$repo/.github/prompts" -name "*.prompt.md" -exec basename {} \; 2>/dev/null | sed 's/^/    - /'
        else
            echo "  ✗ prompt files: 0"
        fi
    else
        echo "  ✗ .github/prompts/: NO"
    fi
    
    # Check for LEARNINGS.md
    if [ -f "$repo/LEARNINGS.md" ]; then
        lines=$(wc -l < "$repo/LEARNINGS.md")
        # Count bullet points as a proxy for number of learnings
        learnings=$(grep -c "^- " "$repo/LEARNINGS.md" || echo "0")
        echo "  ✓ LEARNINGS.md: YES ($lines lines, ~$learnings entries)"
    else
        echo "  ✗ LEARNINGS.md: NO"
    fi
    
    # Check for AGENTS.md
    if [ -f "$repo/AGENTS.md" ]; then
        lines=$(wc -l < "$repo/AGENTS.md")
        echo "  ✓ AGENTS.md: YES ($lines lines)"
    else
        echo "  ✗ AGENTS.md: NO"
    fi
    
    # Check for CLAUDE.md
    if [ -f "$repo/CLAUDE.md" ]; then
        lines=$(wc -l < "$repo/CLAUDE.md")
        echo "  ✓ CLAUDE.md: YES ($lines lines)"
    else
        echo "  ✗ CLAUDE.md: NO"
    fi
    
    # Detect primary stack from markers
    stack=""
    [ -f "$repo/pyproject.toml" ] && stack="${stack}Python "
    [ -f "$repo/package.json" ] && stack="${stack}TypeScript/Node "
    [ -f "$repo/CMakeLists.txt" ] && stack="${stack}C++/CMake "
    [ -f "$repo/Cargo.toml" ] && stack="${stack}Rust "
    [ -z "$stack" ] && stack="(unknown)"
    echo "  Stack: $stack"
    
    echo ""
done

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Audit Complete                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
