# verify_mesh

After join, re-run `list_instances` and assert each host in `aap_add_node_targets` appears in the Controller instance list.

Warns (does not fail) when a hostname is registered but has no heartbeat yet.

## Requirements

- Prior discovery / join that populated `aap_add_node_targets`.
- Working `list_instances` / controller access.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_target_group` | `aap_add_node_targets` | Dynamic group of hosts that were joined |

See `meta/argument_specs.yml`.

## Dependencies

- `redhat_official.aap_containerized_add_node.list_instances`

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: redhat_official.aap_containerized_add_node.verify_mesh
```

## License

GPL-3.0-or-later
