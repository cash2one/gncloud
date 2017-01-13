#!/bin/bash
genisoimage -output /data/kvm/initcloud/config.iso -volid cidata -joliet -rock /data/kvm/initcloud/user-data /data/kvm/initcloud/meta-data

