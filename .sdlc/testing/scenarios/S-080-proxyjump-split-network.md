# S-080: ProxyJump Split Network Topology

## Metadata

- **Priority**: P2
- **Topology**: Split network with jumpbox
- **Status**: Untested
- **Phase**: PHASE-002

## Description

Test adding an execution node when control host cannot directly SSH to both controller and EN. Requires ProxyJump/bastion hosts.

## Use Case

```
Network A                          Network B
┌─────────────────┐                ┌─────────────────┐
│   Controller    │                │ Execution Node  │
│ (carmaap1.lan)  │                │ (aap-exec1)     │
└────────▲────────┘                └────────▲────────┘
         │                                  │
         │ SSH                              │ SSH
         │                                  │
┌────────┴────────┐                ┌────────┴────────┐
│   Jumpbox A     │                │   Jumpbox B     │
│ (aap-flex1)     │◄───────────────│ (or same host)  │
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

Use aap-flex1-rhel9 as jumpbox to simulate split network:

| Role | Host | Notes |
|------|------|-------|
| Control Host | localhost (Mac) | Where playbook runs |
| Jumpbox | aap-flex1-rhel9 | SSH proxy |
| Controller | carmaap1.lan | Via jumpbox |
| Execution Node | aap-exec1-rhel9 | Via jumpbox |

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
carmaap1.lan ansible_ssh_common_args='-o ProxyJump=ansible@aap-flex1-rhel9'

[execution_nodes]
aap-exec1-rhel9 ansible_ssh_common_args='-o ProxyJump=ansible@aap-flex1-rhel9' receptor_peers='["carmaap1.lan"]'

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
  -e aap_add_node_target_hostname=aap-exec1-rhel9 \
  -e aap_add_node_receptor_peers='["carmaap1.lan"]'
```

**Step 2: Transfer via jumpbox**

```bash
# Copy bundle to jumpbox
scp offline-bundles/offline-bundle-aap-exec1-rhel9-*.tar.gz \
  ansible@aap-flex1-rhel9:/tmp/

# From jumpbox, copy to EN
ssh ansible@aap-flex1-rhel9 \
  "scp /tmp/offline-bundle-*.tar.gz ansible@aap-exec1-rhel9:/tmp/"
```

**Step 3: Install on EN**

```bash
ssh -J ansible@aap-flex1-rhel9 ansible@aap-exec1-rhel9

cd /tmp
tar -xzf offline-bundle-aap-exec1-rhel9-*.tar.gz
cd offline-bundle-aap-exec1-rhel9-*
sudo ansible-playbook -c local install.yml
```

### Part C: Verify

```bash
# Via jumpbox
ssh -J ansible@aap-flex1-rhel9 ansible@carmaap1.lan \
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
Host carmaap1.lan
  ProxyJump ansible@aap-flex1-rhel9

Host aap-exec1-rhel9
  ProxyJump ansible@aap-flex1-rhel9
```

## Cleanup

```bash
# Via jumpbox
ssh -J ansible@aap-flex1-rhel9 ansible@aap-exec1-rhel9 \
  'sudo systemctl stop receptor; sudo rm -rf /etc/receptor /var/run/receptor'

ssh -J ansible@aap-flex1-rhel9 ansible@carmaap1.lan \
  'podman exec automation-controller-task awx-manage deprovision_instance --hostname=aap-exec1-rhel9'
```

## Results Log

| Date | Method | Result | Notes |
|------|--------|--------|-------|
| | | | |
