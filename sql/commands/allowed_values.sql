CREATE TABLE `allowed_values` (
  `table_name` text NOT NULL,
  `column_name` text NOT NULL,
  `allowed_value` text NOT NULL
);

DELIMITER ;;

CREATE TRIGGER prevent_duplicated_allowed_values
  BEFORE INSERT ON allowed_values
  FOR EACH ROW
BEGIN
  IF EXISTS (
    SELECT 1 FROM `allowed_values` WHERE
      `table_name` = NEW.table_name AND
      `column_name` = NEW.column_name AND
      `allowed_value` = NEW.allowed_value)
  THEN
    SIGNAL SQLSTATE '2201R' SET MESSAGE_TEXT = 'The entered allowed value already exists for this table / column';
  END IF;
END ;;

DELIMITER ;
