#! /bin/bash
path=$1
rm -f $path/default*
rm -f $path/user-data
ssh-keygen -f $path/default -N ''
cp $path/base_user-data $path/user-data
echo '-' `cat $path/default.pub` >> $path/user-data
genisoimage -output $path/config.iso -volid cidata -joliet -rock $path/user-data $path/meta-data