#! /bin/bash
genisoimage -output /data/kvm/scripts/initcloud/config.iso -volid cidata -joliet -rock /data/kvm/scripts/initcloud/user-data /data/kvm/scripts/initcloud/meta-data