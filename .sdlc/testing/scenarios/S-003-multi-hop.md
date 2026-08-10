# S-003: Multi-Hop Topology (EN via HN)

## Metadata

- **Priority**: P1
- **Topology**: AIO + HN + EN (EN → HN → controller)
- **Status**: Tested
- **TEST.md**: T-26-AIO-EN-VIA-HN, T-27-AIO-EN-VIA-HN

## Description

Add hop and execution node in one inventory / one `add_node.yml` run. Hop peers controller; EN peers hop. Prefer outbound dial.

## Prerequisites

| Requirement | Value |
|-------------|-------|
| Controller | Containerized AAP 2.6+ AIO |
| Container | `automation-controller-task` running |
| SSH | Passwordless to controller, hop, and EN |
| Node disk | ≥ 32 GB each (prefer 64 GB) |
| Node OS | RHEL 9.x validated; RHEL 10 EN validated only as S-001 (direct), not yet as EN-via-HN |

## Inventory

```ini
[execution_nodes]
hn-01.example.com ansible_host=... ansible_user=ansible \
  receptor_type=hop receptor_peers='["controller.example.com"]' \
  routable_hostname=hn-01.example.com
en-01.example.com ansible_host=... ansible_user=ansible \
  receptor_type=execution receptor_peers='["hn-01.example.com"]' \
  routable_hostname=en-01.example.com
```

Confirm `receptor_peers` is a **list** (`ansible-inventory --host …`).

## Steps

1. Preflight: [checklists/preflight.md](../checklists/preflight.md)
2. Run `playbooks/add_node.yml` per [TEST.md](../../../TEST.md)
3. Verify: [checklists/verification.md](../checklists/verification.md) — both hosts green; EN capacity > 0

## Pass Criteria

- [ ] Playbook exit `0`
- [ ] Hop green (`node_type=hop`)
- [ ] EN green (`node_type=execution`, capacity > 0, real `ansible-runner-*`)
- [ ] Heartbeats may lag 1–3 minutes after success

## Related

- [S-001](S-001-single-en.md), [S-002](S-002-single-hop.md)
- REQ-002, ADR-003 (outbound-first)

## Results Log

| Date | AAP Version | Controller OS | Node OS | Result | Notes |
|------|-------------|---------------|---------|--------|-------|
| 2026-08 | 2.6 AIO | RHEL 9 | RHEL 9 | Pass | T-26-AIO-EN-VIA-HN — see TEST.md |
| 2026-08-10 | 2.7 AIO | RHEL 10.2 | RHEL 9.8 HN+EN | Pass | T-27-AIO-EN-VIA-HN; raw log local only under `.ignore/lab/runs/` |
