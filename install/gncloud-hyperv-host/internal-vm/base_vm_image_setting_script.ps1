################# vm base image setting ##############

# windows server 2012 버전 미만 혹은 windows 10 버전 미만은 베이스 이미지로 하지 않음
if([environment]::OSVersion.version.Major -lt 6) { return }

## 방화벽 해제 커맨드
netsh advfirewall set allprofiles state off;

## 데스크탑 원격접속 허용 커맨드
(Get-WmiObject Win32_TerminalServiceSetting -Namespace root\cimv2\TerminalServices).SetAllowTsConnections(1,1) | Out-Null
(Get-WmiObject -Class "Win32_TSGeneralSetting" -Namespace root\cimv2\TerminalServices -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0) | Out-Null
Get-NetFirewallRule -DisplayName "Remote Desktop*" | Set-NetFirewallRule -enabled true;

## powershell 포트 inbound 허용 규칙 세팅
New-NetFirewallRule -DisplayName psremote -Direction Inbound -Action Allow -EdgeTraversalPolicy Allow -Protocol TCP -LocalPort 5985, 5986;

## inbound rule remove : 실제 vm 띄우고 나서 다 닫을 때 필요
#   Remove-NetFirewallRule -DisplayName psremote;

## 스크립트가 Windows PowerShell에서 실행될 수 있도록 설정
Set-ExecutionPolicy RemoteSigned -Force;

powershell ./set_personal_network_setting.ps1
## powserShell 접근 가능하도록 설정
Enable-PSRemoting -Force;

## windows OS 이름 얻는 방법
# Get-CIMInstance -ClassName Win32_OperatingSystem -Property * | select caption | ConvertTo-Json

## Create admin user  ##windows 2012 server version만 실행됨
if([environment]::OSVersion.version.Major -eq 6) 
  $Username = "gncloud"
  $Password = "gnc=1151"
  $group = "Administrators"
  $adsi = [ADSI]"WinNT://$env:COMPUTERNAME"
  $existing = $adsi.Children | where {$_.SchemaClassName -eq 'user' -and $_.Name -eq $Username }
  if ($existing -eq $null) {
      Write-Host "Creating new local user $Username."
      & NET USER $Username $Password /add /y /expires:never
      
      Write-Host "Adding local user $Username to $group."
      & NET LOCALGROUP $group $Username /add
  }
  else {
      Write-Host "Setting password for existing local user $Username."
      $existing.SetPassword($Password)
  }
  Write-Host "Ensuring password for $Username never expires."
  & WMIC USERACCOUNT WHERE "Name='$Username'" SET PasswordExpires=FALSE
}

