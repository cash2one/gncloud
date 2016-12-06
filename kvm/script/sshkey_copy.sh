#! /bin/bash
genisoimage -output /var/lib/libvirt/initcloud/config.iso -volid cidata -joliet -rock /var/lib/libvirt/initcloud/user-data /var/lib/libvirt/initcloud/meta-data