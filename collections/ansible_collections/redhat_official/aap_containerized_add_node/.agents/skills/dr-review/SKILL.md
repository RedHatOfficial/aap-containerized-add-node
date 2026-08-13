---
name: dr-review
description: >-
  Resolve open Decision Requests. Use when deciding DRs, resolving
  blockers, "what should we do about DR-X", "decide the blocking question",
  or when `/sdlc-status` shows open DRs. Do NOT use for creating new
  DRs (use dr-new instead) or just viewing status (use sdlc-status instead).
argument-hint: "[DR-NNN] [--quick]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---

# DR Review

Resolve open Decision Requests.

## Arguments

Parse `$ARGUMENTS` for:
- `DR-NNN` → review that specific DR directly
- `--quick` → use recommendations with minimal prompts

If no argument, list open DRs and prompt for selection.

## Usage

```
/dr-review              # List open DRs, select one
/dr-review DR-001       # Review specific DR
/dr-review --quick      # Use recommendations, minimal prompts
```

## Behavior

### 1. List Open DRs

Scan `.sdlc/decisions/open/DR-*.md` and present sorted by priority:

```
Found N open Decision Requests:

| Priority | DR | Question |
|----------|-----|----------|
| High | DR-001 | Offline Join Bundle |
...

Which DR to review? (number or "next" for highest priority)
```

**Empty state:** "No open Decision Requests. All caught up!"

### 2. Present DR Summary

Read the selected DR file and present:
- **Question**: Core decision needed
- **Context**: Why it matters (2-3 sentences)
- **Options**: Each with pros/cons
- **Recommendation**: Highlight if present

### 3. Facilitate Decision

```
What is your decision?
1. [Option A description]
2. [Option B description]
...
D. Defer for later
M. Need more information
```

**On option selected:**
- Ask for rationale
- Ask for action items (optional)

**On defer:**
- Ask when to revisit
- Keep in `open/`

### 4. Record Decision

Update the DR file:
- `Status:` → Decided / Deferred
- `Decision:` → chosen option
- `Rationale:` → user's rationale
- `Action Items:` → if any
- `Decided:` → today's date

### 5. Move to Closed

Move from `.sdlc/decisions/open/` to `.sdlc/decisions/closed/`.

### 6. Update README Index

Edit `.sdlc/decisions/README.md`:
- Remove from "Open" table
- Add to "Closed" table with decision summary

### 7. Offer ADR (If Architectural)

If decision affects architecture:
```
This decision affects architecture. Create an ADR? (Y/n)
```

If yes: `/adr-new --from-dr DR-NNN`

### 8. Summary

```
Done! DR-001 decided: [brief summary]
- Moved to closed/
- README updated

Action items:
- [ ] [any recorded items]

Review another DR? (Y/n)
```

## Quick Mode

With `--quick` flag:
1. Show DR question and recommended option
2. Ask for confirmation only
3. Use recommendation text as rationale
4. Skip action items prompt
