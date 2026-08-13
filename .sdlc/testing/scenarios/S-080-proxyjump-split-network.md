# S-080: ProxyJump Split Network Topology

## Metadata

- **Priority**: P2
- **Topology**: Split network with jumpbox
- **Status**: Part A + Part B Passed (2026-08-12)
- **Phase**: PHASE-002

## Description

Test adding an execution node when control host cannot directly SSH to both controller and EN. Requires ProxyJump/bastion hosts.

## Use Case

```
Network A                          Network B
┌─────────────────┐                ┌─────────────────┐
│   Controller    │                │ Execution Node  │
│ (controller)    │                │ (exec1)         │
└────────▲────────┘                └────────▲────────┘
         │                                  │
         │ SSH                              │ SSH
         │                                  │
┌────────┴────────┐                ┌────────┴────────┐
│   Jumpbox A     │                │   Jumpbox B     │
│ (jumpbox)       │◄───────────────│ (or same host)  │
└────────▲────────┘    Network     └─────────────────┘
         │
         │ SSH
         │
┌────────┴────────┐
│  Control Host   │
│   (localhost)   │
└─────────────────┘
```

## Lab Simulation

Use a jumpbox to simulate split network:

| Role | Host | Notes |
|------|------|-------|
| Control Host | localhost (Mac) | Where playbook runs |
| Jumpbox | RHEL9 bastion | SSH proxy |
| Controller | AAP 2.7 | Via jumpbox |
| Execution Node | RHEL9 | Via jumpbox |

**Simulation:** Block direct SSH from control host to controller/EN, force through jumpbox.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Control host | SSH to jumpbox only |
| Jumpbox | SSH to both controller and EN |
| Firewall | Block direct control→controller, control→EN |

## Test Steps

### Part A: Online with ProxyJump

**Inventory:**
```ini
[automationcontroller]
controller.example.com ansible_ssh_common_args='-o ProxyJump=ansible@jumpbox.example.com'

[execution_nodes]
exec1.example.com ansible_ssh_common_args='-o ProxyJump=ansible@jumpbox.example.com' receptor_peers='["controller.example.com"]'

[all:vars]
ansible_user=ansible
```

**Run:**
```bash
# Verify SSH works via jumpbox
ansible -i inventory-proxyjump.yml all -m ping

# Run add_node
ansible-playbook playbooks/add_node.yml \
  -i inventory-proxyjump.yml \
  -e aap_setup_dir="${SETUP}"
```

### Part B: Offline Bundle via ProxyJump

**Step 1: Generate bundle (controller via jumpbox)**

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory-proxyjump.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_target_hostname=exec1.example.com \
  -e aap_add_node_receptor_peers='["controller.example.com"]'
```

**Step 2: Transfer via jumpbox**

```bash
# Copy bundle to jumpbox
scp offline-bundles/offline-bundle-exec1.example.com-*.tar.gz \
  ansible@jumpbox.example.com:/tmp/

# From jumpbox, copy to EN
ssh ansible@jumpbox.example.com \
  "scp /tmp/offline-bundle-*.tar.gz ansible@exec1.example.com:/tmp/"
```

**Step 3: Install on EN**

```bash
ssh -J ansible@jumpbox.example.com ansible@exec1.example.com

cd /tmp
tar -xzf offline-bundle-exec1.example.com-*.tar.gz
cd offline-bundle-exec1.example.com-*
sudo ansible-playbook -c local install.yml
```

### Part C: Verify

```bash
# Via jumpbox
ssh -J ansible@jumpbox.example.com ansible@controller.example.com \
  "podman exec automation-controller-task awx-manage list_instances"
```

## Pass Criteria

### Part A (Online ProxyJump)
- [ ] ansible ping works via jumpbox to all hosts
- [ ] add_node.yml completes successfully
- [ ] EN registered with heartbeat

### Part B (Offline ProxyJump)
- [ ] Bundle generated (controller via jumpbox)
- [ ] Bundle transferred via jumpbox chain
- [ ] Local install succeeds
- [ ] EN registered with heartbeat

## Simulating Split Network

To properly test, block direct SSH:

```bash
# On control host (Mac) - add to /etc/hosts or firewall
# Option 1: Fake DNS to force jumpbox route
# Option 2: Use SSH config to enforce ProxyJump

# ~/.ssh/config
Host controller.example.com
  ProxyJump ansible@jumpbox.example.com

Host exec1.example.com
  ProxyJump ansible@jumpbox.example.com
```

## Cleanup

```bash
# Via jumpbox
ssh -J ansible@jumpbox.example.com ansible@exec1.example.com \
  'sudo systemctl stop receptor; sudo rm -rf /etc/receptor /var/run/receptor'

ssh -J ansible@jumpbox.example.com ansible@controller.example.com \
  'podman exec automation-controller-task awx-manage deprovision_instance --hostname=exec1.example.com'
```

## Results Log

| Date | Method | Result | Notes |
|------|--------|--------|-------|
| 2026-08-12 | Part A: Online ProxyJump | PASS | All preflight/discovery via jumpbox; EN already registered |
| 2026-08-12 | Part B: Offline Bundle | PASS | Bundle generated on controller, transferred to EN, local install succeeded |

### 2026-08-12 Test Details

**Environment:**
- Control host: macOS (localhost)
- Jumpbox: RHEL9
- Controller: AAP 2.7 containerized
- Execution Node: RHEL9

**Issue Found:** macOS podman-machine config leaked via `delegate_to`, causing "Cannot connect to Podman" errors on remote. 

**Fix Applied:** Changed `list_instances` role to use raw SSH command instead of Ansible `delegate_to` for podman exec operations. This prevents Mac container config from polluting remote podman execution.

**Test Inventory:**
```yaml
all:
  vars:
    ansible_user: ansible
    registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
  children:
    automationcontroller:
      hosts:
        controller.example.com:
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o ProxyJump=ansible@jumpbox.example.com'
          ansible_python_interpreter: /usr/bin/python3
    execution_nodes:
      hosts:
        exec1.example.com:
          ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o ProxyJump=ansible@jumpbox.example.com'
          receptor_peers:
            - controller.example.com
```

**Result:**
- Preflight passed (8 checks including SSH via jumpbox)
- Discovery completed (found EN already registered)
- All plays no-op'd as expected for existing node
