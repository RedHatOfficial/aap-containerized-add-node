# S-NNN: [Scenario Name]

## Metadata

- **Priority**: P1 | P2 | P3
- **Topology**: [e.g., AIO + EN, Cluster + HN]
- **Status**: Untested | Tested | Blocked

## Description

Brief description of what this scenario tests.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | [e.g., Containerized AAP 2.6+ AIO] |
| Container | [e.g., automation-controller-task running] |
| SSH | [e.g., Passwordless to controller and new nodes] |
| Node disk | [e.g., >= 32 GB] |
| Node OS | [e.g., RHEL 9.x] |

## Inventory

```ini
[automationcontroller]
controller.example.com ansible_host=x.x.x.x ansible_user=ansible

[execution_nodes]
node.example.com ansible_host=y.y.y.y ansible_user=ansible \
  receptor_type=execution \
  receptor_peers='["controller.example.com"]' \
  routable_hostname=node.example.com
```

## Steps

### 1. Pre-flight

```bash
# Commands to verify prerequisites
```

### 2. Run playbook

```bash
SETUP=/path/to/containerized-setup-2.x
export ANSIBLE_COLLECTIONS_PATH="${SETUP}/collections:${ANSIBLE_COLLECTIONS_PATH}"

ansible-playbook playbooks/add_node.yml \
  -i inventory \
  -e aap_setup_dir="${SETUP}"
```

### 3. Verify

```bash
# Verification commands
```

## Pass Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Failure Recovery

Steps to recover if scenario fails.

## Related

- REQ-NNN: Related requirement
- S-NNN: Related scenario

## Results Log

| Date | AAP Version | Node OS | Result | Notes |
|------|-------------|---------|--------|-------|
| YYYY-MM-DD | X.Y | RHEL N | Pass/Fail | Notes |
