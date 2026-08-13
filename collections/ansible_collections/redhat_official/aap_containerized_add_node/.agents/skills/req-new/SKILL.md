---
name: req-new
description: >-
  Create a Requirement spec. Use when adding a new feature, "I want to
  spec out X", "new requirement", "create REQ for this". Do NOT use for
  modifying existing REQs or viewing status (use sdlc-status instead).
argument-hint: "[Feature Name] [--phase PHASE-NNN]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---

# REQ New

Create a Requirement spec.

## Arguments

Parse `$ARGUMENTS` for:
- Feature name in quotes → use as requirement name
- `--phase PHASE-NNN` → assign to phase
- `--status X` → set initial status

## Usage

```
/req-new                              # Interactive mode
/req-new "Feature Name"               # Start with name
/req-new "Feature" --phase PHASE-002  # Assign to phase
```

## Behavior

### 1. Determine Next REQ Number

Scan `.sdlc/specs/REQ-*.md` for highest number, increment by 1.

### 2. Assign to Phase

If phases exist:
```
Which phase does this requirement belong to?

| Phase | Name | Status |
|-------|------|--------|
| PHASE-001 | Initial Collection | Complete |
| PHASE-002 | Offline Bundle | Planned |

Enter phase number (or "none"):
```

### 3. Gather Information

```
Feature name?
```

```
What problem does this solve?
```

```
Acceptance criteria (bullet list):
```

```
Status? (1=Open, 2=Implemented)
```

### 4. Create REQ File

Create `.sdlc/specs/REQ-NNN-feature-slug.md` using template from `.sdlc/templates/requirement.md`.

**Slug:** 2-4 words from feature name, lowercase, hyphens.

Fill:
- Title, Status, Phase
- Parent RFE (if applicable)
- Requirement description
- Rationale
- Acceptance criteria
- Implementation artifacts
- Related items

### 5. Update Indexes

**Update `.sdlc/specs/README.md`:**
```
| REQ-NNN | Feature Name | Status | Phase |
```

**Update `.sdlc/README.md`:**
Add to Requirements table.

### 6. Summary

```
Done!
- Created: .sdlc/specs/REQ-NNN-slug.md
- Phase: PHASE-002
- Status: Open

Next: Implement or add to backlog
```
