# Mesh Topology Guide

**Quick start:** [QUICKSTART.md](QUICKSTART.md) — decision tree to pick your topology.
**Ready-to-use inventories:** [examples/README.md](../examples/README.md) — copy and adapt.

## Overview

AAP mesh networking uses receptor to connect execution nodes to the controller.
The direction of the TCP connection determines firewall requirements and service disruption.

**Key concepts:**
- **tcp-listener**: Node accepts incoming connections (server side)
- **tcp-peer**: Node initiates outbound connection to another node's listener (client side)
- Once connected, communication is **bidirectional** - the direction only affects who initiates

## Peer Direction Patterns

### Pattern 1: Outbound Dial (EN -> Controller) - RECOMMENDED

The execution node initiates the connection to the controller. This is the default and recommended pattern.

```
┌─────────────────┐                      ┌─────────────────┐
│ Execution Node  │  ──TCP:27199───────> │   Controller    │
│   (tcp-peer)    │      outbound        │ (tcp-listener)  │
└─────────────────┘                      └─────────────────┘
```

**Configuration:**
```ini
[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]'
exec2.example.com receptor_peers='["controller.example.com"]'
```

**Firewall requirements:**
| Node | Direction | Port | Notes |
|------|-----------|------|-------|
| EN | Outbound | 27199/TCP | To controller (usually allowed by default) |
| Controller | Inbound | 27199/TCP | From ENs |

**Advantages:**
- Works through most firewalls (outbound typically unrestricted)
- **Zero disruption** to existing mesh
- No changes needed on controller (except AIO local-only fix)
- Scales to many ENs without controller config changes

---

### Pattern 2: Inbound Dial (Controller -> EN) - OPTIONAL

The controller initiates the connection to execution nodes. Use only when ENs cannot dial out.

> **WARNING: Service Disruption**
>
> Setting `aap_add_node_enable_controller_peer: true` causes:
>
> - **5-10 second mesh disruption** per node added
> - Running jobs may fail if mid-execution
> - Controller receptor restarts for EACH new node
> - Controller receptor.conf is modified
>
> **Use only when:**
> - EN cannot dial out to controller (strict egress firewall)
> - Customer accepts maintenance window requirement
>
> **Prefer outbound dial** (Pattern 1) whenever possible.

```
┌─────────────────┐                      ┌─────────────────┐
│   Controller    │  ──TCP:27199───────> │ Execution Node  │
│   (tcp-peer)    │      outbound        │ (tcp-listener)  │
└─────────────────┘                      └─────────────────┘
```

**Configuration:**
```ini
[execution_nodes]
exec1.example.com routable_hostname=exec1.example.com

[all:vars]
aap_add_node_enable_controller_peer=true
```

**Firewall requirements:**
| Node | Direction | Port | Notes |
|------|-----------|------|-------|
| Controller | Outbound | 27199/TCP | To each EN |
| EN | Inbound | 27199/TCP | From controller |

**When to use:**
- EN sits behind NAT with no outbound to controller
- Security policy blocks EN->Controller but allows Controller->EN
- DMZ topology where only controller can initiate connections

---

### Pattern 3: Bi-directional (Both Ways)

Both controller and EN can initiate. Provides redundancy but requires both firewall rules.

```
┌─────────────────┐  <──TCP:27199──────> ┌─────────────────┐
│   Controller    │                      │ Execution Node  │
│ (peer+listener) │  ──TCP:27199──────>  │ (peer+listener) │
└─────────────────┘                      └─────────────────┘
```

**Configuration:**
```ini
[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]'

[all:vars]
aap_add_node_enable_controller_peer=true
```

**Firewall requirements:**
| Node | Direction | Port |
|------|-----------|------|
| EN | Outbound | 27199/TCP |
| EN | Inbound | 27199/TCP |
| Controller | Outbound | 27199/TCP |
| Controller | Inbound | 27199/TCP |

**When to use:**
- Maximum redundancy required
- Network path may fail in either direction
- Note: Still causes controller restart disruption

---

### Pattern 4: Multi-hop (EN -> Hop -> Controller)

Execution nodes connect through intermediate hop nodes. Useful for network segmentation.

```
┌──────────────┐              ┌──────────────┐              ┌──────────────┐
│     EN 1     │──TCP:27199──>│              │              │              │
└──────────────┘              │   Hop Node   │──TCP:27199──>│  Controller  │
┌──────────────┐              │              │              │              │
│     EN 2     │──TCP:27199──>│              │              │              │
└──────────────┘              └──────────────┘              └──────────────┘
```

**Use case:** When ENs cannot reach controller directly (DMZ, air-gap bridge, network segmentation).

**Configuration:**
```ini
[execution_nodes]
# ENs peer to hop node
exec1.example.com receptor_peers='["hop1.example.com"]'
exec2.example.com receptor_peers='["hop1.example.com"]'

# Hop node peers to controller
hop1.example.com receptor_type=hop receptor_peers='["controller.example.com"]'
```

**Firewall requirements:**
| Node | Direction | Port | Destination |
|------|-----------|------|-------------|
| EN | Outbound | 27199/TCP | Hop node |
| Hop | Inbound | 27199/TCP | From ENs |
| Hop | Outbound | 27199/TCP | Controller |
| Controller | Inbound | 27199/TCP | From hop |

---

### Pattern 5: Multi-hop Chain (EN -> Hop1 -> Hop2 -> Controller)

Multiple hop layers for complex network topologies.

```
┌────────┐        ┌────────┐        ┌────────┐        ┌────────────┐
│   EN   │──────> │  Hop1  │──────> │  Hop2  │──────> │ Controller │
│        │ 27199  │  (DMZ) │ 27199  │ (Core) │ 27199  │            │
└────────┘        └────────┘        └────────┘        └────────────┘
```

**Configuration:**
```ini
[execution_nodes]
exec1.example.com receptor_peers='["hop1.dmz.example.com"]'
hop1.dmz.example.com receptor_type=hop receptor_peers='["hop2.core.example.com"]'
hop2.core.example.com receptor_type=hop receptor_peers='["controller.example.com"]'
```

---

## Variable Reference

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `receptor_peers` | Per-host | `[]` | List of hostnames this node dials out to |
| `routable_hostname` | Per-host | inventory_hostname | FQDN registered in controller |
| `receptor_port` | Per-host | `27199` | Receptor listener port |
| `receptor_type` | Per-host | `execution` | Node type: `execution` or `hop` |
| `aap_add_node_enable_controller_peer` | Global | `false` | Enable inbound dial (controller -> EN) |

---

## Complete Inventory Examples

### Example 1: Single Controller, Multiple ENs (Outbound)

Most common setup. ENs dial out to controller.

```ini
# inventory.ini - Outbound dial (default, zero disruption)

[automationcontroller]
controller.example.com ansible_connection=local

[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]' routable_hostname=exec1.example.com
exec2.example.com receptor_peers='["controller.example.com"]' routable_hostname=exec2.example.com
exec3.example.com receptor_peers='["controller.example.com"]' routable_hostname=exec3.example.com

# Optional: Custom Instance Groups
[instance_group_production]
exec1.example.com
exec2.example.com

[instance_group_development]
exec3.example.com

[all:vars]
ansible_user=aapuser
ansible_become=true
registry_username=your_rhn_username
registry_password=your_rhn_password
```

### Example 2: Inbound Dial (Controller Initiates)

Use when ENs cannot dial out due to firewall restrictions.

```ini
# inventory.ini - Inbound dial (causes 5-10s disruption per node)

[automationcontroller]
controller.example.com ansible_connection=local

[execution_nodes]
# No receptor_peers - controller will dial TO these nodes
# routable_hostname required - how controller reaches the node
exec1.example.com routable_hostname=exec1.example.com
exec2.example.com routable_hostname=exec2.example.com

[all:vars]
ansible_user=aapuser
ansible_become=true
registry_username=your_rhn_username
registry_password=your_rhn_password

# Enable controller-initiated peering
aap_add_node_enable_controller_peer=true
```

### Example 3: Mixed Direction (Some Outbound, Some Inbound)

Different ENs have different network constraints.

```ini
# inventory.ini - Mixed topology

[automationcontroller]
controller.example.com ansible_connection=local

[execution_nodes]
# These can dial out normally
exec1.example.com receptor_peers='["controller.example.com"]'
exec2.example.com receptor_peers='["controller.example.com"]'

# These are in restricted network - controller must dial to them
exec3.example.com routable_hostname=exec3.example.com aap_add_node_enable_controller_peer=true
exec4.example.com routable_hostname=exec4.example.com aap_add_node_enable_controller_peer=true

[all:vars]
ansible_user=aapuser
```

### Example 4: Multi-hop with DMZ

ENs in secure zone connect through hop node in DMZ.

```ini
# inventory.ini - Multi-hop topology

[automationcontroller]
controller.corp.example.com ansible_connection=local

[execution_nodes]
# Hop node in DMZ - peers to controller
hop1.dmz.example.com receptor_type=hop receptor_peers='["controller.corp.example.com"]'

# ENs in secure zone - peer to hop (cannot reach controller directly)
exec1.secure.example.com receptor_peers='["hop1.dmz.example.com"]'
exec2.secure.example.com receptor_peers='["hop1.dmz.example.com"]'

[all:vars]
ansible_user=aapuser
```

### Example 5: HA Controllers

ENs can peer to any controller. All controllers share the same mesh CA.

```ini
# inventory.ini - HA controller setup

[automationcontroller]
controller1.example.com
controller2.example.com
controller3.example.com

[execution_nodes]
# Peer to multiple controllers for redundancy
exec1.example.com receptor_peers='["controller1.example.com", "controller2.example.com"]'
exec2.example.com receptor_peers='["controller1.example.com", "controller3.example.com"]'

[all:vars]
ansible_user=aapuser
```

### Example 6: Separate Control Host

Running from a host that is not the controller.

```ini
# inventory.ini - Running from separate control host

[automationcontroller]
# NOT local - SSH to controller required
controller.example.com ansible_user=aapuser ansible_host=192.168.1.100

[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]' ansible_user=aapuser ansible_host=192.168.1.101
exec2.example.com receptor_peers='["controller.example.com"]' ansible_user=aapuser ansible_host=192.168.1.102

[all:vars]
# Registry credentials for image pulls
registry_username=your_rhn_username
registry_password=your_rhn_password
```

### Example 7: Hybrid Cloud (On-Prem ENs → Cloud Controller)

Controller in cloud, ENs on-premises. Firewall allows outbound from on-prem to cloud only.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLOUD (GCP/AWS/Azure)                        │
│  ┌─────────────────┐                                                │
│  │   Controller    │◄── tcp:27199 ──┐                               │
│  │ (tcp-listener)  │                │                               │
│  └─────────────────┘                │                               │
└─────────────────────────────────────│───────────────────────────────┘
                                      │ outbound dial
              ════════════════════════│═══════════════════════════
                     FIREWALL: on-prem → cloud ONLY
              ════════════════════════│═══════════════════════════
                                      │
┌─────────────────────────────────────│───────────────────────────────┐
│                          ON-PREMISES                                │
│                               ┌─────┴───────┐                       │
│                     ┌─────────│  Hop Node   │─────────┐             │
│                     │         │ (tcp-peer)  │         │             │
│                     │         └─────────────┘         │             │
│                     │                                 │             │
│              ┌──────┴──────┐                   ┌──────┴──────┐      │
│              │     EN1     │                   │     EN2     │      │
│              │ (tcp-peer)  │                   │ (tcp-peer)  │      │
│              └─────────────┘                   └─────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

```ini
# inventory.ini - Hybrid cloud topology

[automationcontroller]
aap-controller.cloud.example.com ansible_host=35.x.x.x

[execution_nodes]
# Hop node on-prem - can reach cloud, ENs peer to it
hop1.onprem.example.com receptor_type=hop receptor_peers='["aap-controller.cloud.example.com"]'

# ENs on-prem - peer to hop (or direct to cloud if allowed)
exec1.onprem.example.com receptor_peers='["hop1.onprem.example.com"]'
exec2.onprem.example.com receptor_peers='["hop1.onprem.example.com"]'

[all:vars]
ansible_user=aapuser
```

**Key points:**
- Uses Pattern 1 (outbound dial) — on-prem nodes initiate to cloud
- Controller listens on 27199, no outbound from cloud required
- Hop node optional — ENs can peer direct to cloud controller if allowed
- **Installation requires temporary SSH** from installer to all nodes
- Works with any cloud (GCP, AWS, Azure) or on-prem datacenter

**Firewall rules:**
| Source | Destination | Port | Direction |
|--------|-------------|------|-----------|
| Hop/EN (on-prem) | Controller (cloud) | 27199/TCP | Outbound |
| Installer | All nodes | 22/TCP | Outbound (install-time only) |

---

## routable_hostname vs ansible_host

- `ansible_host`: IP/FQDN Ansible uses for SSH connections during installation
- `routable_hostname`: FQDN registered in Controller and used by receptor mesh

**Example where they differ:**
```ini
exec1.example.com ansible_host=10.0.1.50 routable_hostname=exec1.example.com
```

The controller knows the node as `exec1.example.com`, but the installer connects via `10.0.1.50`.

**Why this matters:**
- TLS certificate SAN validation uses `routable_hostname`
- Receptor node ID must match certificate CN/SAN
- Controller uses `routable_hostname` for job routing
- DNS resolution required for `routable_hostname` on the mesh path

---

## Complete Firewall Matrix

| Source | Destination | Port | Pattern | Disruption |
|--------|-------------|------|---------|------------|
| EN | Controller | 27199/TCP | Outbound (1,3) | None |
| EN | Hop | 27199/TCP | Multi-hop (4,5) | None |
| Hop | Controller | 27199/TCP | Multi-hop (4,5) | None |
| Hop | Hop | 27199/TCP | Chain (5) | None |
| Controller | EN | 27199/TCP | Inbound (2,3) | **5-10s per node** |
| Controller | Hop | 27199/TCP | Inbound to hop | **5-10s per node** |

---

## Choosing a Topology

| Scenario | Recommended Pattern | Notes |
|----------|---------------------|-------|
| Standard deployment | 1: Outbound dial | Default, no disruption |
| EN behind NAT | 4: Multi-hop with bastion | Hop in reachable zone |
| EN egress blocked completely | 2: Inbound dial | Accept disruption |
| Maximum redundancy | 3: Bi-directional | Both paths available |
| Air-gapped DMZ | 4/5: Multi-hop chain | Hop nodes bridge zones |
| HA controllers | 1: Outbound dial | EN peers to any controller |
| Mixed network policies | Varies per EN | Different patterns per node OK |

---

## Troubleshooting

### "Connection refused" from EN to Controller

1. Check controller receptor is listening:
   ```bash
   ssh controller grep tcp-listener ~/aap/receptor/etc/receptor.conf
   ```

2. Check firewall on controller:
   ```bash
   ssh controller sudo firewall-cmd --list-ports
   ```

3. Test connectivity from EN:
   ```bash
   ssh exec-node nc -zv controller.example.com 27199
   ```

### Heartbeat not appearing after registration

1. Check receptor is running on EN:
   ```bash
   ssh exec-node systemctl --user status receptor
   ```

2. Check receptor logs:
   ```bash
   ssh exec-node podman logs receptor
   ```

3. Verify TLS handshake (look for certificate errors in logs)

### Inbound dial not working

1. Verify EN has tcp-listener in receptor.conf:
   ```bash
   ssh exec-node grep tcp-listener ~/aap/receptor/etc/receptor.conf
   ```

2. Check EN firewall allows inbound 27199:
   ```bash
   ssh exec-node sudo firewall-cmd --list-ports
   ```

3. Verify controller receptor.conf has tcp-peer entry:
   ```bash
   ssh controller grep -A2 "tcp-peer" ~/aap/receptor/etc/receptor.conf
   ```

### Duplicate machine-id causing registration failures

Cloned VMs often have identical `/etc/machine-id`. When multiple nodes register with the same UUID, the second node overwrites the first in the database.

**Symptom:** Only one of multiple nodes appears in `list_instances` after parallel registration.

**Fix:**
```bash
# On each cloned VM
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
sudo systemctl restart dbus
```

The preflight playbook now detects this automatically.
