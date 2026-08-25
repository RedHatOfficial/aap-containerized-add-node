# Adding Execution Nodes to Containerized AAP

This guide provides step-by-step instructions for adding execution nodes to an existing AAP 2.6+ containerized deployment without re-running the full installer.

## Table of Contents

1. [Service Disruption Warning](#service-disruption-warning)
2. [Overview](#overview)
3. [Prerequisites](#prerequisites)
4. [Execution Node Preparation](#execution-node-preparation)
5. [Controller Preparation](#controller-preparation)
6. [Installation Steps](#installation-steps)
7. [Verification](#verification)
8. [Instance Groups](#instance-groups)
9. [Troubleshooting](#troubleshooting)
10. [Execution Node Changes Reference](#what-the-playbook-changes-on-execution-nodes)

---

## Service Disruption Warning

**Read this section before proceeding.**

### Controller Impact

| Action | Disruption | Duration | Notes |
|--------|------------|----------|-------|
| Enable tcp-listener (AIO only) | **YES** | 5-10 seconds | Receptor restart required |
| Register new instances | No | - | Database write only |
| Create Instance Groups | No | - | Database write only |

**AIO (All-in-One) Deployments:**

If your controller is configured with `local-only` receptor (default for single-node installs), the playbook will enable `tcp-listener` to allow execution nodes to connect. This requires restarting the receptor service on the controller, causing:

- **5-10 second disruption** to any active receptor connections
- Running jobs may fail if they're mid-execution during this window
- New jobs will queue and run after restart completes

To check if this applies to your deployment:
```bash
ssh aapuser@controller.example.com "grep -E 'local-only|tcp-listener' ~/aap/receptor/etc/receptor.conf"
```

- If output shows `local-only`: receptor restart **WILL** occur
- If output shows `tcp-listener`: no restart needed (already configured)

**Recommendation:** Schedule node additions during a maintenance window or low-usage period.

### Execution Node Impact

No impact to existing AAP services. Changes are isolated to the new execution nodes only.

---

## Overview

This collection enables adding execution nodes (and hop nodes) to containerized AAP deployments. It:

- Fetches mesh CA certificates from the existing controller
- Mints TLS certificates for new nodes
- Configures receptor on execution nodes
- Registers nodes with the controller via `awx-manage`
- Creates custom Instance Groups from inventory

**Tested Configurations:**
- AAP 2.7.1 (Controller 4.8.3)
- RHEL 9.x and RHEL 10.0 execution nodes
- Direct topology (Execution Node → Controller)
- Multiple nodes in single playbook run

---

## Topology Quick Reference

This collection supports **outbound dial** by default: execution nodes initiate connections to the controller.

```
[Execution Node] ──outbound TCP:27199──> [Controller]
       ^                                       ^
  receptor_peers                        tcp-listener
```

For inbound dial (controller initiates to EN), see the Topology Guide in the collection docs.

**Key variables:**
| Variable | Purpose |
|----------|---------|
| `receptor_peers` | Who this node dials out to (list of FQDNs) |
| `routable_hostname` | How Controller identifies this node |
| `aap_add_node_enable_controller_peer` | Enable inbound dial (causes disruption) |

---

## Prerequisites

### Controller Requirements

| Requirement | Details |
|-------------|---------|
| AAP Version | 2.6+ containerized deployment |
| Installer Bundle | Extracted setup directory (e.g., `ansible-automation-platform-containerized-setup-2.7-1`) |
| SSH Access | From installer host to controller |
| Container Running | `automation-controller-task` container must be running |

### Execution Node Requirements

| Requirement | Details |
|-------------|---------|
| Operating System | RHEL 9.x or RHEL 10.x |
| Subscription | Active RHEL subscription with repos enabled |
| User Account | Non-root user with sudo/become access |
| SSH Access | Key-based authentication from installer host |
| Network | Outbound TCP 27199 to controller(s) |
| DNS | Hostname resolution for controller |
| Disk Space | ~40GB for container images |

### Installer Host Requirements

| Requirement | Details |
|-------------|---------|
| Ansible | ansible-core 2.14+ |
| Collections | This collection + dependencies |
| SSH Keys | Configured for controller and execution nodes |

---

## Execution Node Preparation

These steps must be completed on each execution node before running the playbook.

### 1. Verify RHEL Subscription

```bash
# Check subscription status
sudo subscription-manager status

# If not registered:
sudo subscription-manager register
sudo subscription-manager attach --auto

# Verify repos are enabled
sudo dnf repolist
```

### 2. Create Ansible User (if needed)

```bash
# Create user
sudo useradd -m aapuser
sudo passwd aapuser

# Add to wheel group for sudo
sudo usermod -aG wheel aapuser

# Configure passwordless sudo (optional but recommended)
echo "aapuser ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/aapuser
```

### 3. Configure SSH Key Authentication

On your installer host:

```bash
# Copy SSH key to execution node
ssh-copy-id aapuser@exec-node.example.com

# Verify key authentication works
ssh aapuser@exec-node.example.com "hostname"
```

### 4. Verify Network Connectivity

On the execution node:

```bash
# Test connectivity to controller on port 27199
nc -zv controller.example.com 27199

# If firewall blocks outbound, open it:
# (Usually not needed - outbound is typically allowed)
```

### 5. Verify DNS Resolution

```bash
# Must resolve controller hostname
nslookup controller.example.com

# Or add to /etc/hosts if DNS not available:
echo "192.168.1.100 controller.example.com" | sudo tee -a /etc/hosts
```

### 6. Verify Unique Machine-ID (Cloned VMs)

If execution nodes were cloned from a template, they may share the same `/etc/machine-id`. This causes registration failures when adding multiple nodes - the second node overwrites the first in the controller database.

```bash
# Check machine-id
cat /etc/machine-id

# If multiple nodes have the SAME value, regenerate on each:
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
cat /etc/machine-id  # Should now be unique
```

The preflight playbook detects duplicate machine-ids automatically.

---

## Controller Preparation

### 1. Verify Controller is Running

```bash
ssh aapuser@controller.example.com

# Check controller container
podman ps | grep automation-controller-task

# Should show: automation-controller-task ... Up ...
```

### 2. Locate Installer Directory

```bash
# Find the installer setup directory
ls -d ~/aap/ansible-automation-platform-containerized-setup-*

# Example output:
# /home/aapuser/aap/ansible-automation-platform-containerized-setup-2.7-1
```

### 3. Install the Collection

On the control host (where you'll run the playbook):

```bash
# Option 1: Direct from GitHub Release URL
ansible-galaxy collection install \
  https://github.com/RedHatOfficial/aap-containerized-add-node/releases/download/v1.0.0/redhat_official-aap_containerized_add_node-1.0.0.tar.gz

# Option 2: Download then install locally
curl -LO https://github.com/RedHatOfficial/aap-containerized-add-node/releases/download/v1.0.0/redhat_official-aap_containerized_add_node-1.0.0.tar.gz
ansible-galaxy collection install redhat_official-aap_containerized_add_node-1.0.0.tar.gz
```

Replace `v1.0.0` with the latest version from [Releases](https://github.com/RedHatOfficial/aap-containerized-add-node/releases).

Verify installation:

```bash
ansible-galaxy collection list | grep aap_containerized_add_node
# Expected output:
# redhat_official.aap_containerized_add_node  1.0.0
```

---

## Installation Steps

### Step 1: Pick Your Topology

Before creating your inventory, decide on your topology. See [Pick Your Topology](QUICKSTART.md) for the decision tree.

**Common patterns:**

| Pattern | EN peers to | Use when |
|---------|-------------|----------|
| Single EN | Controller | EN can reach controller directly |
| EN via Hop | Hop node | EN cannot reach controller (firewall) |
| Multi-hop | Upstream hop | DMZ traversal, network tiers |

### Step 2: Create Inventory File

Create an inventory file (e.g., `add_nodes.ini`):

```ini
# Controller - use ansible_connection=local if running from controller
[automationcontroller]
controller.example.com ansible_connection=local

# Execution nodes to add
[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]' routable_hostname=exec1.example.com
exec2.example.com receptor_peers='["controller.example.com"]' routable_hostname=exec2.example.com

# Optional: Custom Instance Groups (RPM installer style)
# Nodes listed under instance_group_<name> will be added to that IG
[instance_group_production]
exec1.example.com

[instance_group_development]
exec2.example.com

# Variables
[all:vars]
ansible_user=aapuser
ansible_become_password=your_become_password

# Registry credentials for pulling container images
registry_username=your_rhn_username
registry_password=your_rhn_password
```

**Important Notes:**
- `receptor_peers` must be a JSON array in quotes
- `routable_hostname` should be the FQDN the controller uses to reach the node
- Registry credentials are required for pulling images from registry.redhat.io

### Step 3: Install Collection and Set Up Collections Path

```bash
cd /path/to/aap-containerized-add-node

ansible-galaxy collection install -r requirements.yml
ansible-galaxy collection install --force --no-deps .

# Installer collections for image/role parity (adjust setup path)
export ANSIBLE_COLLECTIONS_PATH=./ansible-automation-platform-containerized-setup-2.7-1/collections:${ANSIBLE_COLLECTIONS_PATH}
```

Run `playbooks/*.yml` from the collection source tree (this repository root after clone or extract).

### Step 4: Run Preflight Checks (Recommended)

Run preflight validation before the actual install to catch issues early:

```bash
ansible-playbook -i add_nodes.ini \
  playbooks/preflight.yml \
  -e aap_setup_dir=/home/aapuser/aap/ansible-automation-platform-containerized-setup-2.7-1
```

This validates:
- SSH connectivity to all nodes
- Controller container is running
- Registry credentials are set
- Network connectivity EN→Controller:27199
- DNS resolution
- Inventory format (receptor_peers)
- Machine-ID uniqueness (cloned VMs)
- AIO local-only status (warns about disruption)

### Step 5: Run the Playbook

```bash
# Dry run first (check mode)
ansible-playbook -i add_nodes.ini \
  playbooks/add_node.yml \
  -e aap_setup_dir=/home/aapuser/aap/ansible-automation-platform-containerized-setup-2.7-1 \
  --check --diff

# Add all nodes (registration is serialized automatically)
ansible-playbook -i add_nodes.ini \
  playbooks/add_node.yml \
  -e aap_setup_dir=/home/aapuser/aap/ansible-automation-platform-containerized-setup-2.7-1
```

**Required Variables:**
- `aap_setup_dir`: Full path to the extracted installer directory

**Optional Variables:**
- `aap_add_node_bundle_install`: Set to `true` for offline/bundle mode (default: `false`)

### Step 6: Wait for Mesh Connectivity

After the playbook completes, wait 30-60 seconds for mesh connectivity to establish.

---

## Verification

### Verify Nodes Appear in Controller

```bash
ssh aapuser@controller.example.com

podman exec automation-controller-task awx-manage list_instances
```

Expected output:
```
[default capacity=167]
    exec1.example.com capacity=16 node_type=execution version=ansible-runner-2.4.3 heartbeat="2026-08-10 11:40:30"
    exec2.example.com capacity=16 node_type=execution version=ansible-runner-2.4.3 heartbeat="2026-08-10 11:40:48"
    controller.example.com capacity=135 node_type=hybrid version=4.8.3 heartbeat="2026-08-10 11:41:30"
[controlplane capacity=135]
    controller.example.com capacity=135 node_type=hybrid version=4.8.3 heartbeat="2026-08-10 11:41:30"
[executionplane capacity=32]
    exec1.example.com capacity=16 node_type=execution version=ansible-runner-2.4.3 heartbeat="2026-08-10 11:40:30"
    exec2.example.com capacity=16 node_type=execution version=ansible-runner-2.4.3 heartbeat="2026-08-10 11:40:48"
[production capacity=16]
    exec1.example.com capacity=16 node_type=execution version=ansible-runner-2.4.3 heartbeat="2026-08-10 11:40:30"
[development capacity=16]
    exec2.example.com capacity=16 node_type=execution version=ansible-runner-2.4.3 heartbeat="2026-08-10 11:40:48"
```

**What to Check:**
- Each node appears with `capacity > 0`
- Each node has a recent `heartbeat` timestamp
- Custom Instance Groups appear with correct node membership

### Verify via AAP Web UI

1. Log in to AAP web interface
2. Navigate to **Administration → Topology View**
3. Verify new nodes appear and show as connected
4. Navigate to **Administration → Instance Groups**
5. Verify custom Instance Groups exist with correct nodes

### Run Validation Playbook

```bash
ansible-playbook -i add_nodes.ini \
  playbooks/validate_mesh.yml
```

This playbook:
- Launches Demo Job Template on each custom Instance Group
- Verifies jobs execute on the correct execution nodes
- Reports pass/fail for each node

---

## Instance Groups

### Automatic Creation via Inventory

Instance Groups are created automatically when you define `instance_group_<name>` groups in your inventory:

```ini
[instance_group_production]
exec1.example.com
exec2.example.com

[instance_group_staging]
exec3.example.com
```

This creates:
- Instance Group `production` with exec1 and exec2
- Instance Group `staging` with exec3

### Per-Host Assignment

Alternatively, set `aap_add_node_instance_groups` per host:

```ini
[execution_nodes]
exec1.example.com aap_add_node_instance_groups='["production", "web-tier"]'
```

### Manual Creation via awx-manage

```bash
podman exec automation-controller-task awx-manage register_queue \
  --queuename=mygroup \
  --hostnames=exec1.example.com
```

---

## Troubleshooting

### Node Not Appearing in list_instances

1. **Check receptor is running on execution node:**
   ```bash
   ssh aapuser@exec1.example.com "systemctl --user status receptor"
   ```

2. **Check receptor logs:**
   ```bash
   ssh aapuser@exec1.example.com "podman logs receptor"
   ```

3. **Verify network connectivity:**
   ```bash
   ssh aapuser@exec1.example.com "nc -zv controller.example.com 27199"
   ```

### Heartbeat Missing (capacity=0, version=???)

1. **Wait 60 seconds** - initial heartbeat can take time

2. **Check receptor.conf has correct node ID:**
   ```bash
   ssh aapuser@exec1.example.com "podman exec receptor cat /etc/receptor/receptor.conf | head -5"
   ```
   
   Should show:
   ```yaml
   - node:
       id: exec1.example.com
   ```

3. **Check TLS certificates:**
   ```bash
   ssh aapuser@exec1.example.com "podman exec receptor ls -la /etc/receptor/tls/"
   ```

### Registry Login Failed

1. **Verify credentials are correct:**
   ```bash
   podman login registry.redhat.io
   ```

2. **Check subscription entitlements:**
   ```bash
   subscription-manager list --consumed
   ```

### SSH Connection Refused

1. **Verify SSH key is deployed:**
   ```bash
   ssh-copy-id aapuser@exec1.example.com
   ```

2. **Check SSH host keys are in known_hosts:**
   ```bash
   ssh-keyscan exec1.example.com >> ~/.ssh/known_hosts
   ```

### Permission Denied During Playbook

1. **Verify become password is correct:**
   ```bash
   ansible-playbook ... -K  # prompts for become password
   ```

2. **Or use inventory variable:**
   ```ini
   [all:vars]
   ansible_become_password=your_password
   ```

---

## What the Playbook Changes on Execution Nodes

For reference, the playbook makes these changes to execution nodes. For detailed package versions and RHEL 9 vs RHEL 10 specifics, see [docs/EXECUTION_NODE.md](EXECUTION_NODE.md).

### Packages Installed

| Package | Purpose |
|---------|---------|
| podman | Container runtime |
| podman-remote | Remote podman client |
| crun | OCI container runtime |
| slirp4netns | User-mode networking |
| fuse-overlayfs | Rootless overlay filesystem |
| polkit | Authorization framework |

**RHEL 10 additional:** `podman-sequoia` (post-quantum cryptography support)

### User Configuration

| Change | Command | Purpose |
|--------|---------|---------|
| Add to systemd-journal group | `usermod -aG systemd-journal <user>` | Allow reading journal logs |
| Enable lingering | `loginctl enable-linger <user>` | Allow user services to run without login |

### Directories Created

| Directory | Contents |
|-----------|----------|
| `~/.config/containers/` | podman configuration (containers.conf, storage.conf) |
| `~/.config/receptor/etc/` | receptor.conf, TLS certificates |
| `~/.config/systemd/user/` | receptor.service unit file |
| `~/.local/share/containers/` | podman rootless image/container storage |

### Firewall

```bash
# Port 27199/tcp opened for receptor mesh (if firewalld active)
firewall-cmd --add-port=27199/tcp --permanent
```

### Container Images

| Image | Size |
|-------|------|
| `registry.redhat.io/ansible-automation-platform-27/receptor-rhel9:latest` | ~530 MB |

### Systemd Services

| Service | Type | State |
|---------|------|-------|
| `receptor.service` | User service | Enabled, running |

### SELinux

No changes. SELinux remains in enforcing mode. Receptor runs in rootless podman with standard container contexts.

---

## Rollback

To remove an execution node:

### On Controller
```bash
podman exec automation-controller-task awx-manage deprovision_instance \
  --hostname=exec1.example.com
```

### On Execution Node
```bash
# Stop and remove receptor
systemctl --user stop receptor
systemctl --user disable receptor
podman rm -f receptor

# Remove configuration
rm -rf ~/.config/receptor
rm -f ~/.config/systemd/user/receptor.service

# Optionally remove images
podman rmi registry.redhat.io/ansible-automation-platform-27/receptor-rhel9:latest
```

---

## Support

This collection is community-supported. For issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review receptor logs on execution node
3. Verify network connectivity and TLS certificates

For AAP product support, contact Red Hat Support.
