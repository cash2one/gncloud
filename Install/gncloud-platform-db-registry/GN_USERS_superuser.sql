connect gncloud;
INSERT INTO `GN_USERS` (`user_id`, `password`, `user_name`, `privilege`, `tel`, `email`, `start_date`, `end_date`) VALUES ('root', password('12345678'), 'Root', NULL, '-', '-', '2017-01-16 12:24:23', NULL);
INSERT INTO `GN_TEAM` (`team_code`, `team_name`, `author_id`, `cpu_quota`, `mem_quota`, `disk_quota`, `create_date`) VALUES ('000', '시스템관리자', 'System', 0, 0, 0, '2017-01-01 17:58:00');
INSERT INTO `GN_USER_TEAMS` (`user_id`, `team_code`, `comfirm`, `apply_date`, `approve_date`, `team_owner`) VALUES ('root', '000', 'Y', '2017-01-03 11:48:21', '2017-01-03 11:45:37', 'sysowner');
INSERT INTO `GN_SYSTEM_SETTING` (`billing_type`, `backup_schedule_type`, `backup_schedule_period`, `monitor_period`, `backup_day`) VALUES ('D', 'W', '0000000', '60', '3');