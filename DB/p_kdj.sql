
DELIMITER $$
DROP PROCEDURE IF EXISTS p_kdj$$

CREATE DEFINER=`root`@`localhost` Procedure `p_KDJ` ( _code varchar(10), _days int, _period int)
BEGIN
	DECLARE _maxdayId int;
	DECLARE _maxdayIdDayPrice int;
	DECLARE _mindayId int;
	DECLARE _currDate Date;
	DECLARE _RSV real;
	DECLARE _close real;

	DECLARE _prog varchar(120);
	DECLARE _Method varchar(120);

	SET _prog = 'p_kdj';
    SET _Method  = '';

	IF _days = null THEN
		SET _days = 9;
    END IF;
	IF _period = null THEN
		SET _period = 9;
    END IF;        

	DELETE FROM KDJ WHERE code = _code and days = _days and period = _period AND J is null;

	SELECT  Max(dayId) into _maxdayId
	FROM KDJ WHERE code = _code and days = _days and period = _period;

call p_log(_prog, _Method, CONCAT('Get _maxdayId: ' , ifnull(cast(_maxdayId as char), 'NULL') ));

	SELECT Max(dayId) into _maxdayIdDayPrice
	FROM DayPrice WHERE code = _code;
call p_log(_prog, _Method, CONCAT('Get _maxdayIdDayPrice: ' , ifnull(cast(_maxdayIdDayPrice as char), 'NULL') ));

	IF _maxdayId is null THEN
		SET  _mindayId = _days + 1 ;

		SELECT  date,  closeprice INTO _currDate, _close FROM DayPrice WHERE code = _code AND dayId = _mindayId ;
call p_log(_prog, _Method, CONCAT('Get _currDate and _close: ' , ifnull(cast(_currDate as char), 'NULL'), ifnull(cast(_close as char),'NULL' )));

		SELECT (_close - min(lowprice))/(max(highprice)- min(lowprice)) * 100 INTO _RSV
		FROM DayPrice
		WHERE   code = _code AND dayId between _mindayId - _days and _mindayId;

		INSERT INTO KDJ (code, date, dayId, days, period, K, D, J)
		SELECT _code,
			_currDate,
			_mindayId,
			_days,
			_period,
			50 * 2/3 + _RSV /3,
			50 * 2/3 + (50 * 2/3 + _RSV /3)/3,
			 _RSV
		FROM DayPrice A
		WHERE A.code = _code
		AND A.dayId =  _mindayId;
		SET _maxdayId = _mindayId;

	END IF;


	WHILE _maxdayId <  _maxdayIdDayPrice DO
		SET _maxdayId = _maxdayId + 1;
		SELECT date , closeprice INTO _currDate, _close FROM DayPrice WHERE code = _code AND dayId = _maxdayId;
		SELECT( _close - min(lowprice))/(max(highprice)- min(lowprice)) * 100 INTO  _RSV
		FROM DayPrice
		WHERE   code = _code AND dayId between _maxdayId - _days and _maxdayId;

		INSERT INTO KDJ (code, date, dayId, days, period, K, D, J)
		SELECT _code,
			_currDate,
			_maxdayId,
			_days,
			_period,
			R.K * 2/3 + _RSV /3,
			R.D * 2/3 + (R.K * 2/3 + _RSV /3)/3, _RSV
		FROM DayPrice A, KDJ R
		WHERE A.code = _code
		AND A.code = R.code
		AND A.dayId = R.dayId + 1
		AND A.dayId = _maxdayId
		AND R.days = _days
		AND R.period = _period;

	END WHILE;
END$$
DELIMITER ;