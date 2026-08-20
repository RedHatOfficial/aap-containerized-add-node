# Quickstart: Add Execution Nodes to AAP 2.x

Two installation methods available. Pick based on your network access:

| Method | Use When | Control Host Needs |
|--------|----------|-------------------|
| **Online** | SSH access from control host to target nodes | SSH to controller + SSH to ENs |
| **Online + ProxyJump** | SSH via bastion/jumpbox | SSH to jumpbox (routes to targets) |
| **Offline** | No SSH to target nodes (air-gap, policy, hybrid cloud) | SSH to controller only |

> **Scope note:** This collection targets containerized installer workflows.
> For OpenShift/operator-based execution node setup, use native AAP UI docs:
> [AAP 2.6](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/administer-proc_set_up_virtual_machines),
> [AAP 2.7](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.7/administer-proc_set_up_virtual_machines).

---

## Method 1: Online Installation

Control host runs playbook that SSHes to both controller and execution nodes.

```
Control Host ──SSH──► Controller
             ──SSH──► Execution Node
```

### Decision Tree

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

### Single EN → Controller

```
Controller ◄── outbound dial ── Execution Node
```

```bash
ansible-playbook playbooks/add_node.yml \
  -i examples/inventory-single-en.yml \
  -e aap_setup_dir=/path/to/setup
```

### Parallel ENs → Controller

```
Controller ◄── outbound dial ── EN1
           ◄── outbound dial ── EN2
           ◄── outbound dial ── EN3
```

```bash
ansible-playbook playbooks/add_node.yml \
  -i examples/inventory-parallel-ens.yml \
  -e aap_setup_dir=/path/to/setup
```

### EN via Hop → Controller

```
Controller ◄── outbound dial ── Hop ◄── outbound dial ── EN
```

```bash
ansible-playbook playbooks/add_node.yml \
  -i examples/inventory-en-via-hn.yml \
  -e aap_setup_dir=/path/to/setup
```

### Fan-out behind Hop

```
Controller ◄── Hop ◄── EN1
               ▲
               └───── EN2
```

See [examples/inventory-fanout-behind-hop.yml](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-fanout-behind-hop.yml).

### Multi-hop Chain

```
Controller ◄── Hop1 ◄── Hop2 ◄── EN
```

See [examples/inventory-multi-hop-chain.yml](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-multi-hop-chain.yml).

### ProxyJump / Bastion

Control host cannot SSH directly — routes through jumpbox:

```
Control Host ──SSH──► Jumpbox ──SSH──► Controller
                            ──SSH──► Execution Node
```

```bash
ansible-playbook playbooks/add_node.yml \
  -i examples/inventory-proxyjump.yml \
  -e aap_setup_dir=/path/to/setup
```

See [examples/inventory-proxyjump.yml](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-proxyjump.yml).

**Note:** SSH routes via jumpbox; receptor mesh (27199) is direct between EN and controller.

---

## Method 2: Offline Installation

Control host generates a bundle, you transfer it manually, then run locally on target.

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

### Step 1: Generate Bundle (on control host)

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir=/path/to/setup \
  -e _target_hostname=exec1.example.com \
  -e _receptor_peers='["controller.example.com"]'
```

Output: `offline-bundles/offline-bundle-exec1.example.com-YYYY-MM-DD.tar.gz`

### Step 2: Transfer Bundle

Transfer via approved secure channel (USB, SFTP, jump host, etc.).

**Security:** Bundle contains TLS private keys. Delete after installation.

### Step 3: Install on Target Node

```bash
# On the execution node
tar -xzf offline-bundle-exec1.example.com-YYYY-MM-DD.tar.gz
cd offline-bundle-exec1.example.com-YYYY-MM-DD
sudo ansible-playbook -c local install.yml
```

### Prerequisites for Target Node

- RHEL 9 or 10 with valid subscription
- `podman` installed
- `ansible-core` installed
- Receptor image pre-pulled:
  ```bash
  podman pull registry.redhat.io/ansible-automation-platform-26/receptor-rhel9:latest
  ```

### Including Container Images

For fully air-gapped environments, include the receptor image in the bundle:

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir=/path/to/setup \
  -e _target_hostname=exec1.example.com \
  -e _receptor_peers='["controller.example.com"]' \
  -e aap_add_node_bundle_include_images=true
```

Bundle size increases from ~50KB to ~500MB.

See [OFFLINE.md](OFFLINE.md) for complete documentation.

---

## After Installation (Both Methods)

1. Wait 1-2 minutes for heartbeat
2. Verify on controller:
   ```bash
   ssh controller "podman exec automation-controller-task awx-manage list_instances"
   ```
3. Check Controller UI → Administration → Topology

### Verify Receptor Status

```bash
# On execution node
systemctl status receptor
journalctl -u receptor -f
podman logs receptor
```

Node should show green with `capacity=16` and recent heartbeat timestamp.

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| No heartbeat | `systemctl status receptor`, `podman logs receptor` |
| Connection refused | Firewall allows 27199/TCP |
| Certificate error | `routable_hostname` matches certificate SAN |
| capacity=0 | Check receptor logs for permission errors |

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed diagnostics.

## Related Documentation

- [TOPOLOGY.md](TOPOLOGY.md) — Peer direction, firewall matrix, topology patterns
- [OFFLINE.md](OFFLINE.md) — Complete offline bundle documentation
- [CONVENTIONS.md](CONVENTIONS.md) — Variable naming and collection structure
