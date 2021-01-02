/************************  p_removehistory  *****************************/
DELIMITER $$

DROP PROCEDURE IF EXISTS `p_removehistory`$$

CREATE  PROCEDURE `p_removehistory`( _code varchar(30))
BEGIN
	DELETE FROM dayprice WHERE code = _code;
    DELETE FROM rsi WHERE code = _code;
    DELETE FROM ema WHERE code = _code;
    DELETE FROM kdj WHERE code = _code;
END$$

DELIMITER ;

