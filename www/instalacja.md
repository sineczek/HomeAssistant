
# Instalacja (dla siebie, potomnych i tych, dla których może to być pomocne)
-------------------------------
> pod $USER$ należy podstawić swój login

1. Instalacja Ubuntu Server (bez dodatkowych pakietów)
	- sudo apt-get update
	- sudo apt-get upgrade
	- sudo reboot

2. Instalacja dockera
	- sudo curl https://releases.rancher.com/install-docker/19.03.sh | sh
	- sudo usermod -aG docker $USER$ 
    > aby można było odpalać dockera bez sudo

	- docker version (sprawdzenie czy działa)

3. Instalacja Kubernetes ( https://microk8s.io/ )       - można pominąć
	- sudo snap install microk8s --channel=1.19 --classic
    - sudo usermod -a -G microk8s $USER$ 
                                        lub sudo chown -f -R $USER% ~/.kube
	- sudo reboot

4. Instalacja Home Assistant
	- sudo -i
	- add-apt-repository universe
	- apt-get update
	- apt-get install -y apparmor-utils apt-transport-https avahi-daemon ca-certificates curl dbus jq network-manager socat software-properties-common
	- curl -sSL https://get.docker.com | sh
	-  docker run -d   --name homeassistant   --privileged   --restart=unless-stopped   -e TZ=Europe/Warsaw   -v /usr/share/hassio:/config   --network=host   ghcr.io/home-assistant/home-assistant:stable
	- deprecated: curl -sL "https://raw.githubusercontent.com/home-assistant/supervised-installer/master/installer.sh" | bash -s

5. Pi-Hole
	- curl -sSL https://install.pi-hole.net | bash

6. VSCode
	- sudo docker run -itd --net=host --name=vscode --user 1000:1000 --restart=always -e PASSWORD=TajneHaslo123 -v /home/sinq/vscode:/home/coder/.local/share/code-server -v /usr/share/hassio/homeassistant/:/home/coder/project codercom/code-server

    > należy sprawdzić czy nie będą się porty pokrywać, VSCode dostępny jest pod portem: 8080

7. Pełny backup VM

8. Instalacja Mosquitto MQTT Broker as a service
	- sudo apt-get install mosquitto
	- sudo mosquitto_passwd -c /etc/mosquitto/passwd $USER$
	  Password: password
	- sudo nano /etc/mosquitto/conf.d/default.conf
		allow_anonymous false
		password_file /etc/mosquitto/passwd
	- sudo systemctl restart mosquitto

-------------------------------
## za duże obciążenie dla NASa

1. Instalacja Ubuntu Server (bez dodatkowych pakietów)
	- sudo apt-get update
	- sudo apt-get upgrade
	- sudo reboot

2. Instalacja dockera
	- sudo curl https://releases.rancher.com/install-docker/19.03.sh | sh
	- sudo usermod -aG docker $USER$ (aby można było odpalać dockera bez sudo)
	- docker version (sprawdzenie czy działa)

3. Instalacja Ranchera
	- docker run -d --restart=unless-stopped -p 80:80 -p 443:443 -v /opt/rancher:/var/rancher rancher/rancher:latest
	- docker ps (sprawdzamy czy działa)
	- wchodzimy na www <IP serwera> i postępujemy zgodnie z instrukcjami
	- aktywujemy DarkMode -> Preferences
	- tworzymy cluster -> Add Cluster
		- From existing nodes (Custom)
		- nazywamy cluster
		- OK
		- Node Options zaznaczamy etcd | Control Plane | Worker oraz kopiujemy polecenie tworzące Kubernetes

4. Instalacja Kubernetes
	instalujemy z CLI poprzez wykonanie skopiowanego polecenia
		sudo docker run -d --privileged --restart=unless-stopped \
		--net=host -v /etc/kubernetes:/etc/kubernetes \
		-v /var/run:/var/run rancher/rancher-agent:v2.4.8 \
		--server https://192.168.x.x \
		--token xxxxxxxxxxxxxxxxxxxxxxxxxx \
		--ca-checksum xxxxxxxxxxxxxxxxxxxxxxxxx \
		--etcd --controlplane --worker

	!!! cały proces może trochę potrwać !!!

5. Instalacja Pi-Hole ( https://www.youtube.com/watch?v=NRe2-vye3ik )
	- najpierw istalacja resolvconf'a
		sudo nano /etc/resolv.conf (sprawdzamy czy jest nameserver dodany)
   		sudo apt install resolvconf
		sudo systemctl status resolvconf.service
		sudo systemctl enable resolvconf.service
		sudo nano /etc/resolvconf/resolv.conf.d/head
			- dopisujemy nameserver 9.9.9.9

		sudo systemctl stop resolvconf.service
		sudo systemctl start resolvconf.service
		sudo systemctl status resolvconf.service
		sudo reboot
		sudo nano /etc/resolv.conf (sprawdzamy czy został nameserver dodany)

	- tworzymy obraz pi-hola w Kubernetes (w Rancher Global - cluster - Default - Deploy)
		- nazwa: pihole
		- docker image: pihole/pihole:latest
		- port mapping:
			dns-tcp		53	TCP	Host Port 	53
			dns-udp		53	UDP	Host Port 	53		
			pihole-http	80	TCP	Host Port 	8001
		- enviroment variables: 
			TZ = Europe/Warsaw
			DNS1 = 9.9.9.9
			DNS2 = 1.1.1.1
			ServerIP = 192.168.x.x
		- ADD Volume --> Bind-mount a directory deom the node
			Volume Name		Path to the Node			Mount Place
			/etc-pihole/ 		/home/$USER$/pihole/etc-pihole/		/etc/pihole/
			pihole-dnsmasq.d 	/home/$USER$/pihole/etc-dnsmasq.d/	/etc/dnsmasq.d/
		- Scaling/Upgrade Policy
			Kill ALL pods then start new
		
		Advance options
		- Networking
			Add Name Server		127.0.0.1
			Add Name Sever		9.9.9.9
		DEPLOY!

		- hasło randomowe można sprawdzić w logach
		- zmiana hasła na własne poprzez CLI Dockera
		- aby poprawnie widziało status Pi-Hola:
			Edit node
				- Advance options
					- Security & Host Config
						- Privelage Escalation: Yes

6. Instalacja Home-Assistant
    > niestety NAS i VM już klękał z bólu i tego kroku nie wykonałem

