import sqlite3 as sql
import pandas as pd

# Connect to database and enable foreign keys
conn = sql.connect("unr_schedule.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Create tables (using provided new schema)
cursor.execute("""
CREATE TABLE College (
    CollegeID TEXT PRIMARY KEY,
    CollegeName TEXT
);
""")

cursor.execute("""
CREATE TABLE Status (
    StatusID TEXT PRIMARY KEY,
    StatusCode TEXT
);
""")

cursor.execute("""
CREATE TABLE Room (
    RoomID TEXT PRIMARY KEY,
    RoomNo TEXT,
    RoomCapacity INTEGER
);
""")

cursor.execute("""
CREATE TABLE Instructor (
    InstructorID TEXT PRIMARY KEY,
    InstructorFirstName TEXT,
    InstructorLastName TEXT
);
""")

cursor.execute("""
CREATE TABLE Class (
    ClassID INTEGER PRIMARY KEY,
    Title TEXT,
    Catalog INTEGER,
    Subject TEXT,
    Section TEXT,
    Enrollment_Capacity INTEGER,
    CollegeID TEXT,
    Term TEXT,
    FOREIGN KEY (CollegeID) REFERENCES College(CollegeID)
);
""")

cursor.execute("""
CREATE TABLE Section (
    SectionClassID INTEGER PRIMARY KEY,
    ClassID INTEGER,
    ClassDays TEXT,
    StartTime REAL,
    EndTime REAL,
    StartDate TEXT,
    EndDate TEXT,
    Room TEXT,
    Component TEXT,
    IsCombined TEXT,
    WaitlistCapacity INTEGER,
    WaitlistTotal INTEGER,
    PrgrssUnt INTEGER,
    StatusID TEXT,
    Term INTEGER,
    InstructionMode TEXT,
    FOREIGN KEY (Room) REFERENCES Room(RoomID),
    FOREIGN KEY (StatusID) REFERENCES Status(StatusID)
);
""")

cursor.execute("""
CREATE TABLE SectionInstructor (
    SectionClassID INTEGER,
    InstructorID TEXT,
    PRIMARY KEY (SectionClassID, InstructorID),
    FOREIGN KEY (SectionClassID) REFERENCES Section(SectionClassID),
    FOREIGN KEY (InstructorID) REFERENCES Instructor(InstructorID)
);
""")

# Read CSV
df = pd.read_csv('sample ClassSched-CS-S25.csv', header=1)

# College table
college_table = df[['College']].drop_duplicates().reset_index(drop=True)
college_table.columns = ['CollegeName']
college_table['CollegeID'] = college_table.index.astype(str) + '_COL'

# Status table
status_table = df[['Class Stat']].drop_duplicates().reset_index(drop=True)
status_table.columns = ['StatusCode']
status_table['StatusID'] = status_table.index.astype(str) + '_STAT'

# Room table
room_table = df[['Room', 'Room Capacity']].drop_duplicates().reset_index(drop=True)
room_table.columns = ['RoomNo', 'RoomCapacity']
room_table['RoomID'] = room_table.index.astype(str) + '_ROOM'

# Instructor table
instructor_table = df[['Instructor First Name', 'Instructor Last Name']].drop_duplicates().reset_index(drop=True)
instructor_table.columns = ['InstructorFirstName', 'InstructorLastName']
instructor_table['InstructorID'] = instructor_table.index.astype(str) + '_INST'

# Merge IDs back to main dataframe
df = df.merge(college_table, left_on='College', right_on='CollegeName', how='left')
df = df.merge(status_table, left_on='Class Stat', right_on='StatusCode', how='left')
df = df.merge(room_table, left_on=['Room', 'Room Capacity'], right_on=['RoomNo', 'RoomCapacity'], how='left')
df = df.merge(instructor_table, left_on=['Instructor First Name', 'Instructor Last Name'], 
              right_on=['InstructorFirstName', 'InstructorLastName'], how='left')

# Class table
class_table = df[[
    'Title', 
    'Catalog', 
    'Subject', 
    'Section', 
    'Enrollment Capacity',  # Match CSV column
    'CollegeID', 
    'Session'
]].drop_duplicates().reset_index(drop=True)
class_table.columns = ['Title', 'Catalog', 'Subject', 'Section', 'Enrollment_Capacity', 'CollegeID', 'Term']
class_table.insert(0, 'ClassID', range(1, len(class_table) + 1))

# Merge ClassID
df = df.merge(class_table, 
              left_on=[
                  'Title', 'Catalog', 'Subject', 'Section',
                  'Enrollment Capacity', 'CollegeID', 'Session'],
              right_on=['Title', 'Catalog', 'Subject', 'Section', 'Enrollment_Capacity',
                        'CollegeID', 'Term'], 
              how='left')

# Section table
section_table = df[[
    'ClassID',
    'Class Days',
    'Class Start Time',
    'Class End Time',
    'Start Date',
    'End Date',
    'RoomID',
    'Component',
    'Combined?',
    'Waitlist Capacity',
    'Waitlist Total',
    'Prgrss Unt',
    'StatusID',
    'Session',
    'Instruction Mode'
]].drop_duplicates().reset_index(drop=True)
section_table.columns = [
    'ClassID',
    'ClassDays',
    'StartTime',
    'EndTime',
    'StartDate',
    'EndDate',
    'Room',
    'Component',
    'IsCombined',
    'WaitlistCapacity',
    'WaitlistTotal',
    'PrgrssUnt',
    'StatusID',
    'Term',
    'InstructionMode'
]
section_table.insert(0, 'SectionClassID', range(1, len(section_table) + 1))
# Debug: Print columns before section_table merge
print("DF Columns before section_table merge:", df.columns.tolist())
print("Section Table Columns:", section_table.columns.tolist())
# Merge SectionClassID
df = df.merge(section_table, 
              left_on=[
                  'ClassID',
                  'Class Days',
                  'Class Start Time',
                  'Class End Time',
                  'Start Date',
                  'End Date',
                  'RoomID',
                  'Component',
                  'Combined?',
                  'Waitlist Capacity',
                  'Waitlist Total',
                  'Prgrss Unt',
                  'StatusID',
                  'Session',
                  'Instruction Mode'
              ], 
              right_on=[
                  'ClassID',
                  'ClassDays',
                  'StartTime',
                  'EndTime',
                  'StartDate',
                  'EndDate',
                  'Room',
                  'Component',
                  'IsCombined',
                  'WaitlistCapacity',
                  'WaitlistTotal',
                  'PrgrssUnt',
                  'StatusID',
                  'Term',
                  'InstructionMode'
              ])

# SectionInstructor table
section_instructor_table = df[['SectionClassID', 'InstructorID']].drop_duplicates().reset_index(drop=True)

# Insert data into tables
college_table.to_sql("College", conn, if_exists="append", index=False)
status_table.to_sql("Status", conn, if_exists="append", index=False)
room_table.to_sql("Room", conn, if_exists="append", index=False)
instructor_table.to_sql("Instructor", conn, if_exists="append", index=False)
class_table.to_sql("Class", conn, if_exists="append", index=False)
section_table.to_sql("Section", conn, if_exists="append", index=False)
section_instructor_table.to_sql("SectionInstructor", conn, if_exists="append", index=False)

# Commit and close
conn.commit()
conn.close()
