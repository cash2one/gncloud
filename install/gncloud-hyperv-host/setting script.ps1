## host machine Setting Script

## HyperV 관리자 프로그램 추가
# 제어판 -> 프로그램 -> windows 기능 켜기/끄기 -> Hyper-V 체크 후 확인 -> 리부팅

## 관리자로 파워쉘 실행 후

Enable-PSRemoting
Enable-WSManCredSSP -Role server

# 가상스위치 생성 스크립트
$net = Get-NetAdapter -physical | where status -eq 'up';
New-VMSwitch -Name out -NetAdapterName $net.Name -AllowManagementOS $true -Notes 'Parent OS, VMs, LAN';
 
## 이미지저장 디렉토리 생성 스크립트
# NAS (SAN) 설정 시 C drive 대신 세팅된 NAS(SAN) 네트워크 드라이브(예: Z)로 설정
$image_path = "C:\images";
New-Item $image_path\vhdx\instance -ItemType directory;
#$image_path = "Z:\images";
New-Item $image_path\vhdx\base -ItemType directory;
New-Item $image_path\vhdx\snapshot -ItemType directory;
New-Item $image_path\vhdx\backup -ItemType directory;
New-Item $image_path\vhdx\manager -ItemType directory;
 
## agent 인바운드 허용
New-NetFirewallRule -DisplayName hypervagent -Direction Inbound -Action Allow -EdgeTraversalPolicy Allow -Protocol TCP -LocalPort 8180 

## Agent service 압축 풀기
Expand-Archive '.\Gncloud Hyper-V Agent.zip'
# hyper-v agent install script
.\"Gncloud Hyper-V Agent\Gncloud Hyper-V Agent"\setup.exe
# hyper-v agent를 관리자 계정 세팅 및 서비스 시작 하기


 
## 원격접속 허용 커맨드
(Get-WmiObject Win32_TerminalServiceSetting -Namespace root\cimv2\TerminalServices).SetAllowTsConnections(1,1) | Out-Null
(Get-WmiObject -Class "Win32_TSGeneralSetting" -Namespace root\cimv2\TerminalServices -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0) | Out-Null
Get-NetFirewallRule -DisplayName "Remote Desktop*" | Set-NetFirewallRule -enabled true
 
#Start-Service 
#$Username = "gncloud"
#$Password = "gnc=1151"
#$group = "Administrators"
#$adsi = [ADSI]"WinNT://$env:COMPUTERNAME"
#$existing = $adsi.Children | where {$_.SchemaClassName -eq 'user' -and $_.Name -eq $Username }
#if ($existing -eq $null) {
#    Write-Host "Creating new local user $Username."
#    & NET USER $Username $Password /add /y /expires:never
    
#    Write-Host "Adding local user $Username to $group."
#    & NET LOCALGROUP $group $Username /add
#}
#else {
#    Write-Host "Setting password for existing local user $Username."
#    $existing.SetPassword($Password)
#}

#Write-Host "Ensuring password for $Username never expires."
#& WMIC USERACCOUNT WHERE "Name='$Username'" SET PasswordExpires=FALSE


# windows 10 버전에는 이미 dotnet framework가 최신으로 설치되어 있어 불필요 함.
if([environment]::OSVersion.version.Major -gt 9 ) { return }

# dotnet install
Configuration Net452Install
{
    node "localhost"
    {
        LocalConfigurationManager
        {
            RebootNodeIfNeeded = $true
        }
        Script Install_Net_4.5.2
        {
            SetScript = {
                $SourceURI = "https://download.microsoft.com/download/F/9/4/F942F07D-F26F-4F30-B4E3-EBD54FABA377/NDP462-KB3151800-x86-x64-AllOS-ENU.exe"
                $FileName = $SourceURI.Split('/')[-1]
                $BinPath = Join-Path $env:SystemRoot -ChildPath "Temp\$FileName"
 
                if (!(Test-Path $BinPath))
                {
                    Invoke-Webrequest -Uri $SourceURI -OutFile $BinPath
                }
 
                write-verbose "Installing .Net 4.5.2 from $BinPath"
                write-verbose "Executing $binpath /q /norestart"
                Sleep 5
                Start-Process -FilePath $BinPath -ArgumentList "/q /norestart" -Wait -NoNewWindow            
                Sleep 5
                Write-Verbose "Setting DSCMachineStatus to reboot server after DSC run is completed"
                $global:DSCMachineStatus = 1
            }
 
            TestScript = {
                [int]$NetBuildVersion = 379893
 
                if (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full' | %{$_ -match 'Release'})
                {
                    [int]$CurrentRelease = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full').Release
                    if ($CurrentRelease -lt $NetBuildVersion)
                    { Write-Verbose "Current .Net build version is less than 4.5.2 ($CurrentRelease)"
                        return $false }
                    else
                    { Write-Verbose "Current .Net build version is the same as or higher than 4.5.2 ($CurrentRelease)"
                        return $true  }
                }
                else
                { Write-Verbose ".Net build version not recognised"
                    return $false     }
            }
            GetScript = {
                if (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full' | %{$_ -match 'Release'})
                {
                    $NetBuildVersion =  (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full').Release
                    return $NetBuildVersion
                }
                else
                { Write-Verbose ".Net build version not recognised"
                    return ".Net 4.5.2 not found"   }
            }
        }
    }
}
Net452Install -OutputPath $env:SystemDrive:\DSCconfig
Set-DscLocalConfigurationManager -ComputerName localhost -Path $env:SystemDrive\DSCconfig -Verbose
Start-DscConfiguration -ComputerName localhost -Path $env:SystemDrive:\DSCconfig -Verbose -Wait -Force