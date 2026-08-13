# preflight

Run installer, controller, inventory, connectivity, and machine-id checks before
adding execution or hop nodes. Enabled by default; opt out with
`aap_add_node_preflight_enabled=false`.

## Requirements

- Inventory with `automationcontroller` and candidate nodes in
  `aap_add_node_inventory_group` (default `execution_nodes`)
- `ansible.containerized_installer` available on `ANSIBLE_COLLECTIONS_PATH`
- For online installs: `registry_username` / `registry_password` in inventory
  (skipped when `aap_add_node_bundle_install=true`)

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_preflight_enabled` | `true` | When false, skip all preflight checks |
| `aap_add_node_preflight_timeout` | `30` | TCP probe timeout (seconds) |
| `aap_add_node_inventory_group` | `execution_nodes` | Candidate EN/HN inventory group |
| `aap_add_node_listener_port` | `27199` | Receptor port for connectivity checks |
| `aap_add_node_bundle_install` | `false` | Skip registry credential checks when true |

See `meta/argument_specs.yml`.

## Dependencies

None (standalone). Invoked from `playbooks/preflight.yml` and
`playbooks/add_node.yml`.

## Example Playbook

```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: redhat_official.aap_containerized_add_node.preflight
```

## License

GPL-3.0-or-later
