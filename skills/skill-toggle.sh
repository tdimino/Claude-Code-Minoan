#!/bin/bash
# Claude Code Skill Toggle Script
# Usage:
#   skill-disable open-souls-paradigm
#   skill-enable open-souls-paradigm

SKILLS_DIR="$HOME/.claude/skills"

skill-disable() {
    local skill_name="$1"
    if [ -z "$skill_name" ]; then
        echo "Usage: skill-disable <skill-name>"
        return 1
    fi

    if [ -d "$SKILLS_DIR/$skill_name" ]; then
        mv "$SKILLS_DIR/$skill_name" "$SKILLS_DIR/$skill_name.disabled"
        echo "✅ Disabled skill: $skill_name"
        echo "   (Restart Claude Code or wait a moment for changes to take effect)"
    elif [ -d "$SKILLS_DIR/$skill_name.disabled" ]; then
        echo "⚠️  Skill '$skill_name' is already disabled"
    else
        echo "❌ Skill '$skill_name' not found in $SKILLS_DIR"
    fi
}

skill-enable() {
    local skill_name="$1"
    if [ -z "$skill_name" ]; then
        echo "Usage: skill-enable <skill-name>"
        return 1
    fi

    if [ -d "$SKILLS_DIR/$skill_name.disabled" ]; then
        mv "$SKILLS_DIR/$skill_name.disabled" "$SKILLS_DIR/$skill_name"
        echo "✅ Enabled skill: $skill_name"
        echo "   (Restart Claude Code or wait a moment for changes to take effect)"
    elif [ -d "$SKILLS_DIR/$skill_name" ]; then
        echo "⚠️  Skill '$skill_name' is already enabled"
    else
        echo "❌ Skill '$skill_name.disabled' not found in $SKILLS_DIR"
    fi
}

skill-list() {
    echo "📋 Installed Skills:"
    echo ""
    echo "Enabled:"
    for dir in "$SKILLS_DIR"/*; do
        if [ -d "$dir" ] && [[ ! "$dir" == *.disabled ]]; then
            basename "$dir"
        fi
    done | sed 's/^/  ✅ /'

    echo ""
    echo "Disabled:"
    for dir in "$SKILLS_DIR"/*.disabled; do
        if [ -d "$dir" ]; then
            basename "$dir" .disabled
        fi
    done | sed 's/^/  ❌ /'
}

# Export functions
export -f skill-disable
export -f skill-enable
export -f skill-list
