# Collection Conventions

This collection follows AAP containerized installer conventions for compatibility and consistency.

## Variable Naming

### Inventory Variables (match installer)

Use these variable names in inventory to match the containerized installer:

| Variable | Type | Description |
|----------|------|-------------|
| `receptor_type` | string | Node type: `execution` or `hop` (default: `execution`) |
| `receptor_peers` | list | List of peer hostnames to connect to |
| `receptor_port` | int | Receptor listener port (default: `27199`) |
| `routable_hostname` | string | FQDN for mesh addressing (default: `inventory_hostname`) |

**Example inventory:**
```ini
[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]' routable_hostname=exec1.example.com
hop1.example.com receptor_type='hop' receptor_peers='["controller.example.com"]'
```

### Role Variables (collection-specific)

Variables specific to this collection use `aap_add_node_` prefix to avoid conflicts:

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_controller_container` | `automation-controller-task` | Controller container name |
| `aap_add_node_awx_manage_retries` | `5` | Retry count for awx-manage commands |
| `aap_add_node_instance_groups` | `[]` | Custom instance groups to add node to |

## Registration (awx-manage only)

Instance join matches the containerized installer: `awx-manage` via `podman exec` on the
controller task container. There is no Controller API path for provisioning, receptor address,
or peer registration.

| Step | Mechanism |
|------|-----------|
| Provision instance | `awx-manage provision_instance` |
| Register receptor address | `awx-manage add_receptor_address` |
| Register peers | `awx-manage register_peers` |
| Register queues / instance groups | `awx-manage register_queue` |

### awx-manage commands (match installer)

```bash
# Provision instance (create in DB)
awx-manage provision_instance --hostname=<fqdn> --uuid=<uuid> --node_type=<type>

# Register receptor address
awx-manage add_receptor_address --instance=<fqdn> --address=<fqdn> --port=27199 --canonical

# Register peers
awx-manage register_peers <fqdn> --exact <peer1>,<peer2>

# Register to queue/instance group
awx-manage register_queue --queuename=<name> --hostname=<fqdn>
```

## Instance Groups

### Inventory-based (RPM installer style)

```ini
[instance_group_production]
exec1.example.com
exec2.example.com
```

Groups with `instance_group_` prefix are parsed and assigned via `awx-manage register_queue`.

## File/Directory Conventions

Match installer paths:

| Path | Purpose |
|------|---------|
| `~/aap/receptor/etc/` | Receptor config directory |
| `~/.config/systemd/user/` | User systemd units |
| `~/.config/containers/` | Podman configuration |

## Collection Structure

```
redhat_official.aap_containerized_add_node/
├── galaxy.yml
├── playbooks/
│   ├── add_node.yml          # Main entry point
│   └── validate_mesh.yml     # Post-install validation
├── roles/
│   ├── discover_new_nodes/   # Find nodes not in controller
│   ├── register_instance/    # awx-manage registration
│   ├── install_receptor_node/# Receptor container setup
│   └── ...
└── docs/
    └── CONVENTIONS.md        # This file
```

## Notes

- Always test with `--check --diff` before full runs
- Run `playbooks/preflight.yml` before add_node.yml in change windows

## Control host and `delegate_to`

Plays that run on `localhost` with `connection: local` execute on the machine where you invoke `ansible-playbook`. That machine may be a gateway, controller, or external host.

**Rule:** Any task with `delegate_to: <inventory_host>` must set:

```yaml
connection: "{{ hostvars[<inventory_host>].ansible_connection | default('ssh') }}"
```

Use `connection: local` only for `delegate_to: localhost` tasks that must touch files on the control host (for example mesh material under `bundles/_mesh_material/`).

Reference: `vars/aap_add_node_delegate.yml` in this collection.

## Controller target (HA)

Optional `aap_add_node_controller_target` overrides `groups['automationcontroller'][0]` for
`awx-manage`, mesh material fetch, preflight checks, and bundle pre-registration. Use when
the first controller in inventory is down or unreachable but another controller is healthy.

```yaml
-e aap_add_node_controller_target=cn02.example.com
```

Default is empty (use inventory order). Defined in `roles/list_instances/defaults/main.yml`.

## Peer Topology

See [TOPOLOGY.md](TOPOLOGY.md) for detailed peer direction documentation.

| Mode | Variable | Disruption |
|------|----------|------------|
| Outbound (default) | `receptor_peers` | None |
| Inbound (optional) | `aap_add_node_enable_controller_peer=true` | 5-10s per node |
