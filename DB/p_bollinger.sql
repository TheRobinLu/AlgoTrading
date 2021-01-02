DELIMITER $$
DROP PROCEDURE IF EXISTS p_bollinger$$
CREATE PROCEDURE `p_bollinger`( _code varchar(10), _days int, _emplify decimal(10,2), _start datetime)
BEGIN
    DECLARE _startid int;
    DECLARE _endid int;
    DECLARE _cursorid int;
    DECLARE _cnt int;
    DECLARE _dev real;

 	DECLARE _prog varchar(120);
	DECLARE _Method varchar(120);

	SET _prog = 'p_bollinger';
    SET _Method  = '';

	IF _days = null THEN
		SET _days = 10;
    END IF;
	IF _emplify = null THEN
		SET _emplify = 2;
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
    AND D.date > _start;

call p_log(_prog, _Method, CONCAT('Get _startid and _endid: ' , cast(_startid as char) , ' and ' , cast(_endid as char) ));

    CREATE TEMPORARY TABLE IF NOT EXISTS _bollinger
    (`code` varchar(20) NOT NULL,
	  `dayid` int NOT NULL,
	  `days` int NOT NULL,
	  `emplify` double NOT NULL,
      `deviation` double NULL,
      `closeprice` double NULL,
	  `ema` double DEFAULT '0',
	  `dma` double DEFAULT '0',
      `upper` double NULL,
      `lower` double NULL
      );
    TRUNCATE TABLE _bollinger;
    SET _cursorid = _startid;
    WHILE _cursorid <= _endid DO
		SELECT stddev(closeprice) INTO _dev FROM dayprice WHERE code = _code AND dayid between  _cursorid - _days + 1 and _cursorid;
        INSERT INTO _bollinger
		SELECT 	D.code,
			D.dayid,
			_days as days,
            _emplify as Emplify,
			_dev as Deviation,
			D.closeprice,
			E.ema,
            E.dema,
			E.ema + _dev * _emplify  as upper,
			E.ema - _dev * _emplify  as lower
		FROM dayprice D, ema E
		WHERE D.code = _code and E.code = _code
			AND D.dayId = E.dayId AND E.days = _days
			and D.dayid = E.Dayid
            AND D.dayid = _cursorid;

        SET _cursorid = _cursorid + 1;

    END WHILE;

    SELECT * FROM _bollinger;

END$$
DELIMITER ;
