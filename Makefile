all: git-pull gncloud-kvm gncloud-hyperv gncloud-docker gncloud-manager gncloud-scheduler gncloud-web

git-pull:
	cd /var/lib/gncloud; git pull

gncloud-kvm:
	docker build -t gncloud/gncloud-kvm /var/lib/gncloud/KVM

gncloud-hyperv:
	docker build -t gncloud/gncloud-hyperv /var/lib/gncloud/HyperV


gncloud-docker:
	docker build -t gncloud/gncloud-docker /var/lib/gncloud/Docker

gncloud-manager:
	docker build -t gncloud/gncloud-manager /var/lib/gncloud/Manager

gncloud-scheduler:
	docker build -t gncloud/gncloud-scheduler /var/lib/gncloud/Scheduler

gncloud-web:
	docker build -t gncloud/gncloud-web /var/lib/gncloud/Web

clean:
	docker rm gncloud/gncloud-kvm gncloud/gncloud-hyperv gncloud/gncloud-docker gncloud/gncloud-manager gncloud/gncloud-scheduler gncloud/gncloud-web


