# Adding an Execution Node to Containerized AAP

## Prerequisites

### Controller Requirements
- AAP 2.6+ containerized deployment running
- SSH access to controller host
- AAP installer bundle extracted (e.g., `ansible-automation-platform-containerized-setup-2.7-1`)

### Execution Node Requirements (Minimal OS Install)

**OS**: RHEL 9 or RHEL 10

**Packages to be installed by playbook**:
- [ ] podman
- [ ] podman-remote
- [ ] crun
- [ ] slirp4netns
- [ ] fuse-overlayfs
- [ ] polkit
- [ ] ansible-core (if running bundle locally)

**Network**:
- [ ] Outbound TCP 27199 to controller(s)
- [ ] DNS resolution for controller hostname

**User Setup**:
- [ ] Non-root user with sudo access
- [ ] SSH key authentication from installer host

**Disk**:
- [ ] ~40GB for container images (EE images are large)

## Procedure (SSH Mode)

### Step 1: Prepare Inventory

```ini
[automationcontroller]
controller.example.com ansible_connection=local

[execution_nodes]
exec1.example.com receptor_peers='["controller.example.com"]' routable_hostname=exec1.example.com

[all:vars]
ansible_user=aapuser
```

### Step 2: Run Node Addition

```bash
cd mesh-node-addition

ansible-playbook -i tests/inventory.aap27 \
  lennysh.aap_add_node/playbooks/add_node.yml \
  -e aap_setup_dir=/home/aapuser/aap/ansible-automation-platform-containerized-setup-2.7-1 \
  -e aap_add_node_hostname=exec1.example.com \
  -e aap_add_node_type=execution \
  -e aap_add_node_peers='["controller.example.com"]' \
  -K  # for become password
```

### Step 3: Verify

```bash
# Check mesh status
ssh aapuser@controller.example.com "podman exec automation-controller-task awx-manage list_instances"

# Expected output includes:
# exec1.example.com capacity=NN node_type=execution version=X.X.X heartbeat="..."
```

### Step 4: Test Job Execution

1. In AAP UI: Administration → Instance Groups → Create
2. Add new execution node to instance group
3. Run "Demo Job Template" targeting the instance group
4. Verify job completes on new execution node

## Troubleshooting

### Node not appearing in list_instances
- Check receptor is running: `systemctl --user status receptor`
- Check receptor logs: `journalctl --user -u receptor`
- Verify peer address in receptor.conf

### Heartbeat missing
- Wait 1-3 minutes for initial heartbeat
- Check network connectivity to controller:27199
- Verify TLS certificates are correct

### Capacity is 0
- Check podman is running
- Verify EE images are loaded: `podman images`

## Changes Made to Execution Node (Minimal Install)

*Documented from testing on aap-exec1-rhel9.lan and aap-exec1-rhel10.lan (2026-08-10):*

### Starting State (Minimal RHEL Install)

Both test nodes started as minimal RHEL installations with:
- Base RHEL packages only
- Network configured (DHCP)
- User account with sudo access
- SSH server running
- RHEL subscription registered

### Packages Installed (by playbook)

**RHEL 9:**
```
crun-1.27-1.el9_8
fuse-overlayfs-1.16-1.el9_7
podman-5.8.2-5.el9_8
polkit-0.117-14.el9
slirp4netns-1.3.3-1.el9
```

**RHEL 10:**
```
crun-1.27-2.el10_2
fuse-overlayfs-1.16-1.el10_1
podman-5.8.2-5.el10_2
podman-sequoia-0.4.0~pqc.3-1.el10_2
polkit-125-4.el10
slirp4netns-1.3.3-1.el10
```

### Firewall Rules
```bash
# Port 27199/tcp opened for receptor mesh (if firewalld active)
firewall-cmd --add-port=27199/tcp --permanent
firewall-cmd --reload

# Verify:
firewall-cmd --list-ports
# Output: 27199/tcp
```

### SELinux Contexts
No custom contexts required. Receptor runs in rootless podman with standard container contexts.
SELinux remains in enforcing mode.

### User/Group Setup
```bash
# User added to systemd-journal group (by playbook)
usermod -aG systemd-journal pgriffit

# Verify:
groups pgriffit
# Output: pgriffit wheel systemd-journal

# Lingering enabled for rootless podman systemd units
loginctl enable-linger pgriffit

# Verify:
loginctl show-user pgriffit -p Linger
# Output: Linger=yes
```

### Directories Created
```
~/.config/containers/           # podman configuration
~/.config/receptor/etc/         # receptor.conf, TLS certs (via container volume)
~/.config/systemd/user/         # receptor.service
~/.local/share/containers/      # podman rootless storage
```

### Container Images Pulled
```bash
# Verify:
podman images --format '{{.Repository}}:{{.Tag}}'

# Output:
registry.redhat.io/ansible-automation-platform-27/receptor-rhel9:latest
```

### Systemd Services
```bash
# receptor.service (user service)
systemctl --user status receptor

# Output:
# ● receptor.service - Podman receptor.service
#      Loaded: loaded (~/.config/systemd/user/receptor.service; enabled)
#      Active: active (running)
```

### Podman Configuration Files
```
~/.config/containers/containers.conf   # crun runtime config
~/.config/containers/storage.conf      # rootless storage path
```

### RHEL 9 vs RHEL 10 Differences

| Aspect | RHEL 9 | RHEL 10 |
|--------|--------|---------|
| Packages | Same versions | +podman-sequoia (post-quantum crypto) |
| Receptor image | receptor-rhel9 | receptor-rhel9 (same) |
| Behavior | Identical | Identical |
| Configuration | Same | Same |

**Both work identically** — tested successfully on both OS versions.

### Pre-requisites Before Running Playbook

1. **RHEL subscription** — repos must be enabled
   ```bash
   sudo subscription-manager status
   sudo dnf repolist
   ```

2. **SSH access** — installer host must SSH as ansible_user with key auth
   ```bash
   ssh-copy-id user@exec-node.example.com
   ```

3. **Network** — outbound TCP 27199 to controller(s)
   ```bash
   nc -zv controller.example.com 27199
   ```

4. **DNS** — hostname resolution for controller
   ```bash
   nslookup controller.example.com
   ```

5. **Registry credentials** — for pulling images from registry.redhat.io
   - Provided via inventory `registry_username` / `registry_password`
   - Or pre-login: `podman login registry.redhat.io`

### Instance Groups (Optional)

Create custom instance groups via inventory:
```ini
[instance_group_mygroup]
exec1.example.com
exec2.example.com
```

The playbook parses `instance_group_*` prefixed groups and creates IGs via `awx-manage register_queue`.

### Post-Installation Verification

```bash
# On execution node - check receptor
systemctl --user status receptor
podman logs receptor | tail -10

# On controller - check mesh
podman exec automation-controller-task awx-manage list_instances

# Expected: node shows with capacity>0 and recent heartbeat
```
