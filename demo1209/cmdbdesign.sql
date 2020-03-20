SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

SHOW WARNINGS;
DROP SCHEMA IF EXISTS `cmdb_design` ;

CREATE SCHEMA IF NOT EXISTS `cmdb_design` DEFAULT CHARACTER SET utf8 ;
SHOW WARNINGS;
USE `cmdb_design` ;

DROP TABLE IF EXISTS `cmdb_design`.`release` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `cmdb_design`.`release` (
  `ReleaseID` INT(11) NOT NULL ,
  `Product_Descriptors` VARCHAR(50) NULL DEFAULT NULL,
  `DateTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Release_Branch_Name` VARCHAR(50) NOT NULL,
  `Version` INT(11) NOT NULL AUTO_INCREMENT,
  `SRP` VARCHAR(50) NULL DEFAULT NULL,
  `Tollgate_URL` VARCHAR(1024) NULL DEFAULT NULL,
  `Build_Machine` VARCHAR(1024) NULL DEFAULT NULL,
  `Jenkinsfile_Commit_No` VARCHAR(50) NULL DEFAULT NULL,
  `Software_Tools` VARCHAR(1024) NULL DEFAULT NULL,
  `Hardware_Platform` VARCHAR(1024) NULL DEFAULT NULL,
  `Testing_Tools` VARCHAR(1024) NULL DEFAULT NULL,
  `BoM` VARCHAR(1024) NULL DEFAULT NULL,
  `Comments` VARCHAR(100) NULL DEFAULT NULL,
  `DEF_DSRVW` VARCHAR(50) NULL DEFAULT NULL,
  `DSRVW_Status` VARCHAR(50) NULL DEFAULT NULL,
  `Product_Descriptor_Level3` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY `id_release_version` (Release_Branch_Name,Version))ENGINE=MyISAM 
DEFAULT CHARACTER SET = utf8;

SHOW WARNINGS;
CREATE UNIQUE INDEX `ReleaseID_UNIQUE` ON `cmdb_design`.`release` (`ReleaseID` ASC) ;

SHOW WARNINGS;
CREATE INDEX `SRP` ON `cmdb_design`.`release` (`SRP` ASC) ;

SHOW WARNINGS;

DROP TABLE IF EXISTS `cmdb_design`.`sco` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `cmdb_design`.`sco` (
  `SRP` VARCHAR(50)  NULL,
  `SCO` INT(11)  NULL,
  CONSTRAINT `fk_SRP_Release1`
    FOREIGN KEY (`SRP`)
    REFERENCES `cmdb_design`.`release` (`SRP`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

SHOW WARNINGS;
CREATE UNIQUE INDEX `SCO_UNIQUE` ON `cmdb_design`.`sco` (`SCO` ASC) ;

SHOW WARNINGS;
CREATE INDEX `SCO` ON `cmdb_design`.`sco` (`SCO` ASC) ;

SHOW WARNINGS;
CREATE INDEX `fk_SRP_Release1_idx` ON `cmdb_design`.`sco` (`SRP` ASC) ;

SHOW WARNINGS;

DROP TABLE IF EXISTS `cmdb_design`.`defect` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `cmdb_design`.`defect` (
  `SCO` INT(11)  NULL,
  `SRP` VARCHAR(50) NULL,
  `id` VARCHAR(50) NULL DEFAULT NULL,
  CONSTRAINT `fk_SCO_SRP`
    FOREIGN KEY (`SCO`)
    REFERENCES `cmdb_design`.`sco` (`SCO`),
  CONSTRAINT `fk_SCO_SRP1`
    FOREIGN KEY (`SRP`)
    REFERENCES `cmdb_design`.`sco` (`SRP`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

SHOW WARNINGS;
CREATE UNIQUE INDEX `SCO_UNIQUE` ON `cmdb_design`.`defect` (`SCO` ASC) ;

SHOW WARNINGS;
CREATE INDEX `fk_SCO_SRP_idx` ON `cmdb_design`.`defect` (`SCO` ASC) ;

SHOW WARNINGS;
CREATE INDEX `fk_SCO_SRP1_idx` ON `cmdb_design`.`defect` (`SRP` ASC) ;

SHOW WARNINGS;
DROP TABLE IF EXISTS `cmdb_design`.`repo` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `cmdb_design`.`repo` (
  `Repo_ID` VARCHAR(50) NOT NULL,
  `ReleaseID` INT(11) NOT NULL,
  `Repo_URL` VARCHAR(1024) NULL DEFAULT NULL,
  `Status` VARCHAR(50) NOT NULL,
  `DTR` VARCHAR(100) NULL DEFAULT NULL,
  `VersionFixed` VARCHAR(100) NULL DEFAULT NULL,
  PRIMARY KEY (`Repo_ID`),
  CONSTRAINT `fk_Repo_Release2`
    FOREIGN KEY (`ReleaseID`)
    REFERENCES `cmdb_design`.`release` (`ReleaseID`)
 ) ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;

SHOW WARNINGS;
CREATE UNIQUE INDEX `RepoID_UNIQUE` ON `cmdb_design`.`repo` (`Repo_ID` ASC) ;

SHOW WARNINGS;
CREATE INDEX `fk_Repo_Release1_idx` ON `cmdb_design`.`repo` (`ReleaseID` ASC) ;

SHOW WARNINGS;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- Table `cmdb_design`.`Properties`

-- -----------------------------------------------------
SHOW WARNINGS;
DROP TABLE IF EXISTS `cmdb_design`.`repocommits` ;

SHOW WARNINGS;
CREATE TABLE IF NOT EXISTS `cmdb_design`.`repocommits` (
  `Repo_Commit_ID` INT(11) NOT NULL AUTO_INCREMENT ,
  `Repo_ID` VARCHAR(50) NOT NULL,
  `Commit_No` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`Repo_Commit_ID`)
  )ENGINE = InnoDB;
  


SHOW WARNINGS;
CREATE UNIQUE INDEX `RepoCommitID_UNIQUE` ON `cmdb_design`.`repocommits` (`Repo_Commit_ID` ASC) ;



CREATE TABLE IF NOT EXISTS `cmdb_design`.`Properties` (

  

  `PropertyName` VARCHAR(45) NOT NULL,

  `PropertyValue` VARCHAR(100) NOT NULL,

  `VersionNo` INT NOT NULL AUTO_INCREMENT,

  `UpdatedBy` VARCHAR(45) NULL,

  `UpdatedTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  
  
  PRIMARY KEY `id_property_version` (PropertyName,VersionNo))ENGINE=MyISAM ;
  
  



 

CREATE TABLE IF NOT EXISTS `cmdb_design`.`AuditLogs` (

  `LogID` INT NOT NULL AUTO_INCREMENT,
  
  `BuildNumber` VARCHAR(45) NOT NULL,

  `ScriptName` VARCHAR(45) NULL,

  `LogLevel` VARCHAR(45) NULL,

  `LogMessage` VARCHAR(1024) NULL,

  `LogTimestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (`LogID`))

 


 

