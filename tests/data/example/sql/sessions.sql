CREATE TABLE `sessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) DEFAULT NULL,
  `name` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER validate_name_before_insert_to_sessions
  BEFORE INSERT ON sessions
  FOR EACH ROW
BEGIN
  IF NEW.name NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'sessions'
    AND column_name = 'name')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column name is not allowed in table sessions';
  END IF;
END ;;


CREATE TRIGGER validate_name_before_update_to_sessions
  BEFORE UPDATE ON sessions
  FOR EACH ROW
BEGIN
  IF NEW.name NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'sessions'
    AND column_name = 'name')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column name is not allowed in table sessions';
  END IF;
END ;;

DELIMITER ;
