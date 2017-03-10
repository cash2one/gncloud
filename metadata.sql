connect gncloud;

CREATE TABLE `GN_BACKUP` (
	`vm_id` VARCHAR(8) NOT NULL COLLATE 'utf8_unicode_ci',
	`backup_time` TIMESTAMP NULL DEFAULT NULL,
	`team_code` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`author_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`vm_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`vm_name` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`team_name` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`author_name` VARCHAR(20) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	PRIMARY KEY (`vm_id`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_BACKUP_HIST` (
	`vm_id` VARCHAR(8) NOT NULL COLLATE 'utf8_unicode_ci',
	`filename` VARCHAR(150) NOT NULL COLLATE 'utf8_unicode_ci',
	`backup_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
	`vm_type` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`host_ip` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	PRIMARY KEY (`vm_id`, `filename`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
;

CREATE TABLE `GN_CLUSTER` (
	`id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(50) NULL DEFAULT NULL,
	`ip` VARCHAR(20) NULL DEFAULT NULL,
	`type` VARCHAR(10) NULL DEFAULT NULL COMMENT 'kvm, hyperv, docker',
	`swarm_join` VARCHAR(200) NULL DEFAULT NULL,
	`create_time` TIMESTAMP NULL DEFAULT NULL,
	`status` VARCHAR(10) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
;

CREATE TABLE `GN_DOCKER_CONTAINERS` (
	`service_id` VARCHAR(8) NOT NULL DEFAULT '',
	`internal_id` VARCHAR(100) NOT NULL DEFAULT '',
	`internal_name` VARCHAR(100) NOT NULL DEFAULT '',
	`host_id` VARCHAR(8) NOT NULL,
	`status` VARCHAR(10) NULL DEFAULT NULL,
	PRIMARY KEY (`service_id`, `internal_id`, `internal_name`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_DOCKER_IMAGES` (
	`id` VARCHAR(8) NOT NULL,
	`base_image` VARCHAR(8) NULL DEFAULT NULL,
	`view_name` VARCHAR(200) NULL DEFAULT '' COMMENT '전제현 주임 >> RepoTags를 여기에 넣으면 될 것 같',
	`name` VARCHAR(200) NULL DEFAULT '',
	`tag` VARCHAR(200) NULL DEFAULT NULL,
	`os` VARCHAR(50) NULL DEFAULT NULL COMMENT 'docker base image',
	`os_ver` VARCHAR(45) NULL DEFAULT NULL,
	`sub_type` VARCHAR(10) NULL DEFAULT '' COMMENT '예) win_10_pro_64.vhdx\\\\n전제현 주임 >> docker에서는 필요없어 보인',
	`team_code` VARCHAR(10) NULL DEFAULT NULL,
	`author_id` VARCHAR(15) NULL DEFAULT NULL,
	`create_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
	`status` VARCHAR(10) NULL DEFAULT NULL,
	`icon` VARCHAR(50) NULL DEFAULT NULL,
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
ROW_FORMAT=COMPACT
;

CREATE TABLE `GN_DOCKER_PORTS` (
	`service_id` VARCHAR(8) NOT NULL,
	`protocol` VARCHAR(10) NOT NULL,
	`target_port` VARCHAR(5) NOT NULL DEFAULT '',
	`published_port` VARCHAR(5) NOT NULL DEFAULT '',
	PRIMARY KEY (`service_id`, `target_port`, `published_port`, `protocol`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_DOCKER_SERVICES` (
	`service_id` VARCHAR(8) NOT NULL DEFAULT '',
	`image` VARCHAR(100) NULL DEFAULT NULL,
	PRIMARY KEY (`service_id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
;

CREATE TABLE `GN_DOCKER_VOLUMES` (
	`service_id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(200) NOT NULL DEFAULT '',
	`source_path` VARCHAR(200) NOT NULL DEFAULT '',
	`destination_path` VARCHAR(200) NOT NULL DEFAULT '',
	`status` VARCHAR(10) NULL DEFAULT NULL,
	PRIMARY KEY (`service_id`, `name`, `source_path`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;


CREATE TABLE `GN_ERROR_HIST` (
	`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`type` VARCHAR(10) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`action` VARCHAR(11) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`team_code` VARCHAR(10) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`author_id` VARCHAR(50) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`action_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`solve_time` TIMESTAMP NULL DEFAULT NULL,
	`solver_id` VARCHAR(100) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`vm_id` VARCHAR(8) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`vm_name` VARCHAR(50) NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`action_year` VARCHAR(4) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`action_month` VARCHAR(2) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`solve_content` TEXT NULL COLLATE 'utf8_unicode_ci',
	`cause` VARCHAR(1000) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	PRIMARY KEY (`id`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
AUTO_INCREMENT=109
;


CREATE TABLE `GN_HOST_MACHINES` (
	`id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(100) NULL DEFAULT '',
	`ip` VARCHAR(50) NULL DEFAULT '',
	`type` VARCHAR(10) NULL DEFAULT '' COMMENT 'kvm, hyperv, docker',
	`cpu` INT(2) UNSIGNED NULL DEFAULT NULL COMMENT '실제 cpu 코어 갯수',
	`mem` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT '실제 메모리 용량, MB 단위',
	`disk` BIGINT(20) UNSIGNED NULL DEFAULT NULL COMMENT '실제 HDD, SSD 등 GB 단위',
	`host_agent_port` INT(5) UNSIGNED NULL DEFAULT NULL,
	`image_path` VARCHAR(200) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_ID` (
	`id` VARCHAR(8) NOT NULL,
	`type` VARCHAR(20) NOT NULL COMMENT 'host, kvm, hyperv, docker, controller, kvm_image, hyperv_image, docker_image',
	`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_IMAGES_POOL` (
	`host_id` VARCHAR(8) NOT NULL,
	`id` VARCHAR(8) NULL DEFAULT NULL,
	`type` VARCHAR(10) NULL DEFAULT NULL COMMENT 'kvm, hyperv',
	`local_path` VARCHAR(200) NULL DEFAULT NULL COMMENT '/{nework} on mount/{host_id}/image/kvm',
	`nas_path` VARCHAR(200) NULL DEFAULT NULL,
	`manager_path` VARCHAR(200) NULL DEFAULT NULL,
	PRIMARY KEY (`host_id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_INSTANCE_ACTION_HISTORY` (
	`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`action` VARCHAR(10) NULL DEFAULT NULL COMMENT 'Create, Resume,Suspend,Reboot,Delete' COLLATE 'utf8_unicode_ci',
	`action_time` TIMESTAMP NULL DEFAULT NULL,
	`user_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`team_code` VARCHAR(30) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	PRIMARY KEY (`id`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
AUTO_INCREMENT=1101
;

CREATE TABLE `GN_INSTANCE_STATUS` (
	`vm_id` VARCHAR(8) NOT NULL COLLATE 'utf8_unicode_ci',
	`vm_name` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`delete_time` TIMESTAMP NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`author_name` VARCHAR(20) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`team_code` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`team_name` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`price` INT(11) NULL DEFAULT NULL,
	`price_type` VARCHAR(2) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`cpu` BIGINT(20) NULL DEFAULT NULL,
	`memory` BIGINT(20) NULL DEFAULT NULL,
	`disk` BIGINT(20) NULL DEFAULT NULL,
	PRIMARY KEY (`vm_id`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_INVOICE_RESULT` (
	`year` VARCHAR(4) NOT NULL COLLATE 'utf8_unicode_ci',
	`month` VARCHAR(2) NOT NULL COLLATE 'utf8_unicode_ci',
	`team_code` VARCHAR(10) NOT NULL COLLATE 'utf8_unicode_ci',
	`invoice_data` VARCHAR(15000) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	PRIMARY KEY (`year`, `month`, `team_code`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_MONITOR` (
	`id` VARCHAR(8) NOT NULL,
	`type` VARCHAR(6) NOT NULL COMMENT 'host, hyperv, kvm, docker',
	`cpu_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL COMMENT '% 단위',
	`mem_usage` DECIMAL(15,4) UNSIGNED NULL DEFAULT NULL,
	`disk_usage` DECIMAL(15,4) UNSIGNED NULL DEFAULT NULL,
	`net_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL,
	PRIMARY KEY (`id`, `type`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
;

CREATE TABLE `GN_MONITOR_HIST` (
	`id` VARCHAR(8) NOT NULL,
	`type` VARCHAR(6) NOT NULL COMMENT 'host, hyperv, kvm, docker',
	`cur_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`cpu_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL COMMENT '% 단위',
	`mem_usage` DECIMAL(15,4) UNSIGNED NULL DEFAULT NULL,
	`disk_usage` DECIMAL(15,4) UNSIGNED NULL DEFAULT NULL,
	`net_usage` DECIMAL(11,4) UNSIGNED NULL DEFAULT NULL,
	`seq` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (`seq`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
AUTO_INCREMENT=191308
;

CREATE TABLE `GN_NOTICE` (
	`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`title` TEXT NULL COLLATE 'utf8_unicode_ci',
	`text` TEXT NULL COLLATE 'utf8_unicode_ci',
	`write_date` TIMESTAMP NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
AUTO_INCREMENT=90
;

CREATE TABLE `GN_QNA` (
	`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`title` VARCHAR(200) NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`text` TEXT NULL COLLATE 'utf8_unicode_ci',
	`team_code` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`farent_id` INT(11) NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`create_date` TIMESTAMP NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
AUTO_INCREMENT=131
;

CREATE TABLE `GN_SSH_KEYS` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `team_code` varchar(50) NOT NULL DEFAULT '',
  `name` varchar(100) NOT NULL DEFAULT '',
  `fingerprint` varchar(50) DEFAULT NULL,
  `download_yn` varchar(1) NOT NULL DEFAULT 'N',
  `create_time` timestamp NULL DEFAULT NULL,
  `pub` text,
  `org` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1231313260 DEFAULT CHARSET=utf8;


CREATE TABLE `GN_SSH_KEYS_MAPPING` (
	`ssh_key_id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`vm_id` VARCHAR(8) NULL DEFAULT NULL,
	PRIMARY KEY (`ssh_key_id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_SYSTEM_SETTING` (
	`billing_type` VARCHAR(2) NOT NULL DEFAULT '' COMMENT 'D,H' COLLATE 'utf8_unicode_ci',
	`backup_schedule_type` VARCHAR(2) NULL DEFAULT NULL COMMENT 'D,W' COLLATE 'utf8_unicode_ci',
	`backup_schedule_period` VARCHAR(13) NULL DEFAULT NULL COMMENT '27|1010101' COLLATE 'utf8_unicode_ci',
	`monitor_period` VARCHAR(4) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`backup_day` VARCHAR(11) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	PRIMARY KEY (`billing_type`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_TEAM` (
	`team_code` VARCHAR(10) NOT NULL,
	`team_name` VARCHAR(50) NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NULL DEFAULT NULL,
	`cpu_quota` INT(11) UNSIGNED NOT NULL DEFAULT '30',
	`mem_quota` BIGINT(20) UNSIGNED NOT NULL DEFAULT '21474836480',
	`disk_quota` BIGINT(20) UNSIGNED NOT NULL DEFAULT '107374182400',
	`create_date` TIMESTAMP NULL DEFAULT NULL,
	PRIMARY KEY (`team_code`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_TEAM_HIST` (
	`team_code` VARCHAR(10) NOT NULL,
	`team_del_code` VARCHAR(8) NOT NULL,
	`team_name` VARCHAR(50) NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NULL DEFAULT NULL,
	`cpu_quota` BIGINT(11) UNSIGNED NOT NULL DEFAULT '30',
	`mem_quota` BIGINT(20) UNSIGNED NOT NULL DEFAULT '20000',
	`disk_quota` BIGINT(20) UNSIGNED NOT NULL DEFAULT '100',
	`delete_date` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`team_code`, `team_del_code`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
;

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
ENGINE=InnoDB
;

CREATE TABLE `GN_USER_ACCESS_HISTORY` (
	`user_id` VARCHAR(50) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`team_code` VARCHAR(10) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`action` VARCHAR(7) NULL DEFAULT NULL COMMENT 'login, logout' COLLATE 'utf8_unicode_ci',
	`action_time` TIMESTAMP NULL DEFAULT NULL,
	`id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
AUTO_INCREMENT=1574
;

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
ENGINE=InnoDB
;

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
ROW_FORMAT=COMPACT
;

CREATE TABLE `GN_VM_IMAGES` (
	`id` VARCHAR(8) NOT NULL,
	`name` VARCHAR(50) NOT NULL DEFAULT '',
	`filename` VARCHAR(100) NULL DEFAULT '' COMMENT '예) win_10_pro_64.vhdx',
	`type` VARCHAR(10) NOT NULL DEFAULT '' COMMENT '종류: kvm, hyperv ',
	`sub_type` VARCHAR(10) NOT NULL DEFAULT '' COMMENT '종류: base, snap',
	`icon` VARCHAR(100) NULL DEFAULT NULL COMMENT 'icon image path & name',
	`os` VARCHAR(100) NULL DEFAULT NULL,
	`os_ver` VARCHAR(20) NULL DEFAULT NULL,
	`os_subver` VARCHAR(20) NULL DEFAULT NULL,
	`os_bit` VARCHAR(2) NULL DEFAULT NULL,
	`team_code` VARCHAR(10) NULL DEFAULT NULL,
	`author_id` VARCHAR(50) NULL DEFAULT NULL,
	`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`status` VARCHAR(10) NULL DEFAULT NULL,
	`ssh_id` VARCHAR(10) NULL DEFAULT '-',
	`pool_id` VARCHAR(8) NULL DEFAULT NULL,
	`host_id` VARCHAR(8) NULL DEFAULT NULL,
	`parent_id` VARCHAR(8) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

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
	`backup_confirm` VARCHAR(5) NULL DEFAULT 'N' COMMENT 'true, false',
	`size_id` VARCHAR(8) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

CREATE TABLE `GN_VM_SIZE` (
	`id` VARCHAR(8) NOT NULL DEFAULT '' COLLATE 'utf8_unicode_ci',
	`cpu` BIGINT(20) NOT NULL,
	`mem` BIGINT(20) NOT NULL,
	`disk` BIGINT(20) NOT NULL,
	`hour_price` INT(11) NULL DEFAULT NULL,
	`day_price` INT(11) NULL DEFAULT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_unicode_ci'
ENGINE=InnoDB
;


INSERT INTO `GN_USERS` (`user_id`, `password`, `user_name`, `privilege`, `tel`, `email`, `start_date`, `end_date`) VALUES ('root', '0efcd128c7ebc05b8847ed430ab25fdd31c6df70315a0c862e', '시스템관리자', NULL, '-', '-', '2017-01-16 12:24:23', NULL);
INSERT INTO `GN_TEAM` (`team_code`, `team_name`, `author_id`, `cpu_quota`, `mem_quota`, `disk_quota`, `create_date`) VALUES ('000', '시스템관리자', 'System', 0, 0, 0, '2017-01-01 17:58:00');
INSERT INTO `GN_USER_TEAMS` (`user_id`, `team_code`, `comfirm`, `apply_date`, `approve_date`, `team_owner`) VALUES ('root', '000', 'Y', '2017-01-03 11:48:21', '2017-01-03 11:45:37', 'sysowner');
INSERT INTO `GN_SYSTEM_SETTING` (`billing_type`, `backup_schedule_type`, `backup_schedule_period`, `monitor_period`, `backup_day`) VALUES ('D', 'W', '0000000', '60', '3');
INSERT INTO `GN_CLUSTER` (`id`, `name`, `ip`, `type`, `swarm_join`, `create_time`, `status`)
VALUES
	('02293106', NULL, 'hyperv', 'hyperv', NULL, '2017-02-27 09:29:43', 'Running'),
	('904ef79d', NULL, 'scheduler', 'scheduler', NULL, '2017-02-27 09:13:14', 'Running'),
	('bbba2a74', NULL, 'docker', 'docker', NULL, '2017-02-27 09:13:14', 'Running'),
	('f5a9ebff', NULL, 'kvm', 'kvm', NULL, '2017-02-27 09:13:14', 'Running');
