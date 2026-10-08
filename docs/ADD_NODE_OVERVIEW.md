# `aap-containerized-add-node` Overview

`aap-containerized-add-node` is a day-2 Ansible collection for adding execution nodes or hop nodes to an existing containerized AAP 2.6+ deployment without rerunning the full installer.

## End-to-end flow

```text
Existing AAP
    │
    ├─ Validate containerized setup tree
    ├─ Check controller and SSH access
    ├─ Run preflight:
    │    ├─ DNS and TCP connectivity
    │    ├─ installer collections
    │    ├─ registry credentials
    │    ├─ machine-ID uniqueness
    │    └─ controller/node clock skew
    │
    ├─ Compare inventory with awx-manage list_instances
    │        │
    │        ├─ Healthy heartbeat → skip
    │        └─ New/incomplete host → target
    │
    ├─ Fetch mesh CA and signing material
    ├─ Enable controller receptor listener if AIO requires it
    ├─ Prepare execution host and container runtime
    ├─ Mint node TLS certificates
    ├─ Register node in Controller database
    ├─ Install/configure receptor
    └─ Verify heartbeat and mesh connectivity
```

## Main phases

| Phase | What it does | Main mechanism |
|---|---|---|
| Validate | Confirms `aap_setup_dir` is a containerized installer tree | Ansible assertions |
| Preflight | Checks SSH, DNS, TCP `27199`, clocks, collections, credentials, and machine IDs | Delegated checks |
| Discover | Finds inventory nodes absent from healthy Controller instances | `awx-manage list_instances` |
| Mesh material | Retrieves mesh CA certificate/key and work public key | Controller filesystem |
| Controller listener | Converts AIO `local-only` receptor config to `tcp-listener` when needed | Receptor config and service restart |
| Host preparation | Installs required packages, Podman configuration, and common prerequisites | `ansible.containerized_installer.common` |
| Certificates | Creates node-specific receptor TLS material | Mesh CA |
| Registration | Creates or updates Controller instance metadata | `awx-manage` |
| Receptor install | Deploys receptor container and configuration on new host | `ansible.containerized_installer.receptor` |
| Verification | Confirms node heartbeat and capacity | `awx-manage list_instances` |

## Controller registration sequence

```text
provision_instance
        ↓
add_receptor_address
        ↓
register_peers
        ↓
register_queue
        ↓
receptor starts
        ↓
heartbeat appears
```

## Important behavior

| Behavior | Result |
|---|---|
| Existing healthy node | Skipped when heartbeat is present |
| Provisioned but incomplete node | Eligible for retry |
| Failed run | No automatic deprovisioning |
| AIO `local-only` receptor | Controller receptor restart may occur; documented 5–10 second disruption |
| Outbound topology | Preferred; execution node dials controller on TCP `27199` |
| Full AAP installer | Not rerun |
| Gateway OAuth registration | Not used |
| RPM installer tree | Unsupported |
| OpenShift/operator deployment | Out of scope |

## Required inputs

- Existing containerized AAP 2.6+ deployment
- Extracted matching containerized setup directory
- Inventory containing controller and new host under `[execution_nodes]`
- SSH access from control host
- Sudo/become access on controller and new host
- RHEL 9 or RHEL 10 execution host
- DNS resolution
- TCP `27199` from execution host to controller or hop
- Registry credentials for online image installation

## What it changes

```text
Controller:
  - Controller instance database
  - Receptor listener only when required
  - Instance groups/queues based on inventory

Execution node:
  - Host prerequisites
  - Receptor container
  - Receptor configuration
  - TLS certificates
  - Mesh peer configuration
```

It does not restart Gateway, Hub, EDA, Redis, or other AAP services.

## Scope

Supported:

- Containerized AAP 2.6+
- Execution nodes
- Hop nodes
- Direct and multi-hop Receptor topologies
- Online and offline installation paths

Not supported:

- RPM installer deployments
- OpenShift/operator-based deployments
- AAP 2.5 and earlier
- Greenfield full installations
- Automated deprovisioning or rollback

## References

- [Collection map](COLLECTION_MAP.md)
- [Architecture](ARCHITECTURE.md)
- [Installation guide](INSTALL.md)
- [Project documentation](https://redhatofficial.github.io/aap-containerized-add-node/)
