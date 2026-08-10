# Containerized installer overlay

Drop-in files for `ansible.containerized_installer` so you can add execution/hop nodes **without** re-running full `install`.

This tree sits next to the standalone Galaxy collection (`redhat_official.aap_containerized_add_node`). Design: [INSTALLER_PLAN.md](../INSTALLER_PLAN.md). Validation: [TEST.md](../TEST.md).

**Status:** scaffold — playbook and task stubs are in place; logic still needs to be filled from the collection / installer roles (see TODOs in each file).

**Targets:** containerized AAP **2.7** first, then **2.6**. Not for RPM or OpenShift.

## Layout

```text
installer-overlay/
└── ansible.containerized_installer/     # rsync *into* the setup-tree collection
    ├── playbooks/
    │   └── add_execution_nodes.yml
    └── roles/
        ├── add_execution_nodes/         # NEW role (discovery, listener helper, verify)
        └── automationcontroller/
            └── tasks/
                └── register_execution_nodes.yml   # NEW (extract from init.yml; no deprovision)
```

After rsync, existing installer roles (`common`, `receptor`, rest of `automationcontroller`) are unchanged except for the **added** task file.

## Apply to a setup tree

```bash
SETUP=/path/to/ansible-automation-platform-containerized-setup-2.7-x
OVERLAY=/path/to/redhat_official.aap_containerized_add_node/installer-overlay/ansible.containerized_installer
DEST="${SETUP}/collections/ansible_collections/ansible/containerized_installer"

# Copy only overlay files (does not delete existing installer files)
rsync -a "${OVERLAY}/" "${DEST}/"

# Confirm playbook is visible
ls "${DEST}/playbooks/add_execution_nodes.yml"
```

From the setup tree (same style as greenfield install):

```bash
cd "${SETUP}"
# Edit inventory / inventory-growth: add hosts under [execution_nodes]
# Peers MUST be a real list in INI: receptor_peers='["peer.example.com"]'

ansible-playbook -i inventory-growth ansible.containerized_installer.add_execution_nodes
```

## Inventory notes

- Use the **same** inventory the cluster was built with (or growth inventory).
- `receptor_type=hop|execution`
- `receptor_peers='["peer.fqdn"]'` in INI (or YAML list) — not a bare hostname
- Set `routable_hostname` when `ansible_host` is an IP

## Relation to the standalone collection

| Tree | Purpose |
|------|---------|
| Repo root (Galaxy collection) | Run today via `playbooks/add_node.yml` |
| `installer-overlay/` | Shape the same capability as installer paths for upstream / local drop-in |

Prefer implementing join behavior in the overlay as it matures; keep the collection as the reference until the overlay is validated on TEST.md scenarios.

## What still needs implementing

1. `roles/add_execution_nodes/tasks/discover.yml` — `list_instances` + heartbeat diff → `execution_nodes_new`
2. `roles/add_execution_nodes/tasks/enable_controller_listener.yml` — AIO `local-only` → `tcp-listener`
3. `roles/automationcontroller/tasks/register_execution_nodes.yml` — EN/HN `awx-manage` sequence **without** migrate/deprovision (lift from `init.yml`)
4. Wire `common` + `receptor` on `execution_nodes_new` only (already sketched in the playbook)
5. `roles/add_execution_nodes/tasks/verify.yml` — post-join `list_instances` check

Reference implementations live under `../roles/` in this repo (`discover_new_nodes`, `register_instance`, `enable_controller_listener`, `verify_mesh`, …).
