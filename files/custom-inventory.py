#!/usr/bin/python
# This is a script that can take an ansible inventory file
# and print the groups of a group.
# It can also print one host per all the groups of a group
# Extremely poor looking python to json string replacement
# at the bottom.  Feel free to improve :)
## https://github.com/CSC-IT-Center-for-Science/ansible-role-pxe_config
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
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
# this could be used for producing json
#import json
# checking if inventory_file exists
import os.path
# for exiting with non-zero rc
import sys

###args
parser = argparse.ArgumentParser(description='Different inventory script')
parser.add_argument('--inventory', dest='inventory_file', action='store', default='hosts')
parser.add_argument('--list', dest='list', action='store_true', help='boolean to list all hosts')
parser.add_argument('--group', dest='group', action='store', help='Use with --single, output groups of a group. This needs to be a top level group')
parser.add_argument('--json', dest='json', action='store_true', help='Output in JSON')
parser.add_argument('--single', dest='single', action='store_true', help='Use with --group, output one host per child group of group')
parser.add_argument('--debug', dest='debug', action='store_true', help='Get some debug output')

args = parser.parse_args()

inventory_file = args.inventory_file
llist = args.list
chosen_group = args.group
want_json = args.json
single = args.single
debug = args.debug

dict_hosts = {}
dict_single_hosts = {}
dict_groups = {}
dict_groups2 = {}

# dict_single_hosts is used to store single hosts from multiple child groups
dict_single_hosts[chosen_group] = []

###

def listfunction(llist):
    variable_manager = VariableManager()
    loader = DataLoader()
    if not os.path.isfile(inventory_file):
        print "%s is not a file - halting. Consider using the '--inventory $path/to/ansible_inventory file' parameter" % inventory_file
        sys.exit(1)
    else:
        inventory = Inventory(loader=loader, variable_manager=variable_manager,  host_list=inventory_file)

    groups = inventory.groups
    for group in groups:
        dogroup = inventory.get_group(group)
        if dogroup.child_groups:
            list_of_hosts = dogroup.child_groups
            # we need to quote the items in the list because JSON
            list_of_hosts2 = ','.join("'{0}'".format(x) for x in list_of_hosts)
            list_of_hosts3 = list_of_hosts2.replace('["', '[')
            list_of_hosts4 = list_of_hosts3.replace('"]', ']')
            # the three lists
            dict_groups2[group] = list_of_hosts # used with --single 
            dict_groups[group] = [ list_of_hosts4 ] # used with --list and --group
            dict_hosts[group] = inventory.list_hosts(group) # used with --single

## Nested child groups
# To make this work with optionally nested groups (example up top) we need to after the group is populated, look in dict_groups if there are any double-nested groups.
    if chosen_group and single:
        child_child_groups = []
        for group in dict_groups2[chosen_group]:
            try:
                dict_groups2[str(group)]
                child_child_groups.append(str(group))
            except KeyError:
                # this group does not have a child group!
                continue


      # here we loop through child_child groups and list the hosts of those groups and then add the last in each group to the dict_single_hosts
    if child_child_groups != []:
        for child in child_child_groups:
            for child_child in dict_groups2[child]:
                child_host = inventory.get_hosts(str(child_child))[-1]
                dict_single_hosts[child_child] = [ child_host ]

##   End of this child of mine

#   make a dict that only has one host per child group
    if chosen_group:
        for host in dict_hosts[chosen_group]:
            groups_for_host = inventory.groups_for_host(str(host))
#           if debug: print "groups_for_host: %s" % groups_for_host

            for group in groups_for_host:
                if group in dict_groups2[chosen_group]:
                #this host is in one of the child groups of the chosen_group
                    if len(dict_single_hosts[chosen_group]) == 0:
                        dict_single_hosts[group] = [ host ]

#   here we populate dict_single_hosts so that the chosen_group key only has a list of hosts that are in separate child groups
    for group in dict_single_hosts:
        if chosen_group == group:
            continue
        if len(dict_single_hosts[chosen_group]) < ( len(dict_single_hosts) - 1 ):
            # -1 because the chosen_group is also in the same dict
            for host in dict_single_hosts[group]:
              # and we first check if it's already in there, that might have been added by the child_child hosts
                if host not in dict_single_hosts[chosen_group]:
                    dict_single_hosts[chosen_group].append(host)

#   here we quote the entries in dict_of_single_hosts (because JSON)
    if single:
        list_of_single_hosts = dict_single_hosts[chosen_group]
        list_of_single_hosts2 = ','.join("'{0}'".format(x) for x in list_of_single_hosts)
        dict_single_hosts[chosen_group] = []
        dict_single_hosts[chosen_group] = [ list_of_single_hosts2 ]
##  ########

#   Some arguments checking - this could probably be done with argparse settings
    if chosen_group:
        if single:
            return(dict_single_hosts[chosen_group])
        else:
            return(dict_groups[chosen_group])
    else:
        return(dict_groups)

#########

# Some more string replacements to produce JSON
if args.list:
    if want_json:
        hostlist = str(listfunction(args.list))
        hostlist2 = hostlist.replace('["', '[')
        hostlist3 = hostlist2.replace('"]', ']')
        hostlist4 = hostlist3.replace('^"', '')
        hostlist5 = hostlist4.replace('"$', '')
        hostlist6 = hostlist5.replace("u'", "'")
        hostlist7 = hostlist6.replace("'", '"')
        print hostlist7
        #print json.dumps(hostlist5)
    else:
        print listfunction(args.list)
elif args.group:
    if want_json:
        hostlist = str(listfunction(args.group))
        hostlist2 = hostlist.replace('["', '[')
        hostlist3 = hostlist2.replace('"]', ']')
        hostlist4 = hostlist3.replace('^"', '')
        hostlist5 = hostlist4.replace('"$', '')
        if not single:
            hostlist6 = hostlist5.replace("u'", "'")
        else:
            hostlist6 = hostlist5
        hostlist7 = hostlist6.replace("'", '"')
        print '{ "%s" : %s }' % (args.group,hostlist7)
        #print json.dumps(hostlist5)
        #print json.dumps(listfunction(args.group))
    else:
        print listfunction(args.group)

