CREATE TABLE `channel_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `Reference` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

CREATE TABLE `channels` (
  `channel_group_id` int(11) DEFAULT NULL,
  `name` text DEFAULT NULL,
  `type` text DEFAULT NULL,
  `units` text DEFAULT NULL,
  `low_cutoff` float DEFAULT NULL,
  `high_cutoff` float DEFAULT NULL,
  `reference` text DEFAULT NULL,
  `groups` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `notch` float DEFAULT NULL,
  `status` text DEFAULT NULL,
  `status_description` text DEFAULT NULL,
  KEY `channel_group_id` (`channel_group_id`),
  CONSTRAINT `channels_ibfk_1` FOREIGN KEY (`channel_group_id`) REFERENCES `channel_groups` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('channels','type','EEG'),('channels','type','ECOG'),('channels','type','SEEG'),('channels','type','EOG'),('channels','type','ECG'),('channels','type','EMG'),('channels','type','TRIG'),('channels','type','MISC'),('channels','type','REF'),('channels','type','OTHER');
INSERT INTO `allowed_values` VALUES ('channels','units','V'),('channels','units','mV'),('channels','units','μV'),('channels','units','µV'),('channels','units','bpm'),('channels','units','%');

DELIMITER ;;

CREATE TRIGGER validate_type_before_insert_to_channels
  BEFORE INSERT ON channels
  FOR EACH ROW
BEGIN
  IF NEW.type NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'channels'
    AND column_name = 'type')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column type is not allowed in table channels';
  END IF;
END ;;

CREATE TRIGGER validate_units_before_update_to_channels
  BEFORE UPDATE ON channels
  FOR EACH ROW
BEGIN
  IF NEW.units NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'channels'
    AND column_name = 'units')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column units is not allowed in table channels';
  END IF;
END ;;

CREATE TRIGGER validate_units_before_insert_to_channels
  BEFORE INSERT ON channels
  FOR EACH ROW
BEGIN
  IF NEW.units NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'channels'
    AND column_name = 'units')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column units is not allowed in table channels';
  END IF;
END ;;

CREATE TRIGGER validate_type_before_update_to_channels
  BEFORE UPDATE ON channels
  FOR EACH ROW
BEGIN
  IF NEW.type NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'channels'
    AND column_name = 'type')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column type is not allowed in table channels';
  END IF;
END ;;

DELIMITER ;
