# PHASE-003: Public Release

## Status

Future

## Timeline

- **Target Start**: TBD
- **Target Complete**: TBD

---

## Objective

Open the repository to public access and establish support model.

## Goals

1. Make repository publicly accessible on GitHub
2. Document support model and Red Hat Support Exception requirement
3. Establish contribution guidelines for external contributors
4. Publish to Ansible Galaxy (optional)

## Support Model

**IMPORTANT:** This collection is not part of the official AAP product.

For customers to use this in a **fully supported** fashion:
- Must have an approved **Red Hat Support Exception**
- Exception covers use of this collection alongside supported AAP installation
- Without exception, collection is provided as-is (community support only)

Documentation must clearly state:
1. Collection is not officially supported by Red Hat
2. Supported usage requires Red Hat Support Exception
3. How to request a Support Exception
4. What the exception covers/doesn't cover

## Deliverables

| Artifact | Description |
|----------|-------------|
| Public repo | Change visibility to public |
| SUPPORT.md | Support model documentation |
| README update | Add support disclaimer prominently |
| Galaxy publish | Optional: `ansible-galaxy collection publish` |
| CONTRIBUTING.md update | External contributor guidelines |

## Prerequisites

- PHASE-001 complete ✓
- PHASE-002 complete (or deferred)
- Legal/product approval for public release
- Support Exception template approved

## Success Criteria

- [ ] Repository publicly accessible
- [ ] Support model clearly documented
- [ ] README includes support disclaimer
- [ ] Contribution process documented for external contributors

## Notes

Upstream migration to `ansible.containerized_installer` (original PHASE-003 scope) is a separate track — that would make this capability officially supported without exception. This phase covers the interim public release.
