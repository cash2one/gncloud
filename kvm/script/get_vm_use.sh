ip=$2
if [ $1 = "cpu" ]; then
 ssh -i /var/lib/libvirt/sshkeys/default centos@${ip}  top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'
elif [ $1 = "mem" ]; then
 ssh -i /var/lib/libvirt/sshkeys/default centos@${ip} free | grep Mem | awk '{ print(100 - ($4/$2 * 100.0)) }'

fi