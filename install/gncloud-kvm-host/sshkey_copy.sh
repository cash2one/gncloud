#!/bin/bash

# "/data" is SAN mount position
mkdir -p /data/kvm
# genisoimage -output /data/kvm/initcloud/config.iso -volid cidata -joliet -rock /data/kvm/initcloud/user-data /data/kvm/initcloud/meta-data
genisoimage -output /var/lib/libvirt/initcloud/config.iso -volid cidata -joliet -rock /var/lib/libvirt/initcloud/user-data /var/lib/libvirt/initcloud/meta-data
