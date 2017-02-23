all: git-pull gncloud-kvm gncloud-hyperv gncloud-docker gncloud-manager gncloud-scheduler gncloud-web

git-pull:
	cd /var/lib/gncloud; git pull

gncloud-kvm:
	cd /var/lib/gncloud/KVM; docker build -t gncloud/gncloud-kvm .

gncloud-hyperv:
	cd /var/lib/gncloud/HyperV; docker build -t gncloud/gncloud-hyperv .


gncloud-docker:
	cd /var/lib/gncloud/Docker; docker build -t gncloud/gncloud-docker .

gncloud-manager:
	cd /var/lib/gncloud/Manager; docker build -t gncloud/gncloud-manager .

gncloud-scheduler:
	cd /var/lib/gncloud/Scheduler; docker build -t gncloud/gncloud-scheduler .

gncloud-web:
	cd /var/lib/gncloud/Web; docker build -t gncloud/gncloud-web .

clean:
	docker rm gncloud/gncloud-kvm gncloud/gncloud-hyperv gncloud/gncloud-docker gncloud/gncloud-manager gncloud/gncloud-scheduler gncloud/gncloud-web


