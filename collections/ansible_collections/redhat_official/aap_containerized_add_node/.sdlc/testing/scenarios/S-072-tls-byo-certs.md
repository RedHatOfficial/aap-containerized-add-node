# S-072: TLS with BYO Certificates (No CA Key)

## Objective

Verify collection handles enterprise PKI where CA private key is not available on controller.

## Prerequisites

- AAP 2.6 containerized installed with BYO certs
- Controller has `~/aap/receptor/etc/mesh-CA.crt` (trust bundle)
- Controller does NOT have `~/aap/tls/ca.key` (or key is password-protected/HSM)
- Customer has pre-signed certificate for new node

## Detection Check

```bash
# On controller
ls ~/aap/tls/ca.key           # Should NOT exist (or not readable)
ls ~/aap/receptor/etc/mesh-CA.crt  # Should exist (trust bundle)
```

## Test Steps

### Without BYO certs (should fail gracefully)

1. Run generate_bundle.yml without cert vars
2. Verify clear error message about missing ca.key

### With BYO certs (should succeed)

1. Customer generates cert externally with required OID:
   ```bash
   # Example CSR generation (customer does this)
   openssl req -new -key exec1.key -out exec1.csr \
     -subj "/CN=exec1.example.com" \
     -addext "subjectAltName=DNS:exec1.example.com,otherName:1.3.6.1.4.1.2312.19.1;UTF8:exec1.example.com"
   
   # Customer signs with their CA
   ```

2. Run generate_bundle.yml with BYO cert:
   ```bash
   ansible-playbook generate_bundle.yml \
     -e _target_hostname=exec1.example.com \
     -e _receptor_peers='["controller.example.com"]' \
     -e aap_add_node_tls_cert=/path/to/exec1.crt \
     -e aap_add_node_tls_key=/path/to/exec1.key
   ```

3. Verify bundle contains provided cert (not minted)
4. Transfer and install on target EN
5. Verify receptor connects with heartbeat

## Expected Result

- Without certs: Clear error explaining need for BYO certs
- With certs: Bundle uses provided cert/key
- Collection validates cert has required OID
- Collection validates cert trusted by mesh-CA.crt
- Receptor connects, heartbeat shows green

## Certificate Requirements for Customer

| Field | Requirement |
|-------|-------------|
| CN | Node hostname |
| SAN DNS | Node hostname |
| SAN OID | `otherName:1.3.6.1.4.1.2312.19.1;UTF8:<node-id>` |
| Signed by | CA in mesh-CA.crt trust bundle |

## Status

- [ ] Tested - no certs provided (error case)
- [ ] Tested - BYO certs provided (success case)

## Notes

This scenario requires enterprise PKI setup. May need to simulate by:
1. Installing AAP with BYO CA
2. Removing ca.key after install
3. Testing collection behavior
