#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Automation Platform
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: eda_credential

short_description: Creates a container registry credential in Automation EDA Controller

version_added: "2.4"

description: Creates a container registry credential in Automation EDA Controller

options:
    eda_server_url:
        description: Automation EDA Controller server URL
        required: true
        type: str
    eda_username:
        description: Automation EDA Controller server administrator username
        required: true
        type: str
    eda_password:
        description: Automation EDA Controller server administrator password
        required: true
        type: str
    eda_validate_certs:
        description: Validate SSL certificates for EDA API connection
        required: true
        type: bool
    name:
        description: Name for credential
        required: true
        type: str
    username:
        description: Username for container repository
        required: true
        type: str
    organization:
        description: Organization for container repository
        required: false
        type: str
    token:
        description: Token for container repository
        required: true
        type: str
    registry_url:
        description: URL for the registry source
        required: true
        type: str
    registry_validate_certs:
        description: Validate SSL certificates for registry connection
        required: false
        type: bool

author:
    - Ansible Automation Platform Team
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.parse import quote_plus
import json


def run_module():
    module_args = dict(
        eda_server_url=dict(type="str", required=True),
        eda_username=dict(type="str", required=True),
        eda_password=dict(type="str", required=True, no_log=True),
        eda_validate_certs=dict(type="bool", required=True),
        name=dict(type="str", required=True),
        username=dict(type="str", required=True),
        organization=dict(type="str", default="Default"),
        token=dict(type="str", required=True, no_log=True),
        registry_url=dict(type="str", required=True),
        registry_validate_certs=dict(type="bool", default=True),
    )

    result = dict(
        changed=False,
        message=[],
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(**result)

    api_url_base = f"{module.params['eda_server_url']}/api/eda/v1"

    api_username = module.params["eda_username"]
    api_password = module.params["eda_password"]
    eda_validate_certs = module.params["eda_validate_certs"]
    header = {"Content-Type": "application/json"}
    organization = module.params["organization"]

    organization_api_url = (
        f"{api_url_base}/organizations/?name={quote_plus(organization)}"
    )
    try:
        organization_str = json.loads(
            open_url(
                organization_api_url,
                method="GET",
                headers=header,
                validate_certs=eda_validate_certs,
                force_basic_auth=True,
                url_username=api_username,
                url_password=api_password,
            ).read()
        )
    except Exception as e:
        result["message"].append(f"Organization not found. Error: {e}")
        module.fail_json("", **result)
    else:
        organization_id = organization_str["results"][0]["id"]

    cred_type_api_url = (
        f"{api_url_base}/credential-types/?name={quote_plus('Container Registry')}"
    )
    try:
        credential_type_str = json.loads(
            open_url(
                cred_type_api_url,
                method="GET",
                headers=header,
                validate_certs=eda_validate_certs,
                force_basic_auth=True,
                url_username=api_username,
                url_password=api_password,
            ).read()
        )
    except Exception as e:
        result["message"].append(
            f"Credential type Container Registry not found, skipping creation. Error: {e}"
        )
        module.fail_json("", **result)
    else:
        credential_type_id = credential_type_str["results"][0]["id"]

    cred_api_url = f"{api_url_base}/eda-credentials/"
    name = module.params["name"]
    username = module.params["username"]
    token = module.params["token"]
    registry_url = module.params["registry_url"]
    registry_validate_certs = module.params["registry_validate_certs"]

    payload = {
        "name": name,
        "credential_type_id": credential_type_id,
        "organization_id": organization_id,
        "inputs": {
            "username": username,
            "password": token,
            "host": registry_url,
            "verify_ssl": registry_validate_certs,
        },
    }

    cred_api_url_by_name = f"{cred_api_url}?name={quote_plus(name)}"
    try:
        cred_check = json.loads(
            open_url(
                cred_api_url_by_name,
                method="GET",
                headers=header,
                validate_certs=eda_validate_certs,
                force_basic_auth=True,
                url_username=api_username,
                url_password=api_password,
            ).read()
        )
    except Exception as e:
        result["message"].append(
            f"Failed to check if '{name}' already exists, skipping creation. Error: {e}"
        )
        module.fail_json("", **result)
    else:
        if not cred_check["count"]:
            try:
                open_url(
                    cred_api_url,
                    method="POST",
                    headers=header,
                    validate_certs=eda_validate_certs,
                    force_basic_auth=True,
                    url_username=api_username,
                    url_password=api_password,
                    data=json.dumps(payload),
                )
            except Exception as e:
                result["message"].append(f"Failed to create '{name}'. Error: {e}")
                module.fail_json("", **result)
            else:
                result["message"].append(f"Created '{name}' credential")
                result["changed"] = True
        else:
            current_registry_url = cred_check["results"][0]["inputs"]["host"]
            if registry_url != current_registry_url:
                cred_id = cred_check["results"][0]["id"]
                cred_api_url_by_id = f"{cred_api_url}{cred_id}/"
                try:
                    open_url(
                        cred_api_url_by_id,
                        method="PATCH",
                        headers=header,
                        validate_certs=eda_validate_certs,
                        force_basic_auth=True,
                        url_username=api_username,
                        url_password=api_password,
                        data=json.dumps(payload),
                    )
                except Exception as e:
                    result["message"].append(f"Failed to update '{name}'. Error: {e}")
                    module.fail_json("", **result)
                else:
                    result["message"].append(f"Updated '{name}' credential")
                    result["changed"] = True
            else:
                result["message"].append(f"'{name}' credential already exists")

        module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
