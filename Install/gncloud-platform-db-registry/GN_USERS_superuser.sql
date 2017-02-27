connect gncloud;
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
