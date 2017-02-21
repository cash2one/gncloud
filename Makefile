# Tobe

all: kvm hyperv docker manager scheduler

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

clean:
	docker rmi kvm-controller hyperv-controller docker-controller manager-controller scheduler

