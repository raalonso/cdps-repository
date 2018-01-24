#!/bin/bash

sudo lxc-attach --clear-env -n bbdd -- uname -a

echo '------------------------------------------------------------'
echo 'Updating...'
sudo lxc-attach --clear-env -n bbdd -- apt update

echo '------------------------------------------------------------'
echo 'Installing postgresql...'
sudo lxc-attach --clear-env -n bbdd -- apt -y install postgresql

sudo lxc-attach --clear-env -n bbdd -- bash -c "echo \"listen_addresses='10.1.4.31'\" >> /etc/postgresql/9.6/main/postgresql.conf"
sudo lxc-attach --clear-env -n bbdd -- bash -c "echo \"host all all 10.1.4.0/24 trust\" >> /etc/postgresql/9.6/main/pg_hba.conf"

echo 'Creating user crm...'
sudo lxc-attach --clear-env -n bbdd -- bash -c "echo \"CREATE USER crm with PASSWORD 'pass123';\" | sudo -u postgres psql"
echo 'Creating database crm...'
sudo lxc-attach --clear-env -n bbdd -- bash -c "echo \"CREATE DATABASE crm;\" | sudo -u postgres psql"
echo 'Granting privileges...'
sudo lxc-attach --clear-env -n bbdd -- bash -c "echo \"GRANT ALL PRIVILEGES ON DATABASE crm to crm;\" | sudo -u postgres psql"

echo 'Restart service postgresql'
sudo lxc-attach --clear-env -n bbdd -- systemctl restart postgresql

exit 0
