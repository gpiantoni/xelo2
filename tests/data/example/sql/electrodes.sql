CREATE TABLE `electrode_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `CoordinateSystem` text DEFAULT NULL,
  `CoordinateUnits` text DEFAULT NULL,
  `IntendedFor` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IntendedFor` (`IntendedFor`),
  CONSTRAINT `electrode_groups_ibfk_1` FOREIGN KEY (`IntendedFor`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER validate_CoordinateSystem_before_insert_to_electrode_groups
  BEFORE INSERT ON electrode_groups
  FOR EACH ROW
BEGIN
  IF NEW.CoordinateSystem NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'electrode_groups'
    AND column_name = 'CoordinateSystem')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column CoordinateSystem is not allowed in table electrode_groups';
  END IF;
END ;;

CREATE TRIGGER validate_CoordinateSystem_before_update_to_electrode_groups
  BEFORE UPDATE ON electrode_groups
  FOR EACH ROW
BEGIN
  IF NEW.CoordinateSystem NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'electrode_groups'
    AND column_name = 'CoordinateSystem')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column CoordinateSystem is not allowed in table electrode_groups';
  END IF;
END ;;

CREATE TRIGGER validate_CoordinateUnits_before_insert_to_electrode_groups
  BEFORE INSERT ON electrode_groups
  FOR EACH ROW
BEGIN
  IF NEW.CoordinateUnits NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'electrode_groups'
    AND column_name = 'CoordinateUnits')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column CoordinateUnits is not allowed in table electrode_groups';
  END IF;
END ;;

CREATE TRIGGER validate_CoordinateUnits_before_update_to_electrode_groups
  BEFORE UPDATE ON electrode_groups
  FOR EACH ROW
BEGIN
  IF NEW.CoordinateUnits NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'electrode_groups'
    AND column_name = 'CoordinateUnits')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column CoordinateUnits is not allowed in table electrode_groups';
  END IF;
END ;;

DELIMITER ;

CREATE TABLE `electrodes` (
  `electrode_group_id` int(11) DEFAULT NULL,
  `name` text DEFAULT NULL,
  `x` float DEFAULT NULL,
  `y` float DEFAULT NULL,
  `z` float DEFAULT NULL,
  `size` float DEFAULT NULL,
  `material` text DEFAULT NULL,
  `manufacturer` text DEFAULT NULL,
  `groups` text DEFAULT NULL,
  `hemisphere` text DEFAULT NULL,
  `type` text DEFAULT NULL,
  `impedance` float DEFAULT NULL,
  `dimension` text DEFAULT NULL,
  KEY `electrode_group_id` (`electrode_group_id`),
  CONSTRAINT `electrodes_ibfk_1` FOREIGN KEY (`electrode_group_id`) REFERENCES `electrode_groups` (`id`) ON DELETE CASCADE
) ;

DELIMITER ;;

CREATE TRIGGER validate_hemisphere_before_insert_to_electrodes
  BEFORE INSERT ON electrodes
  FOR EACH ROW
BEGIN
  IF NEW.hemisphere NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'electrodes'
    AND column_name = 'hemisphere')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column hemisphere is not allowed in table electrodes';
  END IF;
END ;;

CREATE TRIGGER validate_hemisphere_before_update_to_electrodes
  BEFORE UPDATE ON electrodes
  FOR EACH ROW
BEGIN
  IF NEW.hemisphere NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'electrodes'
    AND column_name = 'hemisphere')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column hemisphere is not allowed in table electrodes';
  END IF;
END ;;

DELIMITER ;
