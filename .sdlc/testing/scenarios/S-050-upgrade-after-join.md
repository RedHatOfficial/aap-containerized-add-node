# S-050: Full Upgrade After Join

## Metadata

- **Priority**: P2
- **Topology**: AIO (or cluster) with collection-added HN+EN still in inventory
- **Status**: Tested (2.6 AIO)
- **TEST.md**: T-26-AIO-FULL-UPGRADE (T-27 analog still untested)

## Description

After nodes were joined with this collection, confirm a later **full** containerized install/upgrade (`ansible.containerized_installer.install`) succeeds against the **same** mesh inventory. This proves inventory compatibility (especially `receptor_peers` as a real list) — not the `installer` playbook.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Mesh | Hop + EN already green (e.g. after [S-003](S-003-multi-hop.md)) |
| Setup tree | Upgrade/setup bundle matching the cluster (lab: `aap26-11.1_bundle`) |
| Inventory | Both nodes under `[execution_nodes]` with **list-form** peers |
| Peers check | `ansible-inventory -i inventory-growth --host <node>` shows `receptor_peers` as a JSON array, not a string |

## Inventory reminder

```ini
# INI — peers must be JSON-in-quotes (real list)
hn-01.example.com receptor_type=hop receptor_peers='["controller.example.com"]'
en-01.example.com receptor_type=execution receptor_peers='["hn-01.example.com"]'
```

Bare `receptor_peers=hostname` or INI `receptor_peers=['hostname']` causes full-install failures (`hostvars['a']` / `hostvars['[']`).

## Steps

```bash
cd /path/to/containerized-setup-2.6.x   # upgrade / setup tree
export ANSIBLE_COLLECTIONS_PATH="${PWD}/collections:${ANSIBLE_COLLECTIONS_PATH}"

# Confirm peers are lists
ansible-inventory -i inventory-growth --host hn-01.example.com | grep receptor_peers

ansible-playbook -i inventory-growth ansible.containerized_installer.install
```

After success, re-check mesh with [verification.md](../checklists/verification.md).

## Pass Criteria

- [ ] Install playbook exit `0` (including receptor config on hop/EN/controller)
- [ ] Controller + hop + EN still green
- [ ] Jobs still run on the EN

## Notes

- Optional: set `routable_hostname` when `ansible_host` is an IP.
- See [TROUBLESHOOTING.md](../../../docs/TROUBLESHOOTING.md) for peer/list pitfalls.

## Related

- [S-003](S-003-multi-hop.md)
- [INSTALLER_PLAN.md](../../../INSTALLER_PLAN.md)
- TEST.md T-26-AIO-FULL-UPGRADE

## Results Log

| Date | AAP Version | Setup tree | Result | Notes |
|------|-------------|------------|--------|-------|
| 2026-08-07 | 2.6 AIO (`aap26`) | `aap26-11.1_bundle` | Pass | Collection-added `aap26-hn-01` + `aap26-en-01`; list-form peers; full install OK; mesh remained healthy (T-26-AIO-FULL-UPGRADE) |
