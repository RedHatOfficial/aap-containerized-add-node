# S-064: Offline Bundle - Hybrid Cloud Simulation

## Metadata

- **Priority**: P2
- **Topology**: Cloud controller + on-prem HN + EN (simulated airgap)
- **Status**: Untested
- **Phase**: PHASE-002
- **REQ**: REQ-006

## Description

Simulate hybrid cloud scenario where:
- Controller runs in "cloud" (carmaap1.lan)
- HN and EN run "on-prem" (aap-flex1, aap-exec1)
- No SSH from control host to on-prem nodes (simulated)
- Bundles transferred via "approved channel"

This validates the workflow described in REQ-006 and docs/OFFLINE.md.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | carmaap1.lan (simulates cloud) |
| Control host | Has SSH to controller only |
| On-prem HN | aap-flex1-rhel9 |
| On-prem EN | aap-exec1-rhel9 |

## Test Steps

### 1. Verify No Direct SSH (Simulation)

For this test, pretend SSH to aap-flex1/aap-exec1 doesn't work from control host.
We'll use SSH only for bundle transfer and local execution.

### 2. Generate On-Prem HN Bundle

```bash
# Control host has SSH to controller only
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_target_hostname=hop-onprem.example.com \
  -e aap_add_node_target_type=hop \
  -e aap_add_node_receptor_peers='["carmaap1.lan"]' \
  -e aap_add_node_bundle_include_images=true
```

Note: Using example hostname that differs from SSH hostname to simulate real scenario.

### 3. Generate On-Prem EN Bundle

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_target_hostname=exec-onprem.example.com \
  -e aap_add_node_target_type=execution \
  -e aap_add_node_receptor_peers='["hop-onprem.example.com"]' \
  -e aap_add_node_bundle_include_images=true
```

### 4. "Transfer via Approved Channel"

```bash
# In reality: USB, secure file transfer, etc.
# For test: SCP to simulate transfer
scp offline-bundles/offline-bundle-hop-onprem*.tar.gz ansible@aap-flex1-rhel9:/tmp/
scp offline-bundles/offline-bundle-exec-onprem*.tar.gz ansible@aap-exec1-rhel9:/tmp/
```

### 5. Install HN On-Prem

```bash
ssh ansible@aap-flex1-rhel9
cd /tmp
tar -xzf offline-bundle-hop-onprem*.tar.gz
cd offline-bundle-hop-onprem*
sudo ansible-playbook -c local install.yml
```

### 6. Install EN On-Prem

```bash
ssh ansible@aap-exec1-rhel9
cd /tmp
tar -xzf offline-bundle-exec-onprem*.tar.gz
cd offline-bundle-exec-onprem*
sudo ansible-playbook -c local install.yml
```

### 7. Verify Connectivity

On EN:
```bash
# Should reach HN
podman exec receptor receptorctl ping hop-onprem.example.com

# Should reach controller via HN
podman exec receptor receptorctl ping carmaap1.lan
```

### 8. Verify in Controller

```bash
ssh ansible@carmaap1.lan \
  'podman exec automation-controller-task awx-manage list_instances'
```

### 9. Run Job on On-Prem EN

In Controller UI:
1. Create/select job template
2. Limit to `exec-onprem.example.com`
3. Run and verify job executes successfully

## Pass Criteria

- [ ] Bundles generated without SSH to on-prem nodes
- [ ] HN peers to cloud controller successfully
- [ ] EN peers to HN successfully
- [ ] EN can ping controller via HN relay
- [ ] Both nodes registered and healthy
- [ ] Job executes on on-prem EN
- [ ] No direct connectivity cloud→on-prem required

## Firewall Validation

This scenario validates:
| Source | Destination | Port | Required |
|--------|-------------|------|----------|
| HN (on-prem) | Controller (cloud) | 27199 | Yes |
| EN (on-prem) | HN (on-prem) | 27199 | Yes |
| Controller (cloud) | EN (on-prem) | * | **No** |

## Results Log

| Date | AAP Version | Result | Notes |
|------|-------------|--------|-------|
| | | | |
