# Inventory Examples

Complete, copy-paste ready inventory files for every topology. All examples use **outbound dial** (recommended, zero disruption).

---

## Quick Reference

| Topology | Use Case |
|----------|----------|
| [Single EN](#single-en-controller) | Simple setup, one execution node |
| [Single HN](#single-hn-controller) | Prep relay for future ENs |
| [EN via Hop](#en-via-hop-controller) | EN cannot reach controller directly |
| [Parallel ENs](#parallel-ens-controller) | Scale execution capacity |
| [Fan-out behind Hop](#fan-out-behind-hop) | Multiple ENs at remote site |
| [Multi-hop Chain](#multi-hop-chain) | DMZ traversal, deep segmentation |
| [ProxyJump Bastion](#proxyjump-bastion) | SSH via jumpbox |
| [Inbound Dial](#inbound-dial-controller-en) | EN cannot dial out (rare) |
| [HA Controllers](#ha-controllers) | Multi-controller redundancy |

---

## Single EN Controller

**Scenario:** Simple setup, EN can reach controller directly.

```
┌─────────────────┐
│   Controller    │
│ controller.com  │◄─────────────────┐
│   [listener]    │                  │
└─────────────────┘                  │
                              outbound dial
                                     │
                              ┌──────┴────────┐
                              │  Execution    │
                              │  exec-01.com  │
                              │  [dials out]  │
                              └───────────────┘
```

=== "INI"

    ```ini
    [automationcontroller]
    controller.example.com

    [execution_nodes]
    exec-01.example.com receptor_peers='["controller.example.com"]'

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

      children:
        automationcontroller:
          hosts:
            controller.example.com:

        execution_nodes:
          hosts:
            exec-01.example.com:
              receptor_peers:
                - controller.example.com
    ```

---

## Single HN Controller

**Scenario:** Prepare relay point for future ENs.

```
┌─────────────────┐
│   Controller    │
│ controller.com  │◄─────────────────┐
│   [listener]    │                  │
└─────────────────┘                  │
                              outbound dial
                                     │
                              ┌──────┴────────┐
                              │     Hop       │
                              │  hop-01.com   │
                              │  [dials out]  │
                              └───────────────┘
```

=== "INI"

    ```ini
    [automationcontroller]
    controller.example.com

    [execution_nodes]
    hop-01.example.com receptor_type=hop receptor_peers='["controller.example.com"]'

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

      children:
        automationcontroller:
          hosts:
            controller.example.com:

        execution_nodes:
          hosts:
            hop-01.example.com:
              receptor_type: hop
              receptor_peers:
                - controller.example.com
    ```

---

## EN via Hop Controller

**Scenario:** EN cannot reach controller directly (DMZ, network segmentation).

```
┌─────────────────┐
│   Controller    │
│ controller.com  │◄─────────────────┐
│   [listener]    │                  │
└─────────────────┘                  │
                              outbound dial
                                     │
                              ┌──────┴────────┐
                              │     Hop       │
                              │  hop-01.com   │◄─────────────────┐
                              │   [listener]  │                  │
                              └───────────────┘                  │
                                                          outbound dial
                                                                 │
                                                          ┌──────┴────────┐
                                                          │  Execution    │
                                                          │  exec-01.com  │
                                                          │  [dials out]  │
                                                          └───────────────┘
```

=== "INI"

    ```ini
    [automationcontroller]
    controller.example.com

    [execution_nodes]
    hop-01.example.com receptor_type=hop receptor_peers='["controller.example.com"]'
    exec-01.example.com receptor_peers='["hop-01.example.com"]'

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

      children:
        automationcontroller:
          hosts:
            controller.example.com:

        execution_nodes:
          hosts:
            hop-01.example.com:
              receptor_type: hop
              receptor_peers:
                - controller.example.com

            exec-01.example.com:
              receptor_peers:
                - hop-01.example.com
    ```

---

## Parallel ENs Controller

**Scenario:** Scale out execution capacity, all ENs reach controller.

```
                         ┌─────────────────┐
              ┌─────────►│   Controller    │◄─────────┐
              │          │ controller.com  │          │
              │          │   [listener]    │          │
              │          └────────▲────────┘          │
              │                   │                   │
       outbound dial       outbound dial       outbound dial
              │                   │                   │
       ┌──────┴──────┐     ┌──────┴──────┐     ┌──────┴──────┐
       │  Execution  │     │  Execution  │     │  Execution  │
       │ exec-01.com │     │ exec-02.com │     │ exec-03.com │
       │ [dials out] │     │ [dials out] │     │ [dials out] │
       └─────────────┘     └─────────────┘     └─────────────┘
```

=== "INI"

    ```ini
    [automationcontroller]
    controller.example.com

    [execution_nodes]
    exec-01.example.com receptor_peers='["controller.example.com"]'
    exec-02.example.com receptor_peers='["controller.example.com"]'
    exec-03.example.com receptor_peers='["controller.example.com"]'

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

      children:
        automationcontroller:
          hosts:
            controller.example.com:

        execution_nodes:
          hosts:
            exec-01.example.com:
              receptor_peers:
                - controller.example.com

            exec-02.example.com:
              receptor_peers:
                - controller.example.com

            exec-03.example.com:
              receptor_peers:
                - controller.example.com
    ```

---

## Fan-out behind Hop

**Scenario:** Remote site with multiple workers behind single relay.

```
┌─────────────────┐
│   Controller    │
│ controller.com  │◄─────────────────┐
│   [listener]    │                  │
└─────────────────┘                  │
                              outbound dial
                                     │
                              ┌──────┴────────┐
              ┌──────────────►│     Hop       │◄──────────────┐
              │               │  hop-01.com   │               │
              │               │   [listener]  │               │
              │               └───────────────┘               │
              │                                               │
       outbound dial                                   outbound dial
              │                                               │
       ┌──────┴──────┐                                 ┌──────┴──────┐
       │  Execution  │                                 │  Execution  │
       │ exec-01.com │                                 │ exec-02.com │
       │ [dials out] │                                 │ [dials out] │
       └─────────────┘                                 └─────────────┘
```

=== "INI"

    ```ini
    [automationcontroller]
    controller.example.com

    [execution_nodes]
    hop-01.example.com receptor_type=hop receptor_peers='["controller.example.com"]'
    exec-01.example.com receptor_peers='["hop-01.example.com"]'
    exec-02.example.com receptor_peers='["hop-01.example.com"]'

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

      children:
        automationcontroller:
          hosts:
            controller.example.com:

        execution_nodes:
          hosts:
            hop-01.example.com:
              receptor_type: hop
              receptor_peers:
                - controller.example.com

            exec-01.example.com:
              receptor_peers:
                - hop-01.example.com

            exec-02.example.com:
              receptor_peers:
                - hop-01.example.com
    ```

---

## Multi-hop Chain

**Scenario:** Multi-tier network, DMZ traversal, deep segmentation.

```
┌─────────────────┐
│   Controller    │
│ controller.com  │◄─────────────────┐
│   [listener]    │                  │
└─────────────────┘                  │
                              outbound dial
                                     │
                              ┌──────┴────────┐
                              │    Hop 1      │
                              │  hop-01.com   │◄─────────────────┐
                              │   [listener]  │                  │
                              └───────────────┘                  │
                                                          outbound dial
                                                                 │
                                                          ┌──────┴────────┐
                                                          │    Hop 2      │
                                                          │  hop-02.com   │◄─────────────────┐
                                                          │   [listener]  │                  │
                                                          └───────────────┘                  │
                                                                                      outbound dial
                                                                                             │
                                                                                      ┌──────┴────────┐
                                                                                      │  Execution    │
                                                                                      │  exec-01.com  │
                                                                                      │  [dials out]  │
                                                                                      └───────────────┘
```

=== "INI"

    ```ini
    [automationcontroller]
    controller.example.com

    [execution_nodes]
    hop-01.example.com receptor_type=hop receptor_peers='["controller.example.com"]'
    hop-02.example.com receptor_type=hop receptor_peers='["hop-01.example.com"]'
    exec-01.example.com receptor_peers='["hop-02.example.com"]'

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

      children:
        automationcontroller:
          hosts:
            controller.example.com:

        execution_nodes:
          hosts:
            hop-01.example.com:
              receptor_type: hop
              receptor_peers:
                - controller.example.com

            hop-02.example.com:
              receptor_type: hop
              receptor_peers:
                - hop-01.example.com

            exec-01.example.com:
              receptor_peers:
                - hop-02.example.com
    ```

---

## ProxyJump Bastion

**Scenario:** Control host cannot SSH directly to targets — routes through jumpbox.

```
┌─────────────────┐
│  Control Host   │
│  (laptop/Mac)   │
└────────┬────────┘
         │ SSH
         ▼
┌─────────────────┐
│    Jumpbox      │
│ bastion.example │
└────────┬────────┘
         │ SSH (to both)
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│ Ctrl   │◄─│   EN   │
│listener│  │dials   │
└────────┘  └────────┘
     27199 (direct)
```

**Note:** SSH goes through jumpbox; receptor mesh (27199) is direct between EN and controller.

=== "INI"

    ```ini
    [automationcontroller]
    controller.example.com ansible_ssh_common_args='-o StrictHostKeyChecking=no -o ProxyJump=ansible@bastion.example.com' ansible_python_interpreter=/usr/bin/python3

    [execution_nodes]
    exec-01.example.com ansible_ssh_common_args='-o StrictHostKeyChecking=no -o ProxyJump=ansible@bastion.example.com' receptor_peers='["controller.example.com"]'

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

      children:
        automationcontroller:
          hosts:
            controller.example.com:
              ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o ProxyJump=ansible@bastion.example.com'
              ansible_python_interpreter: /usr/bin/python3

        execution_nodes:
          hosts:
            exec-01.example.com:
              ansible_ssh_common_args: '-o StrictHostKeyChecking=no -o ProxyJump=ansible@bastion.example.com'
              receptor_peers:
                - controller.example.com
    ```

---

## Inbound Dial Controller EN

**Scenario:** EN cannot dial out due to strict egress firewall. Controller initiates connection.

> **⚠️ WARNING: Service Disruption**
>
> Setting `aap_add_node_enable_controller_peer: true` causes:
>
> - **5-10 second mesh disruption** per node added
> - Running jobs may fail if mid-execution
> - Controller receptor restarts for EACH new node
>
> **Use only when:** EN cannot dial out to controller (strict egress firewall)
>
> **Prefer outbound dial** whenever possible.

```
┌─────────────────┐                      ┌─────────────────┐
│   Controller    │  ──TCP:27199───────> │ Execution Node  │
│   (tcp-peer)    │      outbound        │ (tcp-listener)  │
└─────────────────┘                      └─────────────────┘
```

=== "INI"

    ```ini
    [automationcontroller]
    controller.example.com

    [execution_nodes]
    exec-01.example.com routable_hostname=exec-01.example.com
    exec-02.example.com routable_hostname=exec-02.example.com

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    aap_add_node_enable_controller_peer=true
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"
        aap_add_node_enable_controller_peer: true

      children:
        automationcontroller:
          hosts:
            controller.example.com:

        execution_nodes:
          hosts:
            exec-01.example.com:
              routable_hostname: exec-01.example.com

            exec-02.example.com:
              routable_hostname: exec-02.example.com
    ```

---

## HA Controllers

**Scenario:** ENs can peer to any controller. All controllers share the same mesh CA.

=== "INI"

    ```ini
    [automationcontroller]
    controller1.example.com
    controller2.example.com
    controller3.example.com

    [execution_nodes]
    exec-01.example.com receptor_peers='["controller1.example.com", "controller2.example.com"]'
    exec-02.example.com receptor_peers='["controller1.example.com", "controller3.example.com"]'

    [all:vars]
    ansible_user=ansible
    aap_setup_dir=/path/to/ansible-automation-platform-containerized-setup-2.x
    registry_username=your_rhn_username
    registry_password=your_rhn_password
    ```

=== "YAML"

    ```yaml
    all:
      vars:
        ansible_user: ansible
        aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
        registry_username: "{{ lookup('env', 'REGISTRY_USERNAME') }}"
        registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

      children:
        automationcontroller:
          hosts:
            controller1.example.com:
            controller2.example.com:
            controller3.example.com:

        execution_nodes:
          hosts:
            exec-01.example.com:
              receptor_peers:
                - controller1.example.com
                - controller2.example.com

            exec-02.example.com:
              receptor_peers:
                - controller1.example.com
                - controller3.example.com
    ```

---

## Variable Reference

| Variable | Scope | Default | Description |
|----------|-------|---------|-------------|
| `receptor_peers` | Per-host | `[]` | List of hostnames this node dials out to |
| `receptor_type` | Per-host | `execution` | Node type: `execution` or `hop` |
| `routable_hostname` | Per-host | inventory_hostname | FQDN registered in controller (for mesh routing) |
| `receptor_port` | Per-host | `27199` | Receptor listener port |
| `ansible_ssh_common_args` | Per-host | — | SSH options (e.g., ProxyJump) |
| `aap_add_node_enable_controller_peer` | Global | `false` | Enable inbound dial (controller → EN) |

---

## Key Concepts

| Term | Meaning |
|------|---------|
| `[listener]` | tcp-listener on port 27199, accepts connections |
| `[dials out]` | tcp-peer, initiates connection to upstream |
| `outbound dial` | Node connects to upstream listener (default, zero disruption) |
| `inbound dial` | Controller connects to node (causes mesh restart) |

---

## Next Steps

1. Copy example closest to your topology
2. Replace hostnames with your FQDNs
3. Set `aap_setup_dir` to your installer path
4. Set registry credentials (env vars or direct)
5. Run preflight: `ansible-playbook playbooks/preflight.yml -i inventory.yml`
6. Run add_node: `ansible-playbook playbooks/add_node.yml -i inventory.yml`

See [Topology Patterns](topologies.md) for detailed firewall requirements and troubleshooting.
