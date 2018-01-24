#!/bin/bash

sudo lxc-attach --clear-env -n lb -- uname -a

echo '------------------------------------------------------------'
echo 'Starting load balancer (xr)...'

sudo lxc-attach --clear-env -n lb -- nohup bash -c "sudo xr --verbose -d round-robin --server tcp:0:80 --backend 10.1.3.11:3000 --backend 10.1.3.12:3000 --backend 10.1.3.13:3000 --web-interface 0:8001 > /tmp/xr.log 2>&1 &"

echo 'OK'
exit 0
