all: git-pull kvm hyperv docker manager scheduler web

git-pull:
	cd /var/lib/gncloud; git pull

kvm:
	docker build -t gncloud/gncloud-kvm /var/lib/gncloud/KVM

hyperv:
	docker build -t gncloud/gncloud-hyperv /var/lib/gncloud/HyperV


docker:
	docker build -t gncloud/gncloud-docker /var/lib/gncloud/Docker

manager:
	docker build -t gncloud/gncloud-manager /var/lib/gncloud/Manager

scheduler:
	docker build -t gncloud/gncloud-scheduler /var/lib/gncloud/Scheduler

web:
	docker build -t gncloud/gncloud-web /var/lib/gncloud/Web

clean:
	docker rm gncloud/gncloud-kvm gncloud/gncloud-hyperv gncloud/gncloud-docker gncloud/gncloud-manager gncloud/gncloud-scheduler gncloud/gncloud-web


