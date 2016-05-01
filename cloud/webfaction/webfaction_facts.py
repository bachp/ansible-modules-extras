#!/usr/bin/python
#
# Gather facts from Webfaction using Ansible and the Webfaction API
#
# ------------------------------------------
#
# (c) Pascal Bach 2015, with contributions gratefully acknowledged from:
#     * Quentin Stafford-Fraser
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

DOCUMENTATION = '''
---
module: webfaction_facts
short_description: Gather facts from a Webfaction machine
description:
    - Gather facts about applications, databases, websites and domains form a Webfaction machine
author: Pascal Bach (@bachp)
version_added: "2.2"
notes:
    - "You can run playbooks that use this on a local machine, or on a Webfaction host, or elsewhere, since the scripts use the remote webfaction API - the location is not important."
    - See `the webfaction API <http://docs.webfaction.com/xmlrpc-api/>`_ for more info.
options:

    login_name:
        description:
            - The webfaction account to use
        required: true

    login_password:
        description:
            - The webfaction password to use
        required: true

    machine:
        description:
            - The machine name to use (optional for accounts with only one machine)
        required: false
        default: null

'''

EXAMPLES = '''
  - name: Gather webfaction facts
    webfaction_facts:
      login_name={{webfaction_user}}
      login_password={{webfaction_passwd}}
      machine={{webfaction_machine}}
'''

RETURN = '''
webfaction_apps:
    description: List of applications currently existing
    returned: always but can be empty
    type: list
webfaction_dbs:
    description: List of databases currently existing
    returned: always but can be empty
    type: list
webfaction_domains:
    description: List of domains currently existing
    returned: always but can be empty
    type: list
webfaction_websites:
    description: List of websites currently existing
    returned: always but can be empty
    type: list
'''

import xmlrpclib

webfaction = xmlrpclib.ServerProxy('https://api.webfaction.com/')

def main():

    module = AnsibleModule(
        argument_spec = dict(
            login_name = dict(required=True),
            login_password = dict(required=True, no_log=True),
            machine = dict(required=False, default=False),
        ),
        supports_check_mode=True
    )

    if module.params['machine']:
        session_id, account = webfaction.login(
            module.params['login_name'],
            module.params['login_password'],
            module.params['machine']
        )
    else:
        session_id, account = webfaction.login(
            module.params['login_name'],
            module.params['login_password']
        )

    def list2dict(l, field='name'):
        d = {}
        for e in l:
            d[e[field]] = e
        return d

    def get_apps():
        app_list = webfaction.list_apps(session_id)
        return list2dict(app_list)

    def get_dbs():
        db_list = webfaction.list_dbs(session_id)
        return list2dict(db_list)

    def get_domains():
        domain_list = webfaction.list_domains(session_id)
        return list2dict(domain_list, field="domain")

    def get_websites():
        website_list = webfaction.list_websites(session_id)
        return list2dict(website_list)

    module.exit_json(
        changed = False,
        ansible_facts={
            'webfaction_apps': get_apps(),
            'webfaction_dbs': get_dbs(),
            'webfaction_domains': get_domains(),
            'webfaction_websites': get_websites()
        }
    )

from ansible.module_utils.basic import *
main()
