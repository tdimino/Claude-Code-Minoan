#!/bin/bash
# Claude Code session history viewer with auto-categorization

limit=${1:-10}

# Build slug lookup
slugfile=$(mktemp)
find ~/.claude/projects -name "agent-*.jsonl" -exec cat {} + 2>/dev/null | \
  jq -rs 'map(select(.slug)) | group_by(.sessionId) | map({key: .[0].sessionId, value: .[0].slug}) | from_entries' > "$slugfile"

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "  CLAUDE CODE SESSIONS (last $limit)"
echo "═══════════════════════════════════════════════════════════════════════"

jq -rs --slurpfile slugs "$slugfile" '
  # Category detection function (returns max 3 tags with labels)
  def categorize:
    . as $msgs |
    ($msgs | map(.display // "") | join(" ") | ascii_downcase) as $all |
    [
      (if ($all | test("bug|error|broken|issue|debug|crash")) then {e: "🐛", n: "bug"} else null end),
      (if ($all | test("add|create|implement|build|new feature")) then {e: "✨", n: "feature"} else null end),
      (if ($all | test("investigate|explore|search|research|understand")) then {e: "🔍", n: "research"} else null end),
      (if ($all | test("refactor|rename|clean|reorganize|simplify")) then {e: "♻️", n: "refactor"} else null end),
      (if ($all | test("style|css|design|ui|layout|tailwind")) then {e: "🎨", n: "design"} else null end),
      (if ($all | test("test|spec|jest|pytest|coverage")) then {e: "🧪", n: "test"} else null end),
      (if ($all | test("deploy|docker|ci|cd|pipeline|release")) then {e: "🚀", n: "deploy"} else null end),
      (if ($all | test("^/|/commit|/review|/plugin")) then {e: "🔧", n: "commands"} else null end)
    ] | map(select(. != null)) | .[0:3] | {emojis: (map(.e) | join("")), labels: (map(.n) | join(", "))};

  # Extract markdown file names from plan/plans folders only
  def extract_keywords:
    . as $msgs |
    ($msgs | map(.display // "") | join(" ")) as $all |
    [$all | scan("plans?/([A-Za-z][A-Za-z0-9_-]{1,30})\\.md") | .[0]] | unique | .[0:4] | join(", ");

  ($slugs[0] // {}) as $s |
  group_by(.sessionId) |
  map(select(.[0].sessionId)) |
  map({
    sessionId: .[0].sessionId,
    project: .[0].project,
    messages: length,
    ended: (sort_by(.timestamp) | last | .timestamp),
    topic: (sort_by(.timestamp) | .[1:] | map(select(.display | length > 15)) | first | .display // ""),
    latest: (sort_by(.timestamp) | last | .display),
    slug: ($s[.[0].sessionId] // null),
    tags: (. | categorize),
    keywords: (. | extract_keywords)
  }) |
  sort_by(.ended) | reverse | .[:'$limit'] |
  to_entries | .[] |
  "\n\u001b[1;37m[" + ((.key + 1) | tostring) + "]\u001b[0m " +
  (if (.value.tags.emojis | length > 0) then .value.tags.emojis + " " else "" end) +
  (if .value.slug then "\u001b[1;35m" + .value.slug + "\u001b[0m" else "" end) +
  (if (.value.tags.labels | length > 0) then "\n    \u001b[90m(" + .value.tags.labels + ")\u001b[0m" else "" end) +
  (if (.value.keywords | length > 0) then "\n    \u001b[93m📄 " + .value.keywords + "\u001b[0m" else "" end) +
  "\n    \u001b[36m" + (.value.project | split("/") | .[-1]) + "\u001b[0m" +
  "  \u001b[90m" + (.value.messages | tostring) + " msgs\u001b[0m\n" +
  "    \u001b[90m" + .value.project + "\u001b[0m\n" +
  "    \u001b[33mID: " + .value.sessionId[0:8] + "...\u001b[0m  " +
  "\u001b[32m" + (.value.ended / 1000 | strftime("%b %d %H:%M")) + "\u001b[0m\n" +
  "    \u001b[34m📌 " + (.value.topic[0:55] | gsub("\n"; " ")) + "\u001b[0m\n" +
  "    \u001b[90m└─ " + (.value.latest[0:50] | gsub("\n"; " ")) + "...\u001b[0m"
' ~/.claude/history.jsonl 2>/dev/null

rm -f "$slugfile"

echo ""
echo "───────────────────────────────────────────────────────────────────────"
echo "  🐛=bug 🔧=commands ✨=feature 🔍=research ♻️=refactor 🎨=design 🧪=test 🚀=deploy"
echo "  cc-vscode <num>  - Open in VSCode + resume session"
echo "  cc-resume <num>  - Resume in current terminal"
echo "═══════════════════════════════════════════════════════════════════════"
