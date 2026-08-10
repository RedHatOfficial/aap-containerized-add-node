# fetch_mesh_material

Fetch mesh CA cert/key and work signing public key from the first `automationcontroller` host (install-user home), or keep user-supplied override paths when already set.

Publishes paths on `aap_add_node_control` for later plays (`host_prep`, `fetch_or_mint_certs`).

## Requirements

- `[automationcontroller]` in inventory when overrides are empty.
- SSH to `groups['automationcontroller'][0]` as the install user.
- Controller paths under `~/aap/tls/` and `~/aap/receptor/etc/` (containerized defaults).

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_mesh_ca_cert` | `''` | Local cert path; empty → fetch |
| `aap_add_node_mesh_ca_key` | `''` | Local key path; empty → fetch |
| `aap_add_node_work_public_key` | `''` | Local work pubkey; empty → fetch |
| `aap_add_node_material_dir` | `{{ playbook_dir }}/../../bundles/_mesh_material` | Local store for fetched files |
| `aap_add_node_remote_mesh_ca_cert` | `aap/tls/ca.cert` | Remote path under install-user home |
| `aap_add_node_remote_mesh_ca_key` | `aap/tls/ca.key` | Remote path under install-user home |
| `aap_add_node_remote_work_public_key` | `aap/receptor/etc/signing_public.pem` | Remote path under install-user home |

See `meta/argument_specs.yml`.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: redhat_official.aap_containerized_add_node.fetch_mesh_material
```

## License

GPL-3.0-or-later
