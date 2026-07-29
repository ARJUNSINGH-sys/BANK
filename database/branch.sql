CREATE TABLE IF NOT EXISTS nation (
    nation_id VARCHAR(30) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS state (
    state_id VARCHAR(30) PRIMARY KEY,
    nation_id VARCHAR(30),
    FOREIGN KEY (nation_id) REFERENCES nation(nation_id)
);


CREATE TABLE IF NOT EXISTS district (
    DISTRICT_ID VARCHAR(30) PRIMARY KEY,
    state_id VARCHAR(30),
    FOREIGN KEY (state_id) REFERENCES state(state_id)
);



CREATE TABLE IF NOT EXISTS zonal (
    zonal_id VARCHAR(30) PRIMARY KEY,
    DISTRICT_ID VARCHAR(30),
    FOREIGN KEY (DISTRICT_ID) REFERENCES district(DISTRICT_ID)
);

CREATE TABLE IF NOT EXISTS branch_details (
    Branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    zonal_id VARCHAR(30),
    branch_name VARCHAR(100),
    branch_address VARCHAR(100),
    pin_code VARCHAR(12),
    FOREIGN KEY (zonal_id) REFERENCES zonal(zonal_id)
);

CREATE TABLE IF NOT EXISTS customer (
    ID_no INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(100),
    name VARCHAR(100),
    personal_id_type VARCHAR(100),
    personal_id VARCHAR(100),
    address VARCHAR(100),
    Phone_No INT,
    Email VARCHAR(100),
    Branch_NO INT,
    FOREIGN KEY (Branch_NO) REFERENCES branch_details(Branch_id)
);

CREATE TABLE IF NOT EXISTS employee (
    ID_no_employee INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(100),
    name VARCHAR(100),
    personal_id_type VARCHAR(100),
    personal_id VARCHAR(100),
    address VARCHAR(100),
    Phone_No INT,
    Email VARCHAR(100),
    Branch_NO INT,
    FOREIGN KEY (Branch_NO) REFERENCES branch_details(Branch_id)
);

CREATE TABLE IF NOT EXISTS balance(
    ID_no INTEGER,
    balance INTEGER,
    FOREIGN KEY (ID_no) REFERENCES customer(ID_no)
)