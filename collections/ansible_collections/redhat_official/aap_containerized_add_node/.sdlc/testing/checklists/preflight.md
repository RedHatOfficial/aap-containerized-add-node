# Pre-flight Checklist

Run before any test scenario.

## Controller Checks

- [ ] Controller container running
  ```bash
  ssh ansible@controller podman ps | grep controller-task
  ```

- [ ] awx-manage accessible
  ```bash
  ssh ansible@controller 'podman exec automation-controller-task awx-manage --version'
  ```

- [ ] Existing instances healthy
  ```bash
  ssh ansible@controller 'podman exec automation-controller-task awx-manage list_instances'
  ```

## New Node Checks

- [ ] SSH accessible as non-root
  ```bash
  ssh ansible@new-node hostname
  ```

- [ ] User is non-root
  ```bash
  ssh ansible@new-node id
  # uid should NOT be 0
  ```

- [ ] Disk space sufficient (>= 32 GB)
  ```bash
  ssh ansible@new-node df -h /
  ```

- [ ] Network to controller
  ```bash
  ssh ansible@new-node 'nc -zv controller.example.com 27199'
  ```

## Inventory Checks

- [ ] receptor_peers is a list
  ```bash
  ansible-inventory -i inventory --host new-node | jq .receptor_peers
  # Should be: ["controller.example.com"]
  # NOT: "controller.example.com"
  ```

- [ ] receptor_type is valid
  ```bash
  ansible-inventory -i inventory --host new-node | jq .receptor_type
  # Should be: "execution" or "hop"
  ```

- [ ] routable_hostname set (if ansible_host is IP)
  ```bash
  ansible-inventory -i inventory --host new-node | jq .routable_hostname
  ```

## Setup Directory Checks

- [ ] Collections present
  ```bash
  ls ${SETUP}/collections/ansible_collections/ansible/containerized_installer/
  ```

- [ ] Bundle images present (if bundle install)
  ```bash
  ls ${SETUP}/bundle/images/
  ```

## Environment Checks

- [ ] ANSIBLE_COLLECTIONS_PATH set
  ```bash
  echo $ANSIBLE_COLLECTIONS_PATH | grep -q containerized_installer
  ```
