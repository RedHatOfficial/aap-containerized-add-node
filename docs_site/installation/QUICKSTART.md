# Quickstart: Pick Your Installation Method

Two installation methods available. Pick based on network access:

| Method | Use When | Control Host Needs |
|--------|----------|-------------------|
| **[Online](#method-1-online-installation)** | SSH access from control host to target nodes | SSH to controller + SSH to ENs |
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

### Quick Steps

1. **Generate bundle:**
   ```bash
   ansible-playbook playbooks/generate_bundle.yml \
     -i inventory.yml \
     -e aap_setup_dir=/path/to/setup \
     -e aap_add_node_target_hostname=exec1.example.com \
     -e aap_add_node_receptor_peers='["controller.example.com"]'
   ```

2. **Transfer** via approved secure channel (USB, SFTP, jump host)

3. **Install on target:**
   ```bash
   tar -xzf offline-bundle-exec1.example.com-*.tar.gz
   cd offline-bundle-exec1.example.com-*
   sudo ansible-playbook -c local install.yml
   ```

### Target Prerequisites

- RHEL 9 or 10 with valid subscription
- `podman` installed
- `ansible-core` installed
- Receptor image pre-pulled:
  ```bash
  podman pull registry.redhat.io/ansible-automation-platform-26/receptor-rhel9:latest
  ```

See [Offline Installation](OFFLINE.md) for complete documentation including:

- Hop node bundles
- Multi-node chains (HN + EN)
- BYO TLS certificates
- Preflight checks

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
