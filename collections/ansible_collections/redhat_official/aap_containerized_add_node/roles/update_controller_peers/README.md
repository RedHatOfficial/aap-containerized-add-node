# update_controller_peers

Opt-in **inbound dial**: add `tcp-peer` entries on the controller `receptor.conf`
so the controller dials new nodes. Restarts receptor and causes brief mesh
disruption (about 5–10 seconds).

Default topology is **outbound** (new nodes dial the controller). Enable this
role only when firewall policy blocks outbound dial and a maintenance window is
acceptable.

## Requirements

- Play runs on `automationcontroller` with `gather_facts: true`
- `aap_add_node_enable_controller_peer=true`
- Dynamic group `aap_add_node_targets` populated (from discover)

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_enable_controller_peer` | `false` | Enable inbound dial / receptor edits |
| `aap_add_node_listener_port` | `27199` | Default peer listener port |
| `aap_add_node_receptor_config_dir` | `''` | Path to receptor config dir; empty resolves to `<remote user home>/aap/receptor/etc` in tasks |

See `meta/argument_specs.yml`.

## Dependencies

None. Invoked from `playbooks/add_node.yml` when inbound dial is enabled.

## Example Playbook

```yaml
- hosts: automationcontroller
  gather_facts: true
  roles:
    - role: redhat_official.aap_containerized_add_node.update_controller_peers
      vars:
        aap_add_node_enable_controller_peer: true
```

## License

GPL-3.0-or-later
