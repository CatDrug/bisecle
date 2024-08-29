curl -L -O https://mirrors.huaweicloud.com/filebeat/7.2.0/filebeat-7.2.0-amd64.deb
sudo dpkg -i filebeat-7.2.0-amd64.deb


output.logstash:
  # The Logstash hosts
  hosts: ["10.128.0.123:5044"]
