[![Build Status](https://travis-ci.org/CSC-IT-Center-for-Science/ansible-role-pxe_config.svg)](https://travis-ci.org/CSC-IT-Center-for-Science/ansible-role-pxe_config)
ansible-role-pxe\_config
=========

Configures PXE

Requirements
------------

a hosts file that looks like:

<pre>

[compute]
node1 ip_address=10.1.2.1 mac_address=00:11:22:33:44:55 pxe=yes

[pxe_bootable_nodes:children]
compute

</pre>

Role Variables
--------------

generate_ssh_host_keys: True

See defaults/main.yml for some examples

Dependencies
------------

   * currently tightly integrated with dhcp\_server and pxe\_bootstrap

      * https://github.com/CSC-IT-Center-for-Science/ansible-role-pxe\_bootstrapo
      * https://github.com/CSC-IT-Center-for-Science/ansible-role-dhcp\_server



Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: ansible-role-pxe_config }

License
-------

MIT

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
