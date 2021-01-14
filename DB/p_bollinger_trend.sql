DELIMITER $$
DROP PROCEDURE IF EXISTS p_bollinger_trend$$
CREATE PROCEDURE `p_bollinger_trend`( _code varchar(10), _days int, _trenddays int, _start datetime, _end datetime)
BEGIN
    DECLARE _startid int;
    DECLARE _endid int;
    DECLARE _cursorid int;
    DECLARE _cnt int;
    DECLARE _dev real;

 	DECLARE _prog varchar(120);
	DECLARE _Method varchar(120);

	SET _prog = 'p_bollinger_trend';
    SET _Method  = '';

	IF _days = null THEN
		SET _days = 20;
    END IF;
	IF _trenddays = null THEN
		SET _trenddays = 5;
    END IF;

    SELECT count(*) INTO _cnt FROM ema WHERE code = _code AND days = _days;

    IF _cnt = 0 THEN
		call p_ema(_code, _days);
	END IF;

    SELECT Min(D.dayid), Max(D.dayid) INTO _startid, _endid
    FROM dayprice D, ema E
    WHERE D.code = _code AND E.code = _code
    AND D.dayid = E.dayid
    AND E.days = _days
    AND D.date between _start and _end;


call p_log(_prog, _Method, CONCAT('Get _startid and _endid: ' , cast(_startid as char) , ' and ' , cast(_endid as char) ));

    CREATE TEMPORARY TABLE IF NOT EXISTS _bollinger
    (`code` varchar(20) NOT NULL,
	  `dayid` int NOT NULL,
      `date` datetime NOT NULL,
	  `days` int NOT NULL,
      `deviation` double NULL,
      `closeprice` double NULL,
	  `ema` double DEFAULT '0',
	  `dma` double DEFAULT '0'
      );
    TRUNCATE TABLE _bollinger;
    SET _cursorid = _startid;
    WHILE _cursorid <= _endid DO
		SELECT stddev(closeprice) INTO _dev FROM dayprice WHERE code = _code AND dayid between  _cursorid - _days + 1 and _cursorid;
        INSERT INTO _bollinger
		SELECT 	D.code,
			D.dayid,
            D.date,
			_days as days,
			_dev as Deviation,
			D.closeprice,
			E.ema,
            TE.dema
		FROM dayprice D, ema E, ema TE
		WHERE D.code = _code and E.code = _code and TE.code = _code
			AND D.dayId = E.dayId AND E.days = _days
			and D.dayid = TE.Dayid AND TE.days = _trenddays
            AND D.dayid = _cursorid;


        SET _cursorid = _cursorid + 1;

    END WHILE;

    SELECT * FROM _bollinger;


END$$
DELIMITER ;
