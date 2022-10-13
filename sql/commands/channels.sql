CREATE TABLE `channel_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL COMMENT 'Name: Arbitrary name to refer to this channel group (this information is not used in BIDS).',
  `Reference` text DEFAULT NULL COMMENT 'Reference: General description of the reference scheme used and (when applicable) of location of the reference electrode in the raw recordings (e.g., "left mastoid", "bipolar", "T01" for electrode with name T01, "intracranial electrode on top of a grid, not included with data", "upside down electrode").',
  PRIMARY KEY (`id`)
) ;

CREATE TABLE `channels` (
  `channel_group_id` int(11) DEFAULT NULL,
  `name` text DEFAULT NULL COMMENT 'Name: Label of the channel. The label must correspond to _electrodes.tsv name and all ieeg type channels are required to have a position.',
  `type` text DEFAULT NULL COMMENT 'Type: Type of channel.',
  `units` text DEFAULT NULL COMMENT 'Units: Physical unit of the value represented in this channel, e.g., V for Volt, specified according to the SI unit symbol and possibly prefix symbol (e.g., mV, μV).',
  `low_cutoff` float DEFAULT NULL COMMENT 'Low Cutoff: Frequencies used for the low pass filter applied to the channel in Hz. If no low pass filter was applied, use n/a. Note that anti-alias is a low pass filter, specify its frequencies here if applicable.',
  `high_cutoff` float DEFAULT NULL COMMENT 'High Cutoff: Frequencies used for the high pass filter applied to the channel in Hz. If no high pass filter applied, use n/a.',
  `reference` text DEFAULT NULL COMMENT 'Reference: Specification of the reference (e.g., "mastoid", "ElectrodeName01", "intracranial", "CAR", "other", "n/a"). If the channel is not an electrode channel (e.g., a microphone channel) use n/a',
  `groups` text DEFAULT NULL COMMENT 'Group: Which group of channels (grid/strip/seeg/depth) this channel belongs to. This is relevant because one group has one cable-bundle and noise can be shared. This can be a name or number. ',
  `description` text DEFAULT NULL COMMENT 'Description: Brief free-text description of the channel, or other information of interest (e.g., position (e.g., "left lateral temporal surface", etc.).',
  `notch` float DEFAULT NULL COMMENT 'Notch Filter: Frequencies used for the notch filter applied to the channel, in Hz. If no notch filter applied, use n/a.',
  `status` text DEFAULT NULL COMMENT 'Status: Data quality observed on the channel (good/bad). A channel is considered bad if its data quality is compromised by excessive noise. Description of noise type SHOULD be provided in [status_description].',
  `status_description` text DEFAULT NULL COMMENT 'Status Description: Freeform text description of noise or artifact affecting data quality on the channel. It is meant to explain why the channel was declared bad in [status].',
  KEY `channel_group_id` (`channel_group_id`),
  CONSTRAINT `channels_ibfk_1` FOREIGN KEY (`channel_group_id`) REFERENCES `channel_groups` (`id`) ON DELETE CASCADE
) ;

INSERT INTO `allowed_values` VALUES ('channels','type','EEG'),('channels','type','ECOG'),('channels','type','SEEG'),('channels','type','EOG'),('channels','type','ECG'),('channels','type','EMG'),('channels','type','TRIG'),('channels','type','MISC'),('channels','type','REF'),('channels','type','OTHER');
INSERT INTO `allowed_values` VALUES ('channels','units','V'),('channels','units','mV'),('channels','units','μV'),('channels','units','bpm'),('channels','units','%');

DELIMITER ;;

CREATE TRIGGER validate_type_before_insert_to_channels
  BEFORE INSERT ON channels
  FOR EACH ROW
BEGIN
  IF NEW.type IS NOT NULL AND
    BINARY NEW.type NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'channels'
    AND column_name = 'type')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column type is not allowed in table channels';
  END IF;
END ;;

CREATE TRIGGER validate_type_before_update_to_channels
  BEFORE UPDATE ON channels
  FOR EACH ROW
BEGIN
  IF NEW.type IS NOT NULL AND
    NEW.type NOT IN (
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
  IF NEW.units IS NOT NULL AND
    BINARY NEW.units NOT IN (
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
  IF NEW.units IS NOT NULL AND
    BINARY NEW.units NOT IN (
    SELECT allowed_value FROM allowed_values
    WHERE table_name = 'channels'
    AND column_name = 'units')
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'Entered value in column units is not allowed in table channels';
  END IF;
END ;;

DELIMITER ;
