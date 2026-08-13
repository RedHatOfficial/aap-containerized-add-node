# list_instances

Run `awx-manage list_instances` inside the controller task container via `podman exec`, with color disabled and ANSI stripped from stdout.

Publishes:

- `aap_add_node_list_instances_stdout`
- `aap_add_node_existing_hostnames`
- `aap_add_node_ready_hostnames` (non-DISABLED lines with `heartbeat=`)

## Requirements

- Same controller SSH / container prerequisites as `assert_controller_container` (included by this role).

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_controller_container` | `automation-controller-task` | Podman name of the controller task container |

See `meta/argument_specs.yml`.

## Dependencies

- `redhat_official.aap_containerized_add_node.assert_controller_container`

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: redhat_official.aap_containerized_add_node.list_instances
```

## License

GPL-3.0-or-later
