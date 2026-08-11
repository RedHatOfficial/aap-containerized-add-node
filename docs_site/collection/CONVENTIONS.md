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

### API Mode Variables

For API-based instance group management (instead of awx-manage):

| Variable | Description |
|----------|-------------|
| `aap_add_node_controller_host` | AAP URL (e.g., `https://controller.example.com`) |
| `aap_add_node_controller_username` | Admin username |
| `aap_add_node_controller_password` | Admin password |
| `aap_add_node_validate_certs` | Validate TLS certs (default: `true`) |

## Platform Collections Usage

### Prefer Platform Collections

Use official platform collections where possible:

| Task | Collection | Module | Status |
|------|------------|--------|--------|
| Create Instance Groups | `ansible.controller` | `instance_group` | ✅ Used (API mode) |
| Update instance settings | `ansible.controller` | `instance` | ✅ Used (API mode) |
| Provision instance | N/A | N/A | ❌ Not available - use awx-manage |
| Register receptor address | N/A | N/A | ❌ Not available - use awx-manage |
| Register peers | N/A | N/A | ❌ Not available - use awx-manage |
| Gateway tokens | `ansible.platform` | `token` | ⚠️ Does NOT work with controller API |

### When to Use awx-manage

Use `awx-manage` via podman exec when:

1. **Instance provisioning** - `ansible.controller.instance` cannot create new instances
2. **Receptor address registration** - No API equivalent
3. **Peer registration** - No API equivalent
4. **No API credentials** - Running from controller without network API access

### awx-manage Commands (match installer)

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

Groups with `instance_group_` prefix are parsed and created automatically.

### API vs awx-manage

| Mode | When Used | Collection |
|------|-----------|------------|
| API | `aap_add_node_controller_host` + credentials set | `ansible.controller.instance_group` |
| awx-manage | Default (no API credentials) | None (podman exec) |

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

- Gateway tokens (`ansible.platform.token`) do NOT work with controller API
- Controller API requires basic auth or controller-specific OAuth tokens
- Always test with `--check --diff` before full runs
- Run `playbooks/preflight.yml` before add_node.yml in change windows

## Peer Topology

See [TOPOLOGY.md](TOPOLOGY.md) for detailed peer direction documentation.

| Mode | Variable | Disruption |
|------|----------|------------|
| Outbound (default) | `receptor_peers` | None |
| Inbound (optional) | `aap_add_node_enable_controller_peer=true` | 5-10s per node |
