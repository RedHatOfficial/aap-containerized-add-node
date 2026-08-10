# Lab test scenarios

Reusable checklist for validating `redhat_official.aap_containerized_add_node` against containerized AAP.
Update the **Status** column and the per-scenario **Last result** notes when you re-run.

Scope: **containerized AAP 2.5+ only** (RPM / OpenShift out of scope).

## How to use this file

1. Pick a scenario ID below.
2. Confirm **Lab prerequisites**.
3. Follow **Pre-flight**, **Run**, and **Pass criteria**.
4. Record date, cluster FQDN, collection commit/version, and pass/fail in **Last result**.
5. On failure, note the failing play/task and whether a re-run or `deprovision_instance` was needed (see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)).

### Installer command pattern

```bash
SETUP=/path/to/ansible-automation-platform-containerized-setup-2.x   # or lab bundle path
COL=/path/to/redhat_official.aap_containerized_add_node
export ANSIBLE_COLLECTIONS_PATH="${SETUP}/collections:${ANSIBLE_COLLECTIONS_PATH}"

# 1) Edit ${SETUP}/inventory (or inventory-growth): add hosts under [execution_nodes]
# 2) Run from installer host that can SSH to controller + new nodes as the install user
ansible-playbook "${COL}/playbooks/add_node.yml" \
  -i "${SETUP}/inventory-growth" \
  -e aap_setup_dir="${SETUP}" \
  -e @"${COL}/examples/add_node.secrets.yml" \
  -e aap_add_node_skip_image_load_if_present=true
```

Lab secrets (gitignored under `.ignore/lab/`) are per cluster, e.g.
`.ignore/lab/secrets.aap26.yml` / `.ignore/lab/secrets.aap27.yml`.
Copy them to the installer host or pass with `-e @…` as needed.

### Pass criteria (all join scenarios)

- Playbook exit code `0`.
- `awx-manage list_instances` shows each new hostname.
- Within a few minutes, instances are **green** with a recent heartbeat:
  - Hop: `node_type=hop`
  - Execution: `node_type=execution`, non-zero `capacity`, real `ansible-runner-*` version (not `???`)
- Topology / Instances UI matches peer intent (`receptor_peers`).

### Manual cleanup between runs

```bash
# On controller, as install user:
podman exec automation-controller-task \
  awx-manage deprovision_instance --hostname=NODE.example.com
podman exec automation-controller-task awx-manage list_instances
```

Then remove or update the host line in inventory before abandoning a join; keep it if you intend to finish.

---

## Lab prerequisites

| Item | Guidance |
|------|----------|
| Controller | Containerized AAP; task container `automation-controller-task` running |
| SSH | Installer host → controller and new nodes as **non-root install user** (passwordless) |
| Disk on new EN/HN | Prefer **≥32 GB** usable on `/` (lab: **64 GB** after ENOSPC on ~9 GB roots while loading `ee-supported`) |
| Images | Bundle install: `bundle/images` present under `aap_setup_dir` |
| Inventory | Same installer inventory the cluster used; new hosts only in `[execution_nodes]` |
| Peers | Prefer outbound dial; INI `receptor_peers='["hop.or.controller"]'` (real list); `aap_add_node_peers_from_control_nodes: false` |

---

## Scenario matrix

| ID | Scenario | Target | Status |
|----|----------|--------|--------|
| T-26-AIO-EN | Execution node peers **controller** | Containerized 2.6 AIO | :white_check_mark: Tested |
| T-26-AIO-HN | Hop node peers **controller** | Containerized 2.6 AIO | :white_check_mark: Tested |
| T-26-AIO-EN-VIA-HN | Hop→controller + EN→hop (same playbook run) | Containerized 2.6 AIO | :white_check_mark: Tested (re-run OK) |
| T-26-AIO-RERUN | Re-run after failed mid-join (no deprovision) | Containerized 2.6 AIO | :white_check_mark: Tested (disk ENOSPC → resize → re-run) |
| T-26-AIO-DEPROV-REJOIN | Deprovision, new VMs/same names, join again | Containerized 2.6 AIO | :white_check_mark: Tested |
| T-26-AIO-FULL-UPGRADE | Full `install` / upgrade after collection-added HN+EN | Containerized 2.6 AIO | :white_check_mark: Tested |
| T-25-AIO-EN | Execution peers controller | Containerized 2.5 AIO | :white_large_square: Untested |
| T-25-AIO-HN | Hop peers controller | Containerized 2.5 AIO | :white_large_square: Untested |
| T-25-AIO-EN-VIA-HN | Hop + EN via hop | Containerized 2.5 AIO | :white_large_square: Untested |
| T-26-CLU-EN | Execution on multi-controller cluster | Containerized 2.6 cluster | :white_large_square: Untested |
| T-26-CLU-HN | Hop on multi-controller cluster | Containerized 2.6 cluster | :white_large_square: Untested |
| T-26-CLU-EN-VIA-HN | Hop + EN via hop on cluster | Containerized 2.6 cluster | :white_large_square: Untested |
| T-27-AIO-EN | Execution peers controller | Containerized 2.7 AIO | :white_large_square: Untested |
| T-27-AIO-HN | Hop peers controller | Containerized 2.7 AIO | :white_large_square: Untested |
| T-27-AIO-EN-VIA-HN | Hop + EN via hop | Containerized 2.7 AIO | :white_large_square: Untested |
| T-27-CLU-* | Cluster variants (EN / HN / via hop) | Containerized 2.7 cluster | :white_large_square: Untested |
| T-SKIP-IMG | Forced `aap_add_node_skip_image_load=true` with images already present | Any tested target | :white_large_square: Optional / partial (default `*_if_present` used in lab) |
| T-LISTENER | AIO `local-only` → `tcp-listener` on first mesh join | AIO (any version) | :white_large_square: Untested as isolated case (often already listening after first hop) |

High-level matrix also lives in [README.md](README.md#tested-against).

---

## Scenario details

### T-26-AIO-EN — Execution node → controller

**Topology:** `EN --(tcp)--> automationcontroller`

**Inventory sketch:**

```ini
[execution_nodes]
en-01.example.com ansible_host=x.x.x.x ansible_user=ansible \
  receptor_type=execution receptor_peers='["controller.example.com"]' \
  routable_hostname=en-01.example.com
```

**Pre-flight**

- [ ] Controller healthy; only expected instances in `list_instances`
- [ ] EN SSH OK as install user; disk space OK
- [ ] Host added under `[execution_nodes]` with `receptor_type=execution`

**Run:** `playbooks/add_node.yml` as above.

**Pass criteria:** EN green in `default` + `executionplane`; can run a job template on that instance group.

**Last result:** Tested on lab AAP 2.6 AIO (`controller.example.com` / controller node id `controller.example.com`).

---

### T-26-AIO-HN — Hop node → controller

**Topology:** `HN --(tcp)--> automationcontroller`

**Inventory sketch:**

```ini
[execution_nodes]
hn-01.example.com ansible_host=x.x.x.x ansible_user=ansible \
  receptor_type=hop receptor_peers='["controller.example.com"]' \
  routable_hostname=hn-01.example.com
```

**Pre-flight**

- [ ] Hop SSH OK; disk OK
- [ ] `receptor_type=hop`, peers = controller hostname as known to the mesh

**Run:** `playbooks/add_node.yml`

**Pass criteria:** Hop green under `ungrouped` (or equivalent), `node_type=hop`, recent heartbeat.

**Last result:** Tested on lab AAP 2.6 AIO.

---

### T-26-AIO-EN-VIA-HN — Hop + execution via hop (combined)

**Topology:** `EN --(tcp)--> HN --(tcp)--> automationcontroller`

**Inventory sketch:**

```ini
[execution_nodes]
hn-01.example.com ansible_host=... ansible_user=ansible \
  receptor_type=hop receptor_peers='["controller.example.com"]' \
  routable_hostname=hn-01.example.com
en-01.example.com ansible_host=... ansible_user=ansible \
  receptor_type=execution receptor_peers='["hn-01.example.com"]' \
  routable_hostname=en-01.example.com
```

**Pre-flight**

- [ ] Both hosts reachable; inventory peer chain correct (EN peers **hop**, not controller)
- [ ] Prefer adding both in one inventory and one playbook run (discovery targets both)

**Run:** single `add_node.yml` covering both hosts.

**Pass criteria:** Both green; EN capacity &gt; 0; mesh path EN→HN→controller visible in Topology.

**Notes**

- Heartbeats / capacity may lag **1–3 minutes** after playbook success (`ansible-runner-???` / `capacity=0` until ready).
- Root disks under ~10 GB can fail during `ee-supported` image load (`no space left on device`).

**Last result:** Tested twice on lab 2.6 AIO (original join; fresh VMs same names new IPs after deprovision). Both times ended with hop + EN green.

---

### T-26-AIO-RERUN — Mid-join failure then re-run

**Intent:** Confirm incomplete nodes (registered or partially prepared, **no** healthy heartbeat skip) are targeted again without manual deprovision.

**Steps**

1. Start a normal join; interrupt or fail mid-play (lab: image load ENOSPC).
2. Fix the underlying issue (disk, podman, SSH).
3. Re-run the **same** playbook / inventory without `deprovision_instance`.

**Pass criteria:** Playbook completes; hosts reach green. Idempotent `provision_instance` / receptor install.

**Last result:** Lab 2.6 AIO — failed on `ee-supported` load (8.8G root); after resize to 64G and re-run, join completed.

---

### T-26-AIO-DEPROV-REJOIN — Clean deprovision and rejoin

**Intent:** Stability after removing instances and rebuilding nodes.

**Steps**

1. `awx-manage deprovision_instance` for hop and EN.
2. Confirm mesh empty aside from controller.
3. Rebuild VMs (or keep hosts); update `ansible_host` if IPs changed.
4. Run `add_node.yml` again.

**Pass criteria:** Same as T-26-AIO-EN-VIA-HN.

**Last result:** Tested on lab 2.6 AIO with new IPs (`.62` hop / `.63` EN); playbook OK; both green after short settle.

---

### T-26-AIO-FULL-UPGRADE — Full installer upgrade with existing HN+EN

**Intent:** After nodes were joined with this collection, confirm a later **full** containerized install/upgrade (`ansible.containerized_installer.install`) succeeds against the same mesh inventory (no `hostvars['a']` / `hostvars['[']` receptor failures; cluster healthy afterward).

**Pre-flight**

- [ ] Mesh already healthy: hop + EN green (e.g. after T-26-AIO-EN-VIA-HN)
- [ ] Upgrade/setup tree ready (lab: `aap26-11.1_bundle` or equivalent)
- [ ] Inventory under that tree lists both nodes under `[execution_nodes]` with **real list** peers, e.g. `receptor_peers='["controller.example.com"]'`
- [ ] Confirm with `ansible-inventory -i inventory-growth --host <node>` that `receptor_peers` is a JSON array (not a string)

**Run**

```bash
cd /path/to/containerized-setup-2.6.x   # upgrade bundle
ansible-playbook -i inventory-growth ansible.containerized_installer.install
```

**Pass criteria**

- Install playbook exit code `0` (including `Create the receptor configuration` on hop/EN/controller)
- After upgrade: controller + hop + EN still green; jobs still run on the EN

**Notes**

- This validates **inventory compatibility** with the official installer after an additive join — not the `installer-overlay` playbook.
- Optional: set `routable_hostname` when `ansible_host` is an IP.

**Last result:** 2026-08-07 — lab 2.6 AIO (`aap26`) with collection-added `aap26-hn-01` + `aap26-en-01`; full upgrade install succeeded; mesh remained healthy.

---

### Untested templates (copy when validating)

Use the same Pre-flight / Run / Pass criteria as the matching 2.6 AIO scenario; change only version and topology (AIO vs multi-controller).

| ID | Change from 2.6 AIO analog |
|----|----------------------------|
| T-25-AIO-* | `aap_setup_dir` = 2.5 containerized tree; cluster is 2.5 AIO |
| T-27-AIO-* | 2.7 containerized tree + 2.7 AIO |
| T-*-CLU-* | ≥2 controllers in `[automationcontroller]`; confirm `groups['automationcontroller'][0]` is fine for `awx-manage`; peers as designed for HA mesh |
| T-*-AIO-FULL-UPGRADE | After additive join, run full `ansible.containerized_installer.install` on that version’s setup tree |

**Last result:** — (not run)

---

## Known lab pitfalls

| Symptom | Mitigation |
|---------|------------|
| `no space left on device` loading `ee-supported-rhel9` | Enlarge root (≥32–64G); clean `/tmp` ansible image dirs; re-run |
| Rootless podman overlay errors on hop/EN | Reset broken storage or rebuild VM; then re-run |
| EN red / `ansible-runner-???` right after success | Wait a few minutes; re-check `list_instances` |
| Stale inventory IPs after rebuild | Update `ansible_host` before playbook |
| Bare `receptor_peers=hostname` or INI `receptor_peers=['hostname']` | Use `receptor_peers='["hostname"]'` (INI) or a YAML list; confirm with `ansible-inventory --host` |
| Image load every lab re-run | Use `aap_add_node_skip_image_load=true` only when images already loaded; default `*_if_present` skips when refs exist |

---

## Results log (append)

| Date | Scenario ID | Cluster | Collection ref | Result | Notes |
|------|-------------|---------|----------------|--------|-------|
| 2026-08 | T-26-AIO-EN | aap26 AIO | lab branch | Pass | EN→controller |
| 2026-08 | T-26-AIO-HN | aap26 AIO | lab branch | Pass | HN→controller |
| 2026-08 | T-26-AIO-EN-VIA-HN | aap26 AIO | lab branch | Pass | Combined mesh |
| 2026-08-07 | T-26-AIO-RERUN | aap26 AIO | lab branch | Pass | After 64G resize |
| 2026-08-07 | T-26-AIO-DEPROV-REJOIN | aap26 AIO | lab branch | Pass | New VMs, same names, new IPs |
| 2026-08-07 | T-26-AIO-FULL-UPGRADE | aap26 AIO | lab (post-join mesh) | Pass | Full install via aap26-11.1_bundle; list-form receptor_peers; HN+EN healthy after |
