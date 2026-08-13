# add_execution_nodes — change log and variable map

Documents what `playbooks/add_execution_nodes.yml` adds to `ansible.containerized_installer`, what it **does not** modify, and how it uses the **same inventory** as greenfield `install`.

---

## Design principle: additive files only

The growth playbook **does not edit** any pre-existing installer role, playbook, or template. Existing `install.yml` behaviour is unchanged.

| Category | Action |
|----------|--------|
| New playbook | `playbooks/add_execution_nodes.yml` |
| New role | `roles/add_execution_nodes/` |
| New task file under existing role | `roles/automationcontroller/tasks/register_execution_nodes.yml` (thin include) |
| Existing installer files | **Not modified** |

---

## New files (by path)

### Playbook

| File | Purpose |
|------|---------|
| `playbooks/add_execution_nodes.yml` | Add execution/hop nodes to an existing mesh without re-running full install |

### Role `add_execution_nodes` (new)

| File | Purpose |
|------|---------|
| `defaults/main.yml` | Growth-playbook knobs: serial, preflight toggle, material paths, image-skip |
| `handlers/main.yml` | Receptor restart (opt-in inbound dial only) |
| `tasks/preflight.yml` | Early validation |
| `tasks/execution_node_checks.yml` | Per-EN SSH, DNS, machine-id |
| `tasks/discover.yml` | Heartbeat diff → `execution_nodes_new` |
| `tasks/list_instances.yml` | `awx-manage list_instances` |
| `tasks/assert_controller.yml` | SSH + task container |
| `tasks/fetch_mesh_material.yml` | Fetch mesh CA + work pubkey from controller |
| `tasks/enable_controller_listener.yml` | AIO `local-only` → `tcp-listener` |
| `tasks/image_skip.yml` | Skip image load when images present |
| `tasks/host_prep.yml` | Wire inventory vars → `import_role: common` |
| `tasks/mint_certs.yml` | Mint per-node TLS on ansible control host |
| `tasks/register.yml` | `awx-manage` registration sequence |
| `tasks/uuid.yml` | Instance UUID |
| `tasks/discover_instance_groups.yml` | `instance_group_*` inventory groups |
| `tasks/instance_groups.yml` | Custom instance groups |
| `tasks/install_receptor.yml` | Wire inventory vars → `import_role: receptor` |
| `tasks/update_controller_peers.yml` | Opt-in inbound dial (**causes disruption**) |
| `tasks/verify.yml` | Post-join `list_instances` assert |

### Existing role — one new task file

| File | Notes |
|------|-------|
| `roles/automationcontroller/tasks/register_execution_nodes.yml` | Include → `add_execution_nodes/tasks/register.yml`. **Does not change** `init.yml`. |

---

## Pre-existing installer code — not modified

These paths are **unchanged**. The growth playbook calls them via `import_role` with variables from inventory:

| Existing path | How growth playbook uses it |
|---------------|----------------------------|
| `roles/common/` | `host_prep.yml` → `import_role: common` on `execution_nodes_new` only |
| `roles/receptor/` | `install_receptor.yml` → `import_role: receptor` on `execution_nodes_new` only |
| `roles/automationcontroller/tasks/init.yml` | **Not called** — registration uses `register.yml` instead (no migrate/deprovision) |
| `roles/preflight/` | **Not called** — growth preflight is in `add_execution_nodes/tasks/preflight.yml` |
| `playbooks/install.yml` | Unchanged — still full-platform install |
| `roles/receptor/templates/receptor.conf.j2` | Used indirectly when `receptor` role runs on new nodes |
| `roles/receptor/tasks/facts.yml` | Not run on existing controllers during outbound-dial growth |

### Follow-up work for a full installer merge

1. **Split** EN/HN registration out of `init.yml` so `install` and `add_execution_nodes` share one task include.
2. **Peer policy** — document outbound dial as default growth topology; avoid rewriting controller `receptor.conf` on existing nodes.

---

## Inventory variables — reuse vs growth-only

The growth playbook uses the **same inventory file** as greenfield install (`inventory` or `inventory-growth`). Most variables already live there; the playbook reads them instead of duplicating them.

### From installer inventory (reused as-is)

| Variable | Typical location | Used by |
|----------|------------------|---------|
| `receptor_type` | Per EN/HN host | `register.yml`, `install_receptor.yml`, `mint_certs.yml` |
| `receptor_peers` | Per EN/HN host (must be a **list**) | Discovery, `register_peers`, `receptor` role |
| `receptor_port` | Per host or `[all:vars]` | Registration, receptor install, peer dial |
| `receptor_protocol` | Per host / controller | `enable_controller_listener`, peer dial |
| `receptor_firewall_zone` | `[all:vars]` | Listener enablement firewalld |
| `routable_hostname` | Per host when `ansible_host` is IP | TLS SAN, `awx-manage` hostname |
| `receptor_address` | Optional per peer host | TCP dial address override |
| `bundle_install` | `[all:vars]` | `host_prep` → `common` |
| `bundle_dir` | `[all:vars]` | `host_prep` → `common` (fallback: `<setup>/bundle`) |
| `registry_username` / `registry_password` | `[all:vars]` | Preflight (online install) |
| `registry_url` | `[all:vars]` | Image skip probe, receptor image ref |
| `registry_ns_aap` | `[all:vars]` | Image skip probe, receptor image ref |
| `receptor_image` | `[all:vars]` or per host | Image skip, receptor install |
| `ee_minimal_image` / `ee_supported_image` | `[all:vars]` | Image skip probe |
| `container_pull_images` | `[all:vars]` | `host_prep` → `common` |
| `registry_auth` | `[all:vars]` | `host_prep` → `common` |
| `instance_group_*` | Inventory groups | Optional custom instance groups |

INI example:

```ini
[execution_nodes]
en-01.example.com ansible_host=10.0.0.5 receptor_type=execution \
  receptor_peers='["controller.example.com"]' routable_hostname=en-01.example.com
```

### Growth-playbook-only variables (`add_execution_nodes_*`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `add_execution_nodes_preflight_enabled` | `true` | Skip with `-e add_execution_nodes_preflight_enabled=false` |
| `add_execution_nodes_enable_controller_peer` | `false` | **Opt-in** inbound dial — causes controller receptor restart |
| `add_execution_nodes_serial_receptor` | `1` | Serial receptor install (chain topologies) |
| `add_execution_nodes_skip_image_load` | `false` | Force-skip image copy/pull on new nodes |
| `add_execution_nodes_skip_image_load_if_present` | `true` | Auto-skip when images already loaded |
| `add_execution_nodes_enable_controller_listener` | `true` | AIO `local-only` → `tcp-listener` |
| `add_execution_nodes_inventory_group` | `execution_nodes` | Source inventory group |
| `add_execution_nodes_target_group` | `execution_nodes_new` | Dynamic join targets |

### Runtime-only (not in inventory)

Fetched or computed during the playbook; stored on synthetic host `add_execution_nodes_control`:

| Fact | Set by | Purpose |
|------|--------|---------|
| `add_execution_nodes_has_work` | `discover.yml` | Gate downstream plays |
| `add_execution_nodes_mesh_ca_cert` | `fetch_mesh_material.yml` | Prevent new CA generation on EN |
| `add_execution_nodes_mesh_ca_key` | `fetch_mesh_material.yml` | Cert minting on control host |
| `add_execution_nodes_work_public_key` | `fetch_mesh_material.yml` | Execution-node signing |
| `add_execution_nodes_bundle_dir` | `mint_certs.yml` | Per-host minted TLS tree |

---

## Downtime profile (outbound dial default)

| Action | Hosts affected | Disruption |
|--------|----------------|------------|
| Preflight / discover / fetch mesh | None on cluster | None |
| Enable listener (AIO only) | Controller receptor | **~5–10s** on controller when flipping `local-only` → `tcp-listener` (first EN into single-node mesh) |
| `common` on new nodes | `execution_nodes_new` only | None on existing stack |
| Mint certs | Ansible control host | None on cluster |
| `awx-manage` register | Controller DB only | None on receptor mesh |
| `receptor` on new nodes | New nodes only | None on existing mesh |
| `update_controller_peers` | Controller receptor | **Yes** — opt-in only (`add_execution_nodes_enable_controller_peer=true`) |
| Verify | Read-only | None |

**Default path (outbound dial):** new nodes dial to existing listeners via `receptor_peers`. Existing controller/hop `receptor.conf` files are **not** rewritten.

---

## Play order

1. Preflight
2. Discover → `execution_nodes_new`
3. Fetch mesh material
4. Enable controller listener (if AIO + has work)
5. `common` via `host_prep`
6. Mint certs (control host)
7. Register (`serial: 1`)
8. `receptor` via `install_receptor` (`serial: 1` default)
9. Update controller peers (**opt-in**)
10. Verify

---

## Branch-specific defaults

| Branch | `registry_ns_aap` fallback |
|--------|---------------------------|
| `stable-2.7` | `ansible-automation-platform-27` |
| `stable-2.6` | `ansible-automation-platform-26` |

Task logic is otherwise identical; image/registry naming comes from inventory when present.

---

## Not in scope for this playbook

| Feature | Reason |
|---------|--------|
| Offline bundle generation | Separate workflow |
| Functional mesh job validation | Separate playbook |
