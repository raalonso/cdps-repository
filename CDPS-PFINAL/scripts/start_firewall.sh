#!/bin/bash

sudo lxc-attach --clear-env -n fw -- uname -a

echo '------------------------------------------------------------'
echo 'Starting firewall...'

sudo cp ./scripts/fw.fw /var/lib/lxc/fw/rootfs/root

sudo lxc-attach --clear-env -n fw -- bash -c "cd /root; ./fw.fw"
echo 'OK'

exit 0
