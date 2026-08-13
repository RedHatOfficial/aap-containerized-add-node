# register_instance

Register an execution or hop instance the same way the containerized installer does: `awx-manage` via `podman exec` on the controller task container.

Sequence: `provision_instance` → `add_receptor_address` → `register_peers --exact` → `register_queue` (execution only: `default` + `executionplane`).

Resolves an installer-compatible instance UUID from product UUID / machine-id.

## Requirements

- Facts / vars from discovery: `aap_add_node_hostname`, `aap_add_node_type`, peers, port.
- Controller reachable for `assert_controller_container` (included).

## Role Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `aap_add_node_hostname` | yes | — | Receptor/API hostname (FQDN) |
| `aap_add_node_type` | no | `execution` | `execution` or `hop` |
| `aap_add_node_listener_port` | no | `27199` | Port advertised to Controller |
| `aap_add_node_peers` | no | `[]` | Peer hostnames for `register_peers` |
| `aap_add_node_controller_container` | no | `automation-controller-task` | Task container name |
| `aap_add_node_awx_manage_retries` | no | `5` | Retries for `awx-manage` |
| `aap_add_node_awx_manage_delay` | no | `15` | Delay between retries (seconds) |

See `meta/argument_specs.yml`.

## Dependencies

- `redhat_official.aap_containerized_add_node.assert_controller_container`

## Example Playbook

```yaml
- hosts: aap_add_node_targets
  gather_facts: true
  roles:
    - role: redhat_official.aap_containerized_add_node.register_instance
```

## License

GPL-3.0-or-later
