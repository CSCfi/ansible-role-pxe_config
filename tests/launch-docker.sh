#!/bin/bash

sudo docker build --rm -t local/c7-systemd -f tests/Dockerfile .
sudo docker run -it --privileged=true --rm=true -v /sys/fs/cgroup:/sys/fs/cgroup:ro -v `pwd`:/ansible-role-pxe_config:rw local/c7-systemd /bin/bash -c "/ansible-role-pxe_config/tests/test-in-docker-image.sh ${OS_TYPE} ${OS_VERSION} ${ANSIBLE_VERSION}"
