CREATE TABLE `subjects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_of_birth` date DEFAULT NULL COMMENT 'Date of Birth: Date of birth of the participant',
  `sex` text DEFAULT NULL COMMENT 'Sex: Sex of the participant',
  `handedness` text DEFAULT NULL COMMENT 'Handedness: Handedness of the participant',
  PRIMARY KEY (`id`)
);

INSERT INTO `allowed_values` VALUES ('subjects','sex','Female'), ('subjects','sex','Male');
INSERT INTO `allowed_values` VALUES ('subjects','handedness','Left-handed'),('subjects','handedness','Right-handed'),('subjects','handedness','Ambidextrous');

DELIMITER ;;

CREATE TRIGGER validate_sex_before_insert_to_subjects
  BEFORE INSERT ON subjects
  FOR EACH ROW
BEGIN
  IF NEW.sex IS NOT NULL AND
    BINARY NEW.sex NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'subjects'
    AND column_name = 'sex')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column sex is not allowed in table subjects';
  END IF;
END ;;

CREATE TRIGGER validate_sex_before_update_to_subjects
  BEFORE UPDATE ON subjects
  FOR EACH ROW
BEGIN
  IF NEW.sex IS NOT NULL AND
    BINARY NEW.sex NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'subjects'
    AND column_name = 'sex')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column sex is not allowed in table subjects';
  END IF;
END ;;

CREATE TRIGGER validate_handedness_before_insert_to_subjects
BEFORE INSERT ON subjects
  FOR EACH ROW
BEGIN
  IF NEW.handedness IS NOT NULL AND
    BINARY NEW.handedness NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'subjects'
    AND column_name = 'handedness')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column handedness is not allowed in table subjects';
  END IF;
END ;;

CREATE TRIGGER validate_handedness_before_update_to_subjects
  BEFORE UPDATE ON subjects
  FOR EACH ROW
BEGIN
  IF NEW.handedness IS NOT NULL AND
    BINARY NEW.handedness NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'subjects'
    AND column_name = 'handedness')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column handedness is not allowed in table subjects';
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `subject_codes` (
  `subject_id` int(11) DEFAULT NULL,
  `code` varchar(256) NOT NULL COMMENT "Code: Unique identifier for each subject",
  UNIQUE KEY `code` (`code`),
  KEY `subject_id` (`subject_id`),
  CONSTRAINT `subject_codes_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE
) ;
