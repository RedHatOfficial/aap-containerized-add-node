# Findings: historical installer research

> **Not runtime docs.** Current collection supports **containerized AAP 2.6+ only**
> (`awx-manage` over SSH + `ansible.containerized_installer` from `aap_setup_dir`).
> RPM and OpenShift are unsupported. Material below informed the design.

For current architecture see [ARCHITECTURE.md](ARCHITECTURE.md) and [COLLECTION_MAP.md](COLLECTION_MAP.md).

## 1. How RPM installer adds EN/HN (historical)

Collection: `ansible.automation_platform_installer` — role `receptor`.

Typical sequence: mesh CA on controller → CSR/sign per node → work-signing keys →
`receptor.conf` → `awx-manage` (`provision_instance`, `add_receptor_address`,
`register_peers`, `register_queue`) delegated to controller[0].

Full `install.yml` re-enters gateway/controller/hub/EDA/redis — that blast radius is why
an additive path is needed. There is no first-class “add node only” playbook in the RPM tarball.

## 2. How containerized installer adds EN/HN (design source)

Collection: `ansible.containerized_installer`.

- Receptor role: podman + TLS under `~/aap/…`
- Registration: `automationcontroller` init via `awx-manage` (same CLI this collection uses
  with `podman exec` on `automation-controller-task`)
- Inventory: `receptor_type='hop'|'execution'`, `receptor_peers`
- Caution: full `install.yml` can **deprovision** DB instances missing from inventory

## 3. Registration path chosen for this collection

| Approach | Status |
|----------|--------|
| Gateway OAuth + `ansible.controller.instance` | Abandoned — not required |
| `awx-manage` on controller (SSH) | **Current** — matches installers |
| OpenShift install-bundle UI | Out of scope (reference only in `ignore/`) |

## 4. Peer direction

- **Outbound (preferred):** new node dials existing hop/controller — no MW on existing nodes
- **Inbound:** controllers dial new node — needs controller receptor reload / AIO listener flip

## 5. Version notes

| Area | Note |
|------|------|
| Target (current) | Containerized 2.6+ |
| Lab-validated | Containerized 2.6 + 2.7 AIO (EN + hop; EN via hop; RHEL 10 EN per S-001) |
| Cluster topologies | Not yet lab-validated |
| RPM | Research only — rejected by `validate_setup_dir` |
