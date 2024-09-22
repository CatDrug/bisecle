export OS_VERSION=xUbuntu_22.04
export CRIO_VERSION=1.24
export DEBIAN_FRONTEND=noninteractive #Выключаем псевдографические уведомления
apt update -y
echo iptables-persistent iptables-persistent/autosave_v4 boolean true | sudo debconf-set-selections #Заранее настраиваю iptables
echo iptables-persistent iptables-persistent/autosave_v6 boolean true | sudo debconf-set-selections
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
echo br_netfilter >> /etc/modules-load.d/k8s.conf
echo overlay >> /etc/modules-load.d/k8s.conf
echo net.bridge.bridge-nf-call-ip6tables = 1 >> /etc/sysctl.d/k8s.conf 
echo net.bridge.bridge-nf-call-iptables = 1 >> /etc/sysctl.d/k8s.conf  

apt install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common

curl -fsSL https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS_VERSION/Release.key | sudo gpg --dearmor -o /usr/share/keyrings/libcontainers-archive-keyring.gpg
curl -fsSL https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$CRIO_VERSION/$OS_VERSION/Release.key | sudo gpg --dearmor -o /usr/share/keyrings/libcontainers-crio-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/libcontainers-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS_VERSION/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
echo "deb [signed-by=/usr/share/keyrings/libcontainers-crio-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$CRIO_VERSION/$OS_VERSION/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$CRIO_VERSION.list
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg


apt update  -y
apt install -y cri-o cri-o-runc
apt install -y containernetworking-plugins
apt install -y cri-tools
apt install -y git iptables-persistent
apt install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl

sysctl  -p
swapoff -a # Выключаем swapoff

modprobe br_netfilter
modprobe overlay
lsmod | egrep "br_netfilter|overlay"

## sysctl --system ## Попробуем без него
iptables -I INPUT 1 -p tcp --match multiport --dports 6443,2379:2380,10250:10252 -j ACCEPT 
netfilter-persistent save



systemctl enable crio
systemctl start crio
crictl --runtime-endpoint unix:///var/run/crio/crio.sock version
systemctl enable kubelet
systemctl start kubelet
kubectl version --client --output=yaml
# Инициализирую мастер
kubeadm init
# Добавляю конфиг, что бы работал kubectl
# cp /etc/kubernetes/admin.conf /home/$HOME/.kube/config
# chown $(id -u):$(id -g) /home/$HOME/.kube/config
export KUBECONFIG=/etc/kubernetes/admin.conf