apt update
apt install docker docker.io -y
apt install docker-compose docker.io -y
systemctl start docker
systemctl enable docker
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf
sysctl -p

echo "TZ=Europe/Moscow" >> /opt/.global
mkdir /opt/elk
cd /opt/elk
wget https://github.com/CatDrug/bisecle/blob/main/ELK/docker-compose.yml
docker-compose up -d
docker-compose stop
cd /var/lib/docker/volumes/elk_config/_data
rm elasticsearch.yml
wget https://github.com/CatDrug/bisecle/blob/main/ELK/elasticsearch.yml
cd /var/lib/docker/volumes/elk_kconfig/_data
rm kibana.yml
wget https://github.com/CatDrug/bisecle/blob/main/ELK/kibana.yml
cd /opt/elk
docker-compose up -d
docker exec elastic bash bin/elasticsearch-users useradd goodwin -p P@ssw0rd -r superuser
