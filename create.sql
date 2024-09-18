DROP TABLE IF EXISTS `form1`;
DROP TABLE IF EXISTS `prerequisites`;
DROP TABLE IF EXISTS `scheduling`;
DROP TABLE IF EXISTS `transcripts`;
DROP TABLE IF EXISTS `studInfo`;
DROP TABLE IF EXISTS `advisingForm`;
DROP TABLE IF EXISTS `courses`;

DROP TABLE IF EXISTS `recommendationletter`;
DROP TABLE IF EXISTS `priordegrees`;
DROP TABLE IF EXISTS `app_transcript`;
DROP TABLE IF EXISTS `been_reviewed`;
DROP TABLE IF EXISTS `reviewform`;
DROP TABLE IF EXISTS `application`;
DROP TABLE IF EXISTS `pre_app`;

DROP TABLE IF EXISTS `role_assign`;
DROP TABLE IF EXISTS `users`;


CREATE TABLE `users` (
    `uid` int NOT NULL, 
    `fname` varchar(255) DEFAULT NULL, 
    `lname` varchar(255) DEFAULT NULL, 
    `email` varchar(255) NOT NULL, 
    `password` varchar(255) DEFAULT NULL, 
    `role` enum('applicant', 'admin', 'reviewer', 'user', 'gs', 'chair', 'grad_student', 'professor', 'advisor', 'alumni', 'registrar') DEFAULT NULL, 
    `address` varchar(255) DEFAULT NULL, 
    `birthday` varchar(50) DEFAULT NULL, 
PRIMARY KEY (`uid`, `email`), 
UNIQUE KEY `uid` (`uid`), 
UNIQUE KEY `email` (`email`)
);

CREATE TABLE `role_assign` (
    `uid` int NOT NULL, 
    `role` enum('applicant', 'admin', 'reviewer', 'user', 'gs', 'chair', 'grad_student', 'professor', 'advisor', 'alumni', 'registrar') DEFAULT 'user', 
PRIMARY KEY (`uid`, `role`),
CONSTRAINT `role_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON UPDATE CASCADE
);

CREATE TABLE `pre_app` (
    `userid` int NOT NULL AUTO_INCREMENT, 
    `email` varchar(50) NOT NULL, 
    `fname` varchar(50) NOT NULL, 
    `lname` varchar(50) NOT NULL, 
    `password` varchar(50) NOT NULL, 
    `role` enum('applicant', 'admin', 'reviewer', 'user', 'gs', 'chair, advisor, professor, grad_student', 'alumni') NOT NULL DEFAULT 'user', 
PRIMARY KEY (`userid`, `email`)
);

CREATE TABLE `application` (
    `applicationid` int NOT NULL AUTO_INCREMENT, 
    `userid` int NOT NULL, `status` enum('application incomplete', 'application complete and under review', 'decision') DEFAULT NULL,
    `decision` enum( 'admit', 'admit with aid', 'reject', 'undecided') DEFAULT NULL, 
    `decision_date` date, 
    `submission_date` date, 
    `firstname` varchar(50) DEFAULT NULL, 
    `lastname` varchar(50) DEFAULT NULL, 
    `address` varchar(255) DEFAULT NULL, 
    `ssn` varchar(255) NOT NULL,
    `phonenumber` varchar(255) DEFAULT NULL,
    `degreessought` enum('MS', 'PHD') DEFAULT NULL,
    `areas_interest` varchar(255) DEFAULT NULL,
    `priordegrees` enum('BS', 'MS') DEFAULT NULL,
    `greverbal` varchar(3) DEFAULT NULL,
    `grequantitative` varchar(3) DEFAULT NULL,
    `greyearofexam` varchar(4) DEFAULT NULL, 
    `greadvancedscore` varchar(3) DEFAULT NULL,
    `greadvancedsubject` varchar(255) DEFAULT NULL, 
    `priorwork` varchar(255) DEFAULT NULL,
    `uid` int NOT NULL, 
    `semester` varchar(10) DEFAULT NULL,
    `year` varchar(4) DEFAULT NULL, 
    `rec_status` enum('received', 'not received') DEFAULT 'not received',
    `student_decision` enum('undecided', 'accept', 'reject') DEFAULT 'undecided',
    `deposit` enum('received', 'not received') DEFAULT 'not received',
    `matriculated` int(1) DEFAULT 0, 
PRIMARY KEY( `applicationid`, `userid`, `uid`), 
UNIQUE KEY `userid` (`userid`),
UNIQUE KEY `uid` (`uid`), 
CONSTRAINT `application_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `pre_app` (`userid`) ON UPDATE CASCADE) 
AUTO_INCREMENT = 3 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE `reviewform` (
    `reviewid` int NOT NULL AUTO_INCREMENT, 
    `userid` int DEFAULT NULL, 
    `reviewerid` int NOT NULL, 
    `gas_decision` varchar(30) DEFAULT NULL, 
    `missing_course` varchar(255) DEFAULT NULL, 
    `reasons_reject` varchar(20) DEFAULT NULL, 
    `reviewer_comment` varchar(255) DEFAULT NULL, 
    `recommended_advisor` varchar(100) DEFAULT NULL, 
    `review_status` varchar(255) DEFAULT NULL, `finaldecision` enum('reject', 'admit', 'admit with aid', 'undecided') DEFAULT 'undecided', 
    `timestamp` date DEFAULT NULL, 
PRIMARY KEY (`reviewid`, `reviewerid`), 
UNIQUE KEY `unique_reviewerid_userid` (`reviewerid`, `userid`), 
KEY `userid_index` (`userid`), 
CONSTRAINT `reviewform_ibfk_1` FOREIGN KEY (`reviewerid`) REFERENCES `users` (`uid`) ON UPDATE CASCADE, 
CONSTRAINT `reviewform_ibfk_2` FOREIGN KEY (`userid`) REFERENCES `application` (`userid`) ON UPDATE CASCADE
);

CREATE TABLE `been_reviewed` (
    `reviewerid` int NOT NULL, 
    `reviewid` int NOT NULL, 
PRIMARY KEY (`reviewerid`, `reviewid`), 
KEY `reviewid` (`reviewid`), 
CONSTRAINT `been_reviewed_ibfk_1` FOREIGN KEY (`reviewerid`) REFERENCES `users` (`uid`) ON UPDATE CASCADE, 
CONSTRAINT `been_reviewed_ibfk_2` FOREIGN KEY (`reviewid`) REFERENCES `reviewform` (`reviewid`)
);

CREATE TABLE `app_transcript` (
    `transcriptid` int NOT NULL AUTO_INCREMENT, 
    `userid` int DEFAULT NULL, 
    `method` enum('mail', 'link') DEFAULT NULL,
    `link` varchar(255) DEFAULT NULL, 
    `transcriptstatus` enum('received', 'not received') DEFAULT 'not received', 
PRIMARY KEY (`transcriptid`), 
KEY `userid` (`userid`), 
CONSTRAINT `app_transcript_ibfk_1` FOREIGN KEY (`transcriptid`) REFERENCES `application` (`applicationid`) ON UPDATE CASCADE
);

CREATE TABLE `priordegrees` (
    `applicationid` int DEFAULT NULL, 
    `userid` int NOT NULL, 
    `degree_type` enum('BS', 'MS') NOT NULL, 
    `year` varchar(4) DEFAULT NULL, 
    `gpa` varchar(4) DEFAULT NULL, 
    `school` varchar(255) DEFAULT NULL, 
    `major` varchar(100) DEFAULT NULL COMMENT 'New column', 
PRIMARY KEY (`userid`, `degree_type`), KEY `applicationid` (`applicationid`), 
CONSTRAINT `priordegrees_ibfk_1` FOREIGN KEY (`applicationid`) REFERENCES `application` (`applicationid`) ON UPDATE CASCADE, 
CONSTRAINT `priordegrees_ibfk_2` FOREIGN KEY (`userid`) REFERENCES `application` (`userid`) ON UPDATE CASCADE
);

CREATE TABLE `recommendationletter` (
    `letterid` int NOT NULL AUTO_INCREMENT, 
    `userid` int DEFAULT NULL, 
    `rec_name` varchar(100) DEFAULT NULL, 
    `rec_email` varchar(100) DEFAULT NULL, 
    `rec_letter` varchar(255) DEFAULT NULL,
    `rating` varchar(10) DEFAULT NULL, 
    `generic` varchar(10) DEFAULT NULL, 
    `credible` varchar(10) DEFAULT NULL,  
    `status` enum('received', 'not received') DEFAULT 'not received', 
PRIMARY KEY (`letterid`), KEY `userid` (`userid`), 
CONSTRAINT `recommendationletter_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `application` (`userid`) ON UPDATE CASCADE
);

CREATE TABLE `courses` (
    `crn` int NOT NULL, 
    `prof_uid` int NOT NULL, 
    `cid` char(4) NOT NULL, 
    `dept` varchar(50) NOT NULL, 
    `title` varchar(50) NOT NULL, 
    `credits` int NOT NULL, 
PRIMARY KEY (`crn`, `prof_uid`), 
KEY `prof_uid` (`prof_uid`), 
CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`prof_uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE
);

CREATE TABLE `studInfo` (
    `uid` int NOT NULL, 
    `program` varchar(50) NOT NULL, 
    `grad_status` varchar(50) NOT NULL, 
    `thesislink` varchar(50) DEFAULT NULL, 
    `thesisApp` int DEFAULT NULL, 
    `gpa` float DEFAULT NULL, 
    `fid` int DEFAULT NULL, 
    `reg_approval` int(1) DEFAULT 0,
    `form1App` int(1) DEFAULT 0,
PRIMARY KEY (`uid`)
);

CREATE TABLE `transcripts` (
    `grade` varchar(2) DEFAULT 'IP', 
    `semester` varchar(12) NOT NULL, 
    `section` int DEFAULT NULL, 
    `uid` int NOT NULL, 
    `grade_edited` tinyint(1) DEFAULT '0', 
    `tid` varchar(8) NOT NULL, 
    `year` varchar(4) DEFAULT NULL, 
    `crn` int NOT NULL, PRIMARY KEY (`uid`, `semester`, `tid`, `crn`), 
    KEY `crn` (`crn`), 
CONSTRAINT `transcripts_ibfk_1` FOREIGN KEY (`crn`) REFERENCES `courses` (`crn`) ON UPDATE CASCADE, 
CONSTRAINT `transcripts_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON UPDATE CASCADE, 
CONSTRAINT `transcripts_chk_1` CHECK ((`grade` in ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP')))
);

CREATE TABLE `scheduling` (
    `cid` char(4) NOT NULL, 
    `class_day` varchar(2) DEFAULT NULL, 
    `class_time` varchar(20) DEFAULT NULL, 
    `semester` varchar(20) NOT NULL, 
    `section` int NOT NULL, 
    `class_size` int DEFAULT NULL, 
    `crn` int NOT NULL, 
PRIMARY KEY (`cid`, `semester`, `section`, `crn`), 
KEY `crn` (`crn`), 
CONSTRAINT `scheduling_ibfk_1` FOREIGN KEY (`crn`) REFERENCES `courses` (`crn`) ON UPDATE CASCADE
);

CREATE TABLE `prerequisites` (
    `crn` int NOT NULL, 
    `prereq_ID` int NOT NULL, 
PRIMARY KEY (`crn`, `prereq_ID`), 
CONSTRAINT `prerequisites_ibfk_1` FOREIGN KEY (`crn`) REFERENCES `courses` (`crn`) ON UPDATE CASCADE
);

CREATE TABLE `form1` (
    `uid` int NOT NULL, 
    `crn` int NOT NULL, 
PRIMARY KEY (`uid`, `crn`), 
KEY `crn` (`crn`), 
CONSTRAINT `form1_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON UPDATE CASCADE, 
CONSTRAINT `form1_ibfk_2` FOREIGN KEY (`crn`) REFERENCES `courses` (`crn`) ON UPDATE CASCADE
);

CREATE TABLE `advisingForm` (
    `uid` int NOT NULL, 
    `crn` int NOT NULL, 
PRIMARY KEY (`uid`, `crn`), 
KEY `crn` (`crn`),
CONSTRAINT `advisingForm_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON UPDATE CASCADE, 
CONSTRAINT `advisingForm_ibfk_2` FOREIGN KEY (`crn`) REFERENCES `courses` (`crn`) ON UPDATE CASCADE
);



-- APPS Dummy Data
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11115111, 'Gustavo', 'Londono', 'gs@gmail.com', 'pass', 'gs');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (78542937, 'Hashem', 'Abdel Ati', 'chair@gmail.com', 'pass', 'chair');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (98760935, 'Tim', 'Wood', 'wood@gmail.com', 'pass', 'reviewer');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (55555522, 'Rachelle', 'Heller', 'heller@gmail.com', 'pass', 'reviewer');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (66666666, 'Thomas', 'Schmidt', 'admin@gmail.com', 'pass', 'admin');
INSERT INTO pre_app ( userid, email, fname, lname, password, role) VALUES (7, 'johnlennon@gmail.com', 'John', 'Lennon', 'pass', 'applicant');
INSERT INTO application (applicationid, userid, status, decision, submission_date, firstname, lastname, address, ssn, phonenumber, degreessought, areas_interest, priordegrees, greverbal, grequantitative, greyearofexam, greadvancedscore, greadvancedsubject, priorwork, uid, semester, year) VALUES (1, 7, 'application complete and under review', 'undecided', CURRENT_TIMESTAMP, 'John', 'Lennon', '123 Main St, City, Country', '111-11-1111', '555-123-4567', 'MS', 'Computer Science', 'BS', '160', '165', '2022', '115', 'Math','Software Engineer', 12312312, 'Fall', '2025');
INSERT INTO priordegrees (applicationid, userid, degree_type, year, gpa, school, major)VALUES (1, 7, 'BS', '2018', '3.80', 'George Washington University', 'Computer Science');
INSERT INTO recommendationletter (letterid, userid, rec_name, rec_email, rec_letter, status)VALUES (1, 7, 'Yoko Ono', 'yoko@example.com', 'Strongly recommend John for the program', 'received');
INSERT INTO recommendationletter (letterid, userid, rec_name, rec_email, rec_letter, status)VALUES (2, 7, 'Gustavo', 'gustavo@example.com', 'acccept him', 'received');
INSERT INTO recommendationletter (letterid, userid, rec_name, rec_email, rec_letter, status)VALUES (3, 7, 'Aaron', 'aaron@example.com', 'dont let him in', 'received');
INSERT INTO app_transcript (userid, method, transcriptstatus) VALUES (7, 'mail','received');
INSERT INTO pre_app ( userid, email, fname, lname, password, role) VALUES (8, 'ringostarr@gmail.com', 'ringo', 'starr', 'pass', 'applicant');
INSERT INTO application (userid, status, decision, applicationid,firstname, lastname, address, ssn, phonenumber, degreessought, areas_interest, greverbal, grequantitative, greyearofexam, priorwork, uid, semester, year) VALUES (8, 'application incomplete', 'undecided', 2,'Ringo', 'Starr', '456 Oak St, Town, Country', '222-11-1111', '555-987-6543', 'PHD', 'Physics', '155', '160', '2023', 'Research Assistant', 66666666,'Spring', '2025');
INSERT INTO priordegrees (applicationid, userid, degree_type, year, gpa, school, major) VALUES (2,8, 'BS', '2017', '3.6', 'ABC University', 'Physics');
INSERT INTO recommendationletter (letterid, userid, rec_name, rec_email, rec_letter, status) VALUES (4, 8, 'Dr. Smith', 'smith@example.com', 'Really great person','not received');
INSERT INTO recommendationletter (letterid, userid, rec_name, rec_email, rec_letter, status) VALUES (5, 8, 'Dr. John', 'john@example.com','Cool guy', 'not received');
INSERT INTO recommendationletter (letterid, userid, rec_name, rec_email, rec_letter, status) VALUES (6, 8, 'Dr. Tiny', 'tiny@example.com','personable', 'not received');
INSERT INTO app_transcript (userid, transcriptstatus) VALUES (8, 'not received');


-- REGS data 
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111112, 'teststudent2', 'testlname2', 'testuser2@gmail.com', 'pass', 'grad_student', 'testhouse2');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111113, 'Connor', 'Cheung', 'cheung@gmail.com', 'pass', 'grad_student', 'Muson');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111114, 'Reichle', 'Ji', 'reichle@gmail.com', 'pass', 'grad_student', 'Amdam');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111115, 'Hernandez', 'Adelina', 'adelina@gmail.com', 'pass', 'grad_student', 'Amdam');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111116, 'Vaidyan', 'Hannah', 'vaidyan@gmail.com', 'pass', 'grad_student', 'Amdam');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111117, 'Thompson', 'Tadhg', 'thompson@gmail.com', 'pass', 'grad_student', 'Amdam');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111118, 'Foster', 'Meghan', 'foster@gmail.com', 'pass', 'grad_student', 'Mitchell');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111119, 'Devito', 'Danny', 'devito@gmail.com', 'pass', 'grad_student', 'Hensley');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (11111121, 'Felix', 'Joao', 'felix@gmail.com', 'pass', 'grad_student', 'Hensley');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (99999999, 'Diana', 'Krall', 'krall@gmail.com', 'pass', 'grad_student', 'south');
INSERT INTO users (uid, fname, lname, email, password, role, address) VALUES (88888888, 'Billie', 'Holiday', 'holiday@gmail.com', 'pass', 'grad_student', 'California');

INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111112, 'Masters', 'Graduate', 87650987);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111113, 'Doctorate', 'Graduate', 11111125);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111114, 'Masters', 'Graduate', 87650987);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111115, 'Doctorate', 'Graduate', 11111125);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111116, 'Masters', 'Graduate', 87650987);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111117, 'Doctorate', 'Graduate', 11111125);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111118, 'Masters', 'Graduate', 87650987);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111119, 'Doctorate', 'Graduate', 11111125);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (11111121, 'Masters', 'Graduate', 87650987);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (99999999, 'Doctorate', 'Graduate', 11111125);
INSERT INTO studInfo (uid, program, grad_status, fid, reg_approval, gpa) VALUES (88888888, 'Masters', 'Graduate', 87650987, 1, 0.0);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (60606060, 'Doctorate', 'Graduate', 87650987);
INSERT INTO studInfo (uid, program, grad_status, fid) VALUES (12345654, 'Doctorate', 'Graduate', 11111125);

INSERT INTO role_assign (uid, role) VALUES (11111112, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (11111113, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (11111114, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (11111115, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (11111116, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (11111117, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (11111118, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (11111119, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (11111121, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (99999999, 'grad_student');
INSERT INTO role_assign (uid, role) VALUES (88888888, 'grad_student');



INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (87650987, 'June', 'Narahari', 'narahari@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111124, 'Hashem', 'Abdelati', 'abdelati@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111125, 'Bella', 'Dayrit', 'dayrit@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111126, 'Niquita', 'Varier', 'varier@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111127, 'Yelizaveta', 'Hernandaz', 'hernandaz@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111128, 'Derek', 'Chen', 'chen@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111129, 'Zac', 'Hardiman', 'hardiman@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111131, 'Penguin', 'Pingu', 'pingu@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111132, 'John', 'Smith', 'smith@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111133, 'Scarlet', 'Witch', 'witch@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111134, 'Chai', 'Dadog', 'dadog@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111135, 'Dribble', 'DaTurtle', 'daturtle@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111136, 'Agatha', 'Christie', 'christie@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111137, 'Rick', 'Riordan', 'riordan@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111138, 'Percy', 'Jackson', 'jackson@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111139, 'Annabeth', 'Chase', 'chase@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111141, 'Thalia', 'Grace', 'grace@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111142, 'Jason', 'Todd', 'grace2@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111143, 'Harry', 'Potter', 'potter@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111144, 'Hermione', 'Granger', 'granger@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111145, 'Cristiano', 'Ronaldo', 'ronaldo@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111146, 'Lionel', 'Messi', 'messi@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111147, 'Bruce', 'Willis', 'willis@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (11111122, 'secretary', 'secretarylname', 'secretary@gmail.com', 'pass', 'gs');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (22222232, 'Hyeong-Ah', 'Choi', 'choi@gmail.com', 'pass', 'professor');
INSERT INTO users (uid, fname, lname,  email, password, role) VALUES (12524233, 'reg', 'regs', 'regs@gmail.com', 'pass', 'registrar');


INSERT INTO role_assign (uid, role) VALUES (87650987, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111124, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111125, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111126, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111127, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111128, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111129, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111131, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111132, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111133, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111134, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111135, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111136, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111137, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111138, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111139, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111141, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111142, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111143, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111144, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111145, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111146, 'professor');
INSERT INTO role_assign (uid, role) VALUES (11111147, 'professor');
INSERT INTO role_assign (uid, role) VALUES (22222232, 'professor');

INSERT INTO role_assign (uid, role) VALUES (12524233, 'registrar');

-- Insert advisors
INSERT INTO role_assign (uid, role) VALUES (87650987, 'advisor');
INSERT INTO role_assign (uid, role) VALUES (11111124, 'advisor');
INSERT INTO role_assign (uid, role) VALUES (11111125, 'advisor');
INSERT INTO role_assign (uid, role) VALUES (11111126, 'advisor');
INSERT INTO role_assign (uid, role) VALUES (11111127, 'advisor');
INSERT INTO role_assign (uid, role) VALUES (11111128, 'advisor');
INSERT INTO role_assign (uid, role) VALUES (11111138, 'advisor');
INSERT INTO role_assign (uid, role) VALUES (11111134, 'advisor');

INSERT INTO role_assign (uid, role) VALUES (87650987, 'reviewer');


INSERT INTO courses VALUES (2,  87650987, 6461,'CSCI', 'Computer Architecture', 3);
INSERT INTO courses VALUES(3, 22222232, 6212, 'CSCI', 'Algorithms', 3);
INSERT INTO courses VALUES (1, 11111124, 6221, 'CSCI', 'SW Paradigms', 3);
INSERT INTO courses VALUES(4, 11111127, 6220, 'CSCI', 'Machine Learning', 3);
INSERT INTO courses VALUES(5, 11111128, 6232, 'CSCI', 'Networks 1', 3);
INSERT INTO courses VALUES(6, 11111129, 6233, 'CSCI', 'Networks 2', 3);
INSERT INTO courses VALUES(7, 11111131, 6241, 'CSCI', 'Database 1', 3);
INSERT INTO courses VALUES(8, 11111132, 6242, 'CSCI', 'Database 2', 3);
INSERT INTO courses VALUES(9, 11111133, 6246, 'CSCI', 'Compilers', 3);
INSERT INTO courses VALUES(10, 11111134, 6260, 'CSCI', 'Multimedia', 3);
INSERT INTO courses VALUES(11, 11111135, 6251, 'CSCI', 'Cloud Computing', 3);
INSERT INTO courses VALUES(12, 11111136, 6254, 'CSCI', 'SW Engineering', 3);
INSERT INTO courses VALUES(13, 11111137, 6262, 'CSCI', 'Graphics 1', 3);
INSERT INTO courses VALUES(14, 11111138, 6283, 'CSCI', 'Security 1', 3);
INSERT INTO courses VALUES(15, 11111139, 6284, 'CSCI', 'Cryptography', 3);
INSERT INTO courses VALUES(16, 11111141, 6286, 'CSCI', 'Network Security', 3);
INSERT INTO courses VALUES(17, 11111142, 6325, 'CSCI', 'Algorithms 2', 3);
INSERT INTO courses VALUES(18, 11111143, 6339, 'CSCI', 'Embedded Systems', 3);
INSERT INTO courses VALUES(19, 11111144, 6384, 'CSCI', 'Cryptography 2', 3);
INSERT INTO courses VALUES(20, 11111145, 6241, 'ECE', 'Communication Theory', 3);
INSERT INTO courses VALUES(21, 11111146, 6242, 'ECE', 'Information Theory', 2);
INSERT INTO courses VALUES(22, 11111147, 6210, 'MATH', 'Logic', 2);
INSERT INTO courses VALUES(23, 11111125, 6461, 'CSCI', 'Wompwomp', 3);

INSERT INTO prerequisites  VALUES (6, 5);
INSERT INTO prerequisites VALUES (8, 7);
INSERT INTO prerequisites VALUES (9, 23);
INSERT INTO prerequisites VALUES (9, 3);
INSERT INTO prerequisites VALUES (11, 20);
INSERT INTO prerequisites VALUES (12, 23);
INSERT INTO prerequisites VALUES (14, 3);
INSERT INTO prerequisites VALUES (15, 3);
INSERT INTO prerequisites VALUES (16, 14);
INSERT INTO prerequisites VALUES (16, 5);
INSERT INTO prerequisites VALUES (17, 3);
INSERT INTO prerequisites VALUES (18, 23);
INSERT INTO prerequisites VALUES (18, 3);
INSERT INTO prerequisites VALUES (19, 15);

INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (1, '6221', 'M', '1500-1730', 'Fall 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (2, '6461', 'T', '1500-1730', 'Fall 2024', 10, 2);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (3, '6212', 'W', '1500-1730', 'Fall 2024', 10, 4);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (4, '6220', 'M', '1800-2030', 'Fall 2024', 10, 2);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (5, '6232', 'T', '1800-2030', 'Fall 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (6, '6233', 'W', '1800-2030', 'Fall 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (7, '6241', 'R', '1800-2030', 'Fall 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (8, '6242', 'T', '1500-1730', 'Fall 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (9, '6246', 'M', '1800-2030', 'Fall 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (10, '6260', 'M', '1530-1800', 'Fall 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (11, '6251', 'R', '1800-2030', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (12, '6254', 'W', '1800-2030', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (13, '6262', 'T', '1800-2030', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (14, '6283', 'M', '1800-2030', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (15, '6284', 'W', '1800-2030', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (16, '6286', 'W', '1500-1730', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (17, '6325', 'M', '1800-2030', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (18, '6339', 'T', '1800-2030', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (19, '6384', 'W', '1800-2030', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (20, '6241', 'R', '1600-1830', 'Fall 2024', 10, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (21, '6242', 'W', '1500-1730', 'Spring 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (22, '6210', 'T', '1800-2030', 'Spring 2024', 10, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (23, '6461', 'R', '1500-1730', 'Spring 2024', 10, 1);


INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (1, '6221', 'T', '0900-1130', 'Fall 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (2, '6461', 'W', '0900-1130', 'Fall 2024', 11, 2);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (3, '6212', 'R', '0900-1130', 'Fall 2024', 11, 4);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (4, '6220', 'F', '0900-1130', 'Fall 2024', 11, 2);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (5, '6232', 'M', '0900-1130', 'Fall 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (6, '6233', 'T', '1200-1430', 'Fall 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (7, '6241', 'W', '1200-1430', 'Fall 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (8, '6242', 'R', '1200-1430', 'Fall 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (9, '6246', 'F', '1200-1430', 'Fall 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (10, '6260', 'M', '1200-1430', 'Fall 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (11, '6251', 'T', '1400-1630', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (12, '6254', 'W', '1400-1630', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (13, '6262', 'R', '1400-1630', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (14, '6283', 'F', '1400-1630', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (15, '6284', 'M', '1400-1630', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (16, '6286', 'T', '0800-1030', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (17, '6325', 'W', '0800-1030', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (18, '6339', 'R', '0800-1030', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (19, '6384', 'F', '0800-1030', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (20, '6241', 'M', '0800-1030', 'Fall 2024', 11, 0);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (21, '6242', 'T', '0800-1030', 'Spring 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (22, '6210', 'W', '0800-1030', 'Spring 2024', 11, 1);
INSERT INTO scheduling (crn, cid, class_day, class_time, semester, section, class_size) VALUES (23, '6461', 'R', '0800-1030', 'Spring 2024', 11, 1);


INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (2, 'IP', 'Fall 2024', 10, 11111112, FALSE, 'T003');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (3, 'IP', 'Fall 2024', 10, 11111112, FALSE, 'T004');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (4, 'IP', 'Fall 2024', 10, 11111112, FALSE, 'T004');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (3, 'IP', 'Fall 2024', 10, 11111113, FALSE, 'T005');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (4, 'IP', 'Fall 2024', 10, 11111114, FALSE, 'T006');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (2, 'IP', 'Fall 2024', 10, 11111115, FALSE, 'T007');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (5, 'IP', 'Fall 2024', 10, 11111115, FALSE, 'T007');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (6, 'IP', 'Fall 2024', 10, 11111116, FALSE, 'T008');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (7, 'IP', 'Fall 2024', 10, 11111117, FALSE, 'T009');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (8, 'IP', 'Fall 2024', 10, 11111118, FALSE, 'T010');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (9, 'IP', 'Fall 2024', 10, 11111119, FALSE, 'T011');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (10, 'IP', 'Fall 2024', 10, 11111121, FALSE, 'T012');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (2, 'A', 'Spring 2024', 10, 11111119, TRUE, 'T011');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (3, 'B', 'Spring 2024', 10, 11111119, TRUE, 'T011');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (2, 'IP', 'Fall 2024', 10, 88888888, FALSE, 'T013');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (3, 'IP', 'Fall 2024', 10, 88888888, FALSE, 'T013');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (4, 'B+', 'Spring 2024', 10, 88888888, TRUE, 'T013');
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited, tid) VALUES (5, 'F', 'Spring 2024', 10, 88888888, TRUE, 'T013');

-- ADS Dummy Data --
INSERT INTO users (uid, fname, lname, email, password, role, address, birthday) VALUES (55555555, 'Paul', 'McCartney', 'paul@gmail.com', 'pass', 'grad_student', 'OffCampus', 'August 19th, 2004');
INSERT INTO users (uid, fname, lname, email, password, role, address, birthday) VALUES (60606060, 'George', 'Harrison', 'george@gmail.com', 'pass', 'grad_student', 'Homeless', 'None');
INSERT INTO users (uid, fname, lname, email, password, role, address, birthday) VALUES (12345678, 'Ringo', 'Starr', 'ringo@gmail.com', 'pass', 'grad_student', 'Hollywood', 'August 18th, 2004');

INSERT INTO studInfo (uid, program, grad_status, fid, gpa) VALUES (55555555, 'Doctorate', 'Graduate', 11111125, 0.0);

INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (1, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (2, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (3, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (5, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (6, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (7, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (8, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (9, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (10, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (11, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (12, 'A', 'Fall 2024', 10, 55555555, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (13, 'A', 'Fall 2024', 10, 55555555, FALSE);

INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (21, 'C', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (1, 'B', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (2, 'B', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (3, 'B', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (5, 'B', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (6, 'B', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (7, 'B', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (8, 'B', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (14, 'B', 'Fall 2024', 10, 66666666, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (15, 'B', 'Fall 2024', 10, 66666666, FALSE);

INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (1, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (3, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (2, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (4, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (5, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (6, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (7, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (8, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (9, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (10, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (11, 'A', 'Fall 2024', 10, 12345678, FALSE);
INSERT INTO transcripts (crn, grade, semester, section, uid, grade_edited) VALUES (12, 'A', 'Fall 2024', 10, 12345678, FALSE);

