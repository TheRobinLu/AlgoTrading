/************************  p_log  *****************************/
DELIMITER $$

DROP PROCEDURE IF EXISTS `p_log`$$

CREATE  PROCEDURE `p_log`(_program varchar(120), _method varchar(120), _comments varchar(2000))
BEGIN
	INSERT INTO log (program, method, comments, timestampe)
    VALUES (_program, _method, _comments, getdate());

END$$

DELIMITER ;

