# Node Cleanup Checklist

Reset EN/HN nodes to clean state between tests.

**WARNING:** Never run on carmaap1.lan (controller)

## Quick Cleanup (Single Node)

```bash
HOST=aap-exec1-rhel9  # Change as needed

ssh $HOST "
  systemctl --user stop receptor 2>/dev/null || true
  systemctl --user disable receptor 2>/dev/null || true
  podman system reset --force 2>/dev/null || true
  podman unshare rm -rf ~/aap
"
```

## Batch Cleanup (All Test Nodes)

```bash
for host in aap-exec1-rhel9 aap-flex1-rhel9 aap-exec1-rhel10 aap-flex1-rhel10; do
  echo "=== Cleaning $host ==="
  ssh $host "
    systemctl --user stop receptor 2>/dev/null || true
    systemctl --user disable receptor 2>/dev/null || true
    podman system reset --force 2>/dev/null || true
    podman unshare rm -rf ~/aap
  "
done
```

## Verification

```bash
for host in aap-exec1-rhel9 aap-flex1-rhel9 aap-exec1-rhel10 aap-flex1-rhel10; do
  echo "=== $host ==="
  ssh $host "
    systemctl --user is-active receptor 2>/dev/null || echo 'receptor: stopped'
    ls ~/aap 2>/dev/null || echo 'aap dir: removed'
    podman ps -a --format '{{.Names}}' 2>/dev/null | grep -q . && echo 'containers: present' || echo 'containers: none'
  "
done
```

## Expected Clean State

| Check | Expected |
|-------|----------|
| receptor service | stopped/failed |
| ~/aap directory | not present |
| podman containers | none |
| podman images | none (optional) |

## Why `podman unshare rm`?

Rootless podman uses user namespaces. Container overlay dirs have subuid-mapped ownership. Regular `rm -rf` fails with permission denied. `podman unshare` enters the user namespace to delete correctly.

## Deprovision from Controller (Optional)

If node was registered, remove from AAP:

```bash
ssh carmaap1.lan "podman exec automation-controller-task awx-manage deprovision_instance --hostname=<node-fqdn>"
```

## Notes

- Flex hosts (aap-flex1-*) may switch between EN/HN roles — always clean before role change
- Permanent ENs (aap-exec1-*) typically stay as ENs — clean only for re-test
