#!/bin/bash

if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi

USUARIO=$(who mom likes | awk '{print $1}')

IS_ROOT=$(whoami)
if [ "$IS_ROOT" == "root" ]; then
    echo "Don't run as root/(using sudo)";
    exit 0;
fi

#adiciona o repositorio do cassandra
sudo touch /etc/apt/sources.list.d/cassandra.sources.list
sudo add-apt-repository  "deb http://debian.datastax.com/community stable main"
curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -

#adiciona o repositorio do elastic search
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
sudo add-apt-repository "deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main"
#sudo update-rc.d elasticsearch defaults 95 10

sudo apt-get update
cat ./apt-reqs.txt | xargs sudo apt-get install -y

sudo pip-2.7 install virtualenv
sudo pip-2.7 install virtualenv --upgrade

#cria o virtualenv e instala as libs python nele
sudo mkdir -p /var/virtual_envs
sudo mkdir -p /var/virtual_envs/simbiose
sudo chown -R $USUARIO:$USUARIO /var/virtual_envs/

virtualenv /var/virtual_envs/simbiose
source /var/virtual_envs/simbiose/bin/activate
pip install setuptools --upgrade
pip install -r ./pip-reqs.txt 

#cria o keyspace no cassandra
cqlsh < create_db.cql
