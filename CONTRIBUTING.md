# Contributing to AAP Containerized Add Node

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

This project follows the [Red Hat Community Code of Conduct](https://www.redhat.com/en/about/digital-accessibility). Please be respectful and inclusive in all interactions.

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use issue templates when available
3. Include:
   - AAP version (e.g., 2.7.1)
   - RHEL version on execution nodes
   - Relevant inventory configuration (sanitized)
   - Full error output
   - Steps to reproduce

### Submitting Changes

1. **Fork the repository** and create a branch from `devel`
2. **Branch naming**: `feature/description` or `fix/description`
3. **Make your changes** following the style guidelines below
4. **Test your changes** against a real AAP environment if possible
5. **Submit a pull request** to `devel` branch

### Pull Request Process

1. PRs must target `devel` branch (not `main`)
2. All CI checks must pass
3. At least one maintainer approval required
4. Squash commits before merge (or use squash-merge)

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aap-containerized-add-node.git
cd aap-containerized-add-node

# Add upstream remote
git remote add upstream https://github.com/RedHatOfficial/aap-containerized-add-node.git

# Create feature branch
git checkout -b feature/my-feature devel

# Run linting
ansible-lint
yamllint .
```

## Style Guidelines

### Ansible

- Follow [Ansible Best Practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- Use fully qualified collection names (FQCN)
- Use `ansible.builtin.` prefix for all builtin modules
- Task names must be unique and descriptive
- Use `block/rescue` for error handling where appropriate

### YAML

- 2-space indentation
- No trailing whitespace
- Files end with newline
- Use `true`/`false` (not `yes`/`no`)

### Documentation

- Update README.md for user-facing changes
- Update CHANGELOG.md for all changes
- Use present tense ("Add feature" not "Added feature")

## Security

- **Never commit credentials** - use vault references
- **Never hardcode paths** - use variables
- **Validate user input** - especially `receptor_peers` format
- Report security issues per SECURITY.md

## Testing

### Local Testing

```bash
# Lint
ansible-lint
yamllint .

# Syntax check
ansible-playbook playbooks/add_node.yml --syntax-check
```

### Integration Testing

Test against a real AAP environment:
1. Containerized AAP 2.6+ with running controller
2. RHEL 9 or 10 execution node (minimal install)
3. SSH key authentication configured

## Release Process

1. Changes merge to `devel`
2. When ready for release, `devel` merges to `main`
3. Tag created on `main` (e.g., `v1.0.0`)
4. Collection built and published to Galaxy

## Questions?

- Open a GitHub Discussion
- Contact maintainers via issue comments
