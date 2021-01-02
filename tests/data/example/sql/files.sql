
DROP TABLE IF EXISTS `files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `files` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `format` text DEFAULT NULL,
  `path` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3032 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_format_before_insert_to_files
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
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_format_before_update_to_files
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
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


DROP TABLE IF EXISTS `protocols_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `protocols_files` (
  `protocol_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `protocols_files_unique` (`protocol_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `protocols_files_ibfk_1` FOREIGN KEY (`protocol_id`) REFERENCES `protocols` (`id`) ON DELETE CASCADE,
  CONSTRAINT `protocols_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER delete_file_if_no_links_in_protocols_files
  AFTER DELETE ON protocols_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


DROP TABLE IF EXISTS `runs_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `runs_files` (
  `run_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `runs_files_unique` (`run_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `runs_files_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `runs_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER delete_file_if_no_links_in_runs_files
  AFTER DELETE ON runs_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


DROP TABLE IF EXISTS `sessions_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions_files` (
  `session_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `sessions_files_unique` (`session_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `sessions_files_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sessions_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER delete_file_if_no_links_in_sessions_files
  AFTER DELETE ON sessions_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


DROP TABLE IF EXISTS `subjects_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subjects_files` (
  `subject_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `subjects_files_unique` (`subject_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `subjects_files_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE,
  CONSTRAINT `subjects_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER delete_file_if_no_links_in_subjects_files
  AFTER DELETE ON subjects_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


DROP TABLE IF EXISTS `recordings_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recordings_files` (
  `recording_id` int(11) DEFAULT NULL,
  `file_id` int(11) DEFAULT NULL,
  UNIQUE KEY `recordings_files_unique` (`recording_id`,`file_id`),
  KEY `file_id` (`file_id`),
  CONSTRAINT `recordings_files_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recordings_files_ibfk_2` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER delete_file_if_no_links_in_recordings_files
  AFTER DELETE ON recordings_files
  FOR EACH ROW
BEGIN
  IF NOT EXISTS(SELECT file_id FROM subjects_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM sessions_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM protocols_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM runs_files WHERE file_id = OLD.file_id) AND NOT EXISTS(SELECT file_id FROM recordings_files WHERE file_id = OLD.file_id)
  THEN
    DELETE FROM files WHERE id = OLD.file_id ;
  END IF ;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/
