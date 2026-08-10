# validate_setup_dir

Validate `aap_setup_dir` as a containerized AAP setup tree (`ansible.containerized_installer` present; RPM-only trees rejected). Derive registry/image defaults and publish installer host facts on `aap_add_node_operator` for later plays.

## Requirements

- Local access to an extracted `containerized-setup-*` directory.
- Run on the installer host (typically `localhost`).

## Role Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `aap_setup_dir` | yes | — | Path to extracted containerized-setup tree |
| `aap_add_node_inventory_group` | no | `execution_nodes` | Candidate inventory group name |
| `aap_add_node_target_group` | no | `aap_add_node_targets` | Dynamic target group name |
| `aap_add_node_listener_port` | no | `27199` | Default receptor port |
| `aap_add_node_mesh_ca_cert` | no | `''` | Optional local mesh CA cert |
| `aap_add_node_mesh_ca_key` | no | `''` | Optional local mesh CA key |
| `aap_add_node_work_public_key` | no | `''` | Optional local work public key |

See `meta/argument_specs.yml`.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: localhost
  connection: local
  gather_facts: false
  roles:
    - role: redhat_official.aap_containerized_add_node.validate_setup_dir
```

## License

GPL-3.0-or-later
