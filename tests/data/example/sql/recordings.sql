CREATE TABLE `recordings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `run_id` int(11) DEFAULT NULL,
  `modality` text DEFAULT NULL,
  `offset` float DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `run_id` (`run_id`),
  CONSTRAINT `recordings_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER validate_modality_before_insert_to_recordings
  BEFORE INSERT ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings'
    AND column_name = 'modality')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column modality is not allowed in table recordings';
  END IF;
END ;;

CREATE TRIGGER validate_modality_before_update_to_recordings
  BEFORE UPDATE ON recordings
  FOR EACH ROW
BEGIN
  IF NEW.modality NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'recordings'
    AND column_name = 'modality')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column modality is not allowed in table recordings';
  END IF;
END ;;

DELIMITER ;
