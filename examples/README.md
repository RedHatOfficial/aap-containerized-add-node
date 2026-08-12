# Example Inventories

Pick a topology that matches your network. All examples use **outbound dial** (recommended, zero disruption).

## Quick Reference

| Topology | File | Use Case |
|----------|------|----------|
| Single EN | [inventory-single-en.yml](inventory-single-en.yml) | Simple setup |
| Single HN | [inventory-single-hn.yml](inventory-single-hn.yml) | Prep for future ENs |
| EN via Hop | [inventory-en-via-hn.yml](inventory-en-via-hn.yml) | Remote site relay |
| Parallel ENs | [inventory-parallel-ens.yml](inventory-parallel-ens.yml) | Scale execution |
| Fan-out behind Hop | [inventory-fanout-behind-hop.yml](inventory-fanout-behind-hop.yml) | Multiple ENs at remote site |
| Multi-hop Chain | [inventory-multi-hop-chain.yml](inventory-multi-hop-chain.yml) | DMZ traversal |
| Hybrid Cloud | [inventory-hybrid-cloud.yml](inventory-hybrid-cloud.yml) | On-prem ENs → cloud controller |
| **ProxyJump** | [inventory-proxyjump.yml](inventory-proxyjump.yml) | SSH via bastion/jumpbox |

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

**File:** [inventory-single-en.yml](inventory-single-en.yml)

**When to use:** Simple setup, EN can reach controller directly.

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

**File:** [inventory-single-hn.yml](inventory-single-hn.yml)

**When to use:** Prepare relay point for future ENs.

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

**File:** [inventory-en-via-hn.yml](inventory-en-via-hn.yml)

**When to use:** EN cannot reach controller directly (DMZ, network segmentation).

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

**File:** [inventory-parallel-ens.yml](inventory-parallel-ens.yml)

**When to use:** Scale out execution capacity, all ENs reach controller.

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

**File:** [inventory-fanout-behind-hop.yml](inventory-fanout-behind-hop.yml)

**When to use:** Remote site with multiple workers behind single relay.

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

**File:** [inventory-multi-hop-chain.yml](inventory-multi-hop-chain.yml)

**When to use:** Multi-tier network, DMZ traversal, deep segmentation.

---

## Hybrid Cloud (On-Prem → Cloud Controller)

```
┌──────────────────────────────────────────────┐
│                    CLOUD                      │
│  Controller ◄── outbound dial ──┐            │
│  [listener]                     │            │
└─────────────────────────────────│────────────┘
                                  │
          ═══════ FIREWALL: on-prem → cloud ONLY ═══════
                                  │
┌─────────────────────────────────│────────────┐
│                  ON-PREM        │            │
│                          ┌─────┴─────┐      │
│               ┌─────────►│    Hop    │      │
│               │          │[dials out]│      │
│               │          └───────────┘      │
│        ┌──────┴──────┐                      │
│        │     EN      │                      │
│        │ [dials out] │                      │
│        └─────────────┘                      │
└─────────────────────────────────────────────┘
```

**File:** [inventory-hybrid-cloud.yml](inventory-hybrid-cloud.yml)

**When to use:** Controller in cloud (GCP/AWS/Azure), ENs on-premises, firewall only allows outbound from on-prem to cloud.

---

## ProxyJump / Bastion

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

**File:** [inventory-proxyjump.yml](inventory-proxyjump.yml)

**When to use:** Corporate policy requires bastion, control host outside network, VPN unavailable.

**Note:** SSH goes through jumpbox; receptor mesh (27199) is direct between EN and controller.

---

## Key

| Term | Meaning |
|------|---------|
| `[listener]` | tcp-listener on port 27199, accepts connections |
| `[dials out]` | tcp-peer, initiates connection to upstream |
| `outbound dial` | Node connects to upstream listener (default, zero disruption) |

## Other Files

| File | Purpose |
|------|---------|
| [add_node.secrets.yml](add_node.secrets.yml) | Template for registry credentials |
| [inventory-outbound-peer.yml](inventory-outbound-peer.yml) | Generic outbound example |

## Next Steps

1. Copy example closest to your topology
2. Replace hostnames with your FQDNs
3. Set `aap_setup_dir` to your installer path
4. Run preflight: `ansible-playbook playbooks/preflight.yml -i your-inventory.yml`
5. Run add_node: `ansible-playbook playbooks/add_node.yml -i your-inventory.yml`

See [docs/TOPOLOGY.md](../docs/TOPOLOGY.md) for detailed configuration options.
