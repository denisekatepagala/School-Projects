PRAGMA foreign_keys = ON;

CREATE TABLE Location (
  Location_Num INTEGER PRIMARY KEY,
  Location_Name TEXT,
  Address TEXT,
  City TEXT,
  State TEXT,
  Postal_Code TEXT
);

CREATE TABLE Owner (
  Owner_Num TEXT PRIMARY KEY,
  Last_Name TEXT,
  First_Name TEXT,
  Address TEXT,
  City TEXT,
  State TEXT,
  Postal_Code TEXT
);

CREATE TABLE Condo_Unit (
  Condo_ID INTEGER PRIMARY KEY,
  Location_Num INTEGER NOT NULL,
  Unit_Num TEXT,
  Sqr_Ft INTEGER,
  Bdrms INTEGER,
  Baths INTEGER,
  Condo_Fee REAL,
  Owner_Num TEXT NOT NULL,
  FOREIGN KEY (Location_Num) REFERENCES Location(Location_Num) ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (Owner_Num) REFERENCES Owner(Owner_Num) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Service_Category (
  Category_Num INTEGER PRIMARY KEY,
  Category_Description TEXT
);

CREATE TABLE Service_Request (
  Service_ID INTEGER PRIMARY KEY,
  Condo_ID INTEGER NOT NULL,
  Category_Num INTEGER NOT NULL,
  Description TEXT,
  Status TEXT,
  Est_Hours REAL,
  Spent_Hours REAL,
  Next_Service_Date TEXT,
  FOREIGN KEY (Condo_ID) REFERENCES Condo_Unit(Condo_ID) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (Category_Num) REFERENCES Service_Category(Category_Num) ON UPDATE CASCADE ON DELETE RESTRICT
);
INSERT INTO LOCATION
VALUES
(1,'Solmaris Ocean','100 Ocean Ave.','Bowton','FL','31313');
INSERT INTO LOCATION
VALUES
(2,'Solmaris Bayside','405 Bayside Blvd.','Glander Bay','FL','31044');
INSERT INTO CONDO_UNIT
VALUES
(1,1,'102',675,1,1,475.00,'AD057');
INSERT INTO CONDO_UNIT
VALUES
(2,1,'201',1030,2,1,550.00,'EL025');
INSERT INTO CONDO_UNIT
VALUES
(3,1,'306',1575,3,2,625.00,'AN175');
INSERT INTO CONDO_UNIT
VALUES
(4,1,'204',1164,2,2,575.00,'BL720');
INSERT INTO CONDO_UNIT
VALUES
(5,1,'405',1575,3,2,625.00,'FE182');
INSERT INTO CONDO_UNIT
VALUES
(6,1,'401',1030,2,2,550.00,'KE122');
INSERT INTO CONDO_UNIT
VALUES
(7,1,'502',745,1,1,490.00,'JU092');
INSERT INTO CONDO_UNIT
VALUES
(8,1,'503',1680,3,3,670.00,'RO123');
INSERT INTO CONDO_UNIT
VALUES
(9,2,'A03',725,1,1,190.00,'TR222');
INSERT INTO CONDO_UNIT
VALUES
(10,2,'A01',1084,2,1,235.00,'NO225');
INSERT INTO CONDO_UNIT
VALUES
(11,2,'B01',1084,2,2,250.00,'SM072');
INSERT INTO CONDO_UNIT
VALUES
(12,2,'C01',750,1,1,190.00,'AN175');
INSERT INTO CONDO_UNIT
VALUES
(13,2,'C02',1245,2,2,250.00,'WS032');
INSERT INTO CONDO_UNIT
VALUES
(14,2,'C06',1540,3,2,300.00,'RO123');
INSERT INTO OWNER
VALUES
('AD057','Adney','Bruce and Jean','100 Ocean Ave.','Bowton','FL','31313');
INSERT INTO OWNER
VALUES
('AN175','Anderson','Bill','18 Wilcox St.','Brunswick','GA','31522');
INSERT INTO OWNER
VALUES
('BL720','Blake','Jack','2672 Condor St.','Mills','SC','29707');
INSERT INTO OWNER
VALUES
('EL025','Elend','Bill and Sandy','100 Ocean Ave.','Bowton','FL','31313');
INSERT INTO OWNER
VALUES
('FE182','Feenstra','Daniel','7822 Coventry Dr.','Rivard','FL','31062');
INSERT INTO OWNER
VALUES
('JU092','Juarez','Maria','892 Oak St.','Kaleva','FL','31521');
INSERT INTO OWNER
VALUES
('KE122','Kelly','Alyssa','527 Waters St.','Norton','MI','49441');
INSERT INTO OWNER
VALUES
('NO225','Norton','Peter and Caitlin','281 Lakewood Ave.','Lawndale','PA','19111');
INSERT INTO OWNER
VALUES
('RO123','Robinson','Mike and Jane','900 Spring Lake Dr.','Springs','MI','49456');
INSERT INTO OWNER
VALUES
('SM072','Smeltz','Jim and Cathy','922 Garland Dr.','Lewiston','FL','32765');
INSERT INTO OWNER
VALUES
('TR222','Trent','Michael','405 Bayside Blvd.','Glander Bay','FL','31044');
INSERT INTO OWNER
VALUES
('WS032','Wilson','Henry and Karen','25 Nichols St.','Lewiston','FL','32765');
INSERT INTO SERVICE_CATEGORY
VALUES
(1,'Plumbing');
INSERT INTO SERVICE_CATEGORY
VALUES
(2,'Heating/Air Conditioning');
INSERT INTO SERVICE_CATEGORY
VALUES
(3,'Painting');
INSERT INTO SERVICE_CATEGORY
VALUES
(4,'Electrical Systems');
INSERT INTO SERVICE_CATEGORY
VALUES
(5,'Carpentry');
INSERT INTO SERVICE_CATEGORY
VALUES
(6,'Janitorial');
INSERT INTO SERVICE_REQUEST
VALUES
(1,2,1,'Back wall in pantry has mold indicating water seepage. Diagnose and repair.','Service rep has verified the problem. Plumbing contractor has been called.',4,2,'10-12-2015');
INSERT INTO SERVICE_REQUEST
VALUES
(2,5,2,'Air conditioning doesn�t cool.','Service rep has verified problem. Air conditioning contractor has been called.',3,1,'10-12-2015'); 
INSERT INTO SERVICE_REQUEST
VALUES
(3,4,6,'Hardwood floors must be refinished.','Service call has been scheduled.',8,0,'10-16-2015'); 
INSERT INTO SERVICE_REQUEST
VALUES
(4,1,4,'Switches in kitchen and adjoining dining room are reversed. ','Open',1,0,'10-13-2015'); 
INSERT INTO SERVICE_REQUEST (SERVICE_ID, CONDO_ID,  CATEGORY_NUM, DESCRIPTION, STATUS, EST_HOURS, SPENT_HOURS)
VALUES
(5,2,5,'Molding in pantry must be replaced.','Cannot schedule until water leak is corrected.',2,0);
INSERT INTO SERVICE_REQUEST
VALUES
(6,14,3,'Unit needs to be repainted due to previous tenant damage.','Scheduled',7,0,'10-19-2015'); 
INSERT INTO SERVICE_REQUEST (SERVICE_ID, CONDO_ID,  CATEGORY_NUM, DESCRIPTION, STATUS, EST_HOURS, SPENT_HOURS)
VALUES
(7,11,4,'Tenant complained that using microwave caused short circuits on two occasions.','Service rep unable to duplicate problem. Tenant to notify condo management if problem recurs.',1,1);
INSERT INTO SERVICE_REQUEST
VALUES
(8,9,3,'Kitchen must be repainted. Walls discolored due to kitchen fire. ','Scheduled',5,0,'10-16-2015'); 
INSERT INTO SERVICE_REQUEST
VALUES
(9,7,6,'Shampoo all carpets.','Open',5,0,'10-19-2015'); 
INSERT INTO SERVICE_REQUEST
VALUES
(10,9,5,'Repair window sills.','Scheduled',4,0,'10-20-2015'); 

