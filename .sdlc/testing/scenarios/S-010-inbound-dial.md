# S-010: Inbound Dial (Controller → EN)

## Metadata

- **Priority**: P2
- **Topology**: Controller-initiated connection
- **Status**: Untested
- **Phase**: PHASE-002

## Description

Test adding execution node when EN cannot dial out to controller. Controller initiates connection to EN instead.

## Use Case

```
┌─────────────────┐                      ┌─────────────────┐
│   Controller    │  ──TCP:27199───────► │ Execution Node  │
│   (tcp-peer)    │      outbound        │ (tcp-listener)  │
└─────────────────┘                      └─────────────────┘
```

**When needed:**
- EN behind strict egress firewall (no outbound to controller)
- Security policy blocks EN→Controller but allows Controller→EN
- DMZ topology where only controller can initiate connections

## Warning

> **⚠️ SERVICE DISRUPTION**
>
> This mode causes:
> - 5-10 second mesh disruption per node added
> - Running jobs may fail if mid-execution
> - Controller receptor restarts for EACH new node
>
> Prefer outbound dial whenever possible.

## Lab Environment

| Role | Host | Notes |
|------|------|-------|
| Controller | carmaap1.lan | AAP 2.7 containerized |
| Execution Node | aap-flex1-rhel9 | No `receptor_peers` — controller dials to it |

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller reachable from EN | Port 27199/TCP (for initial registration) |
| EN reachable from Controller | Port 27199/TCP (for receptor connection) |
| EN has tcp-listener | Auto-configured when `aap_add_node_enable_controller_peer=true` |

## Test Steps

### Part A: Setup

1. **Deprovision flex node if registered:**
   ```bash
   ssh carmaap1.lan "podman exec automation-controller-task awx-manage deprovision_instance --hostname=aap-flex1-rhel9.lan"
   ```

2. **Create inventory:**
   ```ini
   # inventory-inbound.ini
   [automationcontroller]
   carmaap1.lan

   [execution_nodes]
   aap-flex1-rhel9.lan routable_hostname=aap-flex1-rhel9.lan

   [all:vars]
   ansible_user=ansible
   aap_add_node_enable_controller_peer=true
   ```

### Part B: Run Add Node

```bash
cd /private/tmp/aap-containerized-add-node

ansible-playbook playbooks/add_node.yml \
  -i inventory-inbound.ini \
  -e aap_setup_dir="${SETUP}"
```

### Part C: Verify

1. **Check EN registered:**
   ```bash
   ssh carmaap1.lan "podman exec automation-controller-task awx-manage list_instances" | grep aap-flex1
   ```
   Expected: `aap-flex1-rhel9.lan capacity=X node_type=execution heartbeat=...`

2. **Check EN has tcp-listener (not tcp-peer):**
   ```bash
   ssh aap-flex1-rhel9.lan "grep -E 'tcp-listener|tcp-peer' ~/aap/receptor/etc/receptor.conf"
   ```
   Expected: `tcp-listener` present, no `tcp-peer`

3. **Check controller has tcp-peer to EN:**
   ```bash
   ssh carmaap1.lan "podman exec automation-controller-receptor cat /etc/receptor/receptor.conf" | grep -A2 tcp-peer
   ```
   Expected: `address: aap-flex1-rhel9.lan:27199`

4. **Run job on EN:**
   - Create job template targeting `aap-flex1-rhel9.lan` instance group
   - Run Demo Template
   - Verify executes on EN

## Pass Criteria

- [ ] add_node.yml completes successfully
- [ ] EN registered with heartbeat in list_instances
- [ ] EN receptor.conf has `tcp-listener`, no `tcp-peer`
- [ ] Controller receptor.conf has `tcp-peer` entry for EN
- [ ] Jobs can execute on EN
- [ ] Mesh disruption observed during add (expected)

## Cleanup

```bash
# Deprovision EN
ssh carmaap1.lan "podman exec automation-controller-task awx-manage deprovision_instance --hostname=aap-flex1-rhel9.lan"

# Stop receptor on EN
ssh aap-flex1-rhel9.lan "systemctl --user stop receptor"
```

## Results Log

| Date | Result | Notes |
|------|--------|-------|
| 2026-08-12 | PARTIAL | Logic works through registration; blocked at installer registry login (creds not available) |

### 2026-08-12 Test Details

**Environment:**
- Controller: carmaap1.lan (AAP 2.7.3 containerized)
- Execution Node: aap-flex1-rhel9

**Partial Test Results:**
1. Preflight: PASS (when enabled with creds)
2. Discovery: PASS (found flex node not registered)
3. Registration: PASS (provision_instance succeeded)
4. Host prep: BLOCKED at `ansible.containerized_installer.common` registry login

**Root Cause:** Installer collection requires `registry_username`/`registry_password` even when podman already logged in. Lab creds not in fetchable location.

**Fix Options:**
1. Store registry creds in vault on controller
2. Use offline bundle (no registry needed)
3. Manual cred injection for test

**Inbound Dial Logic Verified:**
- `aap_add_node_enable_controller_peer=true` correctly parsed
- Role `update_controller_peers` would execute after host_prep
- Discovery correctly identified flex node as new
