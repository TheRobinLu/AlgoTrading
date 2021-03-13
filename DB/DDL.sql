DELIMITER $$

CREATE TABLE `stock`.`strategy` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `StrategyName` VARCHAR(45) NULL,
  `Description` VARCHAR(400) NULL,
  PRIMARY KEY (`id`));


CREATE TABLE `stradegyparameters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stradegyid` int NOT NULL,
  `intP1` int DEFAULT NULL,
  `intP2` int DEFAULT NULL,
  `intP3` int DEFAULT NULL,
  `intP4` int DEFAULT NULL,
  `decP5` decimal(10,2) DEFAULT NULL,
  `decP6` decimal(10,2) DEFAULT NULL,
  `decP7` decimal(10,2) DEFAULT NULL,
  `decP8` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `stock`.`backtestsummary` (
  `id` INT NOT NULL,
  `parameterId` INT NOT NULL,
  `code` VARCHAR(45) NOT NULL,
  `start` DATETIME NULL,
  `end` DATETIME NULL,
  `startprice` REAL NULL,
  `endprice` REAL NULL,
  `endValue` REAL NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `stock`.`backteatdetail` (
  `id` INT NOT NULL,
  `backteatid` INT NOT NULL,
  `dayid` INT NOT NULL,
  `cash` REAL NOT NULL,
  `unit` INT NOT NULL,
  `price` REAL NOT NULL,
  `EquityValue` REAL NOT NULL,
  PRIMARY KEY (`id`));

DELIMITER ;
