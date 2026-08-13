# S-061: Offline Bundle - Single Hop Node

## Metadata

- **Priority**: P1
- **Topology**: AIO + HN (outbound dial, offline install)
- **Status**: PASS
- **Phase**: PHASE-002

## Description

Generate offline bundle for a hop node, install locally. Hop nodes relay traffic but cannot run jobs alone.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO |
| Control host | SSH to controller only |
| Target HN | RHEL 9.x or 10.x, podman, ansible-core |
| Receptor image | Pre-pulled or included in bundle |

## Test Steps

### 1. Generate Bundle

```bash
cd /path/to/aap_add_node_collection
SETUP=/path/to/containerized-setup-2.x

ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_target_hostname=aap-flex1-rhel9 \
  -e aap_add_node_target_type=hop \
  -e aap_add_node_receptor_peers='["carmaap1.lan"]'
```

### 2. Verify Bundle

```bash
tar -tzf offline-bundles/offline-bundle-aap-flex1-rhel9-*.tar.gz
```

Expected: NO `work_public_key.pem` (hop nodes don't run jobs).

### 3. Transfer and Install

```bash
scp offline-bundles/offline-bundle-aap-flex1-rhel9-*.tar.gz \
  ansible@aap-flex1-rhel9:/tmp/

ssh ansible@aap-flex1-rhel9
cd /tmp
tar -xzf offline-bundle-aap-flex1-rhel9-*.tar.gz
cd offline-bundle-aap-flex1-rhel9-*
sudo ansible-playbook -c local install.yml
```

### 4. Verify

```bash
# On target
systemctl status receptor
podman exec receptor receptorctl status

# On controller
ssh ansible@carmaap1.lan \
  'podman exec automation-controller-task awx-manage list_instances'
```

## Pass Criteria

- [ ] Bundle generation exit code `0`
- [ ] Bundle does NOT contain `work_public_key.pem`
- [ ] receptor.conf has `tcp-listener` (hop accepts connections)
- [ ] Install playbook exit code `0`
- [ ] `list_instances` shows `aap-flex1-rhel9`
- [ ] `node_type=hop`
- [ ] Node in "ungrouped" (hop nodes not in instance groups)
- [ ] Heartbeat recent

## Results Log

| Date | AAP Version | Target OS | Result | Notes |
|------|-------------|-----------|--------|-------|
| 2026-08-11 | 2.6-8 | RHEL 10 | PASS | node_type=hop, no work_public_key, heartbeat green |
