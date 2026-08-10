# Research: Installer Analysis

## Date

2026-08-10

## Question

How do existing AAP installers add execution/hop nodes?

---

## RPM Installer (`ansible.automation_platform_installer`)

### Pattern

Collection: `ansible.automation_platform_installer` — role `receptor`.

Sequence:
1. Mesh CA on controller
2. CSR/sign per node
3. Work-signing keys
4. `receptor.conf` generation
5. `awx-manage` commands (delegated to controller[0]):
   - `provision_instance`
   - `add_receptor_address`
   - `register_peers`
   - `register_queue`

### Problem

Full `install.yml` re-enters gateway/controller/hub/EDA/redis — blast radius requires maintenance window.

No first-class "add node only" playbook in RPM tarball.

---

## Containerized Installer (`ansible.containerized_installer`)

### Pattern

Collection: `ansible.containerized_installer`.

Key characteristics:
- Receptor role: podman + TLS under `~/aap/…`
- Registration: `automationcontroller` init via `awx-manage`
- Same CLI as RPM, wrapped in `podman exec` on `automation-controller-task`
- Inventory: `receptor_type='hop'|'execution'`, `receptor_peers`

### Caution

Full `install.yml` can **deprovision** DB instances missing from inventory.

This collection avoids full install, preventing accidental deprovision.

---

## Conclusion

Containerized installer has right mechanics — needs additive playbook. Led to ADR-004 (Installer Role Reuse).

---

## Outcome

- ADR-004: Installer Role Reuse
- Collection reuses `ansible.containerized_installer` via `aap_setup_dir`
