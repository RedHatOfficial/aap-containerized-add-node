# Research: Peer Direction

## Date

2026-08-10

## Question

Should new nodes dial out to controller, or should controller dial to new nodes?

---

## Background

Receptor mesh uses TCP connections:
- `tcp-listener`: Accepts incoming connections
- `tcp-peer`: Initiates outbound connections

Direction only affects connection initiation — once connected, communication is bidirectional.

---

## Options Evaluated

### Option A: Outbound Dial (EN → Controller)

**Description**: New node initiates connection to controller.

**Firewall requirements**:
- EN: Outbound 27199/TCP allowed
- Controller: Inbound 27199/TCP from ENs

**Impact**:
- **Zero mesh disruption**
- No controller receptor restart
- Works through most firewalls (outbound typically unrestricted)

**Verdict**: **Default choice**

---

### Option B: Inbound Dial (Controller → EN)

**Description**: Controller initiates connection to new node.

**Firewall requirements**:
- Controller: Outbound 27199/TCP allowed
- EN: Inbound 27199/TCP from controller

**Impact**:
- **5-10 second mesh disruption per node**
- Controller receptor restart required
- Running jobs may fail

**When needed**:
- EN has strict egress-only policy
- EN cannot reach controller (security zone)

**Verdict**: Optional, with warning

---

## Decision

- **Default**: Outbound dial (EN → Controller)
- **Optional**: Inbound dial via `aap_add_node_enable_controller_peer=true`
- **Documentation**: Prominent disruption warning

---

## Outcome

- ADR-003: Outbound-First Topology
- `docs/TOPOLOGY.md`: Full documentation
- `roles/update_controller_peers/`: Inbound dial implementation
