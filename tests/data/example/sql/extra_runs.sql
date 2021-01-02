

DROP TABLE IF EXISTS `runs_speak`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `runs_speak` (
  `run_id` int(11) DEFAULT NULL,
  `overt_covert` text DEFAULT NULL,
  UNIQUE KEY `run_id` (`run_id`),
  CONSTRAINT `runs_speak_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_overt_covert_before_insert_to_runs_speak
  BEFORE INSERT ON runs_speak
  FOR EACH ROW
BEGIN
  IF NEW.overt_covert NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs_speak'
    AND column_name = 'overt_covert')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column overt_covert is not allowed in table runs_speak';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_overt_covert_before_update_to_runs_speak
  BEFORE UPDATE ON runs_speak
  FOR EACH ROW
BEGIN
  IF NEW.overt_covert NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs_speak'
    AND column_name = 'overt_covert')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column overt_covert is not allowed in table runs_speak';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


DROP TABLE IF EXISTS `runs_sensorimotor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `runs_sensorimotor` (
  `run_id` int(11) DEFAULT NULL,
  `body_part` text DEFAULT NULL,
  `left_right` text DEFAULT NULL,
  `execution_imagery` text DEFAULT NULL,
  UNIQUE KEY `run_id` (`run_id`),
  CONSTRAINT `runs_sensorimotor_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_body_part_before_insert_to_runs_sensorimotor
  BEFORE INSERT ON runs_sensorimotor
  FOR EACH ROW
BEGIN
  IF NEW.body_part NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs_sensorimotor'
    AND column_name = 'body_part')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column body_part is not allowed in table runs_sensorimotor';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_left_right_before_insert_to_runs_sensorimotor
  BEFORE INSERT ON runs_sensorimotor
  FOR EACH ROW
BEGIN
  IF NEW.left_right NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs_sensorimotor'
    AND column_name = 'left_right')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column left_right is not allowed in table runs_sensorimotor';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_execution_imagery_before_insert_to_runs_sensorimotor
  BEFORE INSERT ON runs_sensorimotor
  FOR EACH ROW
BEGIN
  IF NEW.execution_imagery NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs_sensorimotor'
    AND column_name = 'execution_imagery')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column execution_imagery is not allowed in table runs_sensorimotor';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_body_part_before_update_to_runs_sensorimotor
  BEFORE UPDATE ON runs_sensorimotor
  FOR EACH ROW
BEGIN
  IF NEW.body_part NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs_sensorimotor'
    AND column_name = 'body_part')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column body_part is not allowed in table runs_sensorimotor';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_left_right_before_update_to_runs_sensorimotor
  BEFORE UPDATE ON runs_sensorimotor
  FOR EACH ROW
BEGIN
  IF NEW.left_right NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs_sensorimotor'
    AND column_name = 'left_right')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column left_right is not allowed in table runs_sensorimotor';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_execution_imagery_before_update_to_runs_sensorimotor
  BEFORE UPDATE ON runs_sensorimotor
  FOR EACH ROW
BEGIN
  IF NEW.execution_imagery NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'runs_sensorimotor'
    AND column_name = 'execution_imagery')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column execution_imagery is not allowed in table runs_sensorimotor';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


DROP TABLE IF EXISTS `runs_mario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `runs_mario` (
  `run_id` int(11) DEFAULT NULL,
  `velocity` text DEFAULT NULL,
  UNIQUE KEY `run_id` (`run_id`),
  CONSTRAINT `runs_mario_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;



CREATE TRIGGER add_id_to_subtable_runs_mario
  AFTER INSERT ON runs
  FOR EACH ROW
BEGIN
  IF NEW.task_name = 'mario'
  THEN
    INSERT INTO runs_mario (run_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER add_id_to_subtable_runs_speak
  AFTER INSERT ON runs
  FOR EACH ROW
BEGIN
  IF NEW.task_name IN ('picnam', 'verb')
  THEN
    INSERT INTO runs_speak (run_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER add_id_to_subtable_runs_sensorimotor
  AFTER INSERT ON runs
  FOR EACH ROW
BEGIN
  IF NEW.task_name IN ('somatosensory', 'motor')
  THEN
    INSERT INTO runs_sensorimotor (run_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER `replace_id_to_subtable_runs_mario` AFTER UPDATE ON `runs` FOR EACH ROW
BEGIN
  IF NEW.task_name <> OLD.task_name AND
    NEW.task_name = 'mario' AND
    NEW.id NOT IN (SELECT run_id FROM runs_mario)
  THEN
    INSERT INTO runs_mario (run_id) VALUES (NEW.id) ;
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `replace_id_to_subtable_runs_sensorimotor` AFTER UPDATE ON `runs` FOR EACH ROW
BEGIN
  IF NEW.task_name <> OLD.task_name AND
    NEW.task_name IN ('somatosensory', 'motor') AND
    NEW.id NOT IN (SELECT run_id FROM runs_sensorimotor )
  THEN
    INSERT INTO runs_sensorimotor (run_id) VALUES (NEW.id) ;
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `replace_id_to_subtable_runs_speak` AFTER UPDATE ON `runs` FOR EACH ROW
BEGIN
  IF NEW.task_name <> OLD.task_name AND
    NEW.task_name IN ('picnam', 'verb') AND
    NEW.id NOT IN (SELECT run_id FROM runs_speak)
  THEN
    INSERT INTO runs_speak (run_id) VALUES (NEW.id) ;
  END IF;
END */;;
DELIMITER ;
