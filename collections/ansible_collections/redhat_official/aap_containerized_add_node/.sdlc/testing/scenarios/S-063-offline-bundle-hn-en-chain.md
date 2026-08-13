# S-063: Offline Bundle - HN + EN Chain

## Metadata

- **Priority**: P1
- **Topology**: AIO + HN + EN (multi-hop, offline install)
- **Status**: PASS
- **Phase**: PHASE-002

## Description

Generate bundles for hop node and execution node behind it. Install hop first, then EN.

```
Controller ◄── HN ◄── EN
```

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO (carmaap1.lan) |
| Control host | SSH to controller only |
| Target HN | aap-flex1-rhel9 |
| Target EN | aap-exec1-rhel9 |

## Test Steps

### 1. Generate HN Bundle

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_target_hostname=aap-flex1-rhel9 \
  -e aap_add_node_target_type=hop \
  -e aap_add_node_receptor_peers='["carmaap1.lan"]'
```

### 2. Generate EN Bundle (peers to HN, not controller)

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_target_hostname=aap-exec1-rhel9 \
  -e aap_add_node_target_type=execution \
  -e aap_add_node_receptor_peers='["aap-flex1-rhel9"]'
```

### 3. Transfer Both Bundles

```bash
scp offline-bundles/offline-bundle-aap-flex1-rhel9-*.tar.gz ansible@aap-flex1-rhel9:/tmp/
scp offline-bundles/offline-bundle-aap-exec1-rhel9-*.tar.gz ansible@aap-exec1-rhel9:/tmp/
```

### 4. Install HN First

```bash
ssh ansible@aap-flex1-rhel9
cd /tmp
tar -xzf offline-bundle-aap-flex1-rhel9-*.tar.gz
cd offline-bundle-aap-flex1-rhel9-*
sudo ansible-playbook -c local install.yml
```

Verify HN:
```bash
systemctl status receptor
podman exec receptor receptorctl status
```

### 5. Install EN (after HN is up)

```bash
ssh ansible@aap-exec1-rhel9
cd /tmp
tar -xzf offline-bundle-aap-exec1-rhel9-*.tar.gz
cd offline-bundle-aap-exec1-rhel9-*
sudo ansible-playbook -c local install.yml
```

### 6. Verify Chain

On EN:
```bash
podman exec receptor receptorctl ping aap-flex1-rhel9
podman exec receptor receptorctl ping carmaap1.lan
```

On controller:
```bash
podman exec automation-controller-task awx-manage list_instances
```

## Pass Criteria

- [ ] Both bundles generated successfully
- [ ] EN bundle peers to HN (not controller)
- [ ] HN install completes first
- [ ] EN can ping HN via receptor
- [ ] EN can ping controller via HN relay
- [ ] Both nodes appear in `list_instances`
- [ ] HN: `node_type=hop`
- [ ] EN: `node_type=execution`, `capacity > 0`
- [ ] Topology UI shows correct chain: EN → HN → Controller

## Order Dependency

**IMPORTANT:** HN must be installed and running before EN. EN cannot connect until its upstream peer (HN) is available.

If EN installed first:
- receptor starts but fails to connect
- Will auto-reconnect once HN is up (redial: true)
- May take up to 60 seconds for reconnection

## Cleanup

```bash
# EN
ssh ansible@aap-exec1-rhel9 'sudo systemctl stop receptor; sudo rm -rf /etc/receptor /var/run/receptor'

# HN
ssh ansible@aap-flex1-rhel9 'sudo systemctl stop receptor; sudo rm -rf /etc/receptor /var/run/receptor'

# Controller
podman exec automation-controller-task awx-manage deprovision_instance --hostname=aap-exec1-rhel9
podman exec automation-controller-task awx-manage deprovision_instance --hostname=aap-flex1-rhel9
```

## Results Log

| Date | AAP Version | HN OS | EN OS | Result | Notes |
|------|-------------|-------|-------|--------|-------|
| 2026-08-11 | 2.6-8 | RHEL 9 (existing) | RHEL 9 | PASS | EN routes via hop: `carmaap1.lan via aap-flex1-rhel9` |
