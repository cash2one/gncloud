# gncloud private Hyper-V HOST 설치
# gncloud hyperv install
1. 설치 절차
2. gncloud platform hyperv 설치
3. setting script.ps1 내용

<span></span>
1. 설치 절차
------------
- HyperV 사전 작업
    - Administrator 권한획득
    - HyperV 관리자 프로그램 추가
        * 제어판 -> 프로그램 -> windows 기능 켜기/끄기 -> Hyper-V 체크 후 확인 -> 리부팅
    - gncloud-install.tgz를 설치할 HOST (H/W)에 복사
    - windows zip 프로그램을 이용하여 압축 풀기

<span></span>
2. setting script.ps1 실행
--------------------------------------
- 관리자권한으로 powershell 을 실행
    - powershell에서 압푹이 풀린 폴더 중 gncloud-hyperv-host 로 이동
    - cd ./gncloud-hyperv-host
    - powershell "setting script.ps1" 실행

<span></span>
3. setting script.ps1 내용
--------------------------------------
- 가상스위치 생성
    ```
    $net = Get-NetAdapter -physical | where status -eq 'up';
    New-VMSwitch -Name out -NetAdapterName $net.Name -AllowManagementOS $true -Notes 'Parent OS, VMs, LAN';
    ```
- 이미지저장 디렉토리 생성 스크립트 
    * NAS (SAN) 설정 시 C drive 대신 세팅된 NAS(SAN) 네트워크 드라이브(예: Z)로 설정
    ```
    $image_path = "C:\images";
    New-Item $image_path\vhdx\original -ItemType directory;
    New-Item $image_path\vhdx\base -ItemType directory;
    New-Item $image_path\vhdx\snap -ItemType directory;
    New-Item $image_path\vhdx\backup -ItemType directory;
    ```
- gncloud platform Anget 인바운드 허용
    ```
    New-NetFirewallRule -DisplayName hypervagent -Direction Inbound -Action Allow -EdgeTraversalPolicy Allow -Protocol TCP -LocalPort 8180 
    ```
- Agent service 압축 풀기
    ```
    Expand-Archive '.\Gncloud Hyper-V Agent.zip'
    # hyper-v agent install script
    .\"Gncloud Hyper-V Agent\Gncloud Hyper-V Agent"\setup.exe
    ```
- hyper-v agent를 관리자 계정 세팅 및 서비스 시작 하기
    ```
    1 . Win + R
    2 . services.msc 입력후 Enter 
    3 . Gncloud Hyper-V Agent Service 항목을 더블클릭
    4 . 로그온탭 선택
    5 . 계정 지정 라디오 버튼 선택
        Admin권한의 계정입력
        암호입력
        적용 버튼 클릭
        확인 버튼 클릭
        - 계정이름을 모를경우
          찾아보기 클릭 or Alt + B
          고급버튼 클릭 or Alt + A
          지금찾기 클릭 or Alt + N
          검색결과의 계정명 선택 (Admin의 권한을 가지고 있는 계정선택)
          확인버튼 클릭
          선택한 계정의 비밀번호 입력
          적용 버튼 클릭
          확인 버튼 클릭
    6 . 절차 완료후
        Gncloud Hyper-V Agent Service 서비스 중지 후 다시 시작
    ```
- 원격접속 허용 커맨드
    ```
    (Get-WmiObject Win32_TerminalServiceSetting -Namespace root\cimv2\TerminalServices).SetAllowTsConnections(1,1) | Out-Null
    (Get-WmiObject -Class "Win32_TSGeneralSetting" -Namespace root\cimv2\TerminalServices -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0) | Out-Null
    Get-NetFirewallRule -DisplayName "Remote Desktop*" | Set-NetFirewallRule -enabled true
    ```
 
- windows 10 버전에는 이미 dotnet framework가 최신으로 설치되어 있어 불필요하나 windows server 2012는 필요 함 
    ```
    if([environment]::OSVersion.version.Major -gt 9 ) { return }
    # dotnet install
    .\NDP461-KB3102436-x86-x64-AllOS-ENU.exe
    ```

