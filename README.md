# AAP Containerized Add Node Collection

[![CI](https://github.com/RedHatOfficial/aap-containerized-add-node/actions/workflows/ci.yml/badge.svg)](https://github.com/RedHatOfficial/aap-containerized-add-node/actions/workflows/ci.yml)

Add **Execution Nodes** and **Hop Nodes** to existing **containerized AAP 2.6+** clusters without re-running the full installer.

**Collection:** `redhat_official.aap_containerized_add_node`

## Summary

| | |
|---|---|
| **Purpose** | Day-2 mesh node addition without maintenance window |
| **Supports** | AAP 2.6+, 2.7+ containerized |
| **Node Types** | Execution nodes, Hop nodes |
| **Node OS** | RHEL 9.x, RHEL 10.x |
| **Topology** | Outbound dial (default), Inbound dial (optional) |

## Supported

| Platform | Status |
|----------|--------|
| Containerized AAP 2.6+ | Supported |
| Containerized AAP 2.7+ | Supported |
| RHEL 9 execution/hop nodes | Tested |
| RHEL 10 execution/hop nodes | Tested (S-001; T-27-AIO-EN-VIA-HN on 2.7) |

## Not Supported

| Platform | Reason |
|----------|--------|
| RPM installs | Different installer mechanics |
| OpenShift / Operator | Out of scope |
| AAP 2.5 and earlier | Out of scope (pre-2.6 / pre-gateway) |

## Current Limitations

- Requires SSH access from control host to controller and new nodes
- Controller task container must be running
- Air-gapped bundle generation not yet implemented (see [DR-001](.sdlc/decisions/open/DR-001-offline-join-bundle.md))
- Cluster topologies lab-validated on 2.7 HA (RHEL 10); 2.6 cluster still untested

## SDLC

Architecture decisions, requirements, and development phases: [.sdlc/](.sdlc/README.md)

## Prerequisites

- **Control host** runs `ansible-playbook` with this collection. It may be **any** machine with SSH to the cluster: a laptop, a gateway node, a controller, an execution/hop node, or a bastion. It does not need to be an `automationcontroller` host.
- **SSH user on `automationcontroller`:** the same **non-root install user** used for the containerized install (home has `~/aap/…`). Used for `podman exec … awx-manage` and mesh CA fetch. **No sudo** for those steps (`become: false`).
- **SSH user on new EN/HN:** same non-root install-user pattern (collection rejects root).
- **Optional sudo:** controller `firewalld` when enabling a receptor `tcp-listener` (`enable_controller_listener`).
- **`aap_setup_dir`:** extracted **containerized** setup tree including `ansible.containerized_installer`.
- **Controller task container** must be running (default name `automation-controller-task`).

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for container discovery, failed-join re-runs, and manual `deprovision_instance` rollback.

### Why this exists

The official installers can add EN/HN, but only during a full install run. This collection reuses those same steps (`awx-manage`, mesh CA minting, receptor install from `aap_setup_dir`) against **new hosts only**, so you avoid a cluster-wide maintenance window.

### Notes

- Discover, register, and verify all use **`awx-manage` on the controller** (same tooling as the installers). SSH to `automationcontroller` is required; no gateway OAuth token is needed.
- **Which controller in HA?** Roles target `groups['automationcontroller'][0]`. That is intentional: `awx-manage` writes to the shared Controller DB, so any controller works; `[0]` is just a stable pick. Mesh/platform CA is also expected on each controller.
- **Failed mid-join re-runs:** nodes are not deprovisioned on failure. A later run skips only hosts that already show a **heartbeat** in `list_instances`. Provisioned-but-incomplete nodes (no heartbeat yet) are targeted again so join can finish; `provision_instance` is idempotent.

## Approach

1. Discover missing hosts with `awx-manage list_instances`, then register with `awx-manage` on the controller
2. Mint mesh TLS + copy work public key from the existing mesh CA
3. Install receptor on the **new host only** via `ansible.containerized_installer.receptor` from `aap_setup_dir`

The maintenance window comes from running the **full** installer against every platform host — not from joining the mesh.

| Step | Where | What |
|------|--------|------|
| 1 | Controller (`awx-manage`) | `list_instances` (discover) → `provision_instance` → `add_receptor_address` → `register_peers` → `register_queue` |
| 2 | Control host (mesh CA from controller) | Mint node cert/key; copy mesh CA cert + work public key |
| 3 | New node only | Install receptor via containerized installer role from `aap_setup_dir` |
| 4 | Controller (single-node) | Enable receptor `tcp-listener` if still `local-only` |
| 5 | Controller (`awx-manage`) | `list_instances` again to verify the new hostname |

**Zero / near-zero downtime path:** new node dials **out** to an existing hop/controller listener. Existing `receptor.conf` files stay untouched.

**Inventory:** point at the **same containerized installer inventory** (all nodes, including ones you just added). The playbook diffs `[execution_nodes]` against `awx-manage list_instances` and only targets the net-new hosts. Set `receptor_peers` as a **real list** — in INI use JSON-in-quotes (`receptor_peers='["hop.example.com"]'`), or use a YAML list. Do **not** use a bare hostname or `receptor_peers=['hop.example.com']` (INI leaves those as strings; the full installer then fails with `hostvars['a']` / `hostvars['[']`). Optional overrides (CA paths, image-skip flags) stay in extra-vars/vault — not in that inventory.

**Installer directory:** also point at the extracted containerized setup tree (`aap_setup_dir`) so image tags and the `ansible.containerized_installer` collection match what that install used. Details in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Failure / rollback notes: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Status

End-to-end roles are implemented and driven by `aap_setup_dir` for version alignment (registry/image defaults + `ansible.containerized_installer.receptor`). Lab-validated on containerized AAP **2.6** and **2.7** AIO and **2.7** HA cluster (execution and hop; EN via hop). 2.6 cluster still needs validation before production use.

Each role has a `roles/<name>/README.md`. Flow overview: [docs/COLLECTION_MAP.md](docs/COLLECTION_MAP.md).

Upstream path to fold this into the containerized installer: [INSTALLER_PLAN.md](INSTALLER_PLAN.md). Drop-in file tree for local installer experiments: [installer-overlay/](installer-overlay/).

See [CHANGELOG.rst](CHANGELOG.rst) for release notes (fragments under `changelogs/fragments/`). Contribution and release process: [CONTRIBUTING.md](CONTRIBUTING.md).

## Tested against

Reusable scenario checklists, inventory sketches, and a results log: [TEST.md](TEST.md). Shared-tester workflow and `T-*`/`S-*` mapping: [.sdlc/testing/README.md](.sdlc/testing/README.md).

| Target | Execution | Hop | Parallel | Post-join full upgrade |
|--------|-----------|-----|----------|------------------------|
| Containerized AAP 2.6, AIO | :white_check_mark: Tested | :white_check_mark: Tested | :white_check_mark: Tested | :white_check_mark: **Tested** (see T-26-AIO-FULL-UPGRADE in [TEST.md](TEST.md)) |
| Containerized AAP 2.7, AIO | :white_check_mark: **Tested** (RHEL 9 + RHEL 10; see S-001 / T-27) | :white_check_mark: **Tested** (RHEL 9 + RHEL 10 hop) | :white_check_mark: **Tested** (T-27-AIO-EN-VIA-HN) | :white_large_square: Untested |
| Containerized AAP 2.6/2.7, cluster | :white_large_square: Untested | :white_check_mark: **Tested** (2.7 RHEL 10; T-27-CLU) | :white_check_mark: **Tested** (T-27-CLU-EN-VIA-HN) | :white_large_square: Untested |

## To Do

- [x] Remove the asserts and use arg spec
- [x] Reduce the number of set facts and combine them if possible

## Example Inventories

Pre-built inventory examples for common topologies in `examples/`:

| File | Topology |
|------|----------|
| `inventory-single-en.yml` | Single EN → Controller |
| `inventory-single-hn.yml` | Single HN → Controller |
| `inventory-en-via-hn.yml` | EN → HN → Controller |
| `inventory-parallel-ens.yml` | Multiple ENs → Controller |
| `inventory-fanout-behind-hop.yml` | Multiple ENs → HN → Controller |
| `inventory-multi-hop-chain.yml` | EN → HN2 → HN1 → Controller |

Copy and adapt to your environment. Key fields: `receptor_type`, `receptor_peers` (must be a list), `routable_hostname`.

## Quick start

```bash
SETUP=/path/to/ansible-automation-platform-containerized-setup-2.x

ansible-galaxy collection install -r requirements.yml
ansible-galaxy collection install --force --no-deps .

# Include installer collections for image/role parity
export ANSIBLE_COLLECTIONS_PATH="${SETUP}/collections:${ANSIBLE_COLLECTIONS_PATH}"

# 1) Add the new host to ${SETUP}/inventory under [execution_nodes]
#    Or use an example inventory as a starting point
# 2) Run — discovery targets only hosts not already in Controller
ansible-playbook playbooks/add_node.yml \
  -i "${SETUP}/inventory" \
  -e aap_setup_dir="${SETUP}" \
  -e @examples/add_node.secrets.yml

# Lab re-runs: skip bundle image copy/extract/import (assumes images already loaded)
ansible-playbook playbooks/add_node.yml ... -e aap_add_node_skip_image_load=true
```

By default (`aap_add_node_skip_image_load_if_present=true`) host_prep also auto-skips that path when the receptor + EE images are already present on the node.

### Playbook flow

1. `validate_setup_dir` — require containerized `aap_setup_dir`
2. `discover_new_nodes` — diff `[execution_nodes]` vs `awx-manage list_instances`
3. `fetch_mesh_material` / `enable_controller_listener` — mesh CA + tcp-listener if needed
4. `host_prep` — linger, firewall, images from `aap_setup_dir`
5. `fetch_or_mint_certs` — sign node cert with mesh CA
6. `register_instance` — `awx-manage` via controller task container
7. `install_receptor_node` / `verify_mesh` — receptor install + `list_instances` check


## Collection layout

```
galaxy.yml
README.md
playbooks/add_node.yml
roles/
  validate_setup_dir/
  assert_controller_container/  # podman inspect preflight before awx-manage
  list_instances/            # awx-manage list_instances helper
  discover_new_nodes/
  fetch_mesh_material/
  host_prep/
  fetch_or_mint_certs/
  register_instance/
  install_receptor_node/
  verify_mesh/
meta/runtime.yml
examples/
docs/
ignore/                      # local TARs only (gitignored)
```

Troubleshooting (SSH, container name, rollback): [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Reference material examined (not runtime targets)

| Flavor | Versions | Role |
|--------|----------|------|
| Containerized setup | 2.6, 2.7 | **Supported target** |
| Containerized setup | 2.5 and earlier | Historical research only — not supported |
| RPM setup | 2.5, 2.6 | Historical research only — not supported |
| OpenShift install bundles | 2.5, 2.6, 2.7 | Reference only — how receptor join is packaged elsewhere |

See [docs/FINDINGS.md](docs/FINDINGS.md) for the full analysis.
