# AAP containerized installer

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![pipeline status](https://gitlab.cee.redhat.com/ansible/aap-containerized-installer/badges/main/pipeline.svg)](https://gitlab.cee.redhat.com/ansible/aap-containerized-installer/-/commits/main)
[![Latest Release](https://gitlab.cee.redhat.com/ansible/aap-containerized-installer/-/badges/release.svg)](https://gitlab.cee.redhat.com/ansible/aap-containerized-installer/-/releases)

# Table of Contents

- [AAP containerized installer](#aap-containerized-installer)
- [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Collections](#collections)
  - [Configuration](#configuration)
    - [Common](#common)
    - [Host tuning](#host-tuning)
    - [Images](#images)
    - [Automation Controller](#automation-controller)
      - [Automation Controller - Postinstall](#automation-controller---postinstall)
    - [Automation EDA](#automation-eda)
    - [Automation Gateway](#automation-gateway)
    - [Automation Hub](#automation-hub)
      - [Automation Hub - Shared Storage](#automation-hub---shared-storage)
      - [Automation Hub - Azure Blob Storage](#automation-hub---azure-blob-storage)
      - [Automation Hub - S3 Storage](#automation-hub---s3-storage)
      - [Automation Hub - Postinstall](#automation-hub---postinstall)
      - [Automation Hub - Signing](#automation-hub---signing)
    - [Automation Metrics Service](#automation-metrics-service)
    - [Ansible Lightspeed](#ansible-lightspeed)
      - [Lightspeed chatbot](#lightspeed-chatbot)
      - [Lightspeed MCP tools](#lightspeed-mcp-tools)
      - [Lightspeed WCA](#lightspeed-wca)
    - [Ansible MCP server](#ansible-mcp-server)
    - [Database](#database)
    - [Receptor](#receptor)
    - [Redis](#redis)
    - [Performance Co-Pilot Monitoring](#performance-co-pilot-monitoring)
    - [Log Gathering (sos report)](#log-gathering-sos-report)
  - [Usage](#usage)
    - [Disconnected registry](#disconnected-registry)
    - [Online install](#online-install)
    - [Offline install](#offline-install)
    - [Backup](#backup)
    - [Restore](#restore)
    - [Uninstall](#uninstall)
    - [Collecting Troubleshooting data with sos report](#collecting-troubleshooting-data-with-sos-report)
  - [Access](#access)

## Requirements

- ansible-core

```bash
$ dnf install ansible-core
or
$ pip install --user ansible-core
```

## Collections

The ansible collections used by the installer can be found in the `requirements.yml` file.

- ansible.controller (optional)
- ansible.posix
- community.crypto
- community.postgresql
- containers.podman (>= 1.10.0)
- infra.ah_configuration
- infra.controller_configuration

```bash
$ ansible-galaxy collection install -r requirements.yml
```

Finally, install the `ansible.containerized_installer` collection by running:

```bash
$ ansible-galaxy collection install .
```

## Configuration

### Common

| Name                   | Description                         | Required | Optional | Default                                  |
| ---------------------- | ----------------------------------- | -------- | -------- | ---------------------------------------- |
| bundle_dir             | Bundle directory                    |          |    x     | false                                    |
| bundle_install         | Use offline installation            |          |    x     | false                                    |
| ca_tls_cert            | TLS CA certificate                  |          |    x     |                                          |
| ca_tls_key             | TLS CA key                          |          |    x     |                                          |
| ca_tls_key_passphrase  | TLS CA key passphrase               |          |    x     |                                          |
| ca_tls_remote          | TLS CA remote files                 |          |    x     | false                                    |
| client_request_timeout | End user HTTP timeout, min. 10 sec. |          |    x     | 30                                       |
| container_compress     | Container compress software         |          |    x     | gzip                                     |
| container_keep_images  | Keep container images               |          |    x     | false                                    |
| container_pull_images  | Pull newer container images         |          |    x     | true                                     |
| container_pull_timeout | Pull container image timeout        |          |    x     | 600                                      |
| custom_ca_cert         | Custom TLS CA certificate           |          |    x     |                                          |
| feature_flags          | Feature flags dictionary            |          |    x     |                                          |
| images_tmp_dir         | Path to extract bundled images      |          |    x     | System's TMPDIR                          |
| postgresql_skip_data   | Skip PostgreSQL dump/restore        |          |    x     | false                                    |
| registry_auth          | Use registry authentication         |          |    x     | true                                     |
| registry_ns_aap        | AAP registry namespace              |          |    x     | ansible-automation-platform-26           |
| registry_ns_aap_tp     | AAP tech preview registry namespace |          |    x     | ansible-automation-platform-tech-preview |
| registry_ns_rhel       | RHEL registry namespace             |          |    x     | rhel9                                    |
| registry_tls_verify    | Verify registry TLS                 |          |    x     | true                                     |
| registry_url           | The registry URL                    |          |    x     | registry.redhat.io                       |
| registry_username      | The registry username               |          |    x     |                                          |
| registry_password      | The registry password               |          |    x     |                                          |
| use_archive_compression| Compress backup files               |          |    x     | true                                     |
| use_db_compression     | Compress database dump              |          |    x     | false                                    |

### Host tuning

This installer can optionally tune the host for higher concurrency (vertical scaling). When enabled, it applies:

- Kernel sysctl parameters written to `/etc/sysctl.d/99-aap.conf` and reloaded
  - `fs.inotify.max_user_instances`
  - `fs.inotify.max_user_watches`
  - `kernel.keys.maxkeys` (computed from host memory)
  - `kernel.keys.maxbytes` (computed from host memory)
- User limits via template `/etc/security/limits.d/99-aap-limits.conf`
  - `nofile` soft and hard limits for the user that runs the app containerized services
- Container PID limits in `/etc/containers/containers.conf`
  - Default PID limit set to 80% of system `threads-max` (following systemd's DefaultTasksMax approach)
  - Falls back to `podman_default_pids_limit` (47644, which is 80% of 59555 threads-max on RHEL 9.4) if host tuning is disabled

Enablement is controlled by the `tune_host_limits` boolean. It is applied to all service hosts during install.

| Name                                               | Description                                   | Required | Optional | Default |
| -------------------------------------------------- | --------------------------------------------- | -------- | -------- | ------- |
| tune_host_limits                                   | Apply host tuning during install              |          |    x     | true    |
| host_tuning_sysctl_fs_inotify_max_user_instances   | Max inotify user instances                     |          |    x     | 8192    |
| host_tuning_sysctl_fs_inotify_max_user_watches     | Max inotify user watches                       |          |    x     | 524288  |
| host_tuning_nofile_limit_soft                      | Soft limit for open files (nofile)             |          |    x     | 524288  |
| host_tuning_nofile_limit_hard                      | Hard limit for open files (nofile)             |          |    x     | 524288  |

Example usage:

```yaml
---
# vars.yml
tune_host_limits: true
host_tuning_sysctl_fs_inotify_max_user_instances: 8192
host_tuning_sysctl_fs_inotify_max_user_watches: 524288
host_tuning_nofile_limit_soft: 524288
host_tuning_nofile_limit_hard: 524288
```

Uninstall fully reverts these changes by removing:

- `/etc/sysctl.d/99-aap.conf`
- `/etc/security/limits.d/99-aap-limits.conf`

### Images

| Name                      | Description                            | Required | Optional | Default                         |
|---------------------------|----------------------------------------| -------- | -------- |---------------------------------|
| automationmetrics_image   | Automation Metrics Service image       |          |    x     | metrics-service-rhel9:latest    |
| controller_image          | Automation Controller image            |          |    x     | controller-rhel9:latest         |
| de_extra_images           | Decision Environment extra images      |          |    x     | []                              |
| de_supported_image        | Decision Environment supported image   |          |    x     | de-supported-rhel9:latest       |
| eda_image                 | Automation EDA image                   |          |    x     | eda-controller-rhel9:latest     |
| eda_web_image             | Automation EDA web image               |          |    x     | eda-controller-ui-rhel9:latest  |
| ee_extra_images           | Execution Environment extra images     |          |    x     | []                              |
| ee_minimal_image          | Execution Environment minimal image    |          |    x     | ee-minimal-rhel9:latest         |
| ee_supported_image        | Execution Environment supported image  |          |    x     | ee-supported-rhel9:latest       |
| gateway_image             | Automation Gateway image               |          |    x     | gateway-rhel9:latest            |
| gateway_proxy_image       | Automation Gateway Proxy image         |          |    x     | gateway-proxy-rhel9:latest      |
| hub_image                 | Automation Hub image                   |          |    x     | hub-rhel9:latest                |
| hub_web_image             | Automation Hub web image               |          |    x     | hub-web-rhel9:latest            |
| lightspeed_image          | Ansible Lightspeed image               |          |    x     | lightspeed-rhel9:latest         |
| lightspeed_chatbot_image  | Ansible Lightspeed chatbot image       |          |    x     | lightspeed-chatbot-rhel9:latest |
| mcp_image                 | AAP MCP server image                   |          |    x     | mcp-server-rhel9:latest         |
| mcp_tools_image           | Ansible Lightspeed MCP tools image     |          |    x     | mcp-tools-rhel9:latest          |
| pcp_image                 | Performance Co-Pilot image             |          |    x     | pcp:latest                      |
| postgresql_image          | Postgresql image                       |          |    x     | postgresql-15:latest            |
| receptor_image            | Receptor image                         |          |    x     | receptor-rhel9:latest           |
| redis_image               | Redis image                            |          |    x     | redis-6:latest                  |

### Automation Controller

| Name                                    | Description                                   | Required | Optional | Default            |
| --------------------------------------- | --------------------------------------------- | -------- | -------- | ------------------ |
| controller_admin_password               | Automation Controller admin password          |     x    |          |                    |
| controller_admin_user                   | Automation Controller admin user              |          |    x     | admin              |
| controller_create_preload_data          | Automation Controller create preload data     |          |    x     | true               |
| controller_event_workers                | Automation Controller event workers           |          |    x     |  4                 |
| controller_extra_settings               | Automation Controller extra settings          |          |    x     | []                 |
| controller_license_file                 | Automation Controller license file            |          |    x     |                    |
| controller_nginx_client_max_body_size   | Nginx maximum body size                       |          |    x     | 5m                 |
| controller_nginx_disable_hsts           | Disable Nginx HSTS                            |          |    x     | false              |
| controller_nginx_disable_https          | Disable Nginx HTTPS                           |          |    x     | false              |
| controller_nginx_hsts_max_age           | Nginx HSTS maximum age                        |          |    x     | 63072000           |
| controller_nginx_http_port              | Nginx HTTP port                               |          |    x     | 8080               |
| controller_nginx_https_port             | Nginx HTTPS port                              |          |    x     | 8443               |
| controller_nginx_https_protocols        | Nginx HTTPS protocols                         |          |    x     | [TLSv1.2, TLSv1.3] |
| controller_nginx_user_headers           | Custom Nginx headers                          |          |    x     | []                 |
| controller_nginx_read_timeout           | Computed: (client_request_timeout/2) or min:5 |          |    x     | 15                 |
| controller_percent_memory_capacity      | Automation Controller memory capacity         |          |    x     | 1.0                |
| controller_pg_cert_auth                 | Postgresql Controller TLS auth                |          |    x     | false              |
| controller_pg_database                  | Postgresql Controller database                |          |    x     | awx                |
| controller_pg_host                      | Postgresql Controller host                    |     x    |          |                    |
| controller_pg_password                  | Postgresql Controller password                |          |    x     |                    |
| controller_pg_port                      | Postgresql Controller port                    |          |    x     | 5432               |
| controller_pg_socket                    | Postgresql Controller unix socket             |          |    x     |                    |
| controller_pg_sslmode                   | Postgresql Controller SSL mode                |          |    x     | prefer             |
| controller_pg_tls_cert                  | Postgresql Controller TLS certificate         |          |    x     |                    |
| controller_pg_tls_key                   | Postgresql Controller TLS key                 |          |    x     |                    |
| controller_pg_username                  | Postgresql Controller user                    |          |    x     | awx                |
| controller_postgresql_skip_data         | Skip PostgreSQL dump/restore                  |          |    x     | false              |
| controller_postinstall                  | Enable Controller postinstall                 |          |    x     | false              |
| controller_postinstall_dir              | Postinstall directory                         |          |    x     |                    |
| controller_secret_key                   | Automation Controller secret key              |          |    x     |                    |
| controller_tls_cert                     | Automation Controller TLS certificate         |          |    x     |                    |
| controller_tls_key                      | Automation Controller TLS key                 |          |    x     |                    |
| controller_tls_remote                   | Automation Controller TLS remote files        |          |    x     | false              |
| controller_uwsgi_listen_queue_size      | Automation Controller uwsgi listen queue size |          |    x     | 2048               |
| controller_use_archive_compression      | Automation Controller compress backup files   |          |    x     | true               |
| controller_use_db_compression           | Automation Controller compress database dump  |          |    x     | false              |
| controller_uwsgi_processes              | Automation Controller uwsgi workers           |          |    x     | 2 * CPU + 1        |
| controller_uwsgi_timeout                | Computed: (client_request_timeout/3) or min:3 |          |    x     | 10                 |
| metrics_utility_cronjob_gather_schedule | Metrics gather schedule (systemd format)      |          |    x     | *-*-* *:00:00      |
| metrics_utility_cronjob_report_schedule | Metrics report schedule (systemd format)      |          |    x     | *-*-02 00:00:00    |
| metrics_utility_enabled                 | Enable metrics utility integration            |          |    x     | false              |
| metrics_utility_extra_settings          | Metrics utility extra settings                |          |    x     | []                 |

Extra parameters will need to be passed through an ansible `controller_extra_settings` variable.

For example, you may set:

```yaml
controller_extra_settings:
  - setting: USE_X_FORWARDED_HOST
    value: true
```

#### Automation Controller - Postinstall

The controller postinstall allows one to create resources (projects, users, roles, etc..) after the controller deployment.
This requires the controller license to be installed first (see controller_license_file variable).

| Name                                 | Description                                 | Required | Optional | Default |
| ------------------------------------ | ------------------------------------------- | -------- | -------- | --------|
| controller_postinstall               | Enable Automation Controller postinstall    |          |     x    | false   |
| controller_postinstall_async_delay   | Postinstall delay between retries           |          |     x    | 1       |
| controller_postinstall_async_retries | Postinstall number of tries to attempt      |          |     x    | 30      |
| controller_postinstall_dir           | Automation Controller postinstall directory |          |     x    |         |
| controller_postinstall_ignore_files  | Automation Controller ignore files          |          |     x    | []      |
| controller_postinstall_repo_ref      | Automation Controller repository branch/tag |          |     x    | main    |
| controller_postinstall_repo_url      | Automation Controller repository URL        |          |     x    |         |

The `controller_postinstall_repo_url` variable can be used to define the postinstall repository URL which may include
authentication information.

- `http(s)://<host>/<repo>.git` (public repository without http(s) authentication)
- `http(s)://<user>:<password>@<host>:<repo>.git` (private repository with http(s) authentication)
- `git@<host>:<repo>.git` (public/private repository with ssh authentication)

When using ssh based authentication, the installer doesn't configure anything (ssh key or so) for you and you need
to have everything configured on the installer node.

### Automation EDA

| Name                              | Description                                   | Required | Optional | Default                 |
| --------------------------------- | --------------------------------------------- | -------- | -------- | ----------------------- |
| eda_activation_workers            | Automation EDA activation workers count       |          |    x     | 2                       |
| eda_admin_password                | Automation EDA admin password                 |     x    |          |                         |
| eda_debug                         | Automation EDA debug                          |          |    x     | false                   |
| eda_extra_settings                | Automation EDA extra settings                 |          |    x     | []                      |
| eda_nginx_client_max_body_size    | Nginx maximum body size                       |          |    x     | 1m                      |
| eda_nginx_disable_hsts            | Disable Nginx HSTS                            |          |    x     | false                   |
| eda_nginx_disable_https           | Disable Nginx HTTPS                           |          |    x     | false                   |
| eda_nginx_hsts_max_age            | Nginx HSTS maximum age                        |          |    x     | 63072000                |
| eda_nginx_http_port               | Nginx HTTP port                               |          |    x     | 8082                    |
| eda_nginx_https_port              | Nginx HTTPS port                              |          |    x     | 8445                    |
| eda_nginx_https_protocols         | Nginx HTTPS protocols                         |          |    x     | [TLSv1.2, TLSv1.3]      |
| eda_nginx_user_headers            | Custom Nginx headers                          |          |    x     | []                      |
| eda_nginx_read_timeout            | Computed: (client_request_timeout/2) or min:5 |          |    x     | 15                      |
| eda_pg_cert_auth                  | Postgresql EDA TLS auth                       |          |    x     | false                   |
| eda_pg_database                   | Postgresql EDA database                       |          |    x     | eda                     |
| eda_pg_host                       | Postgresql EDA host                           |     x    |          |                         |
| eda_pg_password                   | Postgresql EDA password                       |          |    x     |                         |
| eda_pg_port                       | Postgresql EDA port                           |          |    x     | 5432                    |
| eda_pg_socket                     | Postgresql EDA unix socket                    |          |    x     |                         |
| eda_pg_sslmode                    | Postgresql EDA SSL mode                       |          |    x     | prefer                  |
| eda_pg_tls_cert                   | Postgresql EDA TLS certificate                |          |    x     |                         |
| eda_pg_tls_key                    | Postgresql EDA TLS key                        |          |    x     |                         |
| eda_pg_username                   | Postgresql EDA user                           |          |    x     | eda                     |
| eda_redis_disable_tls             | Disable TLS Redis (for multiple nodes)        |          |    x     | false                   |
| eda_redis_host                    | Redis EDA host (for multiple nodes)           |          |    x     |                         |
| eda_redis_password                | Redis EDA password (for multiple nodes)       |          |    x     |                         |
| eda_redis_port                    | Redis EDA port (for multiple nodes)           |          |    x     | 6379                    |
| eda_redis_tls_cert                | Automation EDA redis TLS certificate          |          |    x     |                         |
| eda_redis_tls_key                 | Automation EDA redis TLS key                  |          |    x     |                         |
| eda_redis_username                | Redis EDA username (for multiple nodes)       |          |    x     | eda                     |
| eda_safe_plugins                  | Automation EDA safe plugins                   |          |    x     | []                      |
| eda_secret_key                    | Automation EDA secret key                     |          |    x     |                         |
| eda_tls_cert                      | Automation EDA TLS certificate                |          |    x     |                         |
| eda_tls_key                       | Automation EDA TLS key                        |          |    x     |                         |
| eda_tls_remote                    | Automation EDA TLS remote files               |          |    x     | false                   |
| eda_type                          | Automation EDA node type                      |          |    x     | hybrid                  |
| eda_event_stream_prefix_path      | Automation EDA event stream prefix path       |          |    x     | /eda-event-streams      |
| eda_event_stream_url              | Automation EDA event stream URL               |          |    x     | Gateway proxy URL       |
| eda_event_stream_mtls             | Automation EDA event stream mTLS toggle       |          |    x     | true                    |
| eda_event_stream_mtls_prefix_path | Automation EDA event stream mTLS prefix path  |          |    x     | /mtls/eda-event-streams |
| eda_event_stream_mtls_url         | Automation EDA event stream mTLS URL          |          |    x     | Gateway proxy URL       |
| eda_postgresql_skip_data          | Skip PostgreSQL dump/restore                  |          |    x     | false                   |
| eda_workers                       | Automation EDA workers count                  |          |    x     | 2                       |
| eda_use_archive_compression       | Automation EDA compress backup files          |          |    x     | true                    |
| eda_use_db_compression            | Automation EDA compress database dump         |          |    x     | false                   |
| eda_gunicorn_workers              | Automation EDA gunicorn workers count         |          |    x     | 2 per CPU + 1           |
| eda_gunicorn_timeout              | Computed: (client_request_timeout/3) or min:3 |          |    x     | 10                      |
| eda_gunicorn_timeout_grace_period | Automation EDA gunicorn req. grace period     |          |    x     | 2                       |

Extra parameters will need to be passed through an ansible `eda_extra_settings` variable.

For example, you may set:

```yaml
eda_extra_settings:
  - setting: RULEBOOK_READINESS_TIMEOUT_SECONDS
    value: 120
```

### Automation Gateway

| Name                                         | Description                                  | Required | Optional | Default            |
| -------------------------------------------- | -------------------------------------------- | -------- | -------- | -------------------|
| gateway_admin_password                       | Automation Gateway admin password            |     x    |          |                    |
| gateway_admin_user                           | Automation Gateway admin user                |          |    x     | admin              |
| gateway_extra_settings                       | Automation Gateway extra settings            |          |    x     | []                 |
| gateway_main_url                             | Automation Gateway main URL                  |          |    x     |                    |
| gateway_nginx_client_max_body_size           | Nginx maximum body size                      |          |    x     | 5m                 |
| gateway_nginx_disable_hsts                   | Disable Nginx HSTS                           |          |    x     | false              |
| gateway_nginx_disable_https                  | Disable Nginx HTTPS                          |          |    x     | false              |
| gateway_nginx_hsts_max_age                   | Nginx HSTS maximum age                       |          |    x     | 63072000           |
| gateway_nginx_http_port                      | Nginx HTTP port                              |          |    x     | 8083               |
| gateway_nginx_https_port                     | Nginx HTTPS port                             |          |    x     | 8446               |
| gateway_nginx_https_protocols                | Nginx HTTPS protocols                        |          |    x     | [TLSv1.2, TLSv1.3] |
| gateway_nginx_user_headers                   | Custom Nginx headers                         |          |    x     | []                 |
| gateway_nginx_read_timeout                   | Computed:(client_request_timeout/2) or min:5 |          |    x     | 15                 |
| gateway_pg_cert_auth                         | Postgresql Gateway TLS auth                  |          |    x     | false              |
| gateway_pg_database                          | Postgresql Gateway database                  |          |    x     | gateway            |
| gateway_pg_host                              | Postgresql Gateway host                      |     x    |          |                    |
| gateway_pg_password                          | Postgresql Gateway password                  |          |    x     |                    |
| gateway_pg_port                              | Postgresql Gateway port                      |          |    x     | 5432               |
| gateway_pg_sslmode                           | Postgresql Gateway SSL mode                  |          |    x     | prefer             |
| gateway_pg_tls_cert                          | Postgresql Gateway TLS certificate           |          |    x     |                    |
| gateway_pg_tls_key                           | Postgresql Gateway TLS key                   |          |    x     |                    |
| gateway_pg_username                          | Postgresql Gateway user                      |          |    x     | gateway            |
| gateway_postgresql_skip_data                 | Skip PostgreSQL dump/restore                 |          |    x     | false              |
| gateway_redis_disable_tls                    | Disable TLS Redis                            |          |    x     | false              |
| gateway_redis_host                           | Redis Gateway host                           |          |    x     |                    |
| gateway_redis_password                       | Redis Gateway password                       |          |    x     |                    |
| gateway_redis_port                           | Redis Gateway port                           |          |    x     | 6379               |
| gateway_redis_tls_cert                       | Automation Gateway redis TLS certificate     |          |    x     |                    |
| gateway_redis_tls_key                        | Automation Gateway redis TLS key             |          |    x     |                    |
| gateway_redis_username                       | Redis Gateway username                       |          |    x     | gateway            |
| gateway_secret_key                           | Automation Gateway secret key                |          |    x     |                    |
| gateway_tls_cert                             | Automation Gateway TLS certificate           |          |    x     |                    |
| gateway_tls_key                              | Automation Gateway TLS key                   |          |    x     |                    |
| gateway_tls_remote                           | Automation Gateway TLS remote files          |          |    x     | false              |
| gateway_grpc_server_processes                | Gateway auth server processes                |     x    |    x     | 5                  |
| gateway_grpc_server_max_threads_per_process  | Gateway auth server threads/process          |     x    |    x     | 10                 |
| gateway_grpc_auth_service_timeout            | Computed:(client_request_timeout/2) or min:5 |     x    |    x     | 15s                |
| gateway_uwsgi_listen_queue_size              | Automation Gateway uwsgi listen queue size   |          |    x     | 4096               |
| gateway_use_archive_compression              | Automation Gateway compress backup files     |          |    x     | true               |
| gateway_use_db_compression                   | Automation Gateway compress database dump    |          |    x     | false              |
| gateway_uwsgi_processes                      | Automation Gateway uwsgi workers             |          |    x     | 2 * CPU + 1        |
| gateway_uwsgi_timeout                        | Computed:(client_request_timeout/3) or min:3 |          |    x     | 10                 |
| gateway_uwsgi_timeout_grace_period           | Automation Gateway harakiri grace period     |          |    x     | 2                  |
| gateway_jwt_expiration_buffer_in_seconds     | Computed:(client_request_timeout/2) or min:5 |     x    |    x     | 15s                |

Extra parameters will need to be passed through an ansible `gateway_extra_settings` variable.

For example, you may set:

```yaml
gateway_extra_settings:
  - setting: OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS']
    value: 600
```

### Automation Hub

| Name                              | Description                                  | Required | Optional | Default            |
| --------------------------------- | -------------------------------------------- | -------- | -------- | ------------------ |
| hub_admin_password                | Automation Hub admin password                |     x    |          |                    |
| hub_extra_settings                | Automation hub extra settings                |          |    x     | []                 |
| hub_data_path_exclude             | Automation Hub Backup Path to Exclude        |          |    x     | []                 |
| hub_galaxy_importer               | Automation Hub galaxy importer               |          |    x     |                    |
| hub_nginx_client_max_body_size    | Nginx maximum body size                      |          |    x     | 20m                |
| hub_nginx_disable_hsts            | Disable Nginx HSTS                           |          |    x     | false              |
| hub_nginx_disable_https           | Disable Nginx HTTPS                          |          |    x     | false              |
| hub_nginx_hsts_max_age            | Nginx HSTS maximum age                       |          |    x     | 63072000           |
| hub_nginx_http_port               | Nginx HTTP port                              |          |    x     | 8081               |
| hub_nginx_https_port              | Nginx HTTPS port                             |          |    x     | 8444               |
| hub_nginx_https_protocols         | Nginx HTTPS protocols                        |          |    x     | [TLSv1.2, TLSv1.3] |
| hub_nginx_user_headers            | Custom Nginx headers                         |          |    x     | []                 |
| hub_nginx_read_timeout            | Computed:(client_request_timeout/2) or min:5 |          |    x     | 15                 |
| hub_pg_cert_auth                  | Postgresql Hub TLS auth                      |          |    x     | false              |
| hub_pg_database                   | Postgresql Hub database                      |          |    x     | pulp               |
| hub_pg_host                       | Postgresql Hub host                          |     x    |          |                    |
| hub_pg_password                   | Postgresql Hub password                      |          |    x     |                    |
| hub_pg_port                       | Postgresql Hub port                          |          |    x     | 5432               |
| hub_pg_socket                     | Postgresql Hub unix socket                   |          |    x     |                    |
| hub_pg_sslmode                    | Postgresql Hub SSL mode                      |          |    x     | prefer             |
| hub_pg_tls_cert                   | Postgresql Hub TLS certificate               |          |    x     |                    |
| hub_pg_tls_key                    | Postgresql Hub TLS key                       |          |    x     |                    |
| hub_pg_username                   | Postgresql Hub user                          |          |    x     | pulp               |
| hub_postgresql_skip_data          | Skip PostgreSQL dump/restore                 |          |    x     | false              |
| hub_secret_key                    | Automation Hub secret key                    |          |    x     |                    |
| hub_storage_backend               | Automation Hub storage backend               |          |    x     | file               |
| hub_tls_cert                      | Automation Hub TLS certificate               |          |    x     |                    |
| hub_tls_key                       | Automation Hub TLS key                       |          |    x     |                    |
| hub_tls_remote                    | Automation Hub TLS remote files              |          |    x     | false              |
| hub_workers                       | Automation Hub workers count                 |          |    x     | 2                  |
| hub_use_archive_compression       | Automation Hub compress backup files         |          |    x     | true               |
| hub_use_db_compression            | Automation Hub compress database dump        |          |    x     | false              |
| hub_api_workers                   | Automation Hub api workers                   |          |    x     | 2 * CPU + 1        |
| hub_gunicorn_timeout              | Computed:(client_request_timeout/3) or min:3 |          |    x     | 10                 |
| hub_gunicorn_timeout_grace_period | Automation Hub api & content timeout         |          |    x     | 2                  |

Extra parameters will need to be passed through an ansible `hub_extra_settings` variable.

For example, you may set:

```yaml
hub_extra_settings:
  - setting: REDIRECT_IS_HTTPS
    value: True
```
#### Automation Hub - Shared Storage

Shared storage is required when installing more than one Automation Hub with `file` storage backend.
When installing a single instance of the Automation Hub, it is optional

| Name                       | Description                                  | Required | Optional | Default      |
| -------------------------- | -------------------------------------------- | -------- | -------- | ------------ |
| hub_shared_data_path       | NFS share in host:dir format with RWX access |    x     |          |              |
| hub_shared_data_mount_opts | Mount options for NFS share                  |          |    x     | rw,sync,hard |

#### Automation Hub - Azure Blob Storage

When using Azure blob storage backend then `hub_storage_backend` needs to be set to `azure`.
The Azure container needs to exist before running the installer.

| Name                     | Description          | Required | Optional | Default |
| ------------------------ | -------------------- | -------- | -------- | ------- |
| hub_azure_account_key    | Azure account key    |    x     |          |         |
| hub_azure_account_name   | Azure account name   |    x     |          |         |
| hub_azure_container      | Azure container name |          |    x     | pulp    |
| hub_azure_extra_settings | Azure extra settings |          |    x     | {}      |

Extra parameters will need to be passed through an ansible `hub_azure_extra_settings` dictionary.

For example, you may set:

```yaml
hub_azure_extra_settings:
  AZURE_LOCATION: foo
  AZURE_SSL: True
  AZURE_URL_EXPIRATION_SECS: 60
```

The list of all possible configuration can be found [here](https://django-storages.readthedocs.io/en/latest/backends/azure.html#settings)

#### Automation Hub - S3 Storage

When using AWS S3 storage backend then `hub_storage_backend` needs to be set to `s3`.
The AWS S3 bucket needs to exist before running the installer.

| Name                  | Description           | Required | Optional | Default |
| --------------------- | --------------------- | -------- | -------- | ------- |
| hub_s3_access_key     | AWS S3 access key     |    x     |          |         |
| hub_s3_secret_key     | AWS S3 secret name    |    x     |          |         |
| hub_s3_bucket_name    | AWS S3 bucket name    |          |    x     | pulp    |
| hub_s3_extra_settings | AWS S3 extra settings |          |    x     | {}      |

Extra parameters will need to be passed through an ansible `hub_s3_extra_settings` dictionary.

For example, you may set:

```yaml
hub_s3_extra_settings:
  AWS_S3_MAX_MEMORY_SIZE: 4096
  AWS_S3_REGION_NAME: eu-central-1
  AWS_S3_USE_SSL: True
```

The list of all possible configuration can be found [here](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings)

#### Automation Hub - Postinstall

The hub postinstall allows one to create resources (collections, users, groups, etc..) after the hub deployment.

| Name                          | Description                            | Required | Optional | Default |
| ----------------------------- | -------------------------------------- | -------- | -------- | --------|
| hub_postinstall               | Enable Automation Hub postinstall      |          |     x    | false   |
| hub_postinstall_async_delay   | Postinstall delay between retries      |          |     x    | 1       |
| hub_postinstall_async_retries | Postinstall number of tries to attempt |          |     x    | 30      |
| hub_postinstall_dir           | Automation Hub postinstall directory   |          |     x    |         |
| hub_postinstall_ignore_files  | Automation Hub ignore files            |          |     x    | []      |
| hub_postinstall_repo_ref      | Automation Hub repository branch/tag   |          |     x    | main    |
| hub_postinstall_repo_url      | Automation Hub repository URL          |          |     x    |         |

The `hub_postinstall_repo_url` variable can be used to define the postinstall repository URL which may include
authentication information.

- `http(s)://<host>/<repo>.git` (public repository without http(s) authentication)
- `http(s)://<user>:<password>@<host>:<repo>.git` (private repository with http(s) authentication)
- `git@<host>:<repo>.git` (public/private repository with ssh authentication)

When using ssh based authentication, the installer doesn't configure anything (ssh key or so) for you and you need
to have everything configured on the installer node.

#### Automation Hub - Signing

By default, Automation Hub doesn't sign collections and containers.
It's possible to turn on this feature via the `hub_collection_signing` and/or `hub_container_signing` variables.
For collections and/or containers you'll need to provide a GPG key to sign the artifacts.

| Name                           | Description                                  | Required | Optional | Default           |
| ------------------------------ | -------------------------------------------- | -------- | -------- | ----------------- |
| hub_collection_auto_sign       | Enable Automation Hub collection auto sign   |          |    x     |      false        |
| hub_collection_signing         | Enable Automation Hub collection signing     |          |    x     |      false        |
| hub_collection_signing_key     | Automation Hub collection signing key        |          |    x     |                   |
| hub_collection_signing_pass    | Automation Hub collection signing passphrase |          |    x     |                   |
| hub_collection_signing_service | Automation Hub collection signing service    |          |    x     | ansible-default   |
| hub_container_signing          | Enable Automation Hub container signing      |          |    x     |      false        |
| hub_container_signing_key      | Automation Hub container signing key         |          |    x     |                   |
| hub_container_signing_pass     | Automation Hub container signing passphrase  |          |    x     |                   |
| hub_container_signing_service  | Automation Hub container signing service     |          |    x     | container-default |

Note that if the GPG key is protected by a passphrase then you need to provide it via the `hub_collection_signing_pass`
and/or `hub_container_signing_pass` variables.

### Automation Metrics Service

The Automation Metrics Service provides analytics and reporting capabilities for AAP deployments.
It is deployed on dedicated host(s) specified in the `automationmetrics` inventory group.
When `automationcontroller` is also present in the inventory, the metrics service is granted read-only access to the Controller database. The installer creates the required read-only user when `postgresql_admin_password` is provided; otherwise the user must be created manually before installation.

| Name                                         | Description                                  | Required | Optional | Default            |
| -------------------------------------------- | -------------------------------------------- | -------- | -------- | -------------------|
| automationmetrics_api_port                   | Internal app port (localhost only)           |          |    x     | 8006               |
| automationmetrics_controller_db              | Defaults to (controller_pg_database) when not explicitly set) |          |    x     | awx |
| automationmetrics_controller_pg_username     | Read-only controller DB user                 |          |    x     | ms_awx_readonly    |
| automationmetrics_controller_read_pg_cert_auth | Controller DB read certificate authentication|          |    x     | false              |
| automationmetrics_controller_read_pg_host    | Controller DB host for read-only access (required when automationcontroller is deployed) |     x    |          |                    |
| automationmetrics_controller_read_pg_password| Controller DB read password (required when automationcontroller is deployed)             |     x    |          |                    |
| automationmetrics_controller_read_pg_port    | Controller DB port for read-only access      |          |    x     | 5432               |
| automationmetrics_controller_read_pg_sslmode | Controller DB read SSL mode                  |          |    x     | automationmetrics_pg_sslmode |
| automationmetrics_controller_read_pg_tls_cert| Controller DB read TLS certificate           |          |    x     |                    |
| automationmetrics_controller_read_pg_tls_key | Controller DB read TLS key                   |          |    x     |                    |
| automationmetrics_controller_read_pg_tls_remote | Controller DB read TLS certificate on remote host |     |    x     | automationmetrics_tls_remote |
| automationmetrics_dispatcherd_max_tasks      | Dispatcherd max tasks before worker recycle  |          |    x     | 100                |
| automationmetrics_dispatcherd_timeout        | Dispatcherd worker timeout (seconds)         |          |    x     | 1200               |
| automationmetrics_dispatcherd_workers        | Dispatcherd worker count                     |          |    x     | 4                  |
| automationmetrics_extra_settings             | Metrics service extra settings               |          |    x     | []                 |
| automationmetrics_firewall_zone              | Firewall zone                                |          |    x     | public             |
| automationmetrics_gunicorn_timeout           | Gunicorn worker timeout (seconds)            |          |    x     | 10                 |
| automationmetrics_gunicorn_workers           | Gunicorn worker process count                |          |    x     | 2 * CPU + 1        |
| automationmetrics_nginx_client_max_body_size | Nginx maximum body size                      |          |    x     | 5m                 |
| automationmetrics_nginx_disable_hsts         | Disable Nginx HSTS                           |          |    x     | false              |
| automationmetrics_nginx_disable_https        | Disable Nginx HTTPS                          |          |    x     | false              |
| automationmetrics_nginx_hsts_max_age         | Nginx HSTS maximum age                       |          |    x     | 63072000           |
| automationmetrics_nginx_http_port            | Nginx HTTP port                              |          |    x     | 8087               |
| automationmetrics_nginx_https_port           | Nginx HTTPS port                             |          |    x     | 8450               |
| automationmetrics_nginx_https_protocols      | Nginx HTTPS protocols                        |          |    x     | [TLSv1.2, TLSv1.3] |
| automationmetrics_nginx_read_timeout         | Computed: (client_request_timeout/2) or min:5|          |    x     | 15                 |
| automationmetrics_nginx_user_headers         | Custom Nginx headers                         |          |    x     | []                 |
| automationmetrics_pg_cert_auth               | PostgreSQL certificate authentication        |          |    x     | false              |
| automationmetrics_pg_database                | Postgresql Metrics database                  |          |    x     | metrics_service    |
| automationmetrics_pg_host                    | Postgresql Metrics host                      |     x    |          |                    |
| automationmetrics_pg_password                | Postgresql Metrics password                  |     x    |          |                    |
| automationmetrics_pg_port                    | Postgresql Metrics port                      |          |    x     | 5432               |
| automationmetrics_pg_sslmode                 | Postgresql Metrics SSL mode                  |          |    x     | prefer             |
| automationmetrics_pg_tls_cert                | Postgresql Metrics TLS certificate           |          |    x     |                    |
| automationmetrics_pg_tls_key                 | Postgresql Metrics TLS key                   |          |    x     |                    |
| automationmetrics_pg_username                | Postgresql Metrics user                      |          |    x     | metrics_service    |
| automationmetrics_postgresql_skip_data       | Skip PostgreSQL dump/restore                 |          |    x     | false              |
| automationmetrics_scheduler_check_interval   | Scheduler polling interval (seconds)         |          |    x     | 30                 |
| automationmetrics_secret_key                 | Metrics service secret key                   |          |    x     |                    |
| automationmetrics_tls_cert                   | Automation Metrics TLS certificate           |          |    x     |                    |
| automationmetrics_tls_key                    | Automation Metrics TLS key                   |          |    x     |                    |
| automationmetrics_tls_remote                 | TLS certificate on remote host               |          |    x     | false              |
| automationmetrics_use_archive_compression    | Metrics service compress backup files        |          |    x     | true               |
| automationmetrics_use_db_compression         | Metrics service compress database dump       |          |    x     | false              |

#### Automation Metrics Service - Gateway Integration

When deploying Automation Metrics with Automation Gateway, the following additional variables configure SSO and authentication integration:

| Name                                              | Description                                       | Required | Optional | Default                                   |
| ------------------------------------------------- | ------------------------------------------------- | -------- | -------- | ----------------------------------------- |
| automationmetrics_jwt_key                         | JWT validation key                                |          |    x     | Gateway proxy URL                         |

#### Automation Metrics Service - Extra Settings

Extra parameters will need to be passed through an ansible `automationmetrics_extra_settings` variable.

For example, you may set:

```yaml
automationmetrics_extra_settings:
  - setting: SOME_SETTING
    value: some_value
```

Example inventory configuration:

```ini
[automationmetrics]
metrics.example.com

[all:vars]
automationmetrics_pg_host=postgres.example.com
automationmetrics_pg_password=secretpassword
automationmetrics_controller_read_pg_password=readonlypassword
```

Note: The Automation Metrics Service is only available with AAP 2.6+ releases.

### Ansible Lightspeed

Ansible lightspeed is in experimental stage and is under active development process.

| Name                                  | Description                                                         | Required | Optional | Default            |
|---------------------------------------|---------------------------------------------------------------------| -------- | -------- |--------------------|
| lightspeed_admin_password             | Ansible Lightspeed admin password                                   |     x    |          |                    |
| lightspeed_admin_user                 | Ansible Lightspeed admin user                                       |          |    x     | admin              |
| lightspeed_chat_rate_throttle         | Chat rate throttle                                                  |          |    x     | 10/minute          |
| lightspeed_nginx_client_max_body_size | Nginx maximum body size                                             |          |    x     | 5m                 |
| lightspeed_nginx_disable_hsts         | Disable Nginx HSTS                                                  |          |    x     | false              |
| lightspeed_nginx_disable_https        | Disable Nginx HTTPS                                                 |          |    x     | false              |
| lightspeed_nginx_hsts_max_age         | Nginx HSTS maximum age                                              |          |    x     | 63072000           |
| lightspeed_nginx_http_port            | Nginx HTTP port                                                     |          |    x     | 8084               |
| lightspeed_nginx_https_port           | Nginx HTTPS port                                                    |          |    x     | 8447               |
| lightspeed_nginx_https_protocols      | Nginx HTTPS protocols                                               |          |    x     | [TLSv1.2, TLSv1.3] |
| lightspeed_nginx_user_headers         | Custom Nginx headers                                                |          |    x     | []                 |
| lightspeed_nginx_read_timeout         | Computed: max(client_request_timeout/2, 60)                         |          |    x     | 60                 |
| lightspeed_pg_cert_auth               | Postgresql Lightspeed TLS auth                                      |          |    x     | false              |
| lightspeed_pg_database                | Postgresql Lightspeed database                                      |          |    x     | lightspeed         |
| lightspeed_pg_host                    | Postgresql Lightspeed host                                          |     x    |          |                    |
| lightspeed_pg_password                | Postgresql Lightspeed password                                      |          |    x     |                    |
| lightspeed_pg_port                    | Postgresql Lightspeed port                                          |          |    x     | 5432               |
| lightspeed_pg_sslmode                 | Postgresql Lightspeed SSL mode                                      |          |    x     | prefer             |
| lightspeed_pg_tls_cert                | Postgresql Lightspeed TLS certificate                               |          |    x     |                    |
| lightspeed_pg_tls_key                 | Postgresql Lightspeed TLS key                                       |          |    x     |                    |
| lightspeed_pg_username                | Postgresql Lightspeed user                                          |          |    x     | lightspeed         |
| lightspeed_postgresql_skip_data       | Skip PostgreSQL dump/restore                                        |          |    x     | false              |
| lightspeed_secret_key                 | Ansible Lightspeed secret key                                       |          |    x     |                    |
| lightspeed_tls_cert                   | Ansible Lightspeed TLS certificate                                  |          |    x     |                    |
| lightspeed_tls_key                    | Ansible Lightspeed TLS key                                          |          |    x     |                    |
| lightspeed_tls_remote                 | Ansible Lightspeed TLS remote files                                 |          |    x     | false              |
| lightspeed_use_archive_compression    | Ansible Lightspeed compress backup files                            |          |    x     | true               |
| lightspeed_use_db_compression         | Ansible Lightspeed compress database dump                           |          |    x     | false              |
| lightspeed_uwsgi_listen_queue_size    | Ansible Lightspeed uwsgi listen queue size                          |          |    x     | 2048               |
| lightspeed_uwsgi_processes            | Ansible Lightspeed uwsgi workers                                    |          |    x     | 2 * CPU + 1        |
| lightspeed_uwsgi_timeout              | Computed: (client_request_timeout/3) or min:60                      |          |    x     | 60                 |
| lightspeed_uwsgi_timeout_grace_period | Ansible Lightspeed uwsgi timeout grace period                       |          |    x     | 2                  |

#### Lightspeed chatbot

| Name                                    | Description                                 | Required | Optional | Default |
|-----------------------------------------|---------------------------------------------| -------- | -------- |---------|
| lightspeed_chatbot_model_url            | Chatbot server url                          |          |    x     |         |
| lightspeed_chatbot_model_verify_ssl     | Chatbot tls verify                          |          |    x     | true    |
| lightspeed_chatbot_default_provider     | Chatbot provider ['rhoai','openai','azure'] |          |    x     | rhoai   |
| lightspeed_chatbot_http_port            | Chatbot http port                           |          |    x     | 8085    |
| lightspeed_chatbot_https_port           | Chatbot https port                          |          |    x     | 8449    |
| lightspeed_chatbot_disable_https        | Disable Chatbot https                       |          |    x     | false   |
| lightspeed_chatbot_tls_cert             | Chatbot TLS certificate                     |          |    x     |         |
| lightspeed_chatbot_tls_key              | Chatbot TLS key                             |          |    x     |         |
| lightspeed_chatbot_model_id             | Chatbot model                               |          |    x     |         |
| lightspeed_chatbot_model_api_key        | Chatbot access token                        |          |    x     |         |
| lightspeed_chatbot_model_extra_settings | Chatbot model extra configuration           |          |    x     | {}      |
| lightspeed_chatbot_agent_extra_settings | Chatbot agent extra configuration           |          |    x     | {}      |

Model extra parameters will need to be passed through an ansible `lightspeed_chatbot_model_extra_settings` dictionary.

For example when lightspeed_chatbot_default_providerequals to azure, you may set:

```yaml
lightspeed_chatbot_model_extra_settings:
  api_version: "1.0.1"
  api_type: ""
```

Agent extra parameters will need to be passed through an ansible `lightspeed_chatbot_agent_extra_settings` dictionary.

For example, you may set:

```yaml
lightspeed_chatbot_agent_extra_settings:
  chatbot_temperature_override: 1.0
```

#### Lightspeed MCP tools

| Name                                | Description                       | Required | Optional | Default |
| ----------------------------------- | --------------------------------- | -------- | -------- | ------- |
| lightspeed_mcp_controller_enabled   | Lightspeed MCP controller enabled |          |    x     | false   |
| lightspeed_mcp_controller_port      | Lightspeed MCP controller port    |          |    x     | 8004    |
| lightspeed_mcp_lightspeed_enabled   | Lightspeed MCP lightspeed enabled |          |    x     | false   |
| lightspeed_mcp_lightspeed_port      | Lightspeed MCP lightspeed port    |          |    x     | 8005    |

#### Lightspeed WCA

| Name                                      | Description                                                                              | Required | Optional | Default                                     |
|-------------------------------------------|------------------------------------------------------------------------------------------|----------|----------|---------------------------------------------|
| lightspeed_wca_model_type                 | IBM Watsonx Code Assistant model deployment mode, Cloud or On-Prem ("wca", "wca-onprem") |          |    x     | wca                                         |
| lightspeed_wca_model_url                  | URL of the IBM watsonx Code Assistant model                                              |          |    x    | https://api.dataplatform.test.cloud.ibm.com |
| lightspeed_wca_model_api_key              | API key of the IBM watsonx Code Assistant model                                          |    x     |          |                                             |
| lightspeed_wca_model_id                   | ID of the IBM watsonx Code Assistant model                                               |          |    x     |                                             |
| lightspeed_wca_model_verify_ssl           | SSL certificate of the IBM watsonx Code Assistant model's verify                         |          |    x     | true                                        |
| lightspeed_wca_model_enable_anonymization | Anonymization of Personally Identifiable Information (PII)                               |          |    x     | true                                        |
| lightspeed_wca_model_username             | IBM Cloud Pak user for Data deployment. Only applicable for type WCA on-prem             |          |    x     |                                             |
| lightspeed_wca_health_check               | Enables or disables WCA health check                                                     |          |    x     | true                                        |
| lightspeed_wca_idp_url                    | WCA Identify Provider URL. Only applicable for type WCA Cloud                            |          |    x     |                                             |
| lightspeed_wca_idp_login                  | WCA Identify Provider login username. Only applicable for type WCA Cloud                 |          |    x     |                                             |
| lightspeed_wca_idp_password               | WCA Identify Provider login password. Only applicable for type WCA Cloud                 |          |    x     |                                             |

### Ansible MCP server

| Name                             | Description                                   | Required | Optional |            Default |
| -------------------------------- | --------------------------------------------- | -------- | -------- | ------------------ |
| mcp_nginx_disable_hsts           | Disable Nginx HSTS                            |          |    x     | false              |
| mcp_nginx_disable_https          | Disable Nginx HTTPS                           |          |    x     | false              |
| mcp_nginx_hsts_max_age           | Nginx HSTS maximum age                        |          |    x     | 63072000           |
| mcp_nginx_http_port              | Nginx HTTP port                               |          |    x     | 8086               |
| mcp_nginx_https_port             | Nginx HTTPS port                              |          |    x     | 8448               |
| mcp_nginx_https_protocols        | Nginx HTTPS protocols                         |          |    x     | [TLSv1.2, TLSv1.3] |
| mcp_nginx_user_headers           | Custom Nginx headers                          |          |    x     | []                 |
| mcp_ignore_certificate_errors    | Ignore the SSL errors                         |          |    x     | false              |
| mcp_public_base_url              | Custom location of the AAP deployment         |          |    x     | ''                 |
| mcp_allow_write_operations       | Allow write operations                        |          |    x     | false              |
| mcp_extra_settings               | MCP extra settings                            |          |    x     | []                 |

### Database

| Name                               | Description                      | Required | Optional | Default       |
| ---------------------------------- | -------------------------------- | -------- | -------- | ------------- |
| postgresql_admin_database          | Postgresql admin database        |          |    x     | postgres      |
| postgresql_admin_username          | Postgresql admin user            |          |    x     | postgres      |
| postgresql_admin_password          | Postgresql admin password        |     x    |          |               |
| postgresql_disable_tls             | Disable Postgresql TLS           |          |    x     | false         |
| postgresql_effective_cache_size    | Postgresql effective cache size  |          |    x     |               |
| postgresql_extra_settings          | Postgresql extra settings        |          |    x     | []            |
| postgresql_keep_databases          | Keep databases during uninstall  |          |    x     | false         |
| postgresql_max_connections         | Postgresql max connections       |          |    x     | 1024          |
| postgresql_log_destination         | Postgresql log file location     |          |    x     | /dev/stderr   |
| postgresql_password_encryption     | Postgresql password encryption   |          |    x     | scram-sha-256 |
| postgresql_port                    | Postgresql port                  |          |    x     | 5432          |
| postgresql_shared_buffers          | Postgresql shared buffers        |          |    x     |               |
| postgresql_tls_cert                | Postgresql TLS certificate       |          |    x     |               |
| postgresql_tls_key                 | Postgresql TLS key               |          |    x     |               |
| postgresql_tls_remote              | Postgresql TLS remote files      |          |    x     | false         |
| postgresql_use_archive_compression | Postgresql compress backup files |          |    x     | true          |

Extra parameters will need to be passed through an ansible `postgresql_extra_settings` variable.

For example, you may set:

```yaml
postgresql_extra_settings:
  - setting: ssl_ciphers
    value: 'HIGH:!aNULL:!MD5'
```
### Receptor

| Name                             | Description                    | Required | Optional |   Default   |
| -------------------------------- | ------------------------------ | -------- | -------- | ----------- |
| receptor_disable_signing         | Disable receptor signing       |          |    x     |    false    |
| receptor_disable_tls             | Disable receptor TLS           |          |    x     |    false    |
| receptor_log_level               | Receptor loggging level        |          |    x     |     info    |
| receptor_mintls13                | Receptor TLS 1.3 minimal       |          |    x     |    false    |
| receptor_peers                   | Receptor peers list            |          |    x     |     []      |
| receptor_port                    | Receptor port                  |          |    x     |    27199    |
| receptor_protocol                | Receptor protocol              |          |    x     |     tcp     |
| receptor_signing_private_key     | Receptor signing private key   |          |    x     |             |
| receptor_signing_public_key      | Receptor signing public key    |          |    x     |             |
| receptor_signing_remote          | Receptor signing remote files  |          |    x     |    false    |
| receptor_tls_cert                | Receptor TLS certificate       |          |    x     |             |
| receptor_tls_key                 | Receptor TLS key               |          |    x     |             |
| receptor_tls_remote              | Receptor TLS remote files      |          |    x     |    false    |
| receptor_type                    | Receptor node type             |          |    x     |  execution  |
| receptor_use_archive_compression | Receptor compress backup files |          |    x     | true        |

**Note:** Hop nodes have reduced resource requirements and are exempt from the standard 16GB RAM preflight check.

### Redis

| Name                          | Description                       | Required | Optional |   Default   |
| ----------------------------- | --------------------------------- | -------- | -------- | ----------- |
| redis_cluster_ip              | Redis cluster IP address          |          |    x     |             |
| redis_disable_tls             | Disable Redis TLS                 |          |    x     | false       |
| redis_mode                    | Redis mode cluster or standalone  |          |    x     | cluster     |
| redis_port                    | Redis port                        |          |    x     | 6379        |
| redis_prefer_ipv6             | Prefer IPv6 in dual-stack         |          |    x     | false       |
| redis_tls_cert                | Redis TLS certificate             |          |    x     |             |
| redis_tls_key                 | Redis TLS key                     |          |    x     |             |
| redis_tls_remote              | Redis TLS remote files            |          |    x     | false       |
| redis_use_archive_compression | Redis compress backup files       |          |    x     | true        |

### Performance Co-Pilot Monitoring

| Name                         | Description                                             | Required | Optional |   Default   |
| ---------------------------- | ------------------------------------------------------- | -------- | -------- | ----------- |
| setup_monitoring             | Setup Performance Co-Pilot on AAP control plane nodes   |          |    x     |    false    |
| pcp_pmcd_port                | Port to serve Performance Metrics Collection Daemon on  |          |    x     |    44321    |
| pcp_pmproxy_port             | Port to serve Performance Metrics Proxy on              |          |    x     |    44322    |
| pcp_firewall_zone            | Firewall zone for pcp services                          |          |    x     |    public   |
| pcp_use_archive_compression  | Performance Co-Pilot compress backup files              |          |    x     |    true     |


### Log Gathering (sos report)

| Name                 | Description                                          | Required | Optional | Default |
| -------------------  | ---------------------------------------------------- | -------- | -------- | ------- |
| case_number          | The support case number being worked                 |          |    x     |         |
| clean                | Obfuscate sensitive data present on the sos report   |          |    x     | false   |
| upload               | Automatically upload the sos report data to Red Hat  |          |    x     | false   |
| target_sos_directory | Generated sos report files directory                 |          |          | /tmp    |

The minimal configuration for running the containerized install will look like the following:

```yaml
---
controller_admin_password: foo
controller_pg_host: 127.0.0.1
controller_pg_password: bar
hub_admin_password: supersecret
hub_pg_host: 127.0.0.1
hub_pg_password: secretsuper
postgresql_admin_password: foobar
...

```

These variables can be put in a `vars.yml` and passed as `-e @vars.yml` to `ansible-playbook` command.
Otherwise, they can be put in the inventory. A sample inventory is included in the `samples` folder.

## Usage

You first need to create the ansible inventory file.
The current topology supports the following groups:
- `automationcontroller`
- `automationeda`
- `automationhub`
- `ansiblelightspeed`
- `automationmetrics`
- `database`
- `execution_nodes`

```ini
[automationcontroller]
node.ansible.com

[automationhub]
node.ansible.com

[automationmetrics]
node.ansible.com

[automationeda]
node.ansible.com

[ansiblelightspeed]
node.ansible.com

[database]
node.ansible.com

[all:vars]
```

Note that `automationeda` is only available with AAP 2.4+ releases.

Note that `ansiblelightspeed` is only available with AAP 2.6+ releases.

Note that the Automation Metrics Service (`automationmetrics` inventory group) is only available with AAP 2.6+ releases.

The same node can be used as `automationcontroller` and `database` or you can use a dedicated node
for each group.

```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.install
```

There are two ways to run the containerized installer:
- Online: The container images will be pulled from a registry
- Offline: The container images will be imported from a tarball

This workflow is controlled via the `bundle_install` variable.

### Disconnected registry
The installer does not manage installation of a disconnected registry.
If needed, you can use <https://github.com/quay/mirror-registry> tool, which will
install a containerized Quay registry.

### Online install

This is the default install scenario (`bundle_install: false`) and will try to pull the container images
from `registry.redhat.io` (which requires authentication).
As such you need to provide the registry username and password for authentication.

```yaml
---
registry_username: foo@ansible.com
registry_password: bar
...
```

As an alternative, you can use the internal registry (without authentication).

```yaml
---
registry_auth: false
registry_url: registry-proxy.engineering.redhat.com
registry_ns_aap: rh-osbs
registry_ns_rhel: rh-osbs
registry_tls_verify: false
controller_image: 'ansible-automation-platform-26-controller-rhel9:latest'
ee_minimal_image: 'ansible-automation-platform-26-ee-minimal-rhel9:latest'
ee_supported_image: 'ansible-automation-platform-26-ee-supported-rhel9:latest'
hub_image: 'ansible-automation-platform-26-hub-rhel9:latest'
hub_web_image: 'ansible-automation-platform-26-hub-web-rhel9:latest'
postgresql_image: 'rhel9-postgresql-15:latest'
redis_image: 'rhel9-redis-6:latest'
...
```

### Offline install

For offline installation, we need to export the container images from the registry  before running the installer.

```bash
$ ansible-playbook ansible.containerized_installer.bundle
```

Note: The default (un)compress tool is gzip but you can change it to pigz to reduce the execution time.

```bash
$ ansible-playbook ansible.containerized_installer.bundle -e container_compress=pigz
```

By default, the container images will be pulled from the public registry.
If you want to use the images from `registry.redhat.io` then you'll need to set extra variables to
that command.

```bash
$ ansible-playbook ansible.containerized_installer.bundle -e registry_auth=true -e registry_username=foo -e registry_password=bar
```

This command will create a `bundle/images` directory with all container images tarball (compressed).
You need to set `bundle_install: true` in your ansible configuration and `bundle_dir` with
the path the bundle directory (without the images subdirectory).

```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.install -e bundle_install=true -e bundle_dir=$(pwd)/bundle
```

If you need to pull container images from a different architecture than the local node then you can use the `container_image_arch`
variable.
By default, podman will pull the container images with the same architecture than the current host.
To download aarch64 container images from a x86_64 host then you can use the following command:

```bash
$ ansible-playbook ansible.containerized_installer.bundle -e container_image_arch=aarch64
```

### Backup

To backup a containerized deployment, execute the `backup.yml` playbook.

```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.backup
```

This will backup the important data deployed by the containerized installer such as:

- postgresql databases
- configuration files
- data files

By default, the backup directory on the ansible host will use ./backups but this can be changed via the `backup_dir` variable.

### Restore

To restore a containerized deployment, execute the `restore.yml` playbook.

```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.restore
```

This will restore the important data deployed by the containerized installer such as:

- postgresql databases
- configuration files
- data files

By default, the backup directory on the ansible host will use ./backups but this can be changed via the `backup_dir` variable.

### Uninstall

To uninstall a containerized deployment, execute the `uninstall.yml` playbook.

```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.uninstall
```

This will stop all systemd units and containers and then delete all resources used by the containerized installer
such as:

* config and data directories/files
* systemd unit files
* podman containers and images
* RPM packages

To keep container images, you can set the `container_keep_images` variable to true.

```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.uninstall -e container_keep_images=true
```

To keep postgresql databases, you can set the `postgresql_keep_databases` variable to true.

```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.uninstall -e postgresql_keep_databases=true
```

Note that you'll have to use the same django secret key values rather than the auto-generated ones.

### Collecting Troubleshooting data with sos report

To collect the sos report from all servers in your inventory, execute the `log_gathering.yml` playbook.
```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.log_gathering
```

This will connect to each node present in the inventory, install the sos tool, and generate new logs.

The sos report files are copied to the /tmp folder for the current server. You can change it by specifying the following EXTRA_VARS:
```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.log_gathering -e 'target_sos_directory=/path/to/files' -s
```

Other options may be provided while creating the sos reports by specifying the following EXTRA_VARS:
```bash
$ ansible-playbook -i </path/to/inventory> ansible.containerized_installer.log_gathering -e 'case_number=0000000' -e 'clean=true' -e 'upload=true' -s
```

## Access

The protocol and ports default values are:
* `https` protocol
* ports `80/443` for gateway

The Automation Gateway UI is available by default at:

```
https://<gateway node>:443
```
