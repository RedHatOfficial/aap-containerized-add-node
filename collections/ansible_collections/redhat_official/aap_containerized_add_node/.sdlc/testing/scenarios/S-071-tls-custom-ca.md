# S-071: TLS with Custom CA

## Objective

Verify collection works when AAP was installed with `custom_ca_cert` (additional enterprise CA in trust bundle).

## Prerequisites

- AAP 2.6 containerized installed WITH `custom_ca_cert` in inventory
- Controller has `~/aap/tls/ca.key` (signing key still available)
- Controller has `~/aap/tls/custom.cert` (enterprise CA)
- `mesh-CA.crt` contains BOTH internal CA and custom CA

## Detection Check

```bash
# On controller
ls ~/aap/tls/ca.key           # Should exist (can still mint)
ls ~/aap/tls/custom.cert      # Should exist
diff ~/aap/tls/ca.cert ~/aap/receptor/etc/mesh-CA.crt  # Should DIFFER

# mesh-CA.crt should have 2 certificates
grep -c "BEGIN CERTIFICATE" ~/aap/receptor/etc/mesh-CA.crt  # Should be 2
```

## Test Steps

1. Generate offline bundle
2. Verify bundle contains combined mesh-CA.crt (not just ca.cert)
3. Transfer and install on target EN
4. Verify receptor connects with heartbeat

## Expected Result

- Bundle includes mesh-CA.crt with both CAs
- New node trusts internal CA AND custom CA
- Receptor connects, heartbeat shows green

## Status

- [ ] Tested
