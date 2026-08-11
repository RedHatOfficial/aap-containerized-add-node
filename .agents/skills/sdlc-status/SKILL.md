---
name: sdlc-status
description: >-
  Show project status, progress, and blockers. Use when asking "what's the
  status?", "where are we?", "what's blocking?", "show me progress", or
  starting a work session. Do NOT use for creating or modifying artifacts
  (use req-new, dr-new, etc. instead).
argument-hint: "[phase or requirement]"
user-invocable: true
metadata:
  author: AAP Add Node Team
  version: 1.0.0
---

# SDLC Status Dashboard

Show project status, progress, and blockers.

## Arguments

If `$ARGUMENTS` is provided (e.g., "PHASE-001" or "REQ-002"), show detailed
status for that specific artifact. Otherwise, show the full dashboard.

## Behavior

Scan SDLC directories, extract status from each artifact, and present a concise dashboard with actionable insights.

### 1. Scan These Locations

| Artifact | Path Pattern |
|----------|--------------|
| Phases | `.sdlc/phases/PHASE-*.md` |
| Requirements | `.sdlc/specs/REQ-*.md` |
| Open DRs | `.sdlc/decisions/open/DR-*.md` |
| Closed DRs | `.sdlc/decisions/closed/DR-*.md` |
| ADRs | `.sdlc/adrs/ADR-*.md` |

### 2. Extract Status

| Artifact | Status Values |
|----------|---------------|
| PHASE | Planned, In Progress, Complete, Future |
| REQ | Open, Implemented, Deferred |
| DR | Open (High/Medium/Low), Decided, Deferred |
| ADR | Proposed, Accepted, Deprecated |

**Phase status:**
- Planned: Not started
- In Progress: Active work
- Complete: All REQs implemented
- Future: Not yet planned

### 3. Present Dashboard

```markdown
# SDLC Status Dashboard

## Phases
| Phase | Title | Status | REQs |
|-------|-------|--------|------|
| PHASE-001 | Initial Collection | Complete | REQ-001, REQ-002, REQ-003, REQ-004 |
| PHASE-002 | Offline Bundle | Complete | REQ-005, REQ-006, REQ-007 |
| PHASE-003 | Upstream Migration | Future | — |

Current Phase: PHASE-003 (Future)

## Requirements
| REQ | Title | Status | Phase |
|-----|-------|--------|-------|
| REQ-001 | Additive Node Join | Implemented | PHASE-001 |
| REQ-002 | Hop and Execution Node Support | Implemented | PHASE-001 |
| REQ-003 | Bidirectional Peering | Implemented | PHASE-001 |
| REQ-004 | Platform Compatibility | Implemented | PHASE-001 |
| REQ-005 | Offline Join Bundle | Implemented | PHASE-002 |
| REQ-006 | Hybrid Cloud Topology | Implemented | PHASE-002 |
| REQ-007 | BYO TLS Certificates | Implemented | PHASE-002 |

## Open Decision Requests
No open decision requests.

## Architecture Decisions
| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Ansible Automation Only | Accepted |
| ADR-002 | Serial Registration | Accepted |
| ADR-003 | Outbound-First Topology | Accepted |
| ADR-004 | Installer Role Reuse | Accepted |
| ADR-005 | Preflight as Opt-Out | Accepted |

## Test Status
| Scenario | Status |
|----------|--------|
| S-060: Single EN offline | PASS |
| S-061: Single HN offline | PASS |
| S-062: Image bundling | BLOCKED |
| S-063: HN + EN chain | PASS |
| S-070: TLS self-signed | PASS |

## Blockers & Warnings
- S-062 (image bundling) not yet implemented

## Quick Actions
- Implement image bundling for fully air-gapped environments
- Plan PHASE-003 upstream migration
```

### 4. Handle Empty States

| Condition | Message |
|-----------|---------|
| No phases | "No phases defined." |
| No REQs | "No requirements defined." |
| No DRs | "No open decision requests." |
| No blockers | "No blockers. Ready to proceed." |

### 5. Identify Blockers

- **Open DRs**: Especially High priority
- **Open REQs**: Requirements not yet implemented
- **Phase dependencies**: Previous phase not complete

### 6. Generate Quick Actions

| Condition | Suggestion |
|-----------|------------|
| Open DRs | "Resolve DR-XXX" |
| Current phase has open REQs | "Implement REQ-XXX" |
| Current phase complete | "Ready for next phase" |
| All phases complete | "Project complete!" |
