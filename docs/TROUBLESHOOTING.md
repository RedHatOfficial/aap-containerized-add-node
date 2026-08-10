# Troubleshooting

## Prerequisites (SSH and privileges)

### Who needs SSH?

From the **control host** (where you run `ansible-playbook`):

| Target | User | Privilege |
|--------|------|-----------|
| `groups['automationcontroller'][0]` | Inventory `ansible_user` — the **same non-root install user** used for the containerized AAP install (home contains `~/aap/…`) | **No sudo** for `awx-manage` / mesh CA fetch (`become: false`) |
| New EN/HN hosts | Same style non-root install user (collection asserts `ansible_user_uid != 0`) | Installer `common` / receptor roles; some steps may escalate as the installer does |
| Installer localhost | Local user running the playbook | No special privileges for the default flow |

**Controller sudo exception:** `enable_controller_listener` opens the receptor port with `firewalld` using `become: true` when converting `local-only` → `tcp-listener` (typical AIO). If that play is skipped or firewall is managed elsewhere, controller sudo is not required.

Passwordless SSH keys (or an equivalent ansible connection plugin) must work for those users. Preflight: `assert_controller_container` runs `ping` then `podman inspect` on the first controller.

### Which controller container?

Default: `automation-controller-task` (`aap_add_node_controller_container`).

That is the long-running task container created by `ansible.containerized_installer` (systemd unit `automation-controller-task.service`). `awx-manage` runs there via `podman exec`, same DB as the rest of Controller.

If your site renamed containers:

```bash
# On the controller host, as the install user:
podman ps --format '{{.Names}} {{.Status}}' | grep -i controller
```

Then override:

```bash
ansible-playbook playbooks/add_node.yml ... \
  -e aap_add_node_controller_container=YOUR_TASK_CONTAINER_NAME
```

Preflight fails clearly if the named container is missing or not `running`.

---

## Failed join — what to do

### Prefer re-run first

This collection does **not** auto-deprovision on failure. Re-running `add_node.yml` is usually enough:

- Hosts that already show a **heartbeat** in `list_instances` are skipped.
- Hosts that were `provision_instance`’d but never became healthy (no heartbeat) are targeted again; `provision_instance` is idempotent.

### Manual rollback (remove a bad instance from Controller)

If you need to wipe a partial/bad registration from the DB (as the install user on a controller):

```bash
podman exec automation-controller-task \
  awx-manage deprovision_instance --hostname=bad-node.example.com
```

Confirm with:

```bash
podman exec automation-controller-task awx-manage list_instances
```

Also:

1. **Inventory** — remove the host from `[execution_nodes]` if you are abandoning the join; otherwise a later full installer run may re-add or conflict. Keeping it in inventory without a healthy instance is OK only if you intend to finish the join.
2. **New node** — stop/remove receptor containers and leftover `~/aap` material if you are not retrying (site-specific; this collection does not ship an uninstall play).
3. **Control host** — optional cleanup under `bundles/<hostname>/` and `bundles/_mesh_material/` (minted certs / fetched CA copies).

There is **no** automated rollback playbook yet. Treat `deprovision_instance` as the Controller-side undo; node disk cleanup is manual.

### Common failures

| Symptom | Likely cause |
|---------|----------------|
| Assert: cannot SSH to controller | Wrong `ansible_user` / keys / `ansible_host`; not the install user |
| Assert: container not running | Stack down; wrong `aap_add_node_controller_container` — use `podman ps \| grep controller` |
| Assert: `receptor_peers` must be a list / bare hostname | INI: `receptor_peers='["peer.example.com"]'` or a YAML list — not `receptor_peers=peer…` or `receptor_peers=['peer…']` |
| `hostvars['a']` / `hostvars['[']` during full installer receptor config | Same: peers still a string; confirm with `ansible-inventory -i … --host HOST` that `receptor_peers` is a JSON array |
| `ansible.containerized_installer` not found | Export `ANSIBLE_COLLECTIONS_PATH=$aap_setup_dir/collections:…` |
| Mesh CA fetch fails | Paths under `~/aap/tls/` missing; wrong user home; not containerized controller |
| Verify finds hostname but no heartbeat | Receptor not dialing peer / firewall / TLS; fix mesh then re-run (no deprovision needed) |

---

## Related docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — design and HA `[0]` controller pick
- [README.md](../README.md) — quick start and scope
