# Tobe

all: git-pull kvm hyperv docker manager scheduler web-front

git-pull:
	cd /var/lib/gncloud; git pull

kvm:
	cd /var/lib/gncloud/KVM; docker build -t kvm-controller .

hyperv:
	cd /var/lib/gncloud/HyperV; docker build -t hyperv-controller .


docker:
	cd /var/lib/gncloud/Docker; docker build -t docker-controller .

manager:
	cd /var/lib/gncloud/Manager; docker build -t manager-controller .

scheduler:
	cd /var/lib/gncloud/Scheduler; docker build -t scheduler .

web-front:
	cd /var/lib/gncloud/Web; docker build -t web-front .

clean:
	docker rmi kvm-controller hyperv-controller docker-controller manager-controller scheduler web-front

