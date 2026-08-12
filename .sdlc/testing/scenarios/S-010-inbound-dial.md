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
| 2026-08-12 | PASS (with manual fix) | Bug found in update_controller_peers role; manual receptor.conf fix required |

### 2026-08-12 Test Details

**Environment:**
- Controller: carmaap1.lan (AAP 2.7.3 containerized)
- Execution Node: aap-flex1-rhel9

**Test Results:**
1. Preflight: PASS
2. Discovery: PASS
3. Registration: PASS
4. Host prep: PASS
5. update_controller_peers: **BUG FOUND**
6. EN heartbeat: PASS (after manual fix)

**Bug Found:** `update_controller_peers` role uses `blockinfile` which inserts `tcp-peer` block incorrectly inside the `tcp-listener:` entry, breaking receptor.conf syntax.

Before (broken):
```yaml
- tcp-listener:
# BEGIN ANSIBLE MANAGED - peer aap-flex1-rhel9
- tcp-peer:
    address: aap-flex1-rhel9:27199
# END ANSIBLE MANAGED - peer aap-flex1-rhel9
    port: 27199
```

After (fixed manually):
```yaml
- tcp-listener:
    port: 27199
    tls: tls_server
# BEGIN ANSIBLE MANAGED - peer aap-flex1-rhel9
- tcp-peer:
    address: aap-flex1-rhel9:27199
    tls: tls_client
# END ANSIBLE MANAGED - peer aap-flex1-rhel9
```

**Inbound Dial Verified:**
- EN has `tcp-listener` (correct)
- Controller has `tcp-peer` to EN (correct after fix)
- EN heartbeat present: capacity=16, node_type=execution
