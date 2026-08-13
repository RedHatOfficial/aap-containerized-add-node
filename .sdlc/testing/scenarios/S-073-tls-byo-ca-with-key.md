# S-073: TLS with BYO CA (Key Available)

## Objective

Verify collection works when AAP was installed with customer-provided CA cert AND key (`ca_tls_cert` + `ca_tls_key`).

## Prerequisites

- AAP 2.6 containerized installed WITH `ca_tls_cert` and `ca_tls_key` in inventory
- Controller has `~/aap/tls/ca.key` (customer's CA signing key)
- Controller has `~/aap/tls/ca.cert` (customer's CA cert)
- CA was provided by customer (not installer-generated)

## Detection Check

```bash
# On controller
ls ~/aap/tls/ca.key           # Should exist (customer provided)
ls ~/aap/tls/ca.cert          # Should exist (customer provided)

# Check CA is not self-signed installer default
openssl x509 -in ~/aap/tls/ca.cert -noout -issuer -subject
# If issuer != subject, it's an intermediate CA (enterprise PKI)
# If issuer == subject but CN is not "Ansible Automation Platform", it's BYO

# Check original inventory
grep -E "ca_tls_cert|ca_tls_key" /path/to/installer/inventory
```

## Test Steps

1. Generate offline bundle
2. Verify new node cert is signed by customer CA
3. Transfer and install on target EN
4. Verify receptor connects with heartbeat

## Expected Result

- Bundle generation succeeds
- New node cert minted and signed by customer CA
- mesh-CA.crt includes customer CA
- Receptor connects, heartbeat shows green

## Distinction from S-070

| Scenario | CA Source | ca.key | Behavior |
|----------|-----------|--------|----------|
| S-070 | Installer-generated | exists | Mint with self-signed CA |
| S-073 | Customer-provided | exists | Mint with customer CA |

Collection behavior is identical - the CA source doesn't matter if key is available.

## Status

- [ ] Tested
