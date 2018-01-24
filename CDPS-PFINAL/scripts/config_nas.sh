#!/bin/bash

sudo lxc-attach --clear-env -n nas1 -- uname -a

echo '------------------------------------------------------------'
echo 'Making each of the three Gluster nodes aware of each other...'
# Using node nas1 to probe the other two nodes nas2 and nas3
sudo lxc-attach --clear-env -n nas1 -- sudo gluster peer probe nas2
sudo lxc-attach --clear-env -n nas1 -- sudo gluster peer probe nas3

sudo lxc-attach --clear-env -n nas1 -- sudo gluster peer status

echo '------------------------------------------------------------'
echo 'Creating replicated GlusterFS volume...'
sudo lxc-attach --clear-env -n nas1 -- sudo gluster volume create nas replica 3 nas1:/nas nas2:/nas nas3:/nas force

echo '------------------------------------------------------------'
echo 'Starting new volume...'
sudo lxc-attach --clear-env -n nas1 -- sudo gluster volume start nas

sudo lxc-attach --clear-env -n nas1 -- sudo gluster volume info

sudo lxc-attach --clear-env -n nas1 -- sudo gluster volume set nas network.ping-timeout 5

exit 0
