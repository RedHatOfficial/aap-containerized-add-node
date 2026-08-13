---
name: dr-new
description: >-
  Create a Decision Request. Use when you have a question that needs
  deciding, "we need to make a decision about X", "capture this as a DR",
  "log this blocking question". Do NOT use for resolving DRs (use dr-review
  instead) or documenting decided architecture (use adr-new instead).
argument-hint: "[Question] [--priority high|medium|low]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---

# DR New

Create a Decision Request.

## Arguments

Parse `$ARGUMENTS` for:
- Question text in quotes → use as DR question
- `--priority X` → set priority (high/medium/low)
- `--category X` → set category

## Usage

```
/dr-new                                # Interactive mode
/dr-new "Question here"                # Start with question
/dr-new "Question" --priority high     # With priority
```

## Behavior

### 1. Determine Next DR Number

Scan `.sdlc/decisions/open/DR-*.md` and `.sdlc/decisions/closed/DR-*.md` for highest number, increment by 1.

### 2. Check for Duplicates

Search existing open DRs for similar topics:
```
Found existing DR-001 "Offline Bundle" which may overlap.
Continue with new DR? (Y/n/view)
```

### 3. Gather Information

```
What question needs to be decided?
```

```
Context — why is this decision needed now?
```

```
Category? (Architecture/Product/Technical/Process)
```

```
Priority? (High/Medium/Low)
```

```
What's blocked if we don't decide?
```

```
Options (one per paragraph, include pros/cons):
```

```
Recommendation? (or "none")
```

### 4. Create DR File

Create `.sdlc/decisions/open/DR-NNN-short-slug.md` using template from `.sdlc/templates/decision-request.md`.

**Slug:** 3-5 words from question, lowercase, hyphens.

Fill:
- Title, Status: Open
- Raised By: User — today's date
- Category, Priority
- Question, Context, Impact
- Options with pros/cons
- Recommendation (if any)
- Related artifacts
- Empty Decision section

### 5. Update README Index

Edit `.sdlc/decisions/README.md`:
- Add row to "Open" table
- Insert in priority order (High > Medium > Low)

### 6. Summary

```
Done!
- Created: open/DR-NNN-short-slug.md
- Priority: High

Next: /dr-review DR-NNN when ready to decide
```
