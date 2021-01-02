CREATE TABLE `sessions_mri` (
  `session_id` int(11) DEFAULT NULL,
  `MagneticFieldStrength` text DEFAULT NULL,
  UNIQUE KEY `session_id` (`session_id`),
  CONSTRAINT `sessions_mri_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER add_id_to_subtable_sessions_mri
  AFTER INSERT ON sessions
  FOR EACH ROW
BEGIN
  IF NEW.name = 'MRI'
  THEN
    INSERT INTO sessions_mri (session_id) VALUES (NEW.id) ;
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

CREATE TRIGGER validate_MagneticFieldStrength_before_insert_to_sessions_mri
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
END ;;

CREATE TRIGGER validate_MagneticFieldStrength_before_update_to_sessions_mri
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
END ;;

DELIMITER ;

CREATE TABLE `sessions_or` (
  `session_id` int(11) DEFAULT NULL,
  `date_of_surgery` date DEFAULT NULL,
  UNIQUE KEY `session_id` (`session_id`),
  CONSTRAINT `sessions_or_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER add_id_to_subtable_sessions_or
  AFTER INSERT ON sessions
  FOR EACH ROW
BEGIN
  IF NEW.name = 'OR'
  THEN
    INSERT INTO sessions_or (session_id) VALUES (NEW.id) ;
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

DELIMITER ;

CREATE TABLE `sessions_iemu` (
  `session_id` int(11) DEFAULT NULL,
  `date_of_implantation` date DEFAULT NULL,
  `date_of_explantation` date DEFAULT NULL,
  UNIQUE KEY `session_id` (`session_id`),
  CONSTRAINT `sessions_iemu_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER add_id_to_subtable_sessions_iemu
  AFTER INSERT ON sessions
  FOR EACH ROW
BEGIN
  IF NEW.name = 'IEMU'
  THEN
    INSERT INTO sessions_iemu (session_id) VALUES (NEW.id) ;
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

DELIMITER ;
