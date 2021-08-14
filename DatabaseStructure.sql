CREATE DATABASE IF NOT EXISTS `tragedy`;
USE `tragedy`;

--
-- Table structure for table `prefix`
--

DROP TABLE IF EXISTS `prefix`;


CREATE TABLE `prefix` (
  `guild` varchar(18) DEFAULT NULL,
  `prefix1` varchar(10) DEFAULT NULL,
  `prefix2` varchar(10) DEFAULT NULL,
  `prefix3` varchar(10) DEFAULT NULL,
  `prefix4` varchar(10) DEFAULT NULL,
  `prefix5` varchar(10) DEFAULT NULL,
  `defaultPrefix` varchar(3) DEFAULT 'xv ',
  UNIQUE KEY `guild` (`guild`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `warns`
--

DROP TABLE IF EXISTS `warns`;


CREATE TABLE `warns` (
  `id` varchar(10) NOT NULL,
  `guild` varchar(19) NOT NULL,
  `user` varchar(18) NOT NULL,
  `warner` varchar(18) NOT NULL,
  `reason` varchar(125) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `guild` (`guild`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `temp-emails`
--

DROP TABLE IF EXISTS `temp-emails`;


CREATE TABLE `temp-emails` (
  `user` varchar(18) NOT NULL,
  `email` varchar(255),
  UNIQUE KEY `user` (`user`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
