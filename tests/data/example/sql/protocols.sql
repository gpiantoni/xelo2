CREATE TABLE `protocols` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) DEFAULT NULL,
  `metc` text NOT NULL COMMENT 'METC: Code of the METC protocol',
  `version` text DEFAULT NULL COMMENT 'Version: Text to indicate version',
  `date_of_signature` date DEFAULT NULL COMMENT 'Date of Signature: Date when the first protocol was signed',
  PRIMARY KEY (`id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `protocols_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('protocols','metc','07-260'),('protocols','metc','14-090'),('protocols','metc','14-420'),('protocols','metc','14-622'),('protocols','metc','16-816'),('protocols','metc','19-562');

DELIMITER ;;
CREATE TRIGGER validate_metc_before_insert_to_protocols
  BEFORE INSERT ON protocols
  FOR EACH ROW
BEGIN
  IF NEW.metc IS NOT NULL AND
    BINARY NEW.metc NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'protocols'
    AND column_name = 'metc')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column metc is not allowed in table protocols';
  END IF;
END ;;

CREATE TRIGGER validate_metc_before_update_to_protocols
  BEFORE UPDATE ON protocols
  FOR EACH ROW
BEGIN
  IF NEW.metc IS NOT NULL AND
    BINARY NEW.metc NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'protocols'
    AND column_name = 'metc')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column metc is not allowed in table protocols';
  END IF;
END ;;

DELIMITER ;
