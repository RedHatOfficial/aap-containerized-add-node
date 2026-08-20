# Collection Structure

## Overview

```
redhat_official.aap_containerized_add_node/
├── playbooks/
│   ├── add_node.yml          # Main: online node addition
│   ├── generate_bundle.yml   # Offline bundle generation
│   ├── preflight.yml         # Pre-flight validation
│   └── validate_mesh.yml     # Post-install verification
│
├── roles/
│   ├── preflight/            # Validate prerequisites
│   ├── validate_setup_dir/   # Check installer directory
│   ├── assert_controller_container/  # Verify controller running
│   ├── fetch_mesh_material/  # Get CA certs from controller
│   ├── fetch_or_mint_certs/  # Generate TLS certificates
│   ├── host_prep/            # Prepare execution nodes
│   ├── install_receptor_node/# Install receptor service
│   ├── register_instance/    # Register with awx-manage
│   ├── generate_bundle/      # Create offline bundle
│   └── verify_mesh/          # Validate mesh connectivity
│
└── examples/                 # Inventory examples
```

## Playbooks

| Playbook | Purpose | When to Use |
|----------|---------|-------------|
| `add_node.yml` | Add nodes via SSH | Online installation |
| `generate_bundle.yml` | Create offline bundle | Air-gapped environments |
| `preflight.yml` | Validate prerequisites | Before any installation |
| `validate_mesh.yml` | Verify mesh health | After installation |

## Key Roles

### preflight

Validates before installation:

- SSH connectivity to all nodes
- Controller container running
- Network EN→Controller:27199
- DNS resolution
- Machine-ID uniqueness (cloned VMs)
- Inventory format validation

### fetch_mesh_material

Fetches from controller:

- `mesh-CA.crt` — Trust bundle for TLS
- `ca.key` — Signing key (online mode only)
- `work_public_key.pem` — Job signing key

### fetch_or_mint_certs

Two modes:

1. **Generate** — Mint new cert signed by CA (default)
2. **BYO** — Use provided `aap_add_node_tls_cert` and `aap_add_node_tls_key`

### install_receptor_node

Installs receptor on target:

- Creates `/etc/receptor/` structure
- Deploys TLS certificates
- Generates `receptor.conf`
- Creates systemd service
- Starts receptor container

### generate_bundle

Creates self-contained archive:

- `install.yml` — Local install playbook
- `receptor.conf` — Pre-configured
- TLS certificates — Pre-minted
- `README.md` — Installation instructions

## Variables

### Required

| Variable | Description |
|----------|-------------|
| `aap_setup_dir` | Path to AAP installer directory |
| `receptor_peers` | List of upstream peer hostnames |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `aap_add_node_target_type` | `execution` | Node type: `execution` or `hop` |
| `aap_add_node_receptor_port` | `27199` | Receptor TCP port |
| `aap_add_node_tls_cert` | — | BYO TLS certificate path |
| `aap_add_node_tls_key` | — | BYO TLS key path |
| `aap_add_node_preflight_enabled` | `true` | Run preflight checks |
| `aap_add_node_bundle_include_images` | `false` | Include container image in bundle |

## Inventory Groups

| Group | Purpose |
|-------|---------|
| `automationcontroller` | Controller host(s) |
| `aap_add_node_targets` | Nodes to add |
| `instance_group_<name>` | Auto-creates instance group |

## Dependencies

- `ansible-core` >= 2.15
- Python `cryptography` library (for cert generation)
- AAP installer directory with `group_vars/`
