# generate_bundle

Build a self-contained offline join bundle for air-gapped execution or hop node
provisioning. The bundle includes pre-minted TLS material, `receptor.conf`, a local
`install.yml` playbook, and optional container images.

Typical workflow:

1. Run `playbooks/generate_bundle.yml` on a control host (SSH to controller only).
2. Transfer the archive to the target node over an approved channel.
3. On the target node, extract and run `ansible-playbook -c local install.yml`.

## Requirements

- `[automationcontroller]` in inventory.
- Mesh CA cert/key available locally (the `generate_bundle.yml` playbook runs
  `fetch_mesh_material` first).
- Controller task container running for optional `awx-manage` pre-registration.
- Target hostname and `receptor_peers` provided as extra-vars (see playbook).

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_target_hostname` | — | FQDN of the bundle target node (required) |
| `aap_add_node_receptor_peers` | — | List of peer hostnames for outbound dial (required) |
| `aap_add_node_target_type` | `execution` | `execution` or `hop` |
| `aap_add_node_bundle_output_dir` | `{{ playbook_dir }}/offline-bundles` | Output directory for archives |
| `aap_add_node_bundle_include_images` | `false` | Include receptor image in bundle (~500MB) |
| `aap_add_node_bundle_format` | `tar.gz` | Archive format: `tar.gz` or `zip` |
| `aap_add_node_receptor_port` | `27199` | Receptor listener port for the target |
| `aap_add_node_tls_bits` | `4096` | TLS key size when minting node certs |
| `aap_add_node_controller_container` | `automation-controller-task` | Controller task container name |
| `aap_add_node_controller_target` | `''` | Override controller for pre-registration (default `[0]`) |
| `aap_add_node_mesh_ca_cert` | `''` | Local mesh CA cert path (required at runtime) |
| `aap_add_node_mesh_ca_key` | `''` | Local mesh CA key path (required at runtime) |
| `aap_add_node_work_public_key` | `''` | Work signing public key (execution nodes) |

See `meta/argument_specs.yml`.

## Dependencies

- `fetch_mesh_material` (or equivalent mesh CA paths on disk).
- `assert_controller_container` (included from `pre_register.yml`).

## Example Playbook

Prefer the collection playbook, which sets mesh paths and validates inputs:

```yaml
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir=/path/to/setup \
  -e aap_add_node_target_hostname=exec1.example.com \
  -e 'aap_add_node_receptor_peers=["controller.example.com"]'
```

Direct role invocation (after mesh material is present):

```yaml
- hosts: localhost
  connection: local
  roles:
    - role: redhat_official.aap_containerized_add_node.generate_bundle
      vars:
        aap_add_node_target_hostname: exec1.example.com
        aap_add_node_receptor_peers:
          - controller.example.com
        aap_add_node_mesh_ca_cert: /path/to/mesh-CA.crt
        aap_add_node_mesh_ca_key: /path/to/mesh-CA.key
```

## License

GPL-3.0-or-later
