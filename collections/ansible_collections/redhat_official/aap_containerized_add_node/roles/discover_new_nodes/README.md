# discover_new_nodes

Diff inventory execution/hop candidates against Controller ready instances and publish hosts that need joining.

Skips only hostnames that already show a **heartbeat** in `list_instances` (provisioned-but-incomplete nodes are re-targeted). Adds targets to the dynamic group `aap_add_node_targets` with normalized `aap_add_node_hostname`, `aap_add_node_type`, peers, and listener port.

## Requirements

- Inventory group for candidates (default `execution_nodes`) with at least one host.
- Working `list_instances` / controller preflight (included by this role).

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_inventory_group` | `execution_nodes` | Inventory group of EN/HN candidates |
| `aap_add_node_target_group` | `aap_add_node_targets` | Dynamic group created for hosts to join |
| `aap_add_node_listener_port` | `27199` | Default receptor port applied to new hosts |

Per-host inventory fields consumed when present: `routable_hostname`, `node_type` / `receptor_type`, `receptor_port` / `listener_port`, `receptor_peers` / `aap_add_node_peers`.

`receptor_peers` / `aap_add_node_peers` must be a **list** (installer-compatible):

- **INI:** `receptor_peers='["peer.example.com"]'` (JSON array inside quotes — Ansible parses a real list)
- **YAML:** `receptor_peers: [peer.example.com]` or a block list

Do **not** use `receptor_peers=peer.example.com` (bare string) or `receptor_peers=['peer.example.com']` (INI still stores a string). Those break full `ansible.containerized_installer.install` with `hostvars['a']` / `hostvars['[']`.

See `meta/argument_specs.yml`.

## Dependencies

- `redhat_official.aap_containerized_add_node.list_instances`

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: redhat_official.aap_containerized_add_node.discover_new_nodes
```

## License

GPL-3.0-or-later
