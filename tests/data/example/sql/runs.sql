CREATE TABLE `experimenters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ;

CREATE TABLE `runs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) DEFAULT NULL,
  `task_name` text NOT NULL,
  `start_time` timestamp(3) NULL DEFAULT NULL,
  `duration` float DEFAULT NULL,
  `xelo_stem` text DEFAULT NULL,
  `performance` text DEFAULT NULL,
  `task_description` text DEFAULT NULL,
  `acquisition` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `runs_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER validate_task_name_before_insert_to_runs
  BEFORE INSERT ON runs
  FOR EACH ROW
BEGIN
  IF NEW.task_name NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs'
    AND column_name = 'task_name')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column task_name is not allowed in table runs';
  END IF;
END ;;

CREATE TRIGGER validate_task_name_before_update_to_runs
  BEFORE UPDATE ON runs
  FOR EACH ROW
BEGIN
  IF NEW.task_name NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs'
    AND column_name = 'task_name')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column task_name is not allowed in table runs';
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `intended_for` (
  `run_id` int(11) DEFAULT NULL,
  `target` int(11) DEFAULT NULL,
  KEY `run_id` (`run_id`),
  KEY `target` (`target`),
  CONSTRAINT `intended_for_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `intended_for_ibfk_2` FOREIGN KEY (`target`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;


CREATE TABLE `runs_experimenters` (
  `run_id` int(11) DEFAULT NULL,
  `experimenter_id` int(11) DEFAULT NULL,
  UNIQUE KEY `runs_experimenters_unique` (`run_id`,`experimenter_id`),
  KEY `experimenter_id` (`experimenter_id`),
  CONSTRAINT `runs_experimenters_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `runs_experimenters_ibfk_2` FOREIGN KEY (`experimenter_id`) REFERENCES `experimenters` (`id`) ON DELETE CASCADE
) ;


CREATE TABLE `runs_protocols` (
  `run_id` int(11) DEFAULT NULL,
  `protocol_id` int(11) DEFAULT NULL,
  UNIQUE KEY `runs_protocols_unique` (`run_id`,`protocol_id`),
  KEY `protocol_id` (`protocol_id`),
  CONSTRAINT `runs_protocols_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `runs_protocols_ibfk_2` FOREIGN KEY (`protocol_id`) REFERENCES `protocols` (`id`) ON DELETE CASCADE
) ;

CREATE TABLE `events` (
  `run_id` int(11) DEFAULT NULL,
  `onset` float DEFAULT NULL,
  `duration` float DEFAULT NULL,
  `trial_type` text DEFAULT NULL,
  `response_time` text DEFAULT NULL,
  `value` text DEFAULT NULL,
  KEY `run_id` (`run_id`),
  CONSTRAINT `events_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;
