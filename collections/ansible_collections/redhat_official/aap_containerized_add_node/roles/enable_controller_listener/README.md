# enable_controller_listener

On AIO / single-controller installs, receptor often starts as `local-only`. This role swaps that for a `tcp-listener` (and opens the firewall port) so new nodes can dial out to the controller.

Skipped when a listener already exists or when `aap_add_node_enable_controller_listener` is false.

## Requirements

- Run against `automationcontroller` hosts (gather facts).
- Install-user home with `~/aap/receptor/etc/receptor.conf`.
- `become` available if firewalld must open the listener port.

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_listener_port` | `27199` | Receptor listener port |
| `aap_add_node_enable_controller_listener` | `true` | When false, skip rewriting `receptor.conf` |
| `receptor_protocol` | `tcp` | Listener protocol |
| `receptor_firewall_zone` | `public` | Firewalld zone for the port |

See `meta/argument_specs.yml`.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: automationcontroller
  gather_facts: true
  roles:
    - role: redhat_official.aap_containerized_add_node.enable_controller_listener
```

## License

GPL-3.0-or-later
