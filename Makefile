all: git-pull gncloud-kvm gncloud-hyperv gncloud-docker gncloud-manager gncloud-scheduler gncloud-web gncloud-mysql gncloud-registry

git-pull:
	git pull

gncloud-kvm:
	cd ./KVM; docker build -t gncloud/gncloud-kvm . ; cd ..  

gncloud-hyperv:
	cd ./HyperV; docker build -t gncloud/gncloud-hyperv . ; cd ..


gncloud-docker:
	cd ./Docker; docker build -t gncloud/gncloud-docker . ; cd ..

gncloud-manager:
	cd ./Manager; docker build -t gncloud/gncloud-manager . ; cd ..

gncloud-scheduler:
	cd ./Scheduler; docker build -t gncloud/gncloud-scheduler . ; cd ..

gncloud-web:
	cd ./Web; docker build -t gncloud/gncloud-web . ; cd ..

gncloud-mysql:
	docker pull mysql
	docker tag mysql gncloud/gncloud-mysql

gncloud-registry:
	docker pull registry
	docker tag registry gncloud/gncloud-registry

clean:
	docker rm gncloud_kvm_1 gncloud_hyperv_1 gncloud_docker_1 gncloud_manager_1 gncloud_scheduler_1 gncloud_web_1


