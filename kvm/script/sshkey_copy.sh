#! /bin/bash
genisoimage -output /data/kvm/initcloud/config.iso -volid cidata -joliet -rock /data/initcloud/user-data /var/lib/libvirt/initcloud/meta-data