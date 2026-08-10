# Verification Checklist

Run after playbook completes successfully.

## Immediate Checks

- [ ] Playbook exit code is `0`

- [ ] list_instances shows new node
  ```bash
  ssh ansible@controller 'podman exec automation-controller-task awx-manage list_instances'
  ```

- [ ] Node type is correct
  - Execution: `node_type=execution`
  - Hop: `node_type=hop`

## Within 3 Minutes

- [ ] Heartbeat is recent (< 5 minutes old)

- [ ] Execution node has capacity > 0
  ```
  # Look for:
  capacity=XX (should be > 0)
  ```

- [ ] Execution node has real ansible-runner version
  ```
  # Look for:
  ansible-runner-X.Y.Z (not ???)
  ```

## UI Verification

- [ ] Instance appears in Administration > Topology

- [ ] Instance shows green status

- [ ] Peer connections match inventory `receptor_peers`

## Functional Tests

### Execution Node

- [ ] Can run ad-hoc command on node
  1. Administration > Instance Groups > default
  2. Run job template limited to new instance

### Hop Node

- [ ] Execution node via hop can run jobs
  1. Add EN peered to hop
  2. Run job on EN
  3. Verify traffic routes through hop

## Regression Checks

- [ ] Existing nodes still healthy

- [ ] Existing jobs still work

- [ ] Controller services not restarted (outbound dial)

## Documentation

- [ ] Record result in scenario's Results Log

- [ ] Update TEST.md if new configuration tested

- [ ] Note any issues or observations
