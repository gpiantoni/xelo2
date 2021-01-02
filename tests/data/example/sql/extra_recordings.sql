
DROP TABLE IF EXISTS `recordings_ieeg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recordings_ieeg` (
  `recording_id` int(11) DEFAULT NULL,
  `channel_group_id` int(11) DEFAULT NULL,
  `electrode_group_id` int(11) DEFAULT NULL,
  `Manufacturer` text DEFAULT NULL,
  `Reference` text DEFAULT NULL,
  UNIQUE KEY `recording_id` (`recording_id`),
  KEY `channel_group_id` (`channel_group_id`),
  KEY `electrode_group_id` (`electrode_group_id`),
  CONSTRAINT `recordings_ieeg_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recordings_ieeg_ibfk_2` FOREIGN KEY (`channel_group_id`) REFERENCES `channel_groups` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recordings_ieeg_ibfk_3` FOREIGN KEY (`electrode_group_id`) REFERENCES `electrode_groups` (`id`) ON DELETE CASCADE
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_Manufacturer_before_insert_to_recordings_ieeg
  BEFORE INSERT ON recordings_ieeg
  FOR EACH ROW
BEGIN
  IF NEW.Manufacturer NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_ieeg'
    AND column_name = 'Manufacturer')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Manufacturer is not allowed in table recordings_ieeg';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER validate_Manufacturer_before_update_to_recordings_ieeg
  BEFORE UPDATE ON recordings_ieeg
  FOR EACH ROW
BEGIN
  IF NEW.Manufacturer NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_ieeg'
    AND column_name = 'Manufacturer')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Manufacturer is not allowed in table recordings_ieeg';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

DROP TABLE IF EXISTS `recordings_mri`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recordings_mri` (
  `recording_id` int(11) DEFAULT NULL,
  `region_of_interest` text DEFAULT NULL,
  `Sequence` text DEFAULT NULL,
  `MultibandAccelerationFactor` int(11) DEFAULT NULL,
  `PhaseEncodingDirection` text DEFAULT NULL,
  `SliceEncodingDirection` text DEFAULT NULL,
  `SliceOrder` text DEFAULT NULL,
  UNIQUE KEY `recording_id` (`recording_id`),
  CONSTRAINT `recordings_mri_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `validate_PhaseEncodingDirection_before_insert_to_recordings_mri` BEFORE INSERT ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.PhaseEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'PhaseEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column PhaseEncodingDirection is not allowed in table recordings_mri';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `validate_SliceEncodingDirection_before_insert_to_recordings_mri` BEFORE INSERT ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.SliceEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceEncodingDirection is not allowed in table recordings_mri';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `validate_Sequence_before_insert_to_recordings_mri` BEFORE INSERT ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.Sequence NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'Sequence')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Sequence is not allowed in table recordings_mri';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `validate_SliceOrder_before_insert_to_recordings_mri` BEFORE INSERT ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.SliceOrder NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceOrder')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceOrder is not allowed in table recordings_mri';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `validate_SliceEncodingDirection_before_update_to_recordings_mri` BEFORE UPDATE ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.SliceEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceEncodingDirection is not allowed in table recordings_mri';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `validate_Sequence_before_update_to_recordings_mri` BEFORE UPDATE ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.Sequence NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'Sequence')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column Sequence is not allowed in table recordings_mri';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `validate_PhaseEncodingDirection_before_update_to_recordings_mri` BEFORE UPDATE ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.PhaseEncodingDirection NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'PhaseEncodingDirection')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column PhaseEncodingDirection is not allowed in table recordings_mri';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`giovanni`@`localhost`*/ /*!50003 TRIGGER `validate_SliceOrder_before_update_to_recordings_mri` BEFORE UPDATE ON `recordings_mri` FOR EACH ROW
BEGIN
  IF NEW.SliceOrder NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings_mri'
    AND column_name = 'SliceOrder')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column SliceOrder is not allowed in table recordings_mri';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;


DROP TABLE IF EXISTS `recordings_epi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recordings_epi` (
  `recording_id` int(11) DEFAULT NULL,
  `RepetitionTime` float DEFAULT NULL,
  `NumberOfVolumesDiscardedByScanner` int(11) DEFAULT NULL,
  UNIQUE KEY `recording_id` (`recording_id`),
  CONSTRAINT `recordings_epi_ibfk_1` FOREIGN KEY (`recording_id`) REFERENCES `recordings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;
