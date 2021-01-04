CREATE TABLE `files` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `format` text DEFAULT NULL,
  `path` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

INSERT INTO `allowed_values` VALUES ('files','format','parrec'),('files','format','xmlrec'),('files','format','nifti'),('files','format','bci2000'),('files','format','micromed'),('files','format','blackrock'),('files','format','task_log'),('files','format','dataglove'),('files','format','scanphyslog'),('files','format','dicom'),('files','format','pdf'),('files','format','docx'),('files','format','image');

DELIMITER ;;

CREATE TRIGGER validate_format_before_insert_to_files
  BEFORE INSERT ON files
  FOR EACH ROW
BEGIN
  IF NEW.format NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'files'
    AND column_name = 'format')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column format is not allowed in table files';
  END IF;
END ;;

CREATE TRIGGER validate_format_before_update_to_files
  BEFORE UPDATE ON files
  FOR EACH ROW
BEGIN
  IF NEW.format NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'files'
    AND column_name = 'format')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column format is not allowed in table files';
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `protocols_files` (
  `protocol_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `protocols_files_unique` (`protocol_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `protocols_files_ibfk_1` FOREIGN KEY (`protocol_id`) REFERENCES `protocols` (`id`) ON DELETE CASCADE,
  CONSTRAINT `protocols_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER delete_file_if_no_links_in_protocols_files
  AFTER DELETE ON protocols_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END ;;

DELIMITER ;

CREATE TABLE `runs_files` (
  `run_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `runs_files_unique` (`run_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `runs_files_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `runs_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;
CREATE TRIGGER delete_file_if_no_links_in_runs_files
  AFTER DELETE ON runs_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END ;;

DELIMITER ;

CREATE TABLE `sessions_files` (
  `session_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `sessions_files_unique` (`session_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `sessions_files_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sessions_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;
CREATE TRIGGER delete_file_if_no_links_in_sessions_files
  AFTER DELETE ON sessions_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END ;;

DELIMITER ;

CREATE TABLE `subjects_files` (
  `subject_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `subjects_files_unique` (`subject_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `subjects_files_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE,
  CONSTRAINT `subjects_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER delete_file_if_no_links_in_subjects_files
  AFTER DELETE ON subjects_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END ;;

DELIMITER ;

CREATE TABLE `recordings_files` (
  `recording_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `recordings_files_unique` (`recording_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `recordings_files_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recordings_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER delete_file_if_no_links_in_recordings_files
  AFTER DELETE ON recordings_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END ;;

DELIMITER ;
