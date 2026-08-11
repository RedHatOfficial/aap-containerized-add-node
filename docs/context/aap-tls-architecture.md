# AAP Containerized Installer TLS Architecture

Research document for understanding AAP 2.x TLS certificate handling.

Source: `ansible.containerized_installer` collection (AAP 2.6-8)

## File Locations

```
~/aap/tls/
├── ca.cert           # Internal CA certificate
├── ca.key            # Internal CA private key
├── custom.cert       # Custom CA cert (if custom_ca_cert provided)
└── extracted/        # Trust bundle directory
    └── pem/
        └── tls-ca-bundle.pem

~/aap/receptor/etc/
├── receptor.crt      # Node TLS certificate
├── receptor.key      # Node TLS private key
└── mesh-CA.crt       # Mesh CA bundle (internal CA + custom CA if present)
```

## Inventory Variables

### Internal CA (Generated)

| Variable | Default | Description |
|----------|---------|-------------|
| `ca_tls_cert` | (undefined) | BYO CA certificate path |
| `ca_tls_key` | (undefined) | BYO CA private key path |
| `ca_tls_key_passphrase` | (undefined) | Passphrase for CA private key |
| `ca_tls_remote` | `false` | If true, cert/key already on target host |

**Behavior:** If `ca_tls_cert` and `ca_tls_key` undefined, installer generates self-signed CA.

### Custom CA (Trust Chain)

| Variable | Default | Description |
|----------|---------|-------------|
| `custom_ca_cert` | (undefined) | Additional CA to trust (enterprise PKI) |

**Behavior:** If defined, copied to `~/aap/tls/custom.cert` and added to mesh-CA bundle.

### Receptor Node Certificates

| Variable | Default | Description |
|----------|---------|-------------|
| `receptor_tls_cert` | (undefined) | BYO receptor certificate path |
| `receptor_tls_key` | (undefined) | BYO receptor private key path |
| `receptor_tls_remote` | `false` | If true, cert/key already on target host |
| `receptor_disable_tls` | `false` | Disable TLS entirely (not recommended) |
| `receptor_mintls13` | `false` | Require TLS 1.3 minimum |

**Behavior:** If `receptor_tls_cert` and `receptor_tls_key` undefined, installer generates cert signed by internal CA.

### Work Signing Keys

| Variable | Default | Description |
|----------|---------|-------------|
| `receptor_signing_private_key` | (undefined) | BYO work signing private key |
| `receptor_signing_public_key` | (undefined) | BYO work signing public key |
| `receptor_disable_signing` | `false` | Disable work signing (not recommended) |

## Certificate Generation Flow

### Internal CA (roles/common/tasks/tls.yml)

```
1. Check if ca_tls_cert/ca_tls_key defined
   ├─ YES → Copy BYO CA to ~/aap/tls/ca.{cert,key}
   └─ NO → Generate self-signed CA:
           - RSA 4096-bit key
           - 10-year validity
           - Basic constraints: CA=true
           - Stored in ~/aap/tls/ca.{cert,key}
```

### Receptor Certificates (roles/receptor/tasks/tls.yml)

```
1. Check if receptor_tls_cert/receptor_tls_key defined
   ├─ YES → Copy BYO cert/key to ~/aap/receptor/etc/receptor.{crt,key}
   └─ NO → Generate signed cert:
           - RSA key (size from installer defaults)
           - CSR with:
             - CN = node hostname
             - SAN DNS = node hostname
             - SAN OID = 1.3.6.1.4.1.2312.19.1 (receptor node-id)
             - SAN IP = node IPs (if available)
           - Signed by internal CA (~/aap/tls/ca.{cert,key})

2. Create mesh-CA.crt bundle:
   - Include internal CA (ca.cert)
   - Include custom CA (custom.cert) if defined
```

## mesh-CA.crt Template

From `roles/receptor/templates/mesh-CA.crt.j2`:

```jinja2
{{ _internal_ca_cert.content | b64decode }}
{% if custom_ca_cert is defined %}
{{ _custom_ca_cert.content | b64decode }}
{% endif %}
```

## Certificate Requirements

### Receptor OID

All receptor certificates MUST include:

```
Subject Alternative Name:
    DNS:<hostname>
    othername:1.3.6.1.4.1.2312.19.1::<node-id>
```

The OID value MUST match `node.id` in receptor.conf or receptor will exit.

**Skip check:** Set `skipreceptornamescheck: true` in tls-server and tls-client config.

### Required Extensions

| Extension | Value |
|-----------|-------|
| Key Usage | Digital Signature, Key Encipherment |
| Extended Key Usage | TLS Web Server Auth, TLS Web Client Auth |
| Subject Alternative Name | DNS + OID as above |

## Detection: What TLS Mode Is In Use?

### Decision Tree

```
1. Does ca.key exist on controller?
   ├─ YES → Can mint new certs (default self-signed or BYO CA)
   │        Check: Is mesh-CA.crt == ca.cert?
   │        ├─ YES → Pure self-signed internal CA
   │        └─ NO  → Custom CA added to trust bundle
   │
   └─ NO  → BYO certs required (enterprise PKI, no signing access)
            Must provide: aap_add_node_tls_cert + aap_add_node_tls_key
```

### Check 1: CA Key Availability

```bash
# If ca.key exists → can mint certs (self-signed or BYO CA with key)
# If ca.key missing → BYO certs required
ls ~/aap/tls/ca.key
```

### Check 2: Self-Signed vs Custom CA

```bash
# If custom.cert exists → custom CA was added
ls ~/aap/tls/custom.cert

# Compare mesh-CA.crt to ca.cert
# Same = pure self-signed
# Different = custom CA bundled (or BYO CA)
diff ~/aap/tls/ca.cert ~/aap/receptor/etc/mesh-CA.crt
```

### Check 3: Certificate Issuer Analysis

```bash
# Check who signed the CA cert (self-signed = issuer == subject)
openssl x509 -in ~/aap/tls/ca.cert -noout -issuer -subject

# Self-signed example:
# issuer=C = UK, L = Bristol, O = Griff Inc
# subject=C = UK, L = Bristol, O = Griff Inc

# BYO CA example (intermediate):
# issuer=C = US, O = Enterprise Root CA
# subject=C = US, O = Enterprise, OU = Ansible, CN = AAP Signing CA
```

### Check 4: Original Inventory

```bash
# Search for BYO TLS vars in installer inventory
grep -E "receptor_tls_cert|receptor_tls_key|ca_tls_cert|ca_tls_key|custom_ca_cert" inventory
```

### Check 5: Certificate OID Presence

```bash
# Check for receptor node-id OID (required for mesh auth)
openssl x509 -in ~/aap/receptor/etc/receptor.crt -noout -text | grep "1.3.6.1.4.1.2312.19.1"

# Verify cert signed by mesh CA
openssl verify -CAfile ~/aap/receptor/etc/mesh-CA.crt ~/aap/receptor/etc/receptor.crt
```

## Scenarios

### Scenario 1: Default (Self-Signed Internal CA)

```ini
# inventory - no TLS vars
[all:vars]
# TLS vars not set - installer generates everything
```

Files created:
- `~/aap/tls/ca.cert` - generated
- `~/aap/tls/ca.key` - generated
- `~/aap/receptor/etc/receptor.crt` - signed by ca.cert
- `~/aap/receptor/etc/mesh-CA.crt` - copy of ca.cert

### Scenario 2: BYO Internal CA

```ini
[all:vars]
ca_tls_cert=/path/to/company-ca.crt
ca_tls_key=/path/to/company-ca.key
ca_tls_key_passphrase=secret
```

Files created:
- `~/aap/tls/ca.cert` - copied from ca_tls_cert
- `~/aap/tls/ca.key` - copied from ca_tls_key
- `~/aap/receptor/etc/receptor.crt` - signed by company CA
- `~/aap/receptor/etc/mesh-CA.crt` - copy of company CA

### Scenario 3: BYO Node Certificates

```ini
[all:vars]
receptor_tls_cert=/path/to/receptor.crt
receptor_tls_key=/path/to/receptor.key
```

Files created:
- `~/aap/tls/ca.cert` - generated (for other services)
- `~/aap/tls/ca.key` - generated
- `~/aap/receptor/etc/receptor.crt` - copied from receptor_tls_cert
- `~/aap/receptor/etc/mesh-CA.crt` - internal CA only

**Note:** BYO certs must be trusted by mesh-CA or have custom_ca_cert set.

### Scenario 4: Custom CA Addition

```ini
[all:vars]
custom_ca_cert=/path/to/enterprise-root-ca.crt
```

Files created:
- `~/aap/tls/ca.cert` - generated
- `~/aap/tls/ca.key` - generated
- `~/aap/tls/custom.cert` - copied from custom_ca_cert
- `~/aap/receptor/etc/receptor.crt` - signed by internal CA
- `~/aap/receptor/etc/mesh-CA.crt` - internal CA + enterprise CA

### Scenario 5: Full BYO (External PKI)

```ini
[all:vars]
ca_tls_cert=/path/to/signing-ca.crt
ca_tls_key=/path/to/signing-ca.key
custom_ca_cert=/path/to/root-ca.crt
receptor_tls_cert=/path/to/receptor.crt
receptor_tls_key=/path/to/receptor.key
```

Files created:
- All copied from provided paths
- mesh-CA.crt includes signing CA + root CA

## Implications for Add-Node Collection

### Current Behavior

1. Fetch `ca.cert` and `ca.key` from `~/aap/tls/`
2. Fetch `mesh-CA.crt` from `~/aap/receptor/etc/`
3. Mint new node cert signed by ca.key
4. Deploy mesh-CA.crt for trust

### Required Changes

1. **Check ca.key availability** before trying to mint
2. **Support BYO certs** via `aap_add_node_tls_cert` / `aap_add_node_tls_key`
3. **Fetch mesh-CA.crt** not ca.cert for trust chain (already correct)
4. **Validate BYO certs** have required OID

### Variable Mapping

| Add-Node Collection | Maps to Installer |
|---------------------|-------------------|
| `aap_add_node_tls_cert` | `receptor_tls_cert` |
| `aap_add_node_tls_key` | `receptor_tls_key` |
| `aap_add_node_custom_ca_cert` | `custom_ca_cert` |
