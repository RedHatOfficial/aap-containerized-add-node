---
name: adr-new
description: >-
  Create an Architecture Decision Record. Use when documenting an
  architecture decision, "record this choice", "we decided to use X", or
  after resolving an architectural DR. Do NOT use for capturing questions
  (use dr-new instead) or reviewing existing ADRs (use sdlc-status instead).
argument-hint: "[Decision Title] [--from-dr DR-NNN] [--status accepted]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---

# ADR New

Create an Architecture Decision Record.

## Arguments

Parse `$ARGUMENTS` for:
- Decision title in quotes → use as ADR title
- `--from-dr DR-NNN` → pre-fill from a decided DR
- `--status X` → set status (proposed/accepted)

## Usage

```
/adr-new                            # Interactive mode
/adr-new "Decision Title"           # Quick mode with title
/adr-new --from-dr DR-001           # Pre-fill from decided DR
/adr-new "Title" --status accepted  # With status
```

## Behavior

### 1. Determine Next ADR Number

Scan `.sdlc/adrs/ADR-*.md` for highest number, increment by 1.

### 2. Gather Information

```
Decision title?
```

```
Context — why is this decision needed?
```

```
Options considered (name: description, pros/cons):
```
Require at least 2 options for meaningful comparison.

```
Decision — which option and why?
```

```
Consequences? (use +/- prefix)
```
Parse into: Positive (+), Negative (-), Neutral (~)

```
Status? (1=Proposed, 2=Accepted)
```

### 3. Create ADR File

Create `.sdlc/adrs/ADR-NNN-title-slug.md` using template from `.sdlc/templates/adr.md`.

**Slug:** 3-5 words, lowercase, hyphens.

Fill:
- Title, Status, Date (today)
- Context
- Options with pros/cons
- Decision and rationale
- "Why not chosen" for rejected options
- Consequences (positive/negative/neutral)
- Implementation notes (if any)
- Related decisions
- Revision history

### 4. Update Index

Edit `.sdlc/adrs/README.md`:
- Add row in numerical order:

```markdown
| [ADR-NNN](ADR-NNN-slug.md) | Title | Status | YYYY-MM-DD |
```

### 5. Link to DR (if applicable)

If `--from-dr DR-NNN` provided:
- Update DR's "Related Artifacts" to reference ADR
- Copy context, options, decision from DR

### 6. Summary

```
Done!
- Created: ADR-NNN-title-slug.md
- Status: [Proposed/Accepted]
- Updated: adrs/README.md

Next: [If Proposed] Share for review | [If Accepted] Implement
```

## From-DR Mode

With `--from-dr DR-NNN`:
1. Read the decided DR
2. Extract context, options, decision, rationale
3. Show summary and ask for confirmation
4. Automatically link ADR ↔ DR
