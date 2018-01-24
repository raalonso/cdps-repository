#!/bin/bash

sudo lxc-attach --clear-env -n fw -- uname -a

echo '------------------------------------------------------------'
echo 'Starting firewall...'

sudo cp ./fw.fw /var/lib/lxc/fw/rootfs/etc

sudo lxc-attach --clear-env -n fw -- bash -c "cd /root; ./fw.fw"
echo 'OK'

exit 0
