# assert_controller_container

Preflight for Controller-side `awx-manage` work: require `[automationcontroller]`, SSH to inventory order `[0]`, and confirm the task container is `running`.

Used by `list_instances` and `register_instance` before `podman exec`.

## Requirements

- Inventory group `automationcontroller` (same as the containerized installer inventory).
- SSH from the installer host to `groups['automationcontroller'][0]` as the install user.
- Podman and a running controller task container on that host.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_controller_container` | `automation-controller-task` | Podman name of the controller task container |

See `meta/argument_specs.yml`.

## Dependencies

None (collection-internal).

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: redhat_official.aap_containerized_add_node.assert_controller_container
```

## License

GPL-3.0-or-later
