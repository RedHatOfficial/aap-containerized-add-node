# S-070: TLS Self-Signed (Default)

## Objective

Verify collection works with default AAP installation using installer-generated self-signed CA.

## Prerequisites

- AAP 2.6 containerized installed WITHOUT any TLS vars in inventory
- Controller has `~/aap/tls/ca.key` (signing key)
- Controller has `~/aap/receptor/etc/mesh-CA.crt` (trust bundle)

## Detection Check

```bash
# On controller
ls ~/aap/tls/ca.key           # Should exist
ls ~/aap/tls/custom.cert      # Should NOT exist
diff ~/aap/tls/ca.cert ~/aap/receptor/etc/mesh-CA.crt  # Should match
```

## Test Steps

1. Generate offline bundle
2. Transfer and install on target EN
3. Verify receptor connects with heartbeat

## Expected Result

- Bundle generation succeeds
- New node cert minted and signed by internal CA
- mesh-CA.crt copied to node (same as ca.cert)
- Receptor connects, heartbeat shows green

## Status

- [x] Tested (2026-08-11) — Bundle generation + install, heartbeat green capacity=16
