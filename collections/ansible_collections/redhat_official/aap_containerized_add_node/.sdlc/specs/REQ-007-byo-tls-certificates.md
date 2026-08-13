# REQ-007: TLS Certificate Options

## Summary

Match AAP installer TLS options — BYO certs, BYO CA, or use existing internal CA.

## AAP Installer TLS Variables

From `ansible.containerized_installer` role analysis:

| Variable | Purpose |
|----------|---------|
| `receptor_tls_cert` | Path to BYO receptor certificate |
| `receptor_tls_key` | Path to BYO receptor private key |
| `receptor_tls_remote` | If true, cert/key already on target (default: false) |
| `custom_ca_cert` | Path to custom CA cert to add to mesh-CA bundle |

### Behavior Matrix

| `receptor_tls_cert/key` | `custom_ca_cert` | Result |
|------------------------|-----------------|--------|
| Not defined | Not defined | Generate cert, sign with internal CA |
| Not defined | Defined | Generate cert, sign with internal CA, add custom CA to bundle |
| Defined | Not defined | Use BYO cert, trust internal CA only |
| Defined | Defined | Use BYO cert, add custom CA to mesh-CA bundle |

## CA File Locations

```
~/aap/tls/
├── ca.cert       # Internal CA cert
├── ca.key        # Internal CA private key
└── extracted/    # Trust bundle

~/aap/receptor/etc/
├── receptor.crt  # Node certificate
├── receptor.key  # Node private key
└── mesh-CA.crt   # Mesh CA bundle (internal + custom if provided)
```

## Detection Strategy

Check existing installation to determine TLS mode:

### Option 1: Read original inventory

```yaml
- name: Check for BYO TLS vars in installer inventory
  ansible.builtin.slurp:
    src: "{{ aap_setup_dir }}/inventory"
  register: _installer_inventory

- name: Parse inventory for TLS vars
  ansible.builtin.set_fact:
    _has_byo_certs: "{{ 'receptor_tls_cert' in (_installer_inventory.content | b64decode) }}"
    _has_custom_ca: "{{ 'custom_ca_cert' in (_installer_inventory.content | b64decode) }}"
```

### Option 2: Check CA key availability

```yaml
- name: Check if CA private key is available
  ansible.builtin.stat:
    path: "{{ ansible_user_dir }}/aap/tls/ca.key"
  delegate_to: "{{ groups['automationcontroller'][0] }}"
  register: _ca_key_stat

# If ca.key exists → can mint certs
# If ca.key missing → BYO certs required
```

### Option 3: Compare mesh-CA.crt to ca.cert

```yaml
- name: Check if custom CA in mesh bundle
  block:
    - ansible.builtin.slurp:
        src: "{{ ansible_user_dir }}/aap/tls/ca.cert"
      register: _internal_ca
    - ansible.builtin.slurp:
        src: "{{ ansible_user_dir }}/aap/receptor/etc/mesh-CA.crt"
      register: _mesh_ca
    - set_fact:
        _has_custom_ca: "{{ (_mesh_ca.content | b64decode) != (_internal_ca.content | b64decode) }}"
```

## Implementation Options

### Option A: Auto-detect from CA key

```yaml
# If CA key available, mint certs
# If CA key missing, require user to provide certs
- name: Check CA key exists
  stat:
    path: "{{ _ca_tls_dir }}/ca.key"
  register: _ca_key

- name: Fail if no CA key and no BYO certs
  assert:
    that:
      - _ca_key.stat.exists or (aap_add_node_tls_cert is defined and aap_add_node_tls_key is defined)
    fail_msg: |
      CA private key not available and no BYO certs provided.
      Either:
      1. Provide certs: -e aap_add_node_tls_cert=/path/to/cert -e aap_add_node_tls_key=/path/to/key
      2. Ensure CA key exists: {{ _ca_tls_dir }}/ca.key
```

### Option B: Match installer vars

Accept same vars as installer:
- `receptor_tls_cert` / `receptor_tls_key` — BYO node certs
- `custom_ca_cert` — Custom CA to trust

### Option C: Offline bundle with CA detection

```bash
# Bundle generation detects TLS mode
ansible-playbook generate_bundle.yml -e _target_hostname=exec1.example.com ...

# If CA key available: Bundle includes signed cert
# If CA key missing: Bundle includes CSR, user must sign externally
```

## Certificate Requirements

Same as AAP installer:

| Field | Value |
|-------|-------|
| CN | Node hostname |
| SAN DNS | Node hostname |
| SAN OID | `otherName:1.3.6.1.4.1.2312.19.1;UTF8:<node-id>` |
| Key Usage | Digital Signature, Key Encipherment |
| Extended Key Usage | TLS Web Server Auth, TLS Web Client Auth |

## Recommended Approach

1. **Fetch material from controller** (current behavior)
   - Gets `mesh-CA.crt` from `~/aap/receptor/etc/` (trust bundle)
   - Gets `ca.key` from `~/aap/tls/` (signing key)
   - Gets `work_public_key.pem` from `~/aap/receptor/etc/`

2. **Detect TLS mode from controller state**
   ```
   ca.key exists?
   ├─ YES → Can mint certs
   │        Self-signed or BYO CA with signing access
   └─ NO  → BYO certs required
            Enterprise PKI without signing key access
   ```

3. **Three TLS modes supported**

   | Mode | ca.key | User Provides | Collection Action |
   |------|--------|---------------|-------------------|
   | Self-signed | exists | nothing | Mint cert with ca.key |
   | BYO CA with key | exists | ca_tls_cert + ca_tls_key (at install) | Mint cert with ca.key |
   | BYO certs | missing | aap_add_node_tls_cert + _key | Copy provided cert |

4. **Accept BYO certs** when ca.key unavailable
   - `aap_add_node_tls_cert` — pre-signed cert path
   - `aap_add_node_tls_key` — private key path
   - Validate cert has required OID
   - Validate cert trusted by mesh-CA.crt

5. **Trust chain handling**
   - Always use `mesh-CA.crt` (includes internal + custom CA)
   - Never just `ca.cert` (misses custom CA if present)

## Variables Summary

| Our Variable | Maps to Installer | Purpose |
|--------------|-------------------|---------|
| `aap_add_node_tls_cert` | `receptor_tls_cert` | BYO node certificate |
| `aap_add_node_tls_key` | `receptor_tls_key` | BYO node private key |
| `aap_add_node_custom_ca_cert` | `custom_ca_cert` | Additional CA to trust |

## Acceptance Criteria

- [ ] Works with existing AAP installation using internal CA
- [ ] Works with existing AAP installation using BYO certs
- [ ] Works with existing AAP installation using custom CA
- [ ] Clear error if CA key missing and no BYO certs provided
- [ ] Validates BYO cert meets receptor requirements
- [ ] Offline bundle handles all TLS modes

## Related

- REQ-005: Offline Bundle
- REQ-006: Hybrid Cloud (enterprise PKI common)
