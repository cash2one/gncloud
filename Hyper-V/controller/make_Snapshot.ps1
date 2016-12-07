################인자값 넘겨줄시 VMName 혹은 ID 값으로 넘겨준다
Import-Module Hyper-V;
$Server = $env:COMPUTERNAME;
$VMName= "Windows10";
$SnapName= "$VMName Clone";
$ExportPath = "C:\images\Windows10";
$snapshot = Checkpoint-VM -Name $VMName -SnapshotName $SnapName -ComputerName $Server ?passthru
$export = Export-VMSnapshot -VMSnapshot $snapshot -Path $ExportPath ?Passthru
$clone = New-VM -Name $snapshot.Name -NoVHD -MemoryStartupBytes $snapshot.MemoryStartup  -ComputerName $Server
ForEach ($drive in $Snapshot.HardDrives) {
$VHD = Split-Path -leaf ($drive.path)
$VHDPath = Join-Path (Join-Path (Join-Path $ExportPath $VMName) "Virtual Hard Disks") $VHD
$addDriveHash=@{
		VMName=$Clone.Name
		Path=$VHDPath
		ControllerType=$drive.ControllerType
		ControllerNumber=$drive.ControllerNumber
		ControllerLocation=$drive.ControllerLocation
		Computername=$Server
	}
	Add-VMHardDiskDrive @addDriveHash
}
$paramhash=@{
	MemoryStartupBytes=$snapshot.MemoryStartup
	ProcessorCount=$snapshot.ProcessorCount
	Notes="Cloned $(Get-Date)"
	Name=$($clone.Name)
	Computername=$Server
	}
if ($snapshot.DynamicMemoryEnabled) {
$paramhash.Add("DynamicMemory",$snapshot.DynamicMemoryEnabled)
$paramhash.Add("MemoryMinimumBytes",$snapshot.MemoryMinimum)
$paramhash.Add("MemoryMaximumBytes",$snapshot.MemoryMaximum)
}
Set-VM @paramhash
#############################get 적용상태 받기.. 필요시 호출하는형태로 
Get-VM $clone.name -ComputerName $Server





###########################적용부분?
$VMPath = Join-Path (Join-Path $ExportPath $VMName) "Virtual Machines"
$VMConfigPath = (dir $vmpath -filter *.xml).FullName
[xml]$config = Get-Content -Path $VMConfigPath
#########################clone id 설정부분 txt 파일을 불러와서 값 변경, 값 수정은 생성id값으로 지정한다
$config.configuration.properties.name.'#text'="My Cloned VM"
$config.Save($VMConfigPath);
Import-VM -Path $VMConfigPath ?Register;
$VHDPath = (Join-Path (Join-Path $ExportPath $VMName) "Virtual Hard Disks");
Import-VM -Path $VMConfigPath -Copy -GenerateNewId -VhdDestinationPath $VHDPath -ComputerName $server;





#<과정 종료후 #text 값으로 클론생성> 
#생성시 임시버퍼처럼 생성되는 VM 이 있음 삭제해야함
