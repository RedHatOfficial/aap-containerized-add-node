# Containerized installer (with add_execution_nodes)

Each `stable-2.6/` and `stable-2.7/` directory is a **complete, runnable**
`ansible.containerized_installer` collection — upstream installer plus
`playbooks/add_execution_nodes.yml` and the `add_execution_nodes` role.

| Branch | Upstream base |
|--------|---------------|
| [stable-2.7](stable-2.7/) | `aap-containerized-installer` `stable-2.7` |
| [stable-2.6](stable-2.6/) | `aap-containerized-installer` `stable-2.6` |

**Docs:** [CHANGES.md](CHANGES.md) — what `add_execution_nodes` adds, variables, play order.

## Run

From the collection root (same as upstream installer development):

```bash
cd installer/stable-2.7
ansible-playbook -i /path/to/inventory playbooks/add_execution_nodes.yml
```

Use the same inventory as greenfield `install` (`inventory` or `inventory-growth` from your
containerized setup tree).

```ini
[execution_nodes]
en-01.example.com receptor_type=execution \
  receptor_peers='["controller.example.com"]' routable_hostname=en-01.example.com
```

Opt-in inbound dial (causes controller mesh disruption):

```bash
ansible-playbook -i /path/to/inventory playbooks/add_execution_nodes.yml \
  -e add_execution_nodes_enable_controller_peer=true
```

## Refresh from upstream

Re-vendor when upstream `stable-2.6` / `stable-2.7` changes (preserves `add_execution_nodes`):

```bash
INSTALLER=/path/to/aap-containerized-installer
REPO=$(pwd)

for branch in stable-2.6 stable-2.7; do
  dest="$REPO/installer/$branch"
  tmp=$(mktemp -d)
  rsync -a \
    --include='playbooks/add_execution_nodes.yml' \
    --include='roles/add_execution_nodes/***' \
    --include='roles/automationcontroller/tasks/register_execution_nodes.yml' \
    --exclude='*' \
    "$dest/" "$tmp/"
  find "$dest" -mindepth 1 -maxdepth 1 ! -name README.md -exec rm -rf {} +
  git -C "$INSTALLER" archive "$branch" | tar -x -C "$dest"
  rsync -a "$tmp/" "$dest/"
  rm -rf "$tmp"
done
```
