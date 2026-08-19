# AAP Containerized Add Node Collection

> **Support Notice:** This collection is not part of the official AAP product.
> For supported usage, customers must have an approved **Red Hat Support Exception (SE)**.
> Contact your TAM or account team to request an SE.
> Without an SE, this collection is provided as-is without Red Hat Support coverage.
> See [SUPPORT.md](SUPPORT.md) for details.

[![CI](https://github.com/RedHatOfficial/aap-containerized-add-node/actions/workflows/ci.yml/badge.svg)](https://github.com/RedHatOfficial/aap-containerized-add-node/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-mkdocs-blue)](https://redhatofficial.github.io/aap-containerized-add-node/)

Add **Execution Nodes** and **Hop Nodes** to existing **containerized AAP 2.6+** clusters without re-running the full installer.

**Collection:** `redhat_official.aap_containerized_add_node`

## Overview

| | |
|---|---|
| **Purpose** | Day-2 mesh node addition without maintenance window |
| **Supports** | AAP 2.6+, 2.7+ containerized |
| **Node Types** | Execution nodes, Hop nodes |
| **Node OS** | RHEL 9.x, RHEL 10.x |
| **Topology** | Outbound dial (default), Inbound dial (optional) |

## Documentation

Full documentation is available at **[redhatofficial.github.io/aap-containerized-add-node](https://redhatofficial.github.io/aap-containerized-add-node/)** or in the `docs/` directory:

| Topic | Description |
|-------|-------------|
| [Quick Start](docs/QUICKSTART.md) | Get started in 5 minutes |
| [Architecture](docs/ARCHITECTURE.md) | How the collection works |
| [Topology](docs/TOPOLOGY.md) | Network topology patterns and examples |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [Conventions](docs/CONVENTIONS.md) | Variable naming and configuration |

### Example Inventories

Pick the topology that matches your network:

| Topology | Example |
|----------|---------|
| Single EN → Controller | [inventory-single-en.yml](examples/inventory-single-en.yml) |
| Multiple ENs → Controller | [inventory-parallel-ens.yml](examples/inventory-parallel-ens.yml) |
| EN → Hop → Controller | [inventory-en-via-hn.yml](examples/inventory-en-via-hn.yml) |
| Multi-hop chain | [inventory-multi-hop-chain.yml](examples/inventory-multi-hop-chain.yml) |
| Hybrid cloud | [inventory-hybrid-cloud.yml](examples/inventory-hybrid-cloud.yml) |

Full inventory index with diagrams: [examples/README.md](examples/README.md)

## Quick Start

```bash
SETUP=/path/to/ansible-automation-platform-containerized-setup-2.x

ansible-galaxy collection install -r requirements.yml
ansible-galaxy collection install --force --no-deps .

export ANSIBLE_COLLECTIONS_PATH="${SETUP}/collections:${ANSIBLE_COLLECTIONS_PATH}"

ansible-playbook playbooks/add_node.yml \
  -i "${SETUP}/inventory" \
  -e aap_setup_dir="${SETUP}" \
  -e @examples/add_node.secrets.yml
```

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for prerequisites and detailed steps.

## Platform Support

| Platform | Status |
|----------|--------|
| Containerized AAP 2.6+ | Supported |
| Containerized AAP 2.7+ | Supported |
| RHEL 9/10 nodes | Tested |
| RPM installs | Not supported |
| OpenShift / Operator | Use native AAP UI workflow (see links below) |

For operator-based (OpenShift) execution node setup, use the official AAP UI docs:

- AAP 2.6: [Set up virtual machines](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/administer-proc_set_up_virtual_machines)
- AAP 2.7: [Set up virtual machines](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.7/administer-proc_set_up_virtual_machines)

## Current Limitations

- Requires SSH access from control host to controller and new nodes
- Controller task container must be running
- Air-gapped bundle generation not yet implemented

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. All commits require DCO sign-off (`git commit -s`).

## Release Notes

See [CHANGELOG.rst](CHANGELOG.rst) for release history.

## License

GPL-3.0 — see [LICENSE](LICENSE).
