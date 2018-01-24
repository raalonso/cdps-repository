#!/bin/bash

sudo lxc-attach --clear-env -n bbdd -- uname -a

echo 'Restart service postgresql'
sudo lxc-attach --clear-env -n bbdd -- systemctl restart postgresql

exit 0
