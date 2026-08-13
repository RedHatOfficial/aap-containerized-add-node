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

Use the collection FQCN (same pattern as `ansible.containerized_installer.install`).
Running `playbooks/add_execution_nodes.yml` by file path does **not** resolve roles unless the
collection is installed on `ANSIBLE_COLLECTIONS_PATH`.

### Lab (recommended)

Overlay this tree into your containerized setup, then run from any control host that can SSH
to the controller and new nodes:

```bash
SETUP=/path/to/ansible-automation-platform-containerized-setup-2.7
REPO=/path/to/aap-containerized-add-node

rsync -a --delete \
  --exclude='collections/' \
  "${REPO}/installer/stable-2.7/" \
  "${SETUP}/collections/ansible_collections/ansible/containerized_installer/"

export ANSIBLE_COLLECTIONS_PATH="${SETUP}/collections:${ANSIBLE_COLLECTIONS_PATH}"

ansible-playbook -i "${SETUP}/inventory-growth" \
  ansible.containerized_installer.add_execution_nodes \
  -e add_execution_nodes_skip_image_load_if_present=true
```

Use `installer/stable-2.6/` and a 2.6 setup tree for 2.6 labs.

### Local development

```bash
cd installer/stable-2.7
ansible-galaxy collection install -r requirements.yml -p ./collections
ansible-galaxy collection install . -p ./collections
export ANSIBLE_COLLECTIONS_PATH="$(pwd)/collections:${ANSIBLE_COLLECTIONS_PATH}"

ansible-playbook -i /path/to/inventory-growth \
  ansible.containerized_installer.add_execution_nodes
```

### Inventory

Same file as greenfield `install` (`inventory` or `inventory-growth` from your setup tree).
`bundle_dir`, `registry_*`, and `receptor_*` vars come from inventory — there is no
`aap_setup_dir` equivalent.

```ini
[execution_nodes]
en-01.example.com receptor_type=execution \
  receptor_peers='["controller.example.com"]' routable_hostname=en-01.example.com
```

Opt-in inbound dial (causes controller mesh disruption):

```bash
ansible-playbook -i /path/to/inventory-growth \
  ansible.containerized_installer.add_execution_nodes \
  -e add_execution_nodes_enable_controller_peer=true
```

Lab test matrix and variable mapping: [TEST.md](../TEST.md) and [CHANGES.md](CHANGES.md).

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
