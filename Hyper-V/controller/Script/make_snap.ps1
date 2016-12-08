$VMname=$args[0];
$CloneVMname=$args[1];
$vm= Get-VM $VMname;
$vmid = $vm.Name;
Export-VM -Name $VMname -Path C:\images\clone\;
Copy-Item C:\images\clone\$VMname\"Virtual Hard Disks"\*.vhdx -Destination C:\images\vhdx\$CloneVMname.vhdx;
#임시저장소삭제
Remove-Item -Path C:\images\clone -Recurse;