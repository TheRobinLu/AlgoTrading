
DELIMITER $$
DROP PROCEDURE IF EXISTS p_RSI$$

CREATE  Procedure `p_RSI` ( _code varchar(10), _days int)
BEGIN
	DECLARE _maxdayId int;
	DECLARE _maxdayIdDayPrice int;
	DECLARE _mindayId int;
	DECLARE _currDate Date;
	DECLARE _EMAWeight real;

	DELETE FROM RSI WHERE code = _code and days = _days and RSI is null;

	SELECT Max(dayId) INTO _maxdayId
	FROM RSI WHERE code = _code and days = _days;

	SELECT Max(dayId) INTO _maxdayIdDayPrice
	FROM DayPrice WHERE code = _code;



	IF _maxdayId is null THEN
		SET  _mindayId = _days + 1 ;

		SELECT date into _currDate FROM DayPrice WHERE code = _code AND dayId = _mindayId;
		#initial avg U and D
		INSERT INTO RSI (code, date, dayId, days, AvgU, AvgD)
		SELECT _code, 
			_currDate,  
			_mindayId,
			_days,
			sum ((A.closePrice - B.closePrice) * (IIF ( A.closePrice > B.closePrice,1, 0 )))/_days,
			sum ((B.closePrice - A.closePrice) * (IIF ( A.closePrice < B.closePrice, 1 , 0 )))/_days
		FROM DayPrice A, DayPrice B 
		WHERE A.dayId = B.dayId + 1  
		AND A.code = B.code
		AND A.code = _code
		AND A.dayId between  _mindayId - _days + 1  AND  _mindayId;

		
		UPDATE RSI
		SET RSI = 100 * AvgU/ (AvgU + AvgD) 
		WHERE code = _code 
		AND dayId = _mindayId
		AND Days = _days;

		SET _maxdayId = _mindayId;

	END IF;

	SET _EMAWeight = 2/(cast(_days as real) + 1);
	SET _EMAWeight = 1/cast(_days as real);

	WHILE _maxdayId <  _maxdayIdDayPrice DO
		SET _maxdayId = _maxdayId + 1;

		SELECT date INTO _currDate FROM DayPrice WHERE code = _code AND dayId = _maxdayId;
			
		INSERT INTO RSI (code, date, dayId, days, AvgU, AvgD)
		SELECT _code, 
			_currDate,  
			_maxdayId,
			_days,
			(IIF ( A.closePrice > B.closePrice, (A.closePrice - B.closePrice), 0)  * _EMAWeight + R.AvgU * (1 - _EMAWeight )) , 
			(IIF ( A.closePrice < B.closePrice, (B.closePrice - A.closePrice), 0)  * _EMAWeight + R.AvgD * (1 - _EMAWeight )) 
		FROM DayPrice A, DayPrice B , RSI R
		WHERE A.code = B.code
		AND A.code = _code
		AND A.code = R.code
		AND A.dayId = B.dayId + 1  
		AND B.dayId = R.dayId
		AND A.dayId = _maxdayId
		AND R.days = _days;

	END WHILE;


	UPDATE RSI
	SET RSI = 100 * AvgU/ (AvgU + AvgD) 
	WHERE code = _code 
	AND dayId is not null
	AND Days = _days;
	

END $$

DELIMITER ;