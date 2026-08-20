# AAP Mesh Node Addition

Add execution and hop nodes to containerized AAP 2.6+ without re-running the full installer.

## Quick Start

Two installation methods:

=== "Online (SSH to targets)"

    ```bash
    # Install collection (from clone or extracted source tree)
    ansible-galaxy collection install -r requirements.yml
    ansible-galaxy collection install --force --no-deps .
    export ANSIBLE_COLLECTIONS_PATH=./aap-setup-2.7-1/collections:${ANSIBLE_COLLECTIONS_PATH}

    # Run preflight checks
    ansible-playbook -i inventory.yml \
      playbooks/preflight.yml \
      -e aap_setup_dir=/path/to/installer

    # Add nodes
    ansible-playbook -i inventory.yml \
      playbooks/add_node.yml \
      -e aap_setup_dir=/path/to/installer
    ```

=== "Offline (air-gapped)"

    ```bash
    # Generate bundle on control host
    ansible-playbook playbooks/generate_bundle.yml \
      -i inventory.yml \
      -e aap_setup_dir=/path/to/setup \
      -e aap_add_node_target_hostname=exec1.example.com \
      -e aap_add_node_receptor_peers='["controller.example.com"]'

    # Transfer bundle to target, then on target:
    tar -xzf offline-bundle-exec1.example.com-*.tar.gz
    cd offline-bundle-exec1.example.com-*
    sudo ansible-playbook -c local install.yml
    ```

## Documentation

| Section | Content |
|:--------|:--------|
| [Installation](INSTALL.md) | Prerequisites and step-by-step guide |
| [Pick Your Topology](QUICKSTART.md) | Online vs Offline decision tree |
| [Offline Installation](OFFLINE.md) | Air-gapped bundle workflow |
| [FAQ](FAQ.md) | Common questions |
| [Topology Patterns](TOPOLOGY.md) | Peer direction and firewall rules |
| [Collection Structure](STRUCTURE.md) | Roles, playbooks, variables |

## Features

- **Two install methods** — Online (SSH) or Offline (bundle transfer)
- **Hop and Execution nodes** — Both node types supported
- **Multi-hop chains** — EN → HN → Controller topologies
- **Parallel node addition** — Multiple nodes in single playbook run
- **Preflight validation** — Catch errors before installation starts
- **Minimal disruption** — No controller restart unless AIO tcp-listener needed
- **Instance Groups via inventory** — `[instance_group_<name>]` groups auto-create IGs
- **RHEL 9 + RHEL 10** — Tested on both
- **BYO TLS certificates** — Use existing certs or generate new ones

## Test Status

| Scenario | Status |
|----------|--------|
| Single EN (online) | PASS |
| Single HN (online) | PASS |
| HN + EN chain (online) | PASS |
| Single EN (offline bundle) | PASS |
| Single HN (offline bundle) | PASS |
| HN + EN chain (offline) | PASS |
| TLS self-signed (default) | PASS |
| Image bundling (air-gap) | BLOCKED |

## Preflight Checks

The `preflight.yml` playbook validates:

| Check | What It Catches |
|-------|-----------------|
| SSH to controller | Connection failures before install |
| Controller container running | Missing `automation-controller-task` |
| SSH to execution nodes | Network/auth issues (online only) |
| Network EN→Controller:27199 | Firewall blocks |
| DNS resolution | Name resolution failures |
| Machine-ID uniqueness | Cloned VM issues |
| Inventory format | `receptor_peers` must be list |
| AIO local-only detection | Warns about disruption |

!!! note "Offline Preflight"
    Offline mode runs **controller-side checks only** — no SSH to target nodes.
    Skip preflight with `-e aap_add_node_preflight_enabled=false`

## Architecture

```
Online Mode:
  Control Host ──SSH──► Controller (fetch certs, register instances)
               ──SSH──► Execution Nodes (install receptor)

Offline Mode:
  Control Host ──SSH──► Controller (generate bundle)
                            │
                    [Transfer bundle]
                            ▼
               Execution Node (local install)

Mesh Topologies:
  EN ──dial:27199──▶ Controller           (direct)
  EN ──▶ Hop ──▶ Controller               (multi-hop)
  EN ──▶ Hop1 ──▶ Hop2 ──▶ Controller     (DMZ chain)
```

## Tested Configurations

| Component | Version |
|-----------|---------|
| AAP Controller | 2.6-8 |
| Execution Nodes | RHEL 9.x, RHEL 10.0 |
| Topology | Direct, Multi-hop, Offline |
