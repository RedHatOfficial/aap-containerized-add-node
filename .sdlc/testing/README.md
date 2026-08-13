# Testing Framework

Structured testing for this collection. **Shared testers:** start here, then use [TEST.md](../../TEST.md) for the living matrix and results log.

## Source of truth (read this first)

| Artifact | Shared in git? | Role |
|----------|----------------|------|
| **[TEST.md](../../TEST.md)** | Yes | **Authoritative** lab matrix (`T-*` IDs), pass criteria, results log |
| **[test-plan.md](test-plan.md)** | Yes | Strategy, platform matrix, priorities |
| **[scenarios/](scenarios/)** | Yes | Detailed procedures (`S-*`); keep in sync with `T-*` via the [mapping](scenarios/README.md#mapping-to-testmd) |
| **[checklists/](checklists/)** | Yes | Reusable preflight / post-join checks |
| **[examples/](../../examples/)** | Yes | Secrets *shape* (`add_node.secrets.yml`) — no real credentials |
| **`.ignore/lab/`** | **No** (gitignored) | Per-tester secrets + optional raw playbook logs |

Do **not** commit lab hostnames/IPs/passwords or full ansible stdout dumps. Record shared outcomes in `TEST.md` (and the scenario Results Log). Keep raw logs under `.ignore/lab/runs/` locally if you want them.

## For shared testers — workflow

1. Read [TEST.md](../../TEST.md) Lab prerequisites + pick a `T-*` (or matching `S-*`) that is Untested or needs re-validation.
2. Copy `examples/add_node.secrets.yml` → local `.ignore/lab/secrets.<lab>.yml` (never commit).
3. Run from a control host that can SSH to controller + nodes as the install user; capture stdout locally.

   **Collection** (`playbooks/add_node.yml`):

   ```bash
   # Optional helper (local only; under .ignore if present):
   # .ignore/lab/runs/capture_add_node.sh aap27 T-27-AIO-EN-VIA-HN

   SETUP=/path/to/containerized-setup
   COL=/path/to/aap-containerized-add-node
   export ANSIBLE_COLLECTIONS_PATH="${SETUP}/collections:${COL}:${ANSIBLE_COLLECTIONS_PATH}"
   ansible-playbook "${COL}/playbooks/add_node.yml" \
     -i "${SETUP}/inventory-growth" \
     -e aap_setup_dir="${SETUP}" \
     -e @.ignore/lab/secrets.<lab>.yml \
     -e aap_add_node_skip_image_load_if_present=true \
     | tee "/tmp/add-node-$(date -u +%Y%m%dT%H%MZ).log"
   ```

   **Installer** (`ansible.containerized_installer.add_execution_nodes`) — when upstream ships it:

   ```bash
   SETUP=/path/to/containerized-setup
   export ANSIBLE_COLLECTIONS_PATH="${SETUP}/collections:${ANSIBLE_COLLECTIONS_PATH}"
   ansible-playbook -i "${SETUP}/inventory-growth" \
     ansible.containerized_installer.add_execution_nodes \
     -e add_execution_nodes_skip_image_load_if_present=true \
     | tee "/tmp/add-execution-nodes-$(date -u +%Y%m%dT%H%MZ).log"
   ```

   Porting spec: [INSTALLER_PLAN.md](../../INSTALLER_PLAN.md). Full commands: [TEST.md](../../TEST.md).

4. Verify with [checklists/verification.md](checklists/verification.md).
5. **Update shared docs** in the same PR (or a follow-up docs PR):
   - Append a row to [TEST.md](../../TEST.md) Results log (`Playbook`: `collection` or `installer`)
   - Flip Status in the TEST.md matrix
   - Append to the matching scenario Results Log (if the `S-*` file exists)
   - Note AAP version, controller OS, **node OS**, topology, branch/commit ref

## Test types

| Type | Location | Purpose | When |
|------|----------|---------|------|
| Static analysis | CI | Lint, changelog, syntax, build | Every PR |
| Scenario / lab | `TEST.md` + `scenarios/` | End-to-end on real AAP | Before release / when claiming a matrix cell |
| Unit / integration | `tests/` (future) | ansible-test | Not required yet |

## Directory structure

```
.sdlc/testing/
├── README.md                 ← You are here
├── test-plan.md              # Strategy + platform matrix
├── scenarios/                # S-* procedures (+ mapping to T-*)
├── checklists/               # Preflight + verification
└── results/README.md         # How results are recorded (no secrets)

TEST.md                       # Authoritative T-* matrix + results log
examples/add_node.secrets.yml # Secrets template
.ignore/lab/                  # Local only: secrets + optional run logs
```

## Quick reference

| Task | Where |
|------|-------|
| What is tested / untested? | [TEST.md](../../TEST.md) |
| Platform / topology priorities | [test-plan.md](test-plan.md) |
| How to run a scenario | Matching `scenarios/S-*.md` or TEST.md scenario details |
| Map `T-*` ↔ `S-*` | [scenarios/README.md](scenarios/README.md#mapping-to-testmd) |
| Record a shared result | TEST.md Results log (+ scenario Results Log) |
| Keep raw ansible logs | Local `.ignore/lab/runs/` only |
| Clean nodes between tests | [checklists/cleanup.md](checklists/cleanup.md) |
