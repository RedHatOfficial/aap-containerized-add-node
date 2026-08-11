# Offline (Air-Gapped) Installation

Add execution or hop nodes without SSH access from the control host to the target nodes.

## When to Use

- Control host cannot SSH to execution nodes (security policy)
- Execution nodes in isolated network segment
- Strict egress-only policies on EN networks
- Compliance requirements prevent direct access
- Hybrid cloud: controller in cloud, ENs on-premises
- Customer policy prohibits SSH from external hosts

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CONTROL HOST                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ ansible-playbook generate_bundle.yml                                   │ │
│  │   - SSH to controller (fetch CA, pre-register instance)               │ │
│  │   - Mint TLS certificates for target node                             │ │
│  │   - Create self-contained archive                                     │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│                        offline-bundle-exec1.tar.gz                          │
└─────────────────────────────────────│───────────────────────────────────────┘
                                      │
                    [Transfer via approved channel]
                    (USB, secure file transfer, etc.)
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXECUTION NODE                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ tar -xzf offline-bundle-exec1.tar.gz                                   │ │
│  │ cd offline-bundle-exec1                                                │ │
│  │ ansible-playbook -c local install.yml                                  │ │
│  │   - Install receptor from bundle                                       │ │
│  │   - Configure TLS from pre-minted certs                                │ │
│  │   - Start receptor service                                             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Preflight Checks

Offline bundle generation runs **controller-side preflight only**:
- SSH to controller
- Controller task container running
- AIO disruption warning (if local-only)
- Required variables provided

**Not checked** (no SSH to target):
- Target node SSH access
- Target node DNS resolution
- Target node firewall/connectivity
- Machine-ID uniqueness

Skip preflight: `-e aap_add_node_preflight_enabled=false`

## Prerequisites

### Control Host

- SSH access to controller (to fetch mesh CA and pre-register instance)
- `aap_setup_dir` pointing to installer directory
- Python cryptography library (`pip install cryptography`)

### Target Execution Node

- RHEL 9 or 10 with valid subscription
- `podman` installed
- `ansible-core` installed (to run the install playbook)
- Receptor container image available:
  - Pre-pulled: `podman pull registry.redhat.io/ansible-automation-platform-26/receptor-rhel9:latest`
  - Or included in bundle with `aap_add_node_bundle_include_images=true`

**Note:** Image path varies by AAP version:
- AAP 2.5: `ansible-automation-platform-25/receptor-rhel8`
- AAP 2.6: `ansible-automation-platform-26/receptor-rhel9`

## Step 1: Generate Bundle

Run on the control host (which has SSH to the controller):

```bash
cd /path/to/aap_add_node/collection

ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x \
  -e _target_hostname=exec1.example.com \
  -e _receptor_peers='["controller.example.com"]'
```

### Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `_target_hostname` | Yes | - | FQDN of target execution node |
| `_receptor_peers` | Yes | - | JSON list of peer hostnames to connect to |
| `_target_type` | No | `execution` | Node type: `execution` or `hop` |
| `_receptor_port` | No | `27199` | Receptor TCP port |
| `aap_add_node_bundle_include_images` | No | `false` | Include receptor container image (~500MB) |
| `aap_add_node_bundle_output_dir` | No | `./offline-bundles` | Output directory |

### Output

```
offline-bundles/
└── offline-bundle-exec1.example.com-2026-08-11.tar.gz
```

## Step 2: Transfer Bundle

Transfer the bundle to the target node via your approved secure channel:

- USB drive
- Secure file transfer (SFTP, SCP via jump host)
- Internal file share
- Sneakernet

**Security note:** The bundle contains TLS private keys. Handle with care and delete after installation.

## Step 3: Install on Target Node

On the target execution node:

```bash
# Extract bundle
tar -xzf offline-bundle-exec1.example.com-2026-08-11.tar.gz
cd offline-bundle-exec1.example.com-2026-08-11

# Review README and vars.yml
cat README.md
cat vars.yml

# Run install (requires root or sudo)
sudo ansible-playbook -c local install.yml
```

## Step 4: Verify

Wait 1-2 minutes for heartbeat, then verify:

```bash
# On the execution node
systemctl status receptor
journalctl -u receptor -f
podman logs receptor

# On the controller
podman exec automation-controller-task awx-manage list_instances
```

Look for green output with `capacity=16` and recent heartbeat timestamp.

Check Controller UI: **Administration → Topology** — node should appear with "Ready" status.

## Bundle Contents

```
offline-bundle-<hostname>-<date>/
├── README.md               # Installation instructions
├── install.yml             # Local install playbook
├── vars.yml                # Configuration variables
├── receptor/
│   ├── receptor.conf       # Receptor configuration
│   ├── work_public_key.pem # Work signature verification
│   └── tls/
│       ├── receptor.crt    # Node TLS certificate
│       ├── receptor.key    # Node TLS private key (SENSITIVE)
│       └── ca/
│           └── mesh-CA.crt # Mesh CA certificate
└── images/                 # (Optional) Container images
    ├── receptor.tar.gz     # Receptor image
    └── README.txt          # Image loading instructions
```

## Including Container Images

For fully air-gapped environments where the target node cannot pull from a registry:

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir=/path/to/setup \
  -e _target_hostname=exec1.example.com \
  -e _receptor_peers='["controller.example.com"]' \
  -e aap_add_node_bundle_include_images=true
```

This increases bundle size from ~50KB to ~500MB but includes the receptor container image.

On the target node, the install playbook will automatically load the image from the bundle.

## Hybrid Cloud Example

Controller in cloud, ENs on-premises, no SSH from control host to ENs:

```bash
# Generate bundle for hop node (install first)
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir=/path/to/setup \
  -e _target_hostname=hop-onprem.example.com \
  -e _target_type=hop \
  -e _receptor_peers='["aap-controller.cloud.example.com"]' \
  -e aap_add_node_bundle_include_images=true

# Generate bundle for each on-prem EN
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir=/path/to/setup \
  -e _target_hostname=exec-onprem-01.example.com \
  -e _receptor_peers='["hop-onprem.example.com"]' \
  -e aap_add_node_bundle_include_images=true
```

**Installation order:** Transfer bundles to on-prem site, install hop first, then ENs.

```
Cloud Controller ◄── outbound dial ── On-Prem Hop ◄── On-Prem EN1
                                          ▲
                                          └───── On-Prem EN2
```

## Troubleshooting

### Bundle generation fails

```bash
# Check SSH to controller
ssh controller.example.com "podman ps | grep controller"

# Check mesh material exists
ssh controller.example.com "ls ~/aap/receptor/etc/certs/"
```

### Install playbook fails

```bash
# Check ansible is available
ansible --version

# Check podman is available
podman --version

# Check receptor image (AAP 2.6)
podman image exists registry.redhat.io/ansible-automation-platform-26/receptor-rhel9:latest

# List available receptor images
podman images | grep receptor
```

### capacity=0 after installation

Check controller task logs for errors:

```bash
# On controller
podman logs automation-controller-task 2>&1 | grep -i "exec1"
```

Common causes:
- **PermissionError on /.ansible_runner_uuid** — Container HOME not set correctly
- **Unknown instance** — Instance deprovisioned after bundle generation

### No heartbeat after installation

```bash
# Check receptor is running
systemctl status receptor
podman logs receptor
journalctl -u receptor -f

# Check mesh routing tables in logs (should show peers)
podman logs receptor 2>&1 | grep -i "routing table"

# Check firewall
firewall-cmd --list-ports | grep 27199
```

## Security Considerations

1. **TLS private keys in bundle** — Handle bundle as sensitive material
2. **Delete after installation** — Remove bundle from target node after successful install
3. **Secure transfer** — Use approved secure channels for transfer
4. **Audit trail** — Bundle generation is logged; document transfers in your change management
5. **Pre-registration** — Instance is registered on controller during bundle generation

## Related Documentation

- [Topology Patterns](../examples/topologies.md) — Topology patterns and firewall requirements
- [Troubleshooting](../collection/TROUBLESHOOTING.md) — Debugging receptor issues
