/************************  p_ema  *****************************/

DELIMITER $$

DROP PROCEDURE IF EXISTS p_ema$$

CREATE PROCEDURE `p_ema`( _code varchar(30), _days int)
BEGIN
	DECLARE _prog varchar(120);
	DECLARE _Method varchar(120);
	DECLARE _lastEmaDayId int;
	DECLARE _origLastEmaDayId int;
	DECLARE _lastDayId int;
    DECLARE _ema real;
    DECLARE _previosEma real;
    DECLARE _previosDEma real;

	SET _prog = 'p_ema';
    SET _Method  = '';

    SELECT Max(dayID) INTO _lastDayId FROM dayprice WHERE code = _code;
    SELECT Max(dayID) INTO _lastEmaDayId FROM ema WHERE code = _code and days = _days;

call p_log(_prog, _Method, CONCAT('Get _lastDayId and _lastEmaDayId: ' , cast(_lastDayId as char) , ' and ' , cast(_lastEmaDayId as char) ));
    IF _lastDayId is not null THEN

		IF _lastEmaDayId is null THEN
			/*calculate 1st ema*/
			INSERT INTO ema (code, dayId, days, ema)
			SELECT _code, _days, _days, avg(closeprice) FROM dayprice WHERE code = _code and dayId <= _days LIMIT 1;
			SET _lastEmaDayId = _days;
			SET _origLastEmaDayId = _days - 1;
		ELSE
			SET _origLastEmaDayId = _lastEmaDayId;
		END IF;

call p_log(_prog, _Method, CONCAT('SET _origLastEmaDayId: ', cast(_origLastEmaDayId as char)));

		WHILE _lastDayId > _lastEmaDayId DO
			/*EMAtoday=α * ( Pricetoday - EMAyesterday ) + EMAyesterday;*/
			/*α =  2/(N+1)*/
			SELECT ema, dema INTO _previosEma, _previosDEma FROM ema WHERE code = _code and dayId = _lastEmaDayId and days = _days;
call p_log(_prog, _Method, CONCAT('GET _previosEma and _previosDEma: ', cast(_previosEma as char) , ' and ' , cast(_previosDEma as char) , 'for ' , cast(_lastEmaDayId as char)) );

			SELECT (T.closePrice - _previosEma) * 2 /(_days + 1) + _previosEma INTO _ema FROM dayPrice T
			WHERE T.code = _code
			AND T.dayId = _lastEmaDayId + 1;
call p_log(_prog, _Method, CONCAT('Calculate Ema: ', cast(_ema as char) ));

			INSERT INTO ema (code, dayId, days, ema, dema, ddema)
			VALUES( _code, _lastEmaDayId + 1, _days, _ema, _ema - _previosEma, _ema - _previosEma - _previosDEma );
call p_log(_prog, _Method, CONCAT('Insert ema dema ddema to table: ', cast(_ema as char), ', ', cast(_ema - _previosEma as char) , ', ',  cast(_ema - _previosEma - _previosDEma as char) ));
			SET _lastEmaDayId = _lastEmaDayId + 1;

		END WHILE;

    END IF;
END$$
DELIMITER ;



