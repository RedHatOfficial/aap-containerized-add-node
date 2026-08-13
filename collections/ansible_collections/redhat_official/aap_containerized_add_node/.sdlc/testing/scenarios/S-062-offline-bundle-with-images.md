# S-062: Offline Bundle - With Container Images

## Metadata

- **Priority**: P2
- **Topology**: AIO + EN (fully air-gapped)
- **Status**: BLOCKED (image bundling not implemented)
- **Phase**: PHASE-002

## Description

Generate offline bundle including receptor container image (~500MB). Target EN has no registry access.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO |
| Control host | SSH to controller, receptor image available locally |
| Target EN | RHEL 9.x or 10.x, podman, ansible-core, NO registry access |

## Test Steps

### 1. Ensure Image Available on Control Host

```bash
# Pull if needed
podman pull registry.redhat.io/ansible-automation-platform/receptor-rhel9:latest

# Verify
podman image exists registry.redhat.io/ansible-automation-platform/receptor-rhel9:latest
```

### 2. Generate Bundle with Images

```bash
ansible-playbook playbooks/generate_bundle.yml \
  -i inventory.yml \
  -e aap_setup_dir="${SETUP}" \
  -e aap_add_node_target_hostname=aap-exec1-rhel9 \
  -e aap_add_node_receptor_peers='["carmaap1.lan"]' \
  -e aap_add_node_bundle_include_images=true
```

### 3. Verify Bundle Size and Contents

```bash
ls -lh offline-bundles/offline-bundle-aap-exec1-rhel9-*.tar.gz
# Should be ~500MB+ with images

tar -tzf offline-bundles/offline-bundle-aap-exec1-rhel9-*.tar.gz | grep images
# Should show images/receptor.tar.gz
```

### 4. Simulate Air-Gap on Target

```bash
ssh ansible@aap-exec1-rhel9

# Remove any existing receptor image
podman rmi registry.redhat.io/ansible-automation-platform/receptor-rhel9:latest 2>/dev/null || true

# Verify no image
podman image exists registry.redhat.io/ansible-automation-platform/receptor-rhel9:latest && echo "FAIL: image exists" || echo "OK: no image"
```

### 5. Transfer and Install

```bash
scp offline-bundles/offline-bundle-aap-exec1-rhel9-*.tar.gz \
  ansible@aap-exec1-rhel9:/tmp/

ssh ansible@aap-exec1-rhel9
cd /tmp
tar -xzf offline-bundle-aap-exec1-rhel9-*.tar.gz
cd offline-bundle-aap-exec1-rhel9-*

# Install - should load image from bundle
sudo ansible-playbook -c local install.yml
```

### 6. Verify Image Loaded

```bash
podman image exists registry.redhat.io/ansible-automation-platform/receptor-rhel9:latest && echo "PASS" || echo "FAIL"
```

## Pass Criteria

- [ ] Bundle size > 400MB (includes image)
- [ ] Bundle contains `images/receptor.tar.gz`
- [ ] Target has no pre-existing receptor image
- [ ] Install playbook loads image from bundle
- [ ] receptor service starts successfully
- [ ] Instance registered and healthy

## Results Log

| Date | AAP Version | Target OS | Bundle Size | Result | Notes |
|------|-------------|-----------|-------------|--------|-------|
| | | | | | |
