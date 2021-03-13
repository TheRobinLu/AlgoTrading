Executing:
USE `stock`;
DROP procedure IF EXISTS `p_bollinger_trend`;

USE `stock`;
DROP procedure IF EXISTS `stock`.`p_bollinger_trend`;
;

DELIMITER $$
USE `stock`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `p_bollinger_trend`( _code varchar(10), _emadays int, _demadays int, _demashort int, _start datetime, _end datetime)
BEGIN
    DECLARE _startid int;
    DECLARE _endid int;
    DECLARE _cursorid int;
    DECLARE _maxid int;
    DECLARE _dev real;

 	DECLARE _prog varchar(120);
	DECLARE _Method varchar(120);

	SET _prog = 'p_bollinger_trend';
    SET _Method  = '';

	IF _emadays = null THEN
		SET _emadays = 20;
    END IF;
	IF _demadays = null THEN
		SET _demadays = 5;
    END IF;

    SELECT max(dayid) INTO _maxid FROM dayprice WHERE code = _code;
    IF EXISTS (SELECT 1 FROM ema WHERE code = _code AND dayid = _maxid AND days = _emadays) THEN
		call p_ema(_code, _emadays);
    END IF;
call p_log(_prog, _Method, CONCAT('Checked ema data: ' , cast(_emadays as char) ));

    IF EXISTS (SELECT 1 FROM ema WHERE code = _code AND dayid = _maxid AND days = _demadays) THEN
		call p_ema(_code, _demadays);
    END IF;
call p_log(_prog, _Method, CONCAT('Checked dema data: ' , cast(_demadays as char) ));

    IF EXISTS (SELECT 1 FROM ema WHERE code = _code AND dayid = _maxid AND days = _demashort) THEN
		call p_ema(_code, _demashort);
    END IF;
call p_log(_prog, _Method, CONCAT('Checked short dema data: ' , cast(_demashort as char) ));

    SELECT Min(D.dayid), Max(D.dayid) INTO _startid, _endid
    FROM dayprice D, ema E
    WHERE D.code = _code AND E.code = _code
    AND D.dayid = E.dayid
    AND E.days = _emadays
    AND D.date between _start and _end;


call p_log(_prog, _Method, CONCAT('Get _startid and _endid: ' , cast(_startid as char) , ' and ' , cast(_endid as char) ));
	DROP TEMPORARY TABLE IF EXISTS _bollinger;
call p_log(_prog, _Method, 'DROP Temp Table');

    CREATE TEMPORARY TABLE IF NOT EXISTS _bollinger
    (`code` varchar(20) NOT NULL,
	  `dayid` int NOT NULL,
      `date` datetime NOT NULL,
		`closeprice` double NULL,
        `days` int NOT NULL,
		`deviation` double NULL,
	  `ema` double DEFAULT '0',
	  `dma` double DEFAULT '0',
      `sdma` double DEFAULT '0'
      );

call p_log(_prog, _Method, CONCAT('Create temp tabel ' ));

#    TRUNCATE TABLE _bollinger;
    SET _cursorid = _startid;
    WHILE _cursorid <= _endid DO
		SELECT stddev(closeprice) INTO _dev FROM dayprice WHERE code = _code AND dayid between  _cursorid - _emadays + 1 and _cursorid;
        call p_log(_prog, _Method, CONCAT('Get _dev and _cursorid ', cast(_dev as char), ' ', cast(_cursorid as char)));
        INSERT INTO _bollinger
		SELECT 	D.code,
			D.dayid,
            D.date,
			D.closeprice,
			_emadays as days,
			_dev as Deviation,
			E.ema,
            TE.dema,
            SE.dema
		FROM dayprice D, ema E, ema TE, ema SE
		WHERE D.code = _code and E.code = _code and TE.code = _code and SE.code = _code
			AND D.dayId = E.dayId AND E.days = _emadays
			and D.dayid = TE.Dayid AND TE.days = _demadays
			and D.dayid = SE.Dayid AND SE.days = _demadays
            AND D.dayid = _cursorid
            AND E.ema is not null AND TE.dema;

        SET _cursorid = _cursorid + 1;

    END WHILE;

    SELECT * FROM _bollinger;


END$$

DELIMITER ;
;



