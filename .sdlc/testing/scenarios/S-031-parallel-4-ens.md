# S-031: Parallel 4 Execution Nodes

## Metadata

- **Priority**: P2
- **Topology**: AIO + 4 ENs
- **Status**: Tested (2026-08-12)
- **Phase**: PHASE-001

## Description

Add 4 execution nodes simultaneously to verify parallel registration and host preparation.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO |
| Execution Nodes | 4 RHEL 9/10 hosts with SSH access |
| Registry | Credentials for registry.redhat.io |

## Inventory

```ini
[automationcontroller]
carmaap1.lan

[execution_nodes]
aap-exec1-rhel9.lan routable_hostname=aap-exec1-rhel9
aap-exec1-rhel10.lan routable_hostname=aap-exec1-rhel10
aap-flex1-rhel9.lan routable_hostname=aap-flex1-rhel9
aap-flex1-rhel10.lan routable_hostname=aap-flex1-rhel10

[all:vars]
ansible_user=pgriffit
receptor_peers=["carmaap1.lan"]
registry_username=<redacted>
registry_password=<redacted>
```

## Test Steps

1. **Deprovision any existing nodes:**
   ```bash
   for node in aap-exec1-rhel9 aap-exec1-rhel10 aap-flex1-rhel9 aap-flex1-rhel10; do
     podman exec automation-controller-task awx-manage deprovision_instance --hostname="$node"
   done
   ```

2. **Run add_node playbook:**
   ```bash
   ansible-playbook playbooks/add_node.yml \
     -i inventory.ini \
     -e aap_setup_dir=/path/to/setup
   ```

3. **Verify all nodes registered:**
   ```bash
   podman exec automation-controller-task awx-manage list_instances
   ```

## Pass Criteria

- [ ] Playbook completes successfully for all 4 nodes
- [ ] All nodes appear in list_instances
- [ ] All nodes show heartbeat within 3 minutes
- [ ] All nodes have capacity > 0
- [ ] Registration serialized (no DB race condition)

## Known Issues

- **Port conflict on re-run**: If receptor process from previous run still holds port 27199, new receptor fails to start. Fix: `fuser -k 27199/tcp` then `systemctl --user restart receptor`

## Results Log

| Date | AAP Version | Nodes | Time | Result | Notes |
|------|-------------|-------|------|--------|-------|
| 2026-08-12 | 2.7.3 | 4 | 3m56s | PASS | Port cleanup needed on RHEL 9 nodes after first run |
