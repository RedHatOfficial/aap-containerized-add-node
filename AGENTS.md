# AAP Add Node Agent Configurations

This document defines the specialized agents used in collection development. It is the
operational companion to `CLAUDE.md` (the project constitution). Read both before
touching code.

## IMPORTANT: Use Agent Skills

**All AI agents working on this repository MUST use the skills defined in `.agents/skills/`.**

Before performing any SDLC task, invoke the appropriate skill:

```
/sdlc-status    → Check project status
/workflow       → Get guidance on what to do next
/req-new        → Create a requirement
/dr-new         → Capture a question or blocker
/dr-review      → Resolve a decision request
/adr-new        → Document an architecture decision
/pr-new         → Submit a pull request
/lean-ci        → CI/CD workflow guidance
```

**Do NOT bypass skills by guessing implementation details.** Skills contain the correct
logic, templates, and conventions for this project. Using skills ensures consistency
across all contributors (human and AI).

## Architectural Invariants

These are non-negotiable. Violating any of them will break the system or create
technical debt. Do **not** work around them — if you think one needs to change,
write an ADR first.

1. **Non-root execution only** (collection design). The collection rejects running as
   root. All tasks use the non-root install user that set up containerized AAP.

2. **Outbound dial is the default** (ADR-003). New nodes dial out to controller via
   `receptor_peers`. Inbound dial (controller dials to nodes) is opt-in only and
   causes mesh disruption.

3. **Serial registration for multi-node** (ADR-002). Registration uses `serial: 1`
   to avoid database race conditions when adding multiple nodes simultaneously.

4. **Installer role reuse** (ADR-004). Collection reuses `ansible.containerized_installer`
   roles from `aap_setup_dir`. Never duplicate installer logic — use the version-matched
   collection from the setup tree.

5. **Preflight by default** (ADR-005). Preflight checks are enabled by default. Users
   must explicitly disable with `-e aap_add_node_preflight_enabled=false`.

6. **receptor_peers is always a list**. Never a bare string. INI inventory must use
   JSON format: `receptor_peers='["peer.example.com"]'`. YAML inventory uses list syntax.

7. **awx-manage over SSH** (design). Registration uses `awx-manage` commands via
   `podman exec` on the controller. No Gateway OAuth tokens required.

8. **ansible-lint must pass**. All code must pass `ansible-lint` with production profile
   before commit. Use skip rules only for documented exceptions.

9. **Inventory matches installer format**. Variables like `receptor_type`, `receptor_peers`,
   `routable_hostname` must match `ansible.containerized_installer` conventions.

10. **No mesh disruption on outbound dial**. Adding nodes via outbound dial must not
    restart any existing services. Only inbound dial (opt-in) causes controller receptor
    restart.

## Agent Roles

### 1. Collection Developer Agent

**Purpose**: Implements roles, playbooks, and tasks.

**Context Files**:
- `CLAUDE.md`
- `docs/ARCHITECTURE.md`
- `docs/CONVENTIONS.md`
- `.sdlc/adrs/*.md`

**Scope**: `roles/`, `playbooks/`, `plugins/`

**Capabilities**:
- Create and modify Ansible roles
- Implement playbook logic
- Write task files
- Handle variable precedence

**Constraints**:
- Must follow `ansible.containerized_installer` conventions
- Must pass `ansible-lint`
- Must not duplicate installer logic
- Must use `become: false` for controller awx-manage tasks

---

### 2. Documentation Agent

**Purpose**: Maintains user-facing and developer documentation.

**Context Files**:
- `docs/*.md`
- `README.md`
- `.sdlc/README.md`

**Scope**: `docs/`, root markdown files, role READMEs

**Capabilities**:
- Write installation guides
- Document topology patterns
- Create troubleshooting guides
- Maintain FAQ

**Constraints**:
- Must keep examples testable
- Must document all variables
- Must include version compatibility notes

---

### 3. SDLC Agent

**Purpose**: Manages spec-driven development artifacts.

**Context Files**:
- `.sdlc/README.md`
- `.sdlc/templates/*.md`
- `.agents/skills/*/SKILL.md`

**Scope**: `.sdlc/`, `.agents/`

**Capabilities**:
- Create requirements (REQ)
- Create decision requests (DR)
- Create architecture decisions (ADR)
- Track phase progress

**Constraints**:
- Must use templates from `.sdlc/templates/`
- Must link related artifacts
- Must update indexes when creating artifacts

---

### 4. CI/CD Agent

**Purpose**: Maintains GitHub Actions workflows and quality gates.

**Context Files**:
- `.github/workflows/*.yml`
- `.ansible-lint`
- `.yamllint`

**Scope**: `.github/`, linter configs

**Capabilities**:
- Configure CI workflows
- Set up quality gates
- Manage release automation

**Constraints**:
- Must pin action versions to SHA
- Must keep CI reproducible locally
- Must not add inline shell logic

## Feedback Rules (Learned)

These rules were learned from past development sessions:

1. **YAML document starts required**. All YAML files (workflows, playbooks) must
   start with `---`. CI lint will fail without it.

2. **Line wrapping for long strings**. Use YAML folded style `>-` for strings
   over 200 characters. Never let lines exceed yamllint limit.

3. **Skip rules must be documented**. When adding ansible-lint skip rules,
   document why in `.ansible-lint` comments or CONTRIBUTING.md.

4. **Collection must be installed for syntax check**. CI must run
   `ansible-galaxy collection install .` before `ansible-playbook --syntax-check`.

5. **Namespace in FQCNs must match galaxy.yml**. Role references must use
   `redhat_official.aap_containerized_add_node.<role>` not shortened forms.

## Skills Reference

| Skill | Purpose |
|-------|---------|
| `/sdlc-status` | Show project status dashboard |
| `/workflow` | Get guidance on what to do next |
| `/req-new` | Create a requirement spec |
| `/dr-new` | Create a decision request |
| `/dr-review` | Resolve a decision request |
| `/adr-new` | Create an architecture decision |
| `/pr-new` | Prepare and submit a pull request |
| `/lean-ci` | GitHub Actions workflow guidance |
