# S-001: Single Execution Node

## Metadata

- **Priority**: P1
- **Topology**: AIO + EN (outbound dial)
- **Status**: Tested
- **TEST.md**: T-26-AIO-EN, T-27-AIO-EN

## Description

Add a single execution node to an AIO controller using outbound dial.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO |
| Container | `automation-controller-task` running |
| SSH | Passwordless to controller and EN |
| EN disk | >= 32 GB |
| EN OS | RHEL 9.x or 10.x |

## Inventory

```ini
[automationcontroller]
controller.example.com ansible_host=x.x.x.x ansible_user=ansible

[execution_nodes]
en-01.example.com ansible_host=y.y.y.y ansible_user=ansible \
  receptor_type=execution \
  receptor_peers='["controller.example.com"]' \
  routable_hostname=en-01.example.com
```

## Steps

### 1. Pre-flight

```bash
# Verify SSH
ssh ansible@en-01.example.com hostname

# Verify disk
ssh ansible@en-01.example.com df -h /

# Verify controller
ssh ansible@controller.example.com podman ps | grep controller-task
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
# On controller
ssh ansible@controller.example.com \
  'podman exec automation-controller-task awx-manage list_instances'
```

## Pass Criteria

- [ ] Playbook exit code `0`
- [ ] `list_instances` shows `en-01.example.com`
- [ ] `node_type=execution`
- [ ] `capacity > 0` (within 3 minutes)
- [ ] Heartbeat recent
- [ ] Instance green in UI
- [ ] Can run job on EN

## Failure Recovery

If playbook fails mid-run:
1. Fix underlying issue (disk, SSH, etc.)
2. Re-run playbook (idempotent)

If need to start fresh:
```bash
podman exec automation-controller-task \
  awx-manage deprovision_instance --hostname=en-01.example.com
```

## Results Log

| Date | AAP Version | Node OS | Result | Notes |
|------|-------------|---------|--------|-------|
| 2026-08 | 2.6 | RHEL 9 | Pass | Initial validation — see also TEST.md T-26-AIO-EN |
| 2026-08 | 2.7.1 | RHEL 9 | Pass | — |
| 2026-08 | 2.7.1 | RHEL 10 | Pass | Isolated EN→controller (S-001); TEST.md T-27-AIO-EN |
