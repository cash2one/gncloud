## 네트워크 개인으로 설정하는 script  시작 -> 설정 -> 네트워크 및 인터넷 -> 이더넷 -> 홈 그룹 -> 네트워크 변경
# Skip network location setting if local machine is joined to a domain. 
if(1,3,4,5 -contains (Get-WmiObject win32_computersystem).DomainRole) { return }
## Get network connections 
$networkListManager = [Activator]::CreateInstance([Type]::GetTypeFromCLSID([Guid]"{DCB00C01-570F-4A9B-8D69-199FDBA5723B}")) ;
$connections = $networkListManager.GetNetworkConnections();
## Set network location to Private for all networks 
$connections | % {$_.GetNetwork().SetCategory(1)};
