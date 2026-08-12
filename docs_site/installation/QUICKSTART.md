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

Pick your topology and copy the inventory from [Inventory Examples](../examples/inventory-examples.md):

| Topology | Example |
|----------|---------|
| Single EN → Controller | [inventory-examples.md#single-en-controller](../examples/inventory-examples.md#single-en-controller) |
| Single HN → Controller | [inventory-examples.md#single-hn-controller](../examples/inventory-examples.md#single-hn-controller) |
| EN via Hop → Controller | [inventory-examples.md#en-via-hop-controller](../examples/inventory-examples.md#en-via-hop-controller) |
| Parallel ENs → Controller | [inventory-examples.md#parallel-ens-controller](../examples/inventory-examples.md#parallel-ens-controller) |
| Fan-out behind Hop | [inventory-examples.md#fan-out-behind-hop](../examples/inventory-examples.md#fan-out-behind-hop) |
| Multi-hop Chain | [inventory-examples.md#multi-hop-chain](../examples/inventory-examples.md#multi-hop-chain) |
| ProxyJump / Bastion | [inventory-examples.md#proxyjump-bastion](../examples/inventory-examples.md#proxyjump-bastion) |

**Run:**
```bash
ansible-playbook playbooks/add_node.yml -i inventory.yml -e aap_setup_dir=/path/to/setup
```

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

### Offline via ProxyJump

**Scenario:** Generate bundle on controller accessed via jumpbox, transfer via jumpbox chain.

**Step 1: Generate bundle (controller via jumpbox)**

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory-proxyjump.yml \
  -e aap_setup_dir=/path/to/setup \
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

---

### Target Prerequisites

- RHEL 9 or 10 with valid subscription
- `podman` installed
- `ansible-core` installed
- Receptor image pre-pulled (unless using `bundle_include_images`):
  ```bash
  podman pull registry.redhat.io/ansible-automation-platform-26/receptor-rhel9:latest
  ```

See [Offline Installation](OFFLINE.md) for complete documentation.

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

See [Inventory Examples](../examples/inventory-examples.md) for complete topologies and [Troubleshooting](../collection/TROUBLESHOOTING.md) for common issues.
