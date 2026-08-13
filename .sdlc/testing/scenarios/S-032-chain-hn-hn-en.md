# S-032: Chain Topology (HN → HN → EN)

## Metadata

- **Priority**: P2
- **Topology**: Controller → HN1 → HN2 → EN
- **Status**: Tested (2026-08-12) - workaround required
- **Phase**: PHASE-001

## Description

Add nodes in chain topology where each node peers to the previous node, not directly to controller.

```
Controller (carmaap1.lan)
    ↑
HN1 (aap-flex1-rhel9) ← peers to controller
    ↑
HN2 (aap-flex1-rhel10) ← peers to HN1
    ↑
EN (aap-exec1-rhel9) ← peers to HN2
```

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO |
| Hop Node 1 | RHEL 9/10 with SSH access |
| Hop Node 2 | RHEL 9/10 with SSH access |
| Execution Node | RHEL 9/10 with SSH access |

## Inventory

**IMPORTANT**: Use short inventory hostnames matching receptor_peers names. Use `ansible_host` for SSH.

```ini
[automationcontroller]
carmaap1.lan

[execution_nodes]
aap-flex1-rhel9 ansible_host=aap-flex1-rhel9.lan receptor_peers='["carmaap1.lan"]' aap_add_node_type=hop
aap-flex1-rhel10 ansible_host=aap-flex1-rhel10.lan receptor_peers='["aap-flex1-rhel9"]' aap_add_node_type=hop
aap-exec1-rhel9 ansible_host=aap-exec1-rhel9.lan receptor_peers='["aap-flex1-rhel10"]'

[all:vars]
ansible_user=pgriffit
registry_username=<redacted>
registry_password=<redacted>
```

## Test Steps

1. **Clean state:**
   ```bash
   for node in aap-flex1-rhel9 aap-flex1-rhel10 aap-exec1-rhel9; do
     podman exec automation-controller-task awx-manage deprovision_instance --hostname="$node"
   done
   ```

2. **Run add_node playbook:**
   ```bash
   ansible-playbook playbooks/add_node.yml \
     -i inventory.ini \
     -e aap_setup_dir=/path/to/setup
   ```

3. **Fix receptor.conf (workaround):**
   The upstream installer puts IP addresses in tcp-peer, but certs use hostname SANs. Manual fix required:
   ```bash
   # On each node that peers to another NEW node (not controller):
   ssh aap-flex1-rhel10.lan "sed -i 's/192.168.x.x/aap-flex1-rhel9/' ~/aap/receptor/etc/receptor.conf"
   ssh aap-exec1-rhel9.lan "sed -i 's/192.168.x.x/aap-flex1-rhel10/' ~/aap/receptor/etc/receptor.conf"
   
   # Restart receptor on affected nodes
   ssh aap-flex1-rhel10.lan "systemctl --user restart receptor"
   ssh aap-exec1-rhel9.lan "systemctl --user restart receptor"
   ```

4. **Verify chain connectivity:**
   ```bash
   # Check routing tables show chain path
   ssh aap-exec1-rhel9.lan "podman logs receptor | grep Routing"
   # Should show: carmaap1.lan via aap-flex1-rhel10 via aap-flex1-rhel9
   ```

## Pass Criteria

- [ ] Playbook completes (with serial receptor install)
- [ ] All nodes registered in Controller
- [ ] Chain routing visible in receptor logs
- [ ] Jobs can execute on EN via hop chain

## Known Issues

1. **IP vs hostname in receptor.conf**: Upstream installer resolves peer hostnames to IPs for receptor.conf, but certificates only have hostname SANs. TLS verification fails. **Workaround**: Manually edit receptor.conf to use hostname.

2. **aap_add_node_type=hop not honored**: Nodes register as `execution` regardless of type variable. Bug in discover_new_nodes variable lookup.

3. **serial: 1 required**: Without serialization, receptor config template fails because peer node hostvars not yet gathered.

## Results Log

| Date | AAP Version | Topology | Result | Notes |
|------|-------------|----------|--------|-------|
| 2026-08-12 | 2.7.3 | HN→HN→EN | PASS (workaround) | Manual receptor.conf fix for IP→hostname |
