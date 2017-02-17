# Gncloud private platform install shell

1. Database
2. ssh key copy


<span></span>
1. Database
-------------

- Cluster Manager

    - docker

    ```
    Node Name : manager, registry
    ```

<span></span>
2. ssh key copy
-------------

- copy gncloud platform host to kvm, docker manager, docker workers, docker registry


    ```
    $ ssh-copy-id -i ~/.ssh/id_rsa root@[IP]
    ```
