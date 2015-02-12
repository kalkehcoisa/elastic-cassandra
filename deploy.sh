#instala o cassandra
echo "deb http://debian.datastax.com/community stable main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
curl -L http://debian.datastax.com/debian/repo_key | sudo apt-key add -

sudo apt-get update
cat ./apt-reqs.txt | xargs sudo apt-get install -y

#cria o virtualenv e instala as libs python nele
virtualenv-2.7 /var/virtual_envs/simbiose
source /var/virtual_envs/simbiose
cat ./pip-reqs.txt | xargs pip install
