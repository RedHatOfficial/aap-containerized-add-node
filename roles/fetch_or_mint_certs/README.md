# fetch_or_mint_certs

Mint per-host receptor TLS using the cluster mesh CA (`ownca`), matching containerized installer SAN / node-id OID behavior.

Writes a bundle under `aap_add_node_bundle_root/<hostname>/` and publishes `aap_add_node_bundle_dir` plus `custom_*` path facts for `install_receptor_node`.

## Requirements

- `community.crypto` (collection dependency).
- Mesh CA cert/key from `fetch_mesh_material` (or overrides).
- `aap_add_node_hostname` set (typically by `discover_new_nodes` / `add_host`).

## Role Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `aap_add_node_hostname` | yes | — | CN / SAN / receptor node id |
| `aap_add_node_mesh_ca_cert` | yes | — | Mesh CA certificate (ownca) |
| `aap_add_node_mesh_ca_key` | yes | — | Mesh CA private key (ownca) |
| `aap_add_node_work_public_key` | no | `''` | Copied for execution nodes when set |
| `aap_add_node_bundle_root` | no | `{{ playbook_dir }}/../../bundles` | Bundle parent directory |
| `aap_add_node_tls_bits` | no | `4096` | RSA key size |
| `aap_add_node_type` | no | `execution` | `execution` or `hop` |

See `meta/argument_specs.yml`.

## Dependencies

- `community.crypto`

## Example Playbook

```yaml
- hosts: aap_add_node_targets
  tasks:
    - ansible.builtin.include_role:
        name: redhat_official.aap_containerized_add_node.fetch_or_mint_certs
        apply:
          delegate_to: localhost
```

## License

GPL-3.0-or-later
