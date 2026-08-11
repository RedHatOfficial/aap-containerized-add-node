# Example Inventories

Pick a topology that matches your network. All examples use **outbound dial** (recommended, zero disruption).

## Quick Reference

| Topology | Use Case |
|----------|----------|
| [Single EN](#single-en-controller) | Simple setup |
| [Single HN](#single-hn-controller) | Prep for future ENs |
| [EN via Hop](#en-via-hop-controller) | Remote site relay |
| [Parallel ENs](#parallel-ens-controller) | Scale execution |
| [Fan-out behind Hop](#fan-out-behind-hop) | Multiple ENs at remote site |
| [Multi-hop Chain](#multi-hop-chain) | DMZ traversal |

---

## Single EN → Controller

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

**When to use:** Simple setup, EN can reach controller directly.

```yaml
all:
  children:
    automationcontroller:
      hosts:
        controller.example.com:

    execution_nodes:
      hosts:
        exec-01.example.com:
          receptor_type: execution
          receptor_peers:
            - controller.example.com
          routable_hostname: exec-01.example.com

  vars:
    ansible_user: ansible
    aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
```

---

## Single HN → Controller

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

**When to use:** Prepare relay point for future ENs.

```yaml
all:
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
          routable_hostname: hop-01.example.com

  vars:
    ansible_user: ansible
    aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
```

---

## EN via Hop → Controller

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

**When to use:** EN cannot reach controller directly (DMZ, network segmentation).

```yaml
all:
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
          routable_hostname: hop-01.example.com

        exec-01.example.com:
          receptor_type: execution
          receptor_peers:
            - hop-01.example.com
          routable_hostname: exec-01.example.com

  vars:
    ansible_user: ansible
    aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
```

---

## Parallel ENs → Controller

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

**When to use:** Scale out execution capacity, all ENs reach controller.

```yaml
all:
  children:
    automationcontroller:
      hosts:
        controller.example.com:

    execution_nodes:
      hosts:
        exec-01.example.com:
          receptor_type: execution
          receptor_peers:
            - controller.example.com
          routable_hostname: exec-01.example.com

        exec-02.example.com:
          receptor_type: execution
          receptor_peers:
            - controller.example.com
          routable_hostname: exec-02.example.com

        exec-03.example.com:
          receptor_type: execution
          receptor_peers:
            - controller.example.com
          routable_hostname: exec-03.example.com

  vars:
    ansible_user: ansible
    aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
```

---

## Fan-out behind Hop

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

**When to use:** Remote site with multiple workers behind single relay.

```yaml
all:
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
          routable_hostname: hop-01.example.com

        exec-01.example.com:
          receptor_type: execution
          receptor_peers:
            - hop-01.example.com
          routable_hostname: exec-01.example.com

        exec-02.example.com:
          receptor_type: execution
          receptor_peers:
            - hop-01.example.com
          routable_hostname: exec-02.example.com

  vars:
    ansible_user: ansible
    aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
```

---

## Multi-hop Chain

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

**When to use:** Multi-tier network, DMZ traversal, deep segmentation.

```yaml
all:
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
          routable_hostname: hop-01.example.com

        hop-02.example.com:
          receptor_type: hop
          receptor_peers:
            - hop-01.example.com
          routable_hostname: hop-02.example.com

        exec-01.example.com:
          receptor_type: execution
          receptor_peers:
            - hop-02.example.com
          routable_hostname: exec-01.example.com

  vars:
    ansible_user: ansible
    aap_setup_dir: /path/to/ansible-automation-platform-containerized-setup-2.x
```

---

## Key

| Term | Meaning |
|------|---------|
| `[listener]` | tcp-listener on port 27199, accepts connections |
| `[dials out]` | tcp-peer, initiates connection to upstream |
| `outbound dial` | Node connects to upstream listener (default, zero disruption) |

## Next Steps

1. Copy example closest to your topology
2. Replace hostnames with your FQDNs
3. Set `aap_setup_dir` to your installer path
4. Run preflight: `ansible-playbook playbooks/preflight.yml -i your-inventory.yml`
5. Run add_node: `ansible-playbook playbooks/add_node.yml -i your-inventory.yml`

See [Topology Guide](../collection/TOPOLOGY.md) for detailed configuration options.
