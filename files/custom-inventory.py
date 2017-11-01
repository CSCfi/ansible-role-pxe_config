#!/usr/bin/python
# This is a script that can take an ansible inventory file
# and print the groups of a group.
# It can also print one host per all the groups of a group
## https://github.com/CSCfi/ansible-role-pxe_config
## Ansible API documentation:
# http://docs.ansible.com/ansible/developing_api.html

  # Example inventory:
  # [login]
  # login
  # [compute:children]
  # compute1
  # compute2
  # [pxe_bootable_nodes:children]
  # compute
  # login

### Libraries used
import argparse
# for parsing the existing inventory
from ansible.parsing.dataloader import DataLoader
#from ansible.vars import VariableManager
# this could be used for producing json
import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

# checking if inventory_file exists
import os.path
# for exiting with non-zero rc
import sys

###args
parser = argparse.ArgumentParser(description='Different inventory script')
parser.add_argument('--inventory', dest='inventory_file', action='store', default='hosts')
parser.add_argument('--list', dest='list', action='store_true', help='boolean to list all hosts')
parser.add_argument('--group', dest='group', action='store', help='Use with --single, output groups of a group. This needs to be a top level group')
parser.add_argument('--single', dest='single', action='store_true', help='Use with --group, output one host per child group of group')
parser.add_argument('--debug', dest='debug', action='store_true', help='Get some debug output')

args = parser.parse_args()

inventory_file = args.inventory_file
llist = args.list # Unused
chosen_group = args.group
single = args.single
debug = args.debug

def listfunction(llist):
    """This function does all the work and lists groups or hosts"""
    variable_manager = VariableManager()
    loader = DataLoader()
    if not os.path.isfile(inventory_file):
        print "%s is not a file - halting. Consider using the '--inventory $path/to/ansible_inventory file' parameter" % inventory_file
        sys.exit(1)
    else:
        inventory = InventoryManager(loader=loader, sources=inventory_file)
        variable_manager = VariableManager(loader=loader, inventory=inventory)


    if chosen_group and single:
        def traverse(agroup, hostset):
            """Recursive depth-first traversal"""
            for child in agroup.child_groups:
                traverse(child, hostset)
            if len(agroup.hosts) > 0:
                hostset.add(agroup.hosts[0].name.encode('utf8'))
        single_hosts = set()
        traverse(inventory.groups[chosen_group], single_hosts)
        return {chosen_group:list(single_hosts)}

    if chosen_group:
        thegroup = inventory.groups[chosen_group]
        newhosts = []
        for h in thegroup.get_hosts():
            newhosts.append(h.name.encode('utf8'))
        return {chosen_group:newhosts}
    else:
        all_groups = {}
        for g in inventory.groups:
            newhosts = []
            for h in inventory.get_hosts(g):
                newhosts.append(h.name.encode('utf8'))
            all_groups[g] = newhosts
        return all_groups

#########

print json.dumps(listfunction(args.list), indent=4)
