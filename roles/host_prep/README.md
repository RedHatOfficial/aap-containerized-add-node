# host_prep

Prepare a new execution/hop host with `ansible.containerized_installer.common` (podman, TLS CA trust, optional image load), using the cluster mesh CA public certificate instead of generating a new platform CA.

Asserts a non-localhost hostname and non-root install user. Optional version-skew soft-check against an existing inventory EN.

## Requirements

- Target hosts in `aap_add_node_targets` (or equivalent), managed as non-root.
- `aap_setup_dir` with `ansible.containerized_installer` on `ANSIBLE_COLLECTIONS_PATH`.
- Mesh CA certificate path (from `fetch_mesh_material`). The mesh CA private key is **not** copied to EN/HN; it remains on the control host for `fetch_or_mint_certs`.

## Role Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `aap_setup_dir` | yes | — | Extracted containerized-setup tree |
| `aap_add_node_mesh_ca_cert` | yes | — | Cluster mesh/platform CA public cert |
| `aap_add_node_type` | no | `execution` | `execution` or `hop` |
| `aap_add_node_bundle_install` | no | `false` | Offline bundle present in setup tree |
| `aap_add_node_listener_port` | no | `27199` | Default receptor port |
| `aap_add_node_skip_image_load` | no | `false` | Force-skip image copy/load/pull |
| `aap_add_node_skip_image_load_if_present` | no | `true` | Auto-skip when images already exist |
| `aap_add_node_check_version_skew` | no | `true` | Soft-check vs existing EN |
| `aap_add_node_fail_on_version_skew` | no | `false` | Fail on skew instead of warn |

See `meta/argument_specs.yml`.

## TLS behaviour

Installer `common` `tls.yml` imports a CA only when **both** `ca_tls_cert` and `ca_tls_key` are set, or generates one when **neither** is set. Passing cert without key skips both paths.

This role pre-seeds `~/aap/tls/ca.cert` from `aap_add_node_mesh_ca_cert` and does not pass `ca_tls_*` vars to `common`, so `update-ca-trust` succeeds on clean nodes without distributing the mesh CA private key.

## Dependencies

- `ansible.containerized_installer.common` (from `aap_setup_dir/collections`)

## Example Playbook

```yaml
- hosts: aap_add_node_targets
  become: false
  gather_facts: true
  roles:
    - role: redhat_official.aap_containerized_add_node.host_prep
```

## License

GPL-3.0-or-later
