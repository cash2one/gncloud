# Docker 환경구성 (CentOS 기준)

1. 공통
2. Master
3. Slave

실행
docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock &

package 설치
pip install docker-py