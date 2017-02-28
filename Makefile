all:
	git pull
	chmod +x *.sh
	docker-compose down
	cd ./KVM; docker build -t gncloud/gncloud-kvm . ; cd ..  
	cd ./HyperV; docker build -t gncloud/gncloud-hyperv . ; cd ..
	cd ./Docker; docker build -t gncloud/gncloud-docker . ; cd ..
	cd ./Manager; docker build -t gncloud/gncloud-manager . ; cd ..
	cd ./Scheduler; docker build -t gncloud/gncloud-scheduler . ; cd ..
	cd ./Web; docker build -t gncloud/gncloud-web . ; cd ..
	docker pull mysql
	docker tag mysql gncloud/gncloud-mysql
	docker pull registry
	docker tag registry gncloud/gncloud-registry

kvm:
	cd ./KVM; docker build -t gncloud/gncloud-kvm . ; cd ..
hyperv:
	cd ./HyperV; docker build -t gncloud/gncloud-hyperv . ; cd ..
docker:
	cd ./Docker; docker build -t gncloud/gncloud-docker . ; cd ..
manager:
	cd ./Manager; docker build -t gncloud/gncloud-manager . ; cd ..
schduler:
	cd ./Scheduler; docker build -t gncloud/gncloud-scheduler . ; cd ..
web:
	cd ./Web; docker build -t gncloud/gncloud-web . ; cd ..
mysql:
	docker pull mysql
	docker tag mysql gncloud/gncloud-mysql
registry:
	docker pull registry
	docker tag registry gncloud/gncloud-registry
clean:
	docker rmi gncloud/gncloud-kvm gncloud/gncloud-hyperv gncloud/gncloud-docker gncloud/gncloud-manager
	docker rmi gncloud/gncloud-scheduler gncloud/gncloud-web gncloud/gncloud-mysql gncloud/gncloud-registry

