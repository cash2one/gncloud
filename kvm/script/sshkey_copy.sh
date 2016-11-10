#! /bin/bash
rm -f default*;
rm -f user-data;
ssh-keygen -f default -N '';
cp base_user-data user-data;
echo '-' `cat ./default.pub` >> ./user-data;
genisoimage -output config.iso -volid cidata -joliet -rock user-data meta-data