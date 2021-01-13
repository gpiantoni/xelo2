CREATE TABLE `electrode_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL COMMENT 'Name: Arbitrary name to refer to this channel group (this information is not used in BIDS).',
  `CoordinateSystem` text DEFAULT NULL COMMENT 'Coordinate System: Defines the coordinate system for the MEG/EEG/iEEG sensors.',
  `CoordinateUnits` text DEFAULT NULL COMMENT 'Coordinate Units: Units of the _electrodes.tsv',
  `IntendedFor` int(11) DEFAULT NULL COMMENT 'Intended For: The MRI/CT it refers to (should be a valid ID from the runs table)',
  PRIMARY KEY (`id`),
  KEY `IntendedFor` (`IntendedFor`),
  CONSTRAINT `electrode_groups_ibfk_1` FOREIGN KEY (`IntendedFor`) REFERENCES `runs` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('electrode_groups','CoordinateSystem','Image'),('electrode_groups','CoordinateSystem','ACPC'),('electrode_groups','CoordinateSystem','Pixels');
INSERT INTO `allowed_values` VALUES ('electrode_groups','CoordinateUnits','mm'),('electrode_groups','CoordinateUnits','m');

DELIMITER ;;

CREATE TRIGGER validate_CoordinateSystem_before_insert_to_electrode_groups
  BEFORE INSERT ON electrode_groups
  FOR EACH ROW
BEGIN
  IF NEW.CoordinateSystem IS NOT NULL AND
    BINARY NEW.CoordinateSystem NOT IN (
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
  IF NEW.CoordinateSystem IS NOT NULL AND
    BINARY NEW.CoordinateSystem NOT IN (
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
  IF NEW.CoordinateUnits IS NOT NULL AND 
    BINARY NEW.CoordinateUnits NOT IN (
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
  IF NEW.CoordinateUnits IS NOT NULL AND 
    BINARY NEW.CoordinateUnits NOT IN (
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
  `name` text DEFAULT NULL COMMENT 'Name: Name of the electrode contact point.',
  `x` float DEFAULT NULL COMMENT 'x: X position. The positions of the center of each electrode in xyz space. Units are in millimeters or pixels',
  `y` float DEFAULT NULL COMMENT 'y: Y position. The positions of the center of each electrode in xyz space. Units are in millimeters or pixels',
  `z` float DEFAULT NULL COMMENT 'z: Z position. The positions of the center of each electrode in xyz space. Units are in millimeters or pixels. If electrodes are in 2D space this should be a column of n/a values.',
  `size` float DEFAULT NULL COMMENT 'Size: Surface area of the electrode, in mm^2.',
  `material` text DEFAULT NULL COMMENT 'Material: Material of the electrodes.',
  `manufacturer` text DEFAULT NULL COMMENT 'Manufacturer: Recommended field to specify the manufacturer for each electrode. Can be used if electrodes were manufactured by more than one company.',
  `groups` text DEFAULT NULL COMMENT 'Group: Optional field to specify the group that the electrode is a part of.',
  `hemisphere` text DEFAULT NULL COMMENT 'Hemisphere: Optional field to specify the hemisphere in which the electrode is placed, one of ["L" or "R"] (use capital).',
  `type` text DEFAULT NULL COMMENT 'Type: Optional type of the electrode, e.g., cup, ring, clip-on, wire, needle, ...',
  `impedance` float DEFAULT NULL COMMENT 'Impedance: Impedance of the electrode in kOhm.',
  `dimension` text DEFAULT NULL COMMENT 'Dimension: Size of the group (grid/strip/probe) that this electrode belongs to. Must be of form [AxB] with the smallest dimension first (e.g., [1x8]).',
  KEY `electrode_group_id` (`electrode_group_id`),
  CONSTRAINT `electrodes_ibfk_1` FOREIGN KEY (`electrode_group_id`) REFERENCES `electrode_groups` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('electrodes','hemisphere','L'),('electrodes','hemisphere','R');

DELIMITER ;;

CREATE TRIGGER validate_hemisphere_before_insert_to_electrodes
  BEFORE INSERT ON electrodes
  FOR EACH ROW
BEGIN
  IF NEW.hemisphere IS NOT NULL AND
    BINARY NEW.hemisphere NOT IN (
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
  IF NEW.hemisphere IS NOT NULL AND
    BINARY NEW.hemisphere NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'electrodes'
    AND column_name = 'hemisphere')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column hemisphere is not allowed in table electrodes';
  END IF;
END ;;

DELIMITER ;
