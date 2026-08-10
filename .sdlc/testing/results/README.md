# Test results (shared vs local)

## What to commit

| Record | Location | Contents |
|--------|----------|----------|
| Matrix status + append-only log | [TEST.md](../../TEST.md) | `T-*` Status, Results log rows |
| Scenario Results Log | Matching `scenarios/S-*.md` | Date, AAP, OS, Pass/Fail, short notes |
| Platform matrix | [test-plan.md](../test-plan.md), REQ-004 | Only when a new OS/AAP cell is proven |

**Do commit:** pass/fail, versions, OS, topology, collection git ref, pointers to public issues.

**Do not commit:** secrets, inventory with real IPs/passwords, full ansible stdout (may contain host data).

## Local-only captures

Testers may keep full playbook logs and filled secrets under **`.ignore/lab/`** (gitignored via `.ignore/`). Suggested layout:

```
.ignore/lab/
├── secrets.<lab>.yml          # from examples/add_node.secrets.yml
└── runs/
    ├── README.md              # optional local index
    └── <lab>-<scenario>-<stamp>.log
```

If your clone has `.ignore/lab/runs/capture_add_node.sh`, use it; otherwise `tee` a log under `/tmp` or `.ignore/lab/runs/`.

## After a shared lab run

1. Append TEST.md Results log  
2. Update TEST.md matrix Status  
3. Append scenario Results Log (if `S-*` exists)  
4. Open/adjust PR so other testers see the claim immediately  
