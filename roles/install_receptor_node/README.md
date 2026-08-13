# install_receptor_node

Install and configure receptor on the new node via `ansible.containerized_installer.receptor`, using certs minted by `fetch_or_mint_certs`.

Forces `routable_hostname` to the API/cert FQDN (not `ansible_host` IP). Seeds peer dial facts on peer inventory hosts using `routable_hostname` / inventory name before IP so receptor TLS SANs match dial targets. Work signing keys are set for execution nodes only.

## Requirements

- `aap_add_node_bundle_dir` from `fetch_or_mint_certs`.
- `ANSIBLE_COLLECTIONS_PATH` including `{{ aap_setup_dir }}/collections`.
- Prior `host_prep` (`common`) on the node.

## Role Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `aap_add_node_bundle_dir` | yes | — | Per-host minted cert bundle directory |
| `aap_setup_dir` | no | `''` | Setup tree (collections / messaging) |
| `aap_add_node_type` | no | `execution` | `execution` or `hop` |
| `aap_add_node_bundle_install` | no | `false` | Offline bundle flag for installer |
| `aap_add_node_default_registry_ns_aap` | no | `''` | Registry namespace for images |
| `aap_add_node_default_receptor_image` | no | `receptor-rhel9:latest` | Receptor image name |

Also consumes host facts from discovery: `aap_add_node_hostname`, `aap_add_node_peers`, `aap_add_node_listener_port`.

See `meta/argument_specs.yml`.

## Dependencies

- `ansible.containerized_installer.receptor` (from `aap_setup_dir/collections`)

## Example Playbook

```yaml
- hosts: aap_add_node_targets
  become: false
  gather_facts: true
  roles:
    - role: redhat_official.aap_containerized_add_node.install_receptor_node
```

## License

GPL-3.0-or-later
