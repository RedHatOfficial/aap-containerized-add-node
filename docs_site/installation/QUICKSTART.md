# Quickstart: Pick Your Installation Method

Two installation methods available. Pick based on network access:

| Method | Use When | Control Host Needs |
|--------|----------|-------------------|
| **[Online](#method-1-online-installation)** | SSH access from control host to target nodes | SSH to controller + SSH to ENs |
| **[Online + ProxyJump](#proxyjump-bastion)** | SSH via bastion/jumpbox | SSH to jumpbox (routes to targets) |
| **[Offline](#method-2-offline-installation)** | No SSH to target nodes (air-gap, policy, hybrid cloud) | SSH to controller only |

---

## Method 1: Online Installation

Control host runs playbook that SSHes to both controller and execution nodes.

```
Control Host ──SSH──► Controller
             ──SSH──► Execution Node
```

### Topology Decision Tree

```
Can your EN reach the Controller directly?
│
├─ YES → Do you need one EN or multiple?
│        │
│        ├─ One EN     → Single EN
│        └─ Multiple   → Parallel ENs
│
└─ NO  → Is there a hop node between EN and Controller?
         │
         ├─ One hop    → EN via Hop
         ├─ Multiple ENs behind hop → Fan-out behind Hop
         └─ Multiple hops (DMZ layers) → Multi-hop Chain
```

---

### Single EN → Controller

**Scenario:** Simple setup, EN can reach controller directly.

```
Controller ◄── outbound dial ── Execution Node
```

**Steps:**

1. Copy [inventory-single-en.yml](../examples/inventory-examples.md#single-en-controller)
2. Replace `controller.example.com` with your controller FQDN
3. Replace `exec-01.example.com` with your EN FQDN
4. Run:
   ```bash
   ansible-playbook playbooks/add_node.yml -i your-inventory.yml -e aap_setup_dir=/path/to/setup
   ```

---

### Parallel ENs → Controller

**Scenario:** Multiple ENs, all can reach controller directly.

```
Controller ◄── outbound dial ── EN1
           ◄── outbound dial ── EN2
           ◄── outbound dial ── EN3
```

**Steps:**

1. Copy [inventory-parallel-ens.yml](../examples/inventory-examples.md#parallel-ens-controller)
2. Add/remove EN entries as needed
3. All ENs set `receptor_peers: ["controller.example.com"]`
4. Run playbook

---

### EN via Hop → Controller

**Scenario:** EN cannot reach controller directly. Hop relays traffic.

```
Controller ◄── outbound dial ── Hop ◄── outbound dial ── EN
```

**Steps:**

1. Copy [inventory-en-via-hn.yml](../examples/inventory-examples.md#en-via-hop-controller)
2. Hop sets `receptor_peers: ["controller.example.com"]`
3. EN sets `receptor_peers: ["hop.example.com"]` (not controller!)
4. Run playbook — adds both in one run

---

### Fan-out behind Hop

**Scenario:** Multiple ENs at remote site, all behind single hop.

```
Controller ◄── Hop ◄── EN1
               ▲
               └───── EN2
```

**Steps:**

1. Copy [inventory-fanout-behind-hop.yml](../examples/inventory-examples.md#fan-out-behind-hop)
2. All ENs peer to hop: `receptor_peers: ["hop.example.com"]`
3. Hop peers to controller
4. Run playbook

---

### Multi-hop Chain

**Scenario:** DMZ traversal, multiple network tiers.

```
Controller ◄── Hop1 ◄── Hop2 ◄── EN
```

**Steps:**

1. Copy [inventory-multi-hop-chain.yml](../examples/inventory-examples.md#multi-hop-chain)
2. Each node peers to its upstream neighbor
3. Run playbook

---

### ProxyJump / Bastion

**Scenario:** Control host cannot SSH directly to targets — routes through jumpbox.

```
Control Host ──SSH──► Jumpbox ──SSH──► Controller
                            ──SSH──► Execution Node
```

**Steps:**

1. Add `ansible_ssh_common_args` to inventory:
   ```yaml
   all:
     children:
       automationcontroller:
         hosts:
           controller.example.com:
             ansible_ssh_common_args: '-o ProxyJump=ansible@jumpbox.example.com'
       execution_nodes:
         hosts:
           exec1.example.com:
             ansible_ssh_common_args: '-o ProxyJump=ansible@jumpbox.example.com'
             receptor_peers:
               - controller.example.com
   ```

2. Run playbook as normal

**Note:** SSH routes via jumpbox; receptor mesh (27199) is direct between EN and controller.

See [inventory-proxyjump.yml](../examples/inventory-examples.md#proxyjump-bastion) for complete example.

---

## Method 2: Offline Installation

Control host generates a bundle, transfer manually, run locally on target.

```
Control Host ──SSH──► Controller
                          │
                    [Generate Bundle]
                          │
                          ▼
              offline-bundle-exec1.tar.gz
                          │
             [Transfer: USB, SFTP, etc.]
                          │
                          ▼
              Execution Node (local install)
```

### When to Use Offline

- No SSH from control host to execution nodes
- Air-gapped networks
- Hybrid cloud (controller in cloud, ENs on-prem)
- Strict security policies prevent direct access

### Offline Topology Decision Tree

```
What type of node are you adding?
│
├─ Execution Node only
│  │
│  ├─ Can EN reach Controller directly?
│  │  │
│  │  ├─ YES → Single EN Bundle
│  │  └─ NO  → EN must peer to existing Hop
│  │
│  └─ Is EN fully air-gapped (no registry access)?
│     │
│     ├─ YES → Bundle with Images
│     └─ NO  → Standard Bundle
│
├─ Hop Node only → Single HN Bundle
│
└─ Hop + EN chain (remote site)
   │
   └─ Generate HN bundle first, then EN bundle
      Install HN, then EN (order matters!)
```

---

### Single EN Bundle

**Scenario:** Add one execution node, can reach controller directly.

```
Control Host ──SSH──► Controller
                          │
                    [Generate Bundle]
                          ▼
              offline-bundle-exec1.tar.gz
                          │
                   [Transfer to EN]
                          ▼
                 Execution Node (local install)
                          │
                          ▼
              EN ──outbound dial──► Controller
```

**Steps:**

1. **Generate:**
   ```bash
   ansible-playbook playbooks/generate_bundle.yml \
     -i inventory.yml \
     -e aap_setup_dir=/path/to/setup \
     -e aap_add_node_target_hostname=exec1.example.com \
     -e aap_add_node_receptor_peers='["controller.example.com"]'
   ```

2. **Transfer** via approved channel (USB, SFTP, jump host)

3. **Install on EN:**
   ```bash
   tar -xzf offline-bundle-exec1.example.com-*.tar.gz
   cd offline-bundle-exec1.example.com-*
   sudo ansible-playbook -c local install.yml
   ```

---

### Single HN Bundle

**Scenario:** Add hop node to relay future EN traffic.

```
Control Host ──SSH──► Controller
                          │
                    [Generate Bundle]
                          ▼
              offline-bundle-hop1.tar.gz
                          │
                   [Transfer to HN]
                          ▼
                  Hop Node (local install)
                          │
                          ▼
              HN ──outbound dial──► Controller
```

**Steps:**

1. **Generate:**
   ```bash
   ansible-playbook playbooks/generate_bundle.yml \
     -i inventory.yml \
     -e aap_setup_dir=/path/to/setup \
     -e aap_add_node_target_hostname=hop1.example.com \
     -e aap_add_node_target_type=hop \
     -e aap_add_node_receptor_peers='["controller.example.com"]'
   ```

2. **Transfer and install** same as EN

---

### HN + EN Chain Bundle

**Scenario:** Remote site needs hop relay plus execution capacity.

```
Control Host ──SSH──► Controller
                          │
               [Generate HN Bundle first]
                          │
               [Generate EN Bundle second]
                          ▼
              offline-bundle-hop1.tar.gz
              offline-bundle-exec1.tar.gz
                          │
            [Transfer BOTH to remote site]
                          ▼
         Install HN first, then EN (order matters!)
                          │
                          ▼
              EN ──► HN ──► Controller
```

**Steps:**

1. **Generate HN bundle:**
   ```bash
   ansible-playbook playbooks/generate_bundle.yml \
     -i inventory.yml \
     -e aap_setup_dir=/path/to/setup \
     -e aap_add_node_target_hostname=hop1.example.com \
     -e aap_add_node_target_type=hop \
     -e aap_add_node_receptor_peers='["controller.example.com"]'
   ```

2. **Generate EN bundle:**
   ```bash
   ansible-playbook playbooks/generate_bundle.yml \
     -i inventory.yml \
     -e aap_setup_dir=/path/to/setup \
     -e aap_add_node_target_hostname=exec1.example.com \
     -e aap_add_node_receptor_peers='["hop1.example.com"]'
   ```

3. **Transfer both bundles**

4. **Install HN first, then EN** (EN needs HN running to connect)

---

### Bundle with Images (Air-Gapped)

**Scenario:** Target node has no registry access.

Add `-e aap_add_node_bundle_include_images=true` to include receptor container image (~500MB).

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir=/path/to/setup \
  -e aap_add_node_target_hostname=exec1.example.com \
  -e aap_add_node_receptor_peers='["controller.example.com"]' \
  -e aap_add_node_bundle_include_images=true
```

---

### Hybrid Cloud (On-Prem ENs → Cloud Controller)

**Scenario:** Controller in cloud, ENs on-premises, firewall blocks SSH from control host to ENs.

```
┌────────────── CLOUD ──────────────┐
│  Control Host ──► Controller      │
│                      │            │
│               [Generate Bundles]  │
└──────────────────────│────────────┘
                       │
        [Transfer via approved channel]
                       │
┌──────────────────────▼────────────┐
│            ON-PREM                │
│    HN (install first)             │
│      │                            │
│      ▼                            │
│    EN1, EN2 (install after HN)    │
└───────────────────────────────────┘
```

**Steps:**

1. Generate HN bundle (peers to cloud controller)
2. Generate EN bundles (peer to on-prem HN)
3. Transfer all bundles to on-prem site
4. Install HN first, wait for heartbeat
5. Install ENs

---

### Target Prerequisites

- RHEL 9 or 10 with valid subscription
- `podman` installed
- `ansible-core` installed
- Receptor image pre-pulled (unless using `bundle_include_images`):
  ```bash
  podman pull registry.redhat.io/ansible-automation-platform-26/receptor-rhel9:latest
  ```

See [Offline Installation](OFFLINE.md) for complete documentation including:

- ProxyJump/bastion topology
- BYO TLS certificates
- Preflight checks
- Troubleshooting

---

## After Running (Both Methods)

1. Wait 1-2 minutes for heartbeat
2. Verify:
   ```bash
   ssh controller "podman exec automation-controller-task awx-manage list_instances"
   ```
3. Check Controller UI → Administration → Topology

## Troubleshooting

- **No heartbeat:** Check `systemctl status receptor` on new node
- **Connection refused:** Verify firewall allows 27199/TCP
- **Certificate error:** Check `routable_hostname` matches certificate SAN

See [Topology Patterns](../examples/topologies.md) for detailed configuration and [Troubleshooting](../collection/TROUBLESHOOTING.md) for common issues.
