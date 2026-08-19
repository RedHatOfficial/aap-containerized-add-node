# Architecture: additive EN/HN join for containerized AAP

> **Scope:** containerized AAP **2.6+** only. RPM is **not** supported.
> OpenShift/operator-based node setup should use the native AAP UI workflow:
> [AAP 2.6](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/administer-proc_set_up_virtual_machines),
> [AAP 2.7](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.7/administer-proc_set_up_virtual_machines).
> Historical installer research (including RPM) lives in [FINDINGS.md](FINDINGS.md).

## Goals

1. Add execution or hop nodes on **containerized** AAP without re-running the full installer.
2. Avoid restarting gateway / controller / hub / EDA / redis.
3. Reuse the containerized installer join pattern (mesh cert tree + `ansible.containerized_installer.receptor` from `aap_setup_dir`).
4. Discover / register / verify via **`awx-manage`** on `automationcontroller` (SSH + `podman exec`; no gateway token).
5. Reuse the **installer inventory** as topology source of truth; only act on net-new / incomplete hosts.

## Non-goals

- OpenShift / operator clusters
- RPM installer trees
- AAP 2.5 and earlier (including pre-gateway / 2.4)
- Greenfield full installs (`setup.sh` / full `install.yml`)
- Automated deprovision / rollback playbook (manual steps in [TROUBLESHOOTING.md](TROUBLESHOOTING.md))
- Gateway OAuth / `ansible.controller.instance` registration
- Putting mesh CA private key paths into the installer inventory

## Inventory model

**Source of truth = the same containerized installer inventory** (controllers, hops, execution nodes — including hosts you are about to add).

1. Add the new host(s) to `[execution_nodes]` (`receptor_type='hop'|'execution'`, `receptor_peers` as a **real list** — INI `receptor_peers='["peer.example.com"]'` or YAML list, etc.).
2. Playbook diffs inventory against `awx-manage list_instances`.
3. Dynamic group `aap_add_node_targets` = hosts without a **heartbeat** yet.
4. Mint / register / receptor install run **only** against that group.
5. Existing nodes are context (peers, mesh CA) and are not reconfigured unless `enable_controller_listener` swaps AIO `local-only` → `tcp-listener`.

```
┌───────────────────┐     ┌─────────────────────────┐
│ Installer         │     │ awx-manage              │
│ inventory         │────▶│ list_instances          │
└───────────────────┘     └───────────┬─────────────┘
         │                            │
         │                            ▼
         │                  ┌─────────────────────┐
         │                  │       Diff          │
         │                  └─────────┬───────────┘
         │                            │
         ▼                            ▼
┌───────────────────┐     ┌─────────────────────────┐
│ Peer / CA context │     │ aap_add_node_targets    │
└───────────────────┘     └─────────┬───────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐  ┌─────────────┐  ┌────────────┐
              │Mint certs│  │awx-manage   │  │Install     │
              │          │  │register     │  │receptor    │
              └──────────┘  └─────────────┘  └────────────┘
```

### Out of the installer inventory

| Material | Where |
|----------|--------|
| Mesh CA private key | Fetched to control host `bundles/_mesh_material/` or override paths |
| `aap_add_node_*` toggles | Extra-vars / vault (`examples/add_node.secrets.yml`) |

```bash
ansible-playbook playbooks/add_node.yml \
  -i /path/to/containerized-setup/inventory \
  -e aap_setup_dir=/path/to/containerized-setup \
  -e @examples/add_node.secrets.yml
```

## Installer directory (`aap_setup_dir`)

Required: extracted **containerized** setup tree with `ansible.containerized_installer`.

| Mode | What it supplies |
|------|------------------|
| Online | Registry/image defaults from installer `common` role |
| Bundle | `bundle/images/*.tar.gz` via `bundle_dir` / `bundle_install` |

```bash
export ANSIBLE_COLLECTIONS_PATH="${aap_setup_dir}/collections:${ANSIBLE_COLLECTIONS_PATH}"
```

**Never invoke** `setup.sh` / full `install.yml` from that tree for an additive join.

## Controller HA

Tasks use `groups['automationcontroller'][0]`. Any controller is fine because `awx-manage` updates the **shared Controller DB**; `[0]` is only a stable SSH/`podman exec` target. Mesh CA is expected under each controller install-user home (`~/aap/tls/…`).

## Control host

The **control host** is wherever you run `ansible-playbook` — not necessarily a controller. Supported patterns:

| Control host | Typical inventory | Notes |
|--------------|-------------------|--------|
| Laptop / bastion | Full cluster inventory; SSH to all targets | Default mental model |
| Gateway (`automationgateway`) | Often `ansible_connection=local` on the gateway host | Plays use `connection: local`; delegated tasks must SSH to controllers and new nodes |
| Controller (AIO or HA) | Controller may have `ansible_connection=local` | Delegation to self uses local connection from inventory |
| Execution / hop node | Same as laptop if SSH keys reach peers | No requirement to run from a controller |

Early plays use `hosts: localhost` + `connection: local` on the control machine. Remote work (`awx-manage`, mesh CA fetch, EN/HN preflight) uses `delegate_to` with `connection: "{{ hostvars[target].ansible_connection | default('ssh') }}"`. See [CONVENTIONS.md](CONVENTIONS.md).

## Zero / near-zero downtime

Prefer **outbound peer dial**: new node → existing hop/controller listener (`receptor_peers`). Existing `receptor.conf` files stay untouched.

Inbound dial (controllers peer to the new node) requires controller receptor edits/reloads — supported only for the AIO `local-only` → `tcp-listener` helper.

## Failed joins

- No auto-deprovision on failure.
- Re-run skips hosts that already show a **heartbeat**.
- Provisioned-but-incomplete hosts (no heartbeat) are re-targeted; `provision_instance` is idempotent.
- Manual undo: `awx-manage deprovision_instance --hostname=…` — see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Role ownership

| Concern | Owner |
|---------|--------|
| Setup tree validation | `validate_setup_dir` |
| SSH + task container preflight | `assert_controller_container` |
| Discovery / verify | `list_instances` + `discover_new_nodes` / `verify_mesh` |
| Mesh CA + work pubkey | `fetch_mesh_material` |
| Node TLS mint | `fetch_or_mint_certs` |
| Host prep / images | `host_prep` → `ansible.containerized_installer.common` |
| DB registration | `register_instance` → `awx-manage` |
| Receptor container | `install_receptor_node` → `ansible.containerized_installer.receptor` |

See [COLLECTION_MAP.md](COLLECTION_MAP.md) for mermaid diagrams of the playbook flow.

## Known gaps

- Cluster (multi-controller) topologies lab-validated on containerized AAP 2.7 (RHEL 10 HA, 2026-08-12). 2.6 cluster still open.
- No automated integration tests against a live AAP cluster (CI covers lint/build/changelog).
