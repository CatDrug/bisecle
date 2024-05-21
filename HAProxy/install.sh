apt update
apt show haproxy
add-apt-repository ppa:vbernat/haproxy-2.7 -y
apt update
apt install haproxy=2.7.\* -y

haconf=/etc/haproxy/haproxy.cfg
echo ""                          >> $haconf
echo "frontend stats"            >> $haconf
echo "        mode http"         >> $haconf
echo "        bind *:8404"       >> $haconf
echo "        http-request use-service prometheus-exporter if { path /metrics }" >> $haconf
echo "        stats enable"      >> $haconf
echo "        stats uri /"       >> $haconf
echo "        stats refresh 10s" >> $haconf

systemctl reload haproxy
curl http://localhost:8404