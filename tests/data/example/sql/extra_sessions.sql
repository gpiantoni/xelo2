
DROP TABLE IF EXISTS `sessions_mri`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions_mri` (
  `session_id` int(11) DEFAULT NULL,
  `MagneticFieldStrength` text DEFAULT NULL,
  UNIQUE KEY `session_id` (`session_id`),
  CONSTRAINT `sessions_mri_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_MagneticFieldStrength_before_insert_to_sessions_mri
  BEFORE INSERT ON sessions_mri
  FOR EACH ROW
BEGIN
  IF NEW.MagneticFieldStrength NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'sessions_mri'
    AND column_name = 'MagneticFieldStrength')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column MagneticFieldStrength is not allowed in table sessions_mri';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_MagneticFieldStrength_before_update_to_sessions_mri
  BEFORE UPDATE ON sessions_mri
  FOR EACH ROW
BEGIN
  IF NEW.MagneticFieldStrength NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'sessions_mri'
    AND column_name = 'MagneticFieldStrength')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column MagneticFieldStrength is not allowed in table sessions_mri';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

DROP TABLE IF EXISTS `sessions_or`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions_or` (
  `session_id` int(11) DEFAULT NULL,
  `date_of_surgery` date DEFAULT NULL,
  UNIQUE KEY `session_id` (`session_id`),
  CONSTRAINT `sessions_or_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;


DROP TABLE IF EXISTS `sessions_iemu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions_iemu` (
  `session_id` int(11) DEFAULT NULL,
  `date_of_implantation` date DEFAULT NULL,
  `date_of_explantation` date DEFAULT NULL,
  UNIQUE KEY `session_id` (`session_id`),
  CONSTRAINT `sessions_iemu_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;


CREATE TRIGGER add_id_to_subtable_sessions_iemu
  AFTER INSERT ON sessions
  FOR EACH ROW
BEGIN
  IF NEW.name = 'IEMU'
  THEN
    INSERT INTO sessions_iemu (session_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER add_id_to_subtable_sessions_or
  AFTER INSERT ON sessions
  FOR EACH ROW
BEGIN
  IF NEW.name = 'OR'
  THEN
    INSERT INTO sessions_or (session_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER add_id_to_subtable_sessions_mri
  AFTER INSERT ON sessions
  FOR EACH ROW
BEGIN
  IF NEW.name = 'MRI'
  THEN
    INSERT INTO sessions_mri (session_id) VALUES (NEW.id) ;
  END IF;
END ;;


CREATE TRIGGER `replace_id_to_subtable_sessions_iemu` AFTER UPDATE ON `sessions` FOR EACH ROW
BEGIN
  IF NEW.name <> OLD.name AND
    NEW.name = 'IEMU' AND
    NEW.id NOT IN (SELECT session_id FROM sessions_iemu)
  THEN
    INSERT INTO sessions_iemu (session_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER `replace_id_to_subtable_sessions_or` AFTER UPDATE ON `sessions` FOR EACH ROW
BEGIN
  IF NEW.name <> OLD.name AND
    NEW.name = 'OR' AND
    NEW.id NOT IN (SELECT session_id FROM sessions_or)
  THEN
    INSERT INTO sessions_or (session_id) VALUES (NEW.id) ;
  END IF;
END ;;


CREATE TRIGGER `replace_id_to_subtable_sessions_mri` AFTER UPDATE ON `sessions` FOR EACH ROW
BEGIN
  IF NEW.name <> OLD.name AND
    NEW.name = 'MRI' AND
    NEW.id NOT IN (SELECT session_id FROM sessions_mri )
  THEN
    INSERT INTO sessions_mri (session_id) VALUES (NEW.id) ;
  END IF;
END ;;
