DELIMITER $$
DROP PROCEDURE IF EXISTS p_buysalepoint$$
CREATE PROCEDURE `p_buysalepoint`( _code varchar(10), _start datetime, _end datetime)
BEGIN
 	DECLARE _prog varchar(120);
	DECLARE _Method varchar(120);
    DECLARE _startid int;
    DECLARE _endid int;
    DECLARE _highid int;
    DECLARE _lowid int;
    DECLARE _cursorid int;
    DECLARE _cnt int;
    DECLARE _period int;
    DECLARE _periodx int;
    DECLARE _gain real;
    DECLARE _loss real;
    DECLARE _gainx real;
    DECLARE _lossx real;
    DECLARE _currentprice real;

	SET _prog = 'p_buysalepoint';
    SET _Method  = '';
    SET _period = 20;
    SET _periodx = 30;
    SET _gain = 1.2;
    SET _loss = 0.95;
    SET _gainx = 1.3;
    SET _lossx = 0.92;

    SELECT Min(dayid) INTO _startid FROM dayprice where code = _code and date >= _start;
    SELECT Max(dayid) INTO _endid FROM dayprice where code = _code and date <= _end and date <= now() - INTERVAL 30 day;

    CREATE TEMPORARY TABLE IF NOT EXISTS _buysalepoint
        (`code` varchar(20) NOT NULL,
          `dayid` int NOT NULL,
          `closeprice` real null,
          `point` int NOT NULL
          );
    TRUNCATE TABLE _buysalepoint;

    SET _cursorid = _startid - 1;
    GOTHROUGH: WHILE _cursorid <= _endid DO

        -- IF gainx 30%
        SET _cursorid = _cursorid + 1;
        SET _highid = 0;
        SET _lowid = 0;
        SELECT closeprice INTO _currentprice FROM dayprice WHERE code = _code AND dayid = _cursorid;

        SELECT Min(dayid) INTO _highid FROM dayprice
        WHERE code = _code AND dayid between _cursorid and _cursorid + _periodx
            AND closeprice > _currentprice * _gainx;
        IF _highid > _cursorid THEN
        -- IF loss 10
            SELECT Min(dayid) INTO _lowid FROM dayprice
            WHERE code = _code AND dayid between _cursorid and _highid
                AND closeprice < _currentprice * _lossx ;
            IF _lowid = 0 THEN
                INSERT INTO _buysalepoint VALUE (_code, _cursorid, _currentprice, 2);
                ITERATE GOTHROUGH;
            END IF;
        END IF;
            -- check gain
        SELECT Min(dayid) INTO _highid FROM dayprice
        WHERE code = _code AND dayid between _cursorid and _cursorid + _period
            AND closeprice >  _currentprice * _gain;

        IF _highid > _cursorid THEN
            SELECT Min(dayid) INTO _lowid FROM dayprice
            WHERE code = _code AND dayid between _cursorid and _highid
                    AND closeprice < _currentprice * _loss ;

            IF _lowid = 0 THEN
                INSERT INTO _buysalepoint VALUE (_code, _cursorid, _currentprice, 1);
                ITERATE GOTHROUGH;
            END IF;
        END IF;

        SET _lowid = 0;
        SELECT Min(dayid) INTO _lowid FROM dayprice
        WHERE code = _code AND dayid between _cursorid and _cursorid + _periodx
            AND closeprice < _currentprice * _lossx ;

        IF _lowid >  _cursorid THEN
            INSERT INTO _buysalepoint VALUE (_code, _cursorid, _currentprice, -2);
            ITERATE GOTHROUGH;
        END IF;

        SELECT Min(dayid) INTO _lowid FROM dayprice
        WHERE code = _code AND dayid between _cursorid and _cursorid + _period
            AND closeprice < _currentprice * _loss ;

        IF _lowid >  _cursorid THEN
            INSERT INTO _buysalepoint VALUE (_code, _cursorid, _currentprice, -1);
            ITERATE GOTHROUGH;
        END IF;

        INSERT INTO _buysalepoint VALUE (_code, _cursorid, _currentprice, 0);
        --
    END WHILE GOTHROUGH;

    SELECT * FROM _buysalepoint;

END$$
DELIMITER ;
