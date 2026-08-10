# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **Red Hat Product Security**: https://access.redhat.com/security/team/contact/
2. **Email**: secalert@redhat.com (PGP key available at https://access.redhat.com/security/team/key/)

Please include:
- Type of issue (e.g., credential exposure, command injection, privilege escalation)
- Full paths of source file(s) related to the issue
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Considerations for This Collection

### Credential Handling

This collection handles sensitive credentials:

- **Registry credentials**: Used to pull container images from registry.redhat.io
- **SSH keys**: Used for Ansible connections to controller and execution nodes
- **Mesh CA keys**: Used to mint TLS certificates for receptor mesh

**Best practices:**
- Use Ansible Vault for `registry_password` and other secrets
- Never commit credentials to version control
- Use `ansible_become_password` via vault or `-K` prompt, not plaintext inventory

### Network Security

- All mesh traffic uses TLS with certificates minted from the AAP mesh CA
- SSH connections should use key-based authentication
- receptor mesh port (27199) should be firewalled appropriately

### Privilege Requirements

- Collection rejects running as root (`ansible_user_uid != 0`)
- Sudo/become is required only for: package installation, firewall rules, systemd lingering
- Controller operations (awx-manage) do NOT require root
