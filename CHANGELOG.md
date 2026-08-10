# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of AAP containerized add-node collection
- Support for adding execution nodes to containerized AAP 2.6+
- Support for adding hop nodes (not yet lab-validated)
- Preflight validation playbook
- Parallel node addition with serialized registration
- Machine-ID collision detection for cloned VMs
- AIO local-only to tcp-listener conversion
- Custom Instance Groups via `[instance_group_*]` inventory groups
- Outbound dial (EN → Controller) - default, zero disruption
- Inbound dial (Controller → EN) - optional, causes disruption
- Multi-hop topology support
- Comprehensive documentation and FAQ

### Tested
- AAP 2.7.1 (Controller 4.8.3)
- RHEL 9.x execution nodes
- RHEL 10.0 execution nodes
