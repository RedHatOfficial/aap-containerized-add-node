# Research: Registration Approaches

## Date

2026-08-10

## Question

How should new nodes be registered with Controller?

---

## Options Evaluated

### Option A: Gateway OAuth + `ansible.controller.instance`

**Description**: Use AAP Gateway token and `ansible.controller` collection.

**Pros**:
- No SSH to controller required
- Uses public API

**Cons**:
- Token management overhead
- `ansible.controller.instance` module exists but registration flow complex
- Gateway OAuth setup varies by deployment

**Verdict**: Abandoned — unnecessary complexity.

---

### Option B: `awx-manage` on Controller (SSH)

**Description**: SSH to controller, run `podman exec awx-manage` commands.

**Pros**:
- Matches how installers work
- Well-tested path
- No token management
- Works on any containerized AAP

**Cons**:
- Requires SSH access to controller
- Requires non-root user with podman access

**Verdict**: **Chosen** — matches installer pattern, simpler.

---

### Option C: OpenShift Install-Bundle UI

**Description**: Use OpenShift UI for node addition.

**Pros**:
- Native UX for OpenShift

**Cons**:
- OpenShift only
- Out of scope for containerized

**Verdict**: Out of scope — referenced in `ignore/` for future research.

---

## Decision

`awx-manage` on controller via SSH.

Implementation:
- SSH to `automationcontroller` group
- `podman exec automation-controller-task awx-manage <command>`
- Commands: `provision_instance`, `add_receptor_address`, `register_peers`, `register_queue`

---

## Outcome

- `roles/register_instance/` wraps awx-manage
- `roles/list_instances/` wraps list_instances
- No Gateway token required
