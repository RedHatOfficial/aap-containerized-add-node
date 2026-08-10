# Collection map — Mermaid

Current runtime map for **containerized AAP 2.5+**. See [ARCHITECTURE.md](ARCHITECTURE.md) for design, [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for SSH/rollback, and [FINDINGS.md](FINDINGS.md) for historical installer research (RPM/OpenShift).

GitHub Mermaid notes: quote node labels that contain `[`, `]`, `{`, `}`, `/`, or `$`.

---

## 1. Scope

```mermaid
flowchart TB
  subgraph IN["In scope"]
    AAP["Containerized AAP 2.5+"]
    NODE["Add EN and/or HN"]
    ADD["Additive only - new hosts"]
    AWX["awx-manage via podman exec"]
    ZERO["Prefer outbound peer dial"]
  end

  subgraph OUT["Out of scope"]
    OCP["OpenShift / operator"]
    RPM["RPM installer"]
    V24["AAP 2.4 / pre-gateway"]
    FULL["Full installer re-run"]
    GW["Gateway OAuth registration"]
  end

  COL["redhat_official.aap_containerized_add_node"] --> IN
  COL -.->|never| OUT
```

---

## 2. Playbook flow (`playbooks/add_node.yml`)

```mermaid
flowchart TD
  V[validate_setup_dir<br/>require containerized aap_setup_dir] --> D[discover_new_nodes]
  D --> L[list_instances<br/>assert_controller_container + awx-manage]
  L --> DIFF[Diff inventory vs ready hostnames<br/>heartbeat required to skip]
  DIFF -->|targets| M[fetch_mesh_material]
  M --> E[enable_controller_listener<br/>AIO local-only to tcp-listener]
  E --> H[host_prep<br/>containerized common]
  H --> C[fetch_or_mint_certs]
  C --> R[register_instance<br/>awx-manage sequence]
  R --> I[install_receptor_node<br/>containerized_installer.receptor]
  I --> VER[verify_mesh<br/>list_instances again]
```

---

## 3. Roles

```mermaid
flowchart LR
  subgraph entry["Entry"]
    PB["playbooks/add_node.yml"]
  end

  subgraph roles["roles/"]
    R0[validate_setup_dir]
    R1[assert_controller_container]
    R2[list_instances]
    R3[discover_new_nodes]
    R4[fetch_mesh_material]
    R5[enable_controller_listener]
    R6[host_prep]
    R7[fetch_or_mint_certs]
    R8[register_instance]
    R9[install_receptor_node]
    R10[verify_mesh]
  end

  PB --> R0
  R3 --> R2
  R2 --> R1
  R8 --> R1
  R10 --> R2
```

| Role | Purpose |
|------|---------|
| `validate_setup_dir` | Require `aap_setup_dir` with `ansible.containerized_installer`; reject RPM trees |
| `assert_controller_container` | SSH ping + `podman inspect` (task container running) |
| `list_instances` | `podman exec … awx-manage list_instances` (ANSI-stripped) |
| `discover_new_nodes` | Diff `[execution_nodes]` vs ready hostnames → `aap_add_node_targets` |
| `fetch_mesh_material` | Fetch mesh CA cert/key + work public key from controller `~/aap/…` |
| `enable_controller_listener` | Optional AIO: `local-only` → `tcp-listener` |
| `host_prep` | `ansible.containerized_installer.common` on new nodes |
| `fetch_or_mint_certs` | Mint node TLS with mesh CA on installer host |
| `register_instance` | `provision_instance` → `add_receptor_address` → `register_peers` → `register_queue` |
| `install_receptor_node` | `ansible.containerized_installer.receptor` + minted certs |
| `verify_mesh` | Re-check `list_instances` for new hostnames |

---

## 4. Controller HA

Always `groups['automationcontroller'][0]`. Any controller works (`awx-manage` → shared DB); `[0]` is a stable SSH/podman target. Mesh CA is expected on each controller under the install-user home.

---

## 5. Discovery skip rule

```mermaid
flowchart TD
  INV[Inventory execution_nodes] --> CHK{Hostname has heartbeat<br/>in list_instances?}
  CHK -->|yes| SKIP[Skip - already healthy]
  CHK -->|no| ADD[Add to aap_add_node_targets]
  ADD --> NOTE[Includes provisioned-but-incomplete<br/>capacity=0 no heartbeat]
```

---

## 6. Register sequence

```mermaid
sequenceDiagram
  participant Op as Installer
  participant Ctrl as automationcontroller[0]
  participant EN as New EN/HN

  Op->>Ctrl: ping + podman inspect task container
  Op->>Ctrl: fetch mesh CA + work pubkey
  Op->>EN: host_prep (common) + mint TLS
  Op->>Ctrl: awx-manage provision_instance
  Op->>Ctrl: add_receptor_address
  Op->>Ctrl: register_peers --exact
  Op->>Ctrl: register_queue default + executionplane
  Op->>EN: containerized_installer.receptor
  Op->>Ctrl: list_instances verify
```
