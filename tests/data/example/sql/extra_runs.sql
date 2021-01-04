CREATE TABLE `runs_speak` (
  `run_id` int(11) DEFAULT NULL,
  `overt_covert` text DEFAULT NULL,
  UNIQUE KEY `run_id` (`run_id`),
  CONSTRAINT `runs_speak_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('runs_speak','overt_covert','overt'),('runs_speak','overt_covert','covert');

DELIMITER ;;

CREATE TRIGGER validate_overt_covert_before_insert_to_runs_speak
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
END ;;

CREATE TRIGGER validate_overt_covert_before_update_to_runs_speak
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
END ;;

DELIMITER ;

CREATE TABLE `runs_sensorimotor` (
  `run_id` int(11) DEFAULT NULL,
  `body_part` text DEFAULT NULL,
  `left_right` text DEFAULT NULL,
  `execution_imagery` text DEFAULT NULL,
  UNIQUE KEY `run_id` (`run_id`),
  CONSTRAINT `runs_sensorimotor_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('runs_sensorimotor','body_part','arm'),('runs_sensorimotor','body_part','elbow'),('runs_sensorimotor','body_part','foot'),('runs_sensorimotor','body_part','hand'),('runs_sensorimotor','body_part','indexfinger'),('runs_sensorimotor','body_part','leg'),('runs_sensorimotor','body_part','littlefinger'),('runs_sensorimotor','body_part','middlefinger'),('runs_sensorimotor','body_part','mouth'),('runs_sensorimotor','body_part','ringfinger'),('runs_sensorimotor','body_part','thumb'),('runs_sensorimotor','body_part','tongue');
INSERT INTO `allowed_values` VALUES ('runs_sensorimotor','left_right','left'),('runs_sensorimotor','left_right','right'),('runs_sensorimotor','left_right','both');
INSERT INTO `allowed_values` VALUES ('runs_sensorimotor','execution_imagery','execution'),('runs_sensorimotor','execution_imagery','imagery');

DELIMITER ;;

CREATE TRIGGER validate_body_part_before_insert_to_runs_sensorimotor
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
END ;;

CREATE TRIGGER validate_left_right_before_insert_to_runs_sensorimotor
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
END ;;

CREATE TRIGGER validate_execution_imagery_before_insert_to_runs_sensorimotor
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
END ;;

CREATE TRIGGER validate_body_part_before_update_to_runs_sensorimotor
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
END ;;

CREATE TRIGGER validate_left_right_before_update_to_runs_sensorimotor
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
END ;;

CREATE TRIGGER validate_execution_imagery_before_update_to_runs_sensorimotor
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
END ;;

DELIMITER ;

CREATE TABLE `runs_mario` (
  `run_id` int(11) DEFAULT NULL,
  `velocity` text DEFAULT NULL,
  UNIQUE KEY `run_id` (`run_id`),
  CONSTRAINT `runs_mario_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

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
END ;;

CREATE TRIGGER `replace_id_to_subtable_runs_sensorimotor` AFTER UPDATE ON `runs` FOR EACH ROW
BEGIN
  IF NEW.task_name <> OLD.task_name AND
    NEW.task_name IN ('somatosensory', 'motor') AND
    NEW.id NOT IN (SELECT run_id FROM runs_sensorimotor )
  THEN
    INSERT INTO runs_sensorimotor (run_id) VALUES (NEW.id) ;
  END IF;
END ;;

CREATE TRIGGER `replace_id_to_subtable_runs_speak` AFTER UPDATE ON `runs` FOR EACH ROW
BEGIN
  IF NEW.task_name <> OLD.task_name AND
    NEW.task_name IN ('picnam', 'verb') AND
    NEW.id NOT IN (SELECT run_id FROM runs_speak)
  THEN
    INSERT INTO runs_speak (run_id) VALUES (NEW.id) ;
  END IF;
END ;;

DELIMITER ;
