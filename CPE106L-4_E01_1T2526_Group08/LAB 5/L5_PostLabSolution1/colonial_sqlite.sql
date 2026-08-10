PRAGMA foreign_keys = ON;

CREATE TABLE Guide (
  Guide_Num TEXT PRIMARY KEY,
  Last_Name TEXT,
  First_Name TEXT,
  Address TEXT,
  City TEXT,
  State TEXT,
  Postal_Code TEXT,
  Phone_Num TEXT,
  Hire_Date TEXT
);

CREATE TABLE Customer (
  Customer_Num TEXT PRIMARY KEY,
  Last_Name TEXT NOT NULL,
  First_Name TEXT,
  Address TEXT,
  City TEXT,
  State TEXT,
  Postal_Code TEXT,
  Phone TEXT
);

CREATE TABLE Trip (
  Trip_ID INTEGER PRIMARY KEY,            -- DECIMAL(3,0) -> INTEGER
  Trip_Name TEXT,
  Start_Location TEXT,
  State TEXT,
  Distance INTEGER,
  Max_Grp_Size INTEGER,
  Type TEXT,
  Season TEXT
);

CREATE TABLE Reservation (
  Reservation_ID TEXT PRIMARY KEY,        -- char(7) -> TEXT
  Trip_ID INTEGER NOT NULL,
  Trip_Date TEXT,
  Num_Persons INTEGER,
  Trip_Price REAL,
  Other_Fees REAL,
  Customer_Num TEXT NOT NULL,
  FOREIGN KEY (Trip_ID) REFERENCES Trip(Trip_ID) ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (Customer_Num) REFERENCES Customer(Customer_Num) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Trip_Guides (
  Trip_ID INTEGER NOT NULL,
  Guide_Num TEXT NOT NULL,
  PRIMARY KEY (Trip_ID, Guide_Num),
  FOREIGN KEY (Trip_ID) REFERENCES Trip(Trip_ID) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (Guide_Num) REFERENCES Guide(Guide_Num) ON UPDATE CASCADE ON DELETE CASCADE
);
