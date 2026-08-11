# S-060: Offline Bundle - Single Execution Node

## Metadata

- **Priority**: P1
- **Topology**: AIO + EN (outbound dial, offline install)
- **Status**: PASS
- **Phase**: PHASE-002

## Description

Generate offline bundle for a single execution node, transfer to target, install locally without SSH from control host.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO |
| Control host | SSH to controller only |
| Target EN | RHEL 9.x or 10.x, podman, ansible-core |
| Receptor image | Pre-pulled or included in bundle |

## Test Steps

### 1. Generate Bundle (on control host)

```bash
cd /path/to/aap_add_node_collection
SETUP=/path/to/containerized-setup-2.x

ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_target_hostname=aap-exec1-rhel9 \
  -e aap_add_node_receptor_peers='["carmaap1.lan"]'
```

### 2. Verify Bundle Created

```bash
ls -la offline-bundles/
tar -tzf offline-bundles/offline-bundle-aap-exec1-rhel9-*.tar.gz
```

Expected contents:
- `README.md`
- `install.yml`
- `vars.yml`
- `receptor/receptor.conf`
- `receptor/tls/receptor.crt`
- `receptor/tls/receptor.key`
- `receptor/tls/ca/mesh-CA.crt`
- `receptor/work_public_key.pem`

### 3. Transfer Bundle (simulate airgap)

```bash
# Copy to target EN
scp offline-bundles/offline-bundle-aap-exec1-rhel9-*.tar.gz \
  ansible@aap-exec1-rhel9:/tmp/
```

### 4. Install on Target EN

```bash
ssh ansible@aap-exec1-rhel9

# Extract
cd /tmp
tar -xzf offline-bundle-aap-exec1-rhel9-*.tar.gz
cd offline-bundle-aap-exec1-rhel9-*

# Review
cat README.md
cat vars.yml

# Verify prereqs
podman --version
ansible --version
podman image exists registry.redhat.io/ansible-automation-platform/receptor-rhel9:latest

# Install (requires root)
sudo ansible-playbook -c local install.yml
```

### 5. Verify on Target EN

```bash
systemctl status receptor
podman exec receptor receptorctl status
```

### 6. Verify on Controller

```bash
ssh ansible@carmaap1.lan \
  'podman exec automation-controller-task awx-manage list_instances'
```

## Pass Criteria

- [ ] Bundle generation exit code `0`
- [ ] Bundle contains all expected files
- [ ] TLS key permissions `0400`
- [ ] Install playbook exit code `0`
- [ ] receptor service running
- [ ] `list_instances` shows `aap-exec1-rhel9`
- [ ] `node_type=execution`
- [ ] `capacity > 0` (within 3 minutes)
- [ ] Heartbeat recent
- [ ] Instance green in UI

## Cleanup

On target EN:
```bash
sudo systemctl stop receptor
sudo systemctl disable receptor
sudo rm -rf /etc/receptor /var/run/receptor /var/lib/receptor
sudo rm /etc/systemd/system/receptor.service
sudo systemctl daemon-reload
rm -rf /tmp/offline-bundle-*
```

On controller:
```bash
podman exec automation-controller-task \
  awx-manage deprovision_instance --hostname=aap-exec1-rhel9
```

## Results Log

| Date | AAP Version | Target OS | Result | Notes |
|------|-------------|-----------|--------|-------|
| 2026-08-11 | 2.6-8 | RHEL 9 | PASS | capacity=16, heartbeat green, all criteria met |
