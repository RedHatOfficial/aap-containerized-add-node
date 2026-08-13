=========================================
AAP Containerized Installer Release Notes
=========================================

.. contents:: Topics

v2.6.0
======

Release Summary
---------------

This adds new features and fixes issues for the AAP containerized.

v2.5.0
======

Release Summary
---------------

This adds new features and fixes issues for the AAP containerized installer.

Major Changes
-------------

- Add TCP socket support to redis (components still use Unix socket by default).
- Add TLS support with TCP socket is used (enabled by default).
- Add a backup playbook to create database and files archives for each components.
- Add a restore playbook to restore database and files from archives for each components.
- Add an update workflow for recreating the containers when the images changed.
- Add components prefix for nginx variables.
- Add experimental support for Automation Gateway.
- Add mTLS authentication when TCP socket is used.
- Allow automation eda node type with api, hybrid and worker.
- Allow deploying multiple redis services on the same node (unix and tcp sockets)
- Allow using multiple EDA nodes.
- Requires an Automation Gateway node to be present.
- Update postgresql container version to 15.
- Use Ansible Automation Platform 2.5 by default.
- Use EDA settings file instead of environment variables.

Minor Changes
-------------

- Add EDA activation db host variable.
- Add EDA max running activations variables (default to 12)
- Add EDA safe plugins allow list for port forward.
- Add add_receptor_address controller comand for configuring the mesh instance port.
- Add eda rulebook unique queue name for hybrid/worker type.
- Add eda rulebook worker queues list with all worker queue names.
- Add redis support over TCP support for automation gateway.
- Add support for Azure Blob and AWS S3 object storage with Automation Hub.
- Allow one to configure nginx HSTS max age and update default value.
- Allowing adding custom TLS CA certificates.
- Enable HTTP2 in nginx configuration.
- Enable nginx gzip compression and cache on static files.
- Move services fact to systemd task file so it can be reuse.
- Remove LDAP support from Automation Hub.
- Remove the deprecated ee-29 container image.
- Update ansible.controller collection to 4.6.0
- Use TLS 1.2 and 1.3 protocols with nginx.
- Use dedicated receptor image rather than ee-supported.
- Use system profile for gateway/hub nginx TLS ciphers.
- Use the EDA status endpoint to validate that the API is ready.
- Use tmpfs and volumes for web containers using nginx.

Bugfixes
--------

- Add /var/log/tower log directory to automation controller containers.
- Add SYSTEM_UUID parameter in automation controller configuration for insights.
- Add locales directive for controller nginx configuration.
- Add redis data directory path in the configuration.
- Add until statement to hub collection/container gpg key import.
- Fix automation hub container signing condition.
- Fix hub_ldap_extra_settings default value as dict rather than list.
- Fix nginx configuration when providing custom headers.
- Set nginx error log to /dev/stdout and use error level rather than info.
- Use the eda data podman volume for eda user home rather than media subdirectory.

v1.3.3
======

Release Summary
---------------

This fixes issues for the AAP containerized installer.

Minor Changes
-------------

- Allow adding peers to execution nodes via receptor_peers variable.
- Change postgresql password encryption from md5 to scram-sha-256.
- Do not bind mount the entire controller conf.d directory but individual files instead.
- Do not only add receptor execution type instances as controller peers.
- Reduce automation hub delay time when waiting for gpg import.
- Remove automation hub entrypoints and use direct commands.
- Use the gpg_fingerprint lookup from community.crypto collection.

Bugfixes
--------

- Sort systemd requires elements to avoid container updates.

v1.3.2
======

Release Summary
---------------

This fixes issues for the AAP containerized installer.

Minor Changes
-------------

- Ensure the images directory is present within the bundle directory provided.
- Update ansible.controller collection to 4.5.0

Bugfixes
--------

- Add execution_nodes group during bundle execution.
- Add missing receptor firewallrules in configuration file.
- Ensure execution nodes aren't collocated on automation controller node.
- Fix TLS certificate/key copy to other nodes when running the installer after the initial deployment.
- Fix receptor peers from controller to execution nodes.
- Include volumes tasks file in receptor role.

v1.3.1
======

Release Summary
---------------

This fixes issues for the AAP containerized installer.

v1.3.0
======

Release Summary
---------------

This adds new features and fixes issues for the AAP containerized installer.

Major Changes
-------------

- Add Automation Hub postintall configuration.
- Add a new EDA scheduler container when EDA version is greater than 1.0.1.
- Add execution_nodes group for running automation controller jobs on remote nodes via receptor.
- Add new EDA activation worker containers when EDA version is greater than 1.0.1.
- Add support for automation hub collection and container signing.
- Add support for postgresql TLS and enabled by default.
- Add support for receptor TLS and enabled by default.
- Add support for receptor signing and enabled by default.
- Generate or copy TLS CA certificate/key for signing TLS certificate (selfsigned vs ownca)
- Move the receptor code into a dedicated role shared between automation controller and execution nodes.
- Receptor container is using a podman volume for the socket directory.
- Remove default ports for non-root and avoid using 445 as SMB can be blocked in some routers.
- Trust the TLS CA certificate and bind mount the trusted bundle into containers.

Minor Changes
-------------

- Add IP addresses to TLS certificate SAN.
- Add async delay/retries variables for controller postinstall.
- Add execution nodes to default queue.
- Add listener_port option to provision_instance controller command when version is >= 4.5.0.
- Allow keeping the postgresql databases during uninstall playbook.
- Allow overriding the galaxy-importer configuration for Automation Hub.
- Allow providing custom value for automation hub secret key.
- Create EDA Decision environment(s) resources.
- Create EDA registry credentials resource when needed.
- Enable IPv6 listening in Nginx configuration.
- Enable TLS certificate validation during controller postinstall.
- Enable TLS certificate validation during eda resources creation.
- Ignore builtin image volumes (VOLUME within container file) for receptor.
- Only gather facts once during uninstall playbook.
- Reduce postgresql delay time when waiting for initialization.
- Refact uninstall facts to avoid duplicated code.
- Register execution node peers for controller.
- Remove provision_instance call from controller task entrypoint.
- Remove the automation controller secret_key template as we can use the password lookup directly.
- Remove the automation hub database fields jinja template as we can use the random_token plugin directly.
- Split preflight checks into dedicated files per component.
- Trust the Automation Hub registry in podman configuration.
- Update ansible.cfg to reference collections path, inventory and log file.
- Update ansible.controller collection to 4.4.8
- Use a dedicated uWSGI file for the controller configuration.
- Use a fact for automation hub NFS.
- Use a podman volume for receptor data directory.
- Use ansible FQCN for lookup.
- Use same client_max_body_size defaults on controller/hub as VM based installer.

Bugfixes
--------

- Abort install playbook execution on the first error.
- Add EDA nodes to the ostree preflight validation.
- Add database and execution nodes to the ostree preflight validation.
- EDA 1.0.2 fixes using port value in the controller URL.
- Ensure controller_main_url starts with "http(s)://" prefix when provided.
- Ensure hub_main_url starts with "http(s)://" prefix when provided.
- Fix multiple automation hub workers name.
- Notify handlers when the TLS certificate and key are updated.
- Remove non breaking spaces and add gitlab pipeline.
- Remove top level component directories during uninstall.
- The ansible_processor_vcpus fact doesn't exist on s390x before ansible-core 2.15 so adding default event workers value.
- Use apply for run_once on include_tasks
- When no IPv6 addresses are present on the host then disable the nginx IPv6 listening.

v1.2.3
======

Release Summary
---------------

This fixes issues for the AAP containerized installer.

Minor Changes
-------------

- Install the redis cache in parallel for all components.

Bugfixes
--------

- Ensure subuids and subgids are configured for non local users.
- Fix registry logout during uninstall.
- Remove firewalld rules during uninstall.
- Remove uid option from podman volume to avoid insufficient GIDs in user namespace.

v1.2.2
======

Release Summary
---------------

This fixes issues for the AAP containerized installer.

Minor Changes
-------------

- Allow pulling container images from a different architecture with the bundle playbook.

v1.2.1
======

Release Summary
---------------

This fixes issues for the AAP containerized installer.

Bugfixes
--------

- Add missing secrets to automation-controller-web container

v1.2.0
======

Release Summary
---------------

This adds new features and fixes issues for the AAP containerized installer.

Major Changes
-------------

- Add Automation Controller postintall configuration.
- Add EDA support.
- Automation Hub containers are using a podman volume for /var/lib/pulp directory.
- Use Ansible Automation Platform 2.4 by default.
- Use podman secrets for sensitive data.

Minor Changes
-------------

- Add a dedicated image variable for receptor container.
- Allow adding extra Execution Environment container images.
- Allow connecting the Hub to an existing LDAP server.
- Allow customize postgresql memory variables and set better default values.
- Allow scaling hub worker containers.
- Allow sharing the Hub storage using an existing NFS Server.
- Allow using remote repository with Automation Controller postintall configuration.
- Do not remove Podman packages on uninstall.
- Ensure podman is installed before doing podman tasks with the bundle scenario.
- Remove podman version code.
- Retrieve pulpcore version with importlib.metadata.

Bugfixes
--------

- Allow deploying Automation Hub without Automation Controller variables set.
- EDA, Hub and Controller initialize and configure the DB only once.
- Enable postgresql hstore extension on automation hub database.
- Fail if trying to create more than one managed database
- Fix HTTP only provisioning by always installing python3-cryptography
- Fix ansible user fact for bundle scenario when using registry authentication.
- Fix automation hub workers temporary directory creation.
- Fix host metrics not showing in current UI.
- Grant component role to postgres user in case RDS DB is used. In non RDS, it's a noop operation.
- Reload systemd daemon for receptor as well.
- Reload systemd daemon to make aware of any changes to config files.
- Remove podman unnamed receptor volume during uninstall.
- Use RECEPTOR_RELEASE_WORK and AWX_CLEANUP_PATHS True defaults.

v1.1.1
======

Release Summary
---------------

This fixes issues for the AAP containerized installer.

Bugfixes
--------

- Use FQCN for random_token plugin.

v1.1.0
======

Release Summary
---------------

This adds new features and fixes issues for the AAP containerized installer.

Minor Changes
-------------

- AAP 2.4 introduced a new controller container with rsyslog.
- Add ability to auto update the containers by putting special label. User can run podman auto-update to perform such action.
- Add the podman authfile path to the io.containers.autoupdate.authfile label in registry scenario.
- Load all EE container images into the receptor container storage (execution plane).
- Remove systemd daemon-reload tasks because this isn't needed for rootless services.
- The web and task controller containers are using different commands and environment values depending on the controller version.
- Use podman volumes for PostgreSQL and Redis, instead of bind mounts

Bugfixes
--------

- Delete EE container images from receptor container storage during uninstall.
- Ensure remote users are non root user.
- If offline mode is used, do not mount auth.json from host and copy EE image to receptor storage.
- Load EE image into receptor, as it has isolated storage separate from control plane.
- Remove all redis volumes during uninstall playbook execution.
- Remove systemd podman override configuration directory during controller uninstall.
- Some controller containers don't stop cleanly or need more time to be stopped.
- Some unneeded directories were left on disk after the uninstall playbook execdution.
- The container configuration is now stored in the user home directory so this needs to be removed during the uninstall playbook.

v1.0.0
======

Release Summary
---------------

This is the first release of the AAP containerized installer.

Major Changes
-------------

- Disable ee-29 container image in the controller configuration by default. This can be turned back on with `ee_29_enabled=true`.
- Run AAP/AWX containers as rootless. The host location to hold the container volumes is defined by variable ``aap_volumes_dir``, which defaults to $HOME/aap.

Minor Changes
-------------

- Use redis and postgresql container images from sclorg for tests.
- Use the user containers configuration file instead of the global one (/etc/containers/containers.conf).

Bugfixes
--------

- Fix undefined `ai_deny_index` key in the GALAXY_FEATURE_FLAGS hub settings.
- Fix undefined ansible_user_uid fact with bundle playbook.
- Use systemd requires instead of podman to fix on boot race conditions.

Known Issues
------------

- Deploying controller with AAP 2.4 won't work anymore.
- Use AWX 21.x container images in tests since AWX 22.x architecture isn't compatible with the installer
