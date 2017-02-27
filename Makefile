KVM_DEP=./KVM/db ./KVM/SERVICE ./KVM/script ./KVM/templates ./KVM/util ./KVM/__init__.py

all: git-pull kvm hyperv docker manager scheduler web mysql registry

git-pull:
	git pull
	chmod +x *.sh
	docker-compose down
kvm:
	docker rmi gncloud/gncloud-kvm
	cd ./KVM; docker build -t gncloud/gncloud-kvm . ; cd ..  

hyperv:
	docker rmi gncloud/gncloud-hyperv
	cd ./HyperV; docker build -t gncloud/gncloud-hyperv . ; cd ..

docker: 
	docker rmi gncloud/gncloud-docker
	cd ./Docker; docker build -t gncloud/gncloud-docker . ; cd ..

manager:
	docker rmi gncloud/gncloud-manager
	cd ./Manager; docker build -t gncloud/gncloud-manager . ; cd ..

scheduler:
	docker rmi gncloud/gncloud-scheduler
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
	docker rm gncloud_kvm_1 gncloud_hyperv_1 gncloud_docker_1 gncloud_manager_1 gncloud_scheduler_1 gncloud_web_1

