# Getting Started

This guide walks you through adding execution or hop nodes to your containerized AAP cluster.

**Time estimate:** 15-30 minutes (depending on network speed for image transfer)

---

## Flow Overview

```
  1. PREREQS     2. TOPOLOGY     3. INVENTORY     4. RUN     5. VERIFY
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │  Check   │──▶│  Select  │──▶│  Setup   │──▶│ Execute  │──▶│  Check   │
 │ prereqs  │   │ topology │   │ inventory│   │ playbook │   │  mesh    │
 └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

---

## Step 1: Prerequisites Check

Before starting, verify you have everything required.

### Checklist (All Workflows)

| Requirement | How to verify |
|-------------|---------------|
| AAP 2.6+ containerized | `podman ps` on controller shows `automation-controller-*` |
| Setup directory | You have the extracted `ansible-automation-platform-containerized-setup-2.x` |
| SSH to controller | `ssh <install-user>@controller` works without password |
| New node is RHEL 9/10 | `cat /etc/redhat-release` on new node |
| Non-root user | Collection rejects root — use the same user as AAP install |

### Additional Requirements by Workflow

| Workflow | Additional Requirement |
|----------|----------------------|
| **Standard** (this guide) | SSH to new node: `ssh <install-user>@new-node` works without password |
| **Offline** ([OFFLINE.md](OFFLINE.md)) | Physical/out-of-band access to transfer bundle to new node |
| **Inbound dial** ([TOPOLOGY.md](TOPOLOGY.md)) | Controller can reach new node on receptor port (27199) |

### Verify Controller Container

```bash
ssh <install-user>@<controller>
podman ps --format "{{.Names}}" | grep automation-controller-task
# Should output: automation-controller-task
```

### Verify Setup Directory

```bash
ls /path/to/ansible-automation-platform-containerized-setup-2.x/
# Should contain: inventory, collections/, bundle/, etc.
```

**Blocked?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Step 2: Select Your Topology

### 2.1 Network Access Model

First, determine your network access model:

```
Can control host SSH to both controller AND new node?
│
├─ YES → Standard workflow (this guide)
│        New node dials OUT to controller/hop (default)
│
└─ NO → Offline workflow
        ├─ No SSH to new node? → See OFFLINE.md (bundle generation)
        └─ No outbound from new node? → Inbound dial (controller connects to node)
```

| Scenario | SSH Access | Solution |
|----------|------------|----------|
| Standard | Control host → controller ✓, control host → new node ✓ | This guide (outbound dial) |
| Air-gapped EN | Control host → controller ✓, control host → new node ✗ | [OFFLINE.md](OFFLINE.md) — generate bundle, transfer manually |
| No outbound | New node cannot dial out (strict egress policy) | Inbound dial — see [TOPOLOGY.md](TOPOLOGY.md#inbound-dial) |
| Hybrid cloud | Controller in cloud, nodes on-prem | Outbound dial from on-prem to cloud (standard) |

**Proceeding with standard workflow?** Continue below.

### 2.2 Topology Selection

Answer these questions to find your topology:

```
                    ┌─────────────────────────────────┐
                    │  Can new node reach controller  │
                    │     on receptor port (27199)?   │
                    └───────────────┬─────────────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                      YES                        NO
                       │                         │
                       ▼                         ▼
              ┌────────────────┐       ┌────────────────────┐
              │ How many nodes │       │ Need a hop node    │
              │  to add?       │       │ How many hops?     │
              └───────┬────────┘       └─────────┬──────────┘
                      │                          │
            ┌─────────┴─────────┐      ┌─────────┴─────────┐
            │                   │      │                   │
           ONE              MULTIPLE  ONE HOP          MULTI-HOP
            │                   │      │                   │
            ▼                   ▼      ▼                   ▼
       ┌─────────┐       ┌──────────┐ ┌─────────┐    ┌───────────┐
       │ Single  │       │ Parallel │ │ EN→HN→  │    │ EN→HN2→   │
       │   EN    │       │   ENs    │ │   Ctrl  │    │ HN1→Ctrl  │
       └─────────┘       └──────────┘ └─────────┘    └───────────┘
```

### Topology Quick Reference

| I need to... | Topology | Example File |
|--------------|----------|--------------|
| Add one EN that can reach controller | Single EN | [`inventory-single-en.yml`](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-single-en.yml) |
| Add multiple ENs that can reach controller | Parallel ENs | [`inventory-parallel-ens.yml`](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-parallel-ens.yml) |
| Add EN behind a hop node | EN via Hop | [`inventory-en-via-hn.yml`](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-en-via-hn.yml) |
| Add multiple ENs behind one hop | Fan-out | [`inventory-fanout-behind-hop.yml`](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-fanout-behind-hop.yml) |
| Cross multiple network tiers | Multi-hop chain | [`inventory-multi-hop-chain.yml`](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-multi-hop-chain.yml) |
| On-prem nodes → cloud controller | Hybrid cloud | [`inventory-hybrid-cloud.yml`](https://github.com/RedHatOfficial/aap-containerized-add-node/blob/devel/examples/inventory-hybrid-cloud.yml) |

**Not sure?** See [TOPOLOGY.md](TOPOLOGY.md) for detailed diagrams.

---

## Step 3: Set Up Your Inventory

### 3.1 Copy the Example

```bash
# Pick the example that matches your topology
cp examples/inventory-single-en.yml my-inventory.yml
```

### 3.2 Edit Required Fields

Open `my-inventory.yml` and update:

```yaml
all:
  children:
    automationcontroller:
      hosts:
        controller.example.com:        # ← Your controller hostname
          ansible_user: aap            # ← Your install user

    execution_nodes:
      hosts:
        exec1.example.com:             # ← Your new node hostname
          ansible_user: aap            # ← Your install user
          receptor_type: execution     # execution or hop
          receptor_peers:              # Who this node connects TO
            - controller.example.com   # ← Must be a YAML list
```

### 3.3 Key Fields Explained

| Field | Required | Description |
|-------|----------|-------------|
| `ansible_user` | Yes | SSH user (same as AAP install, non-root) |
| `receptor_type` | Yes | `execution` or `hop` |
| `receptor_peers` | Yes | List of nodes this one dials OUT to |
| `routable_hostname` | If different | Hostname/IP other nodes use to reach this one |

### 3.4 Common Mistakes

| Mistake | Fix |
|---------|-----|
| `receptor_peers: controller` | Must be a list: `receptor_peers: ["controller"]` |
| Using root user | Use non-root user with sudo access |
| Wrong peer direction | New node dials OUT to existing node, not vice versa |

---

## Step 4: Run the Playbook

### 4.1 Set Up Environment

```bash
# Point to your setup directory
SETUP=/path/to/ansible-automation-platform-containerized-setup-2.x

# Install collection dependencies
ansible-galaxy collection install -r requirements.yml

# Install this collection
ansible-galaxy collection install --force --no-deps .

# Include installer collections
export ANSIBLE_COLLECTIONS_PATH="${SETUP}/collections:${ANSIBLE_COLLECTIONS_PATH}"
```

### 4.2 Run (Dry Run First)

```bash
# Check mode - see what would happen
ansible-playbook playbooks/add_node.yml \
  -i my-inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  --check --diff
```

### 4.3 Run (For Real)

```bash
ansible-playbook playbooks/add_node.yml \
  -i my-inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e @my-secrets.yml  # Optional: vault file with registry_password
```

### 4.4 Expected Output

```
PLAY [Add execution/hop nodes] ************************************************

TASK [discover_new_nodes : Find nodes not yet in controller] ******************
ok: [controller.example.com]

TASK [host_prep : Prepare new node] *******************************************
changed: [exec1.example.com]

TASK [register_instance : Register with controller] ***************************
changed: [exec1.example.com]

TASK [verify_mesh : Check node joined mesh] ***********************************
ok: [controller.example.com]

PLAY RECAP ********************************************************************
controller.example.com     : ok=8    changed=0
exec1.example.com          : ok=12   changed=8
```

### 4.5 Re-runs

If images are already on the node (from a previous attempt):

```bash
ansible-playbook playbooks/add_node.yml \
  -i my-inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_skip_image_load=true
```

---

## Step 5: Verify Success

### 5.1 Check Controller UI

1. Log in to AAP Controller
2. Go to **Administration → Topology**
3. New node should appear with green status

### 5.2 Check via CLI

```bash
# SSH to controller and check mesh
ssh <user>@<controller>
podman exec automation-controller-task awx-manage list_instances

# Should show your new node with "heartbeat" value
```

### 5.3 Success Criteria

| Check | Expected |
|-------|----------|
| Node in `list_instances` | Yes, with recent heartbeat |
| Node in Topology view | Green, connected |
| Receptor service running | `systemctl status receptor` on new node |
| Can run jobs on node | Test job template targeting instance group |

---

## Troubleshooting

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| "Container not found" | Wrong container name | Check `podman ps` on controller |
| SSH permission denied | Wrong user or key | Verify `ssh <user>@<host>` works |
| Node not appearing | Registration failed | Check `awx-manage list_instances` output |
| No heartbeat | Receptor not connecting | Check firewall, `receptor_peers` config |
| Image pull failed | Registry auth | Verify `registry_password` in secrets |

### Detailed Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for:
- Container discovery issues
- Failed join recovery
- Manual rollback with `deprovision_instance`
- Receptor connectivity debugging

---

## Next Steps

- **Add more nodes**: Repeat steps 2-5 with additional hosts in inventory
- **Upgrade AAP**: Collection-added nodes survive full installer upgrades
- **Custom TLS**: See [CONVENTIONS.md](CONVENTIONS.md) for BYO certificate options
