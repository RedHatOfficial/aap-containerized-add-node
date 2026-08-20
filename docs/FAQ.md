# Frequently Asked Questions

## Where should I run the playbook from?

**Recommended: Run from the controller host itself.**

| Location | Pros | Cons |
|----------|------|------|
| Controller (recommended) | Mesh CA already local, fewer SSH hops, `ansible_connection=local` for controller tasks | Ansible must be installed on controller |
| Separate installer host | Clean separation, works with locked-down controllers | Extra SSH hop, must fetch mesh CA over network |
| Any AAP host (hub, EDA) | Works if SSH access configured | Same as separate host |

**Example from controller:**
```ini
[automationcontroller]
controller.example.com ansible_connection=local

[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]'
```

**Example from separate installer host:**
```ini
[automationcontroller]
controller.example.com ansible_user=aapuser

[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]' ansible_user=aapuser
```

---

## What network access is required?

### SSH Access (Installation only)

| Source | Destination | Port | Purpose |
|--------|-------------|------|---------|
| Installer host | Controller | 22/TCP | Fetch mesh CA, run awx-manage |
| Installer host | Execution nodes | 22/TCP | Install receptor, configure service |

### Mesh Connectivity (Runtime)

**Outbound dial (default, recommended):**

| Source | Destination | Port | Purpose |
|--------|-------------|------|---------|
| Execution nodes | Controller | 27199/TCP | Receptor mesh |

**Inbound dial (optional, causes disruption):**

| Source | Destination | Port | Purpose |
|--------|-------------|------|---------|
| Controller | Execution nodes | 27199/TCP | Receptor mesh |

### Registry Access (Installation only)

| Source | Destination | Port | Purpose |
|--------|-------------|------|---------|
| Execution nodes | registry.redhat.io | 443/TCP | Pull receptor image |

---

## What are the prerequisites?

### Controller
- [ ] AAP 2.6+ containerized deployment running
- [ ] `automation-controller-task` container running
- [ ] SSH access from installer host (key-based)
- [ ] Extracted installer bundle (e.g., `ansible-automation-platform-containerized-setup-2.7-3`)

### Execution Nodes
- [ ] RHEL 9.x or RHEL 10.x
- [ ] Active RHEL subscription with repos enabled
- [ ] Non-root user with sudo access
- [ ] SSH key authentication from installer host
- [ ] Unique `/etc/machine-id` (regenerate if cloned from template)
- [ ] DNS resolution for controller hostname
- [ ] ~40GB disk space for container images

### Installer Host
- [ ] ansible-core 2.15+
- [ ] SSH keys configured for controller and execution nodes
- [ ] Access to AAP installer bundle (for collections)

---

## What downtime is required?

| Scenario | Downtime | Details |
|----------|----------|---------|
| Outbound dial (default) | **None** | EN dials to controller; no controller changes |
| Outbound dial + AIO local-only | **5-10 seconds** | One-time controller receptor restart to enable tcp-listener |
| Inbound dial | **5-10 seconds per node** | Controller receptor restart for each new tcp-peer entry |

**Recommendation:** Use outbound dial and schedule during low-usage period if AIO conversion needed.

The preflight playbook warns if AIO local-only conversion will occur:
```bash
ansible-playbook playbooks/preflight.yml -i inventory -e aap_setup_dir=/path/to/setup
```

---

## What user permissions are required?

### On Controller

| Task | User | Privilege |
|------|------|-----------|
| SSH connection | `ansible_user` (same as AAP install user) | No sudo |
| Run awx-manage | Same user | No sudo (podman exec) |
| Enable tcp-listener (AIO only) | Same user | `become: true` for firewalld |

### On Execution Nodes

| Task | User | Privilege |
|------|------|-----------|
| SSH connection | `ansible_user` | Sudo/become access |
| Install packages | Same user | `become: true` |
| Configure podman | Same user | No sudo (rootless) |
| Start receptor service | Same user | No sudo (user systemd) |
| Open firewall port | Same user | `become: true` |

**Key point:** The collection rejects running as root (`ansible_user_uid != 0`). Use a non-root user with sudo access.

---

## How do I configure outbound vs inbound peering?

### Outbound Dial (Default, Recommended)

Execution node initiates connection to controller. Zero disruption.

```ini
[automationcontroller]
controller.example.com ansible_connection=local

[execution_nodes]
# receptor_peers = who this node dials OUT to
exec1.example.com receptor_peers='["controller.example.com"]'
exec2.example.com receptor_peers='["controller.example.com"]'
```

**Firewall:** EN needs outbound 27199 to controller (usually allowed by default).

### Inbound Dial (Causes Disruption)

Controller initiates connection to execution nodes. Use only when EN cannot dial out.

```ini
[automationcontroller]
controller.example.com ansible_connection=local

[execution_nodes]
# No receptor_peers - controller will dial to us
# routable_hostname = how controller reaches this node
exec1.example.com routable_hostname=exec1.example.com
exec2.example.com routable_hostname=exec2.example.com

[all:vars]
aap_add_node_enable_controller_peer=true
```

**Firewall:** EN needs inbound 27199 from controller.

**Warning:** Each node addition causes 5-10 second mesh disruption.

### Bidirectional (Both Ways)

Maximum redundancy. Both firewall rules required.

```ini
[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]' routable_hostname=exec1.example.com

[all:vars]
aap_add_node_enable_controller_peer=true
```

### Multi-hop (EN → Hop → Controller)

For network segmentation where ENs cannot reach controller directly.

```ini
[execution_nodes]
# Hop node peers to controller
hop1.example.com receptor_type=hop receptor_peers='["controller.example.com"]'

# ENs peer to hop node
exec1.example.com receptor_peers='["hop1.example.com"]'
exec2.example.com receptor_peers='["hop1.example.com"]'
```

---

## What is the difference between receptor_peers and routable_hostname?

| Variable | Purpose | Example |
|----------|---------|---------|
| `receptor_peers` | List of hostnames this node dials **out** to | `'["controller.example.com"]'` |
| `routable_hostname` | FQDN registered in controller, used for **inbound** connections | `exec1.example.com` |

**When they differ:**
```ini
# Ansible connects via IP, but receptor uses FQDN
exec1.example.com ansible_host=10.0.1.50 routable_hostname=exec1.example.com
```

- `ansible_host`: Where Ansible SSHs during installation
- `routable_hostname`: What controller uses to reach the node (must be DNS-resolvable from controller)

---

## Can I add multiple nodes at once?

**Yes.** The playbook handles parallel node addition with serialized registration to avoid database race conditions.

```bash
# Add all nodes in inventory
ansible-playbook playbooks/add_node.yml \
  -i inventory \
  -e aap_setup_dir=/path/to/setup
```

No `-l` limit required. Host preparation and receptor installation run in parallel; only database registration is serialized.

---

## What if a node fails mid-installation?

**Re-run the playbook.** The collection is idempotent:

- Nodes with a heartbeat are skipped (already healthy)
- Nodes without a heartbeat are retried
- `provision_instance` is idempotent

If you need to remove a bad registration:
```bash
# On controller
podman exec automation-controller-task \
  awx-manage deprovision_instance --hostname=bad-node.example.com
```

---

## How do I verify the installation worked?

```bash
# Check mesh status
podman exec automation-controller-task awx-manage list_instances

# Expected output:
# exec1.example.com capacity=16 node_type=execution version=ansible-runner-2.4.3 heartbeat="2026-08-10 11:40:30"
```

**What to check:**
- Node appears in output
- `capacity > 0`
- `heartbeat` timestamp is recent (within last few minutes)
- `version` shows ansible-runner version (not `???`)

---

## Why does my cloned VM fail to register?

Cloned VMs share the same `/etc/machine-id`. When multiple nodes register with identical machine-id, the second overwrites the first in the controller database.

**Fix on each cloned VM:**
```bash
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
cat /etc/machine-id  # Verify unique
```

The preflight playbook detects this automatically:
```bash
ansible-playbook playbooks/preflight.yml -i inventory -e aap_setup_dir=/path/to/setup
```

---

## Where do I find more documentation?

| Topic | File |
|-------|------|
| Step-by-step installation | [INSTALL.md](INSTALL.md) |
| Peer topology patterns | [Topology Patterns](TOPOLOGIES.md) |
| Troubleshooting | [Troubleshooting](TROUBLESHOOTING.md) |
