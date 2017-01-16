connect gncloud;
CREATE TABLE `GN_CLUSTER` (
	`id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(50) NULL DEFAULT NULL,
	`ip` VARCHAR(20) NULL DEFAULT NULL,
	`port` INT(5) NULL DEFAULT NULL,
	`type` VARCHAR(10) NULL DEFAULT NULL COMMENT 'kvm, hyperv, docker',
	`swarm_join` VARCHAR(200) NULL DEFAULT NULL,
	`create_time` TIMESTAMP NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT;

CREATE TABLE `GN_DOCKER_CONTAINERS` (
	`service_id` VARCHAR(8) NOT NULL DEFAULT '',
	`internal_id` VARCHAR(100) NOT NULL DEFAULT '',
	`internal_name` VARCHAR(100) NOT NULL DEFAULT '',
	`host_id` VARCHAR(8) NOT NULL,
	`status` VARCHAR(10) NULL DEFAULT NULL,
	PRIMARY KEY (`service_id`, `internal_id`, `internal_name`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_DOCKER_IMAGES` (
	`id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(200) NOT NULL DEFAULT '' COMMENT '전제현 주임 >> RepoTags를 여기에 넣으면 될 것 같',
	`view_name` VARCHAR(200) NULL DEFAULT '',
	`tag` VARCHAR(200) NULL DEFAULT NULL,
	`os` VARCHAR(50) NULL DEFAULT NULL,
	`os_ver` VARCHAR(45) NULL DEFAULT NULL,
	`sub_type` VARCHAR(10) NOT NULL DEFAULT '' COMMENT '예) win_10_pro_64.vhdx\\n전제현 주임 >> docker에서는 필요없어 보인',
	`team_code` VARCHAR(10) NULL DEFAULT NULL,
	`author_id` VARCHAR(15) NULL DEFAULT NULL,
	`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`status` VARCHAR(10) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
;

CREATE TABLE `GN_DOCKER_IMAGES_DETAIL` (
	`id` VARCHAR(8) NOT NULL,
	`image_id` VARCHAR(8) NOT NULL DEFAULT '',
	`arg_type` VARCHAR(10) NOT NULL DEFAULT '' COMMENT 'path, port, initial',
	`argument` VARCHAR(200) NOT NULL DEFAULT '',
	`description` VARCHAR(300) NULL DEFAULT '',
	`status` VARCHAR(10) NULL DEFAULT NULL,
	PRIMARY KEY (`image_id`, `id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT;

CREATE TABLE `GN_DOCKER_PORTS` (
	`service_id` VARCHAR(8) NOT NULL,
	`protocol` VARCHAR(10) NOT NULL,
	`target_port` VARCHAR(5) NOT NULL DEFAULT '',
	`published_port` VARCHAR(5) NOT NULL DEFAULT '',
	PRIMARY KEY (`service_id`, `target_port`, `published_port`, `protocol`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_DOCKER_SERVICES` (
	`service_id` VARCHAR(8) NOT NULL DEFAULT '',
	`image` VARCHAR(100) NULL DEFAULT NULL,
	PRIMARY KEY (`service_id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT;

CREATE TABLE `GN_DOCKER_VOLUMES` (
	`service_id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(200) NOT NULL DEFAULT '',
	`source_path` VARCHAR(200) NOT NULL DEFAULT '',
	`destination_path` VARCHAR(200) NOT NULL DEFAULT '',
	`status` VARCHAR(10) NULL DEFAULT NULL,
	PRIMARY KEY (`service_id`, `name`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_HOST_DOCKER` (
	`id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(100) NULL DEFAULT '',
	`ip` VARCHAR(50) NULL DEFAULT '',
	`type` VARCHAR(10) NULL DEFAULT '' COMMENT 'manager, worker, registry',
	`cpu` INT(2) UNSIGNED NULL DEFAULT NULL COMMENT '실제 cpu 코어 갯수',
	`mem` INT(7) UNSIGNED NULL DEFAULT NULL COMMENT '실제 메모리 용량, MB 단위',
	`disk` INT(10) UNSIGNED NULL DEFAULT NULL COMMENT '실제 HDD, SSD 등 GB 단위',
	`max_cpu` INT(11) UNSIGNED NULL DEFAULT NULL COMMENT '할당 가능한 최대 갯수 (예, 실제 4 코어 4코어짜리 VM 2개 = 8개 할당. max 할당 이 필요함)',
	`max_mem` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT '할당 가능한 최대 메모리 (실제 운영에 필요한 용량은 남겨 두고 할당 해야 함. 16GB 인데 4GB VM을 4개 할당 하면 HOST가 제대로 동작 하지 않을 수 있음',
	`max_disk` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT 'SAN(NAS) 마운트로 실제 설치된 disk 보다 많이 할당 가능하나 SAN 용량을 넘을수는 없음.',
	`host_agent_port` INT(5) UNSIGNED NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT;

CREATE TABLE `GN_HOST_MACHINES` (
	`id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(100) NULL DEFAULT '',
	`ip` VARCHAR(50) NULL DEFAULT '',
	`type` VARCHAR(10) NULL DEFAULT '' COMMENT 'kvm, hyperv, docker',
	`cpu` INT(2) UNSIGNED NULL DEFAULT NULL COMMENT '실제 cpu 코어 갯수',
	`mem` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT '실제 메모리 용량, MB 단위',
	`disk` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT '실제 HDD, SSD 등 GB 단위',
	`max_cpu` INT(11) UNSIGNED NULL DEFAULT NULL COMMENT '할당 가능한 최대 갯수 (예, 실제 4 코어 4코어짜리 VM 2개 = 8개 할당. max 할당 이 필요함)',
	`max_mem` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT '할당 가능한 최대 메모리 (실제 운영에 필요한 용량은 남겨 두고 할당 해야 함. 16GB 인데 4GB VM을 4개 할당 하면 HOST가 제대로 동작 하지 않을 수 있음',
	`max_disk` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT 'SAN(NAS) 마운트로 실제 설치된 disk 보다 많이 할당 가능하나 SAN 용량을 넘을수는 없음.',
	`host_agent_port` INT(5) UNSIGNED NULL DEFAULT NULL,
	`image_path` VARCHAR(200) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_ID` (
	`id` VARCHAR(8) NOT NULL,
	`type` VARCHAR(20) NOT NULL COMMENT 'host, kvm, hyperv, docker, controller, kvm_image, hyperv_image, docker_image',
	`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_IMAGES_POOL` (
	`id` VARCHAR(8) NOT NULL,
	`type` VARCHAR(10) NULL DEFAULT NULL COMMENT 'kvm, hyperv',
	`image_path` VARCHAR(200) NULL DEFAULT NULL COMMENT '/{nework} on mount/{host_id}/image/kvm',
	`host_id` VARCHAR(8) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_MONITOR` (
	`id` VARCHAR(8) NOT NULL,
	`type` VARCHAR(6) NOT NULL COMMENT 'host, hyperv, kvm, docker',
	`cpu_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL COMMENT '% 단위',
	`mem_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL,
	`disk_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL,
	`net_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL,
	PRIMARY KEY (`id`, `type`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT;

CREATE TABLE `GN_MONITOR_HIST` (
	`id` VARCHAR(8) NOT NULL,
	`type` VARCHAR(6) NOT NULL COMMENT 'host, hyperv, kvm, docker',
	`cur_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`cpu_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL COMMENT '% 단위',
	`mem_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL,
	`disk_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL,
	`net_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL,
	`seq` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (`seq`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
AUTO_INCREMENT=2339;

CREATE TABLE `GN_SSH_KEYS` (
	`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`team_code` VARCHAR(50) NOT NULL DEFAULT '',
	`name` VARCHAR(100) NOT NULL DEFAULT '',
	`fingerprint` VARCHAR(50) NULL DEFAULT NULL,
	`download_yn` VARCHAR(1) NOT NULL DEFAULT 'N',
	`create_time` TIMESTAMP NULL DEFAULT NULL,
	`path` VARCHAR(100) NOT NULL DEFAULT '',
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
AUTO_INCREMENT=1231313226;

CREATE TABLE `GN_SSH_KEYS_MAPPING` (
	`ssh_key_id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`vm_id` VARCHAR(8) NULL DEFAULT NULL,
	PRIMARY KEY (`ssh_key_id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_TEAM` (
	`team_code` VARCHAR(10) NOT NULL,
	`team_name` VARCHAR(50) NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NULL DEFAULT NULL,
	`cpu_quota` INT(11) UNSIGNED NOT NULL DEFAULT '30',
	`mem_quota` BIGINT(20) UNSIGNED NOT NULL DEFAULT '20000',
	`disk_quota` BIGINT(20) UNSIGNED NOT NULL DEFAULT '100',
	`create_date` TIMESTAMP NULL DEFAULT NULL,
	PRIMARY KEY (`team_code`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_TEAM_HIST` (
	`team_code` VARCHAR(10) NOT NULL,
	`team_del_code` VARCHAR(8) NOT NULL,
	`team_name` VARCHAR(50) NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NULL DEFAULT NULL,
	`cpu_quota` INT(11) UNSIGNED NOT NULL DEFAULT '30',
	`mem_quota` INT(11) UNSIGNED NOT NULL DEFAULT '20000',
	`disk_quota` INT(11) UNSIGNED NOT NULL DEFAULT '100',
	`delete_date` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`team_code`, `team_del_code`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT;

CREATE TABLE `GN_USERS` (
	`user_id` VARCHAR(50) NOT NULL,
	`password` VARCHAR(50) NULL DEFAULT '' COLLATE 'utf8mb4_general_ci',
	`user_name` VARCHAR(20) NOT NULL DEFAULT '',
	`privilege` VARCHAR(4) NULL DEFAULT NULL COMMENT 'root, mgr, user',
	`tel` VARCHAR(20) NULL DEFAULT '-',
	`email` VARCHAR(40) NULL DEFAULT '-',
	`start_date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`end_date` TIMESTAMP NULL DEFAULT NULL,
	PRIMARY KEY (`user_id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_USER_TEAMS` (
	`user_id` VARCHAR(50) NOT NULL,
	`team_code` VARCHAR(10) NOT NULL,
	`comfirm` VARCHAR(1) NULL DEFAULT 'N' COMMENT 'Y,N 팀장 승인이 된 팀은 Y, 대기중인것은 N',
	`apply_date` TIMESTAMP NULL DEFAULT NULL,
	`approve_date` TIMESTAMP NULL DEFAULT NULL,
	`team_owner` VARCHAR(10) NOT NULL DEFAULT 'user' COMMENT 'owner or user',
	PRIMARY KEY (`user_id`, `team_code`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_USER_TEAMS_HIST` (
	`user_id` VARCHAR(50) NOT NULL,
	`team_code` VARCHAR(10) NOT NULL,
	`team_del_code` VARCHAR(8) NOT NULL,
	`comfirm` VARCHAR(1) NULL DEFAULT 'N' COMMENT 'Y,N 팀장 승인이 된 팀은 Y, 대기중인것은 N',
	`apply_date` TIMESTAMP NULL DEFAULT NULL,
	`approve_date` TIMESTAMP NULL DEFAULT NULL,
	`team_owner` VARCHAR(10) NOT NULL DEFAULT 'user' COMMENT 'owner or user',
	`delete_date` TIMESTAMP NULL DEFAULT NULL,
	PRIMARY KEY (`user_id`, `team_code`, `team_del_code`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT;

CREATE TABLE `GN_VM_IMAGES` (
	`id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(50) NOT NULL DEFAULT '',
	`filename` VARCHAR(100) NULL DEFAULT '' COMMENT '예) win_10_pro_64.vhdx',
	`type` VARCHAR(10) NOT NULL DEFAULT '' COMMENT '종류: kvm, hyperv ',
	`sub_type` VARCHAR(10) NOT NULL DEFAULT '' COMMENT '종류: base, snap',
	`icon` VARCHAR(100) NULL DEFAULT NULL COMMENT 'icon image path & name',
	`os` VARCHAR(10) NULL DEFAULT NULL,
	`os_ver` VARCHAR(20) NULL DEFAULT NULL,
	`os_subver` VARCHAR(20) NULL DEFAULT NULL,
	`os_bit` VARCHAR(2) NULL DEFAULT NULL,
	`team_code` VARCHAR(10) NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NULL DEFAULT NULL,
	`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`status` VARCHAR(10) NULL DEFAULT NULL,
	`ssh_id` VARCHAR(10) NULL DEFAULT NULL,
	`pool_id` VARCHAR(8) NULL DEFAULT NULL,
	`host_id` VARCHAR(8) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE `GN_VM_MACHINES` (
	`id` VARCHAR(8) NOT NULL DEFAULT '',
	`name` VARCHAR(50) NULL DEFAULT '',
	`tag` VARCHAR(100) NULL DEFAULT '',
	`type` VARCHAR(10) NOT NULL DEFAULT '' COMMENT 'code: kvm, hyperv',
	`internal_id` VARCHAR(100) NULL DEFAULT '',
	`internal_name` VARCHAR(100) NULL DEFAULT '',
	`host_id` VARCHAR(8) NOT NULL DEFAULT '',
	`ip` VARCHAR(20) NULL DEFAULT NULL,
	`cpu` INT(2) NOT NULL COMMENT '개수',
	`memory` BIGINT(20) NOT NULL COMMENT 'byte',
	`disk` BIGINT(20) NULL DEFAULT NULL COMMENT 'byte',
	`os` VARCHAR(10) NULL DEFAULT NULL,
	`os_ver` VARCHAR(20) NULL DEFAULT NULL,
	`os_sub_ver` VARCHAR(20) NULL DEFAULT NULL,
	`os_bit` VARCHAR(2) NULL DEFAULT NULL COMMENT '32, 64',
	`team_code` VARCHAR(10) NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NOT NULL,
	`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`start_time` TIMESTAMP NULL DEFAULT NULL,
	`stop_time` TIMESTAMP NULL DEFAULT NULL,
	`status` VARCHAR(10) NULL DEFAULT NULL COMMENT 'code: running, starting, error, stop, stoping, creating, delete, suspend',
	`hyperv_pass` VARCHAR(50) NULL DEFAULT NULL,
	`image_id` VARCHAR(8) NULL DEFAULT NULL,
	`ssh_key_id` INT(11) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;


