---
name: workflow
description: >-
  Get workflow guidance for spec-driven development. Use when unsure what
  to do next, "help me get started", "what should I work on", "I'm stuck".
  Do NOT use for directly creating artifacts (this skill guides you to
  the right skill for that).
argument-hint: "[next|blockers|start|decision]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---

# Workflow

Get workflow guidance for spec-driven development.

## Arguments

If `$ARGUMENTS` is provided:
- `next` — Single best next action
- `blockers` — Show what's blocking progress
- `start` — Start a new feature
- `decision` — Handle a question or choice

## Usage

```
/workflow              # Interactive guide
/workflow next         # Single best next action
/workflow blockers     # Show what's blocking progress
/workflow start        # Start a new feature
/workflow decision     # Handle a question or choice
```

## Workflow Diagram

```
  1. ASSESS          2. UNBLOCK         3. SPECIFY         4. EXECUTE
  ──────────────     ──────────────     ──────────────     ──────────────
  /sdlc-status ───> /dr-review    ───> /req-new      ───> Implement
  (current state)   (open DRs)         (new feature)      
                                                              │
                        ▲                                     ▼
                        │            ◄────────────────   Architecture
                   /adr-new  ◄───────────────────────   decision?
                        │
                        ▼
                   /dr-new (if question arises)
```

## Behavior

### Default: Interactive Guide

Show workflow diagram, then ask:
```
What would you like to do?
1. Start a new feature
2. Continue existing work
3. Handle a decision
4. Get oriented

Or describe what you're trying to accomplish:
```

### `/workflow next` — Smart Recommendation

Analyze state and return single best action:

1. Scan for open DRs → suggest `/dr-review DR-NNN`
2. Scan for open REQs → suggest implementation
3. Current phase complete → suggest next phase
4. No open work → "All caught up!"

Output:
```
**Recommended next action:**
→ /dr-review DR-001

Reason: High priority DR blocking PHASE-002.
```

### `/workflow blockers` — Quick Blockers Check

Show only blocking items:
```
## Current Blockers

**Open DRs:** DR-001 (High)
**Open REQs:** REQ-005
**Phase Blockers:** PHASE-002 waiting on DR-001

Quick fix: /dr-review DR-001
```

### `/workflow start` — New Feature

1. Check for open DRs that might affect new work
2. If blockers exist, warn and suggest resolving first
3. Ask which phase
4. Guide to `/req-new --phase PHASE-NNN`

### `/workflow decision` — Handle Question/Choice

| Situation | Action |
|-----------|--------|
| Have a question/blocker | `/dr-new` |
| Made an architecture choice | `/adr-new` |
| Need to resolve open DR | `/dr-review` |

## Skill Quick Reference

| Skill | Purpose |
|-------|---------|
| `/sdlc-status` | Dashboard with phase progress |
| `/req-new` | Create requirement |
| `/dr-new` | Capture question/blocker |
| `/dr-review` | Decide and close a DR |
| `/adr-new` | Record architecture decision |
