﻿$VMname=$args[0];
$CloneVMname=$args[1]; #시간정보만 보낸다
$vm= Get-VM $VMname;
$vmid = $vm.Name;
Export-VM -Name $VMname -Path C:\images\$VMname"clone"\;
Move-Item C:\images\$VMname"clone"\$VMname\"Virtual Hard Disks"\$VMname.vhdx -Destination C:\images\vhdx\$vmid$CloneVMname".vhdx";
#임시저장소삭제
Remove-Item -Path C:\images\$VMname"clone" -Recurse;
#Get-VHD -Path C:/images/vhdx/$vmid$CloneVMname".vhdx" | ConvertTo-Json;


#$VMname=$args[0];
#$CloneVMname=$args[1];
#$vm= Get-VM $VMname;
#$vmid = $vm.Name;
#Export-VM -Name $VMname -Path C:\images\$VMname"clone"\;
#Move-Item C:\images\clone\$VMname\"Virtual Hard Disks"\*.vhdx -Destination C:\images\vhdx\$CloneVMname.vhdx;
#임시저장소삭제 #copy 대신 파일 move 약 1/3 으로 스냅샷 생성 시간 단축
#Remove-Item -Path C:\images\clone -Recurse;