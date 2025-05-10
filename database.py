import pandas as pd
import sqlite3 as sql

conn = sql.connect("unr_schedule.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute("""
CREATE TABLE Class (
    ClassID TEXT PRIMARY KEY,
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
    SectionClassID TEXT PRIMARY KEY,
    ClassDays TEXT,
    StartTime REAL,
    EndTime REAL,
    StartDate TEXT,
    EndDate TEXT,
    Room TEXT,
    Component TEXT,
    IsCombined TEXT,
    WaitlistCapactity INTEGER,
    WaitlistTotal INTEGER,
    ProgressUnt INTEGER,
    StatusID TEXT,
    Session INTEGER,
    InstructionMode TEXT,
    FOREIGN KEY (Room) REFERENCES Room(RoomID),
    FOREIGN KEY (StatusID) REFERENCES Status(StatusID)
);
""")

cursor.execute("""
CREATE TABLE SectionInstructor (
    SectionClassID TEXT,
    InstructorID TEXT,
    PRIMARY KEY (SectionClassID, InstructorID),
    FOREIGN KEY (SectionClassID) REFERENCES Section(SectionClassID),
    FOREIGN KEY (InstructorID) REFERENCES Instructor(InstructorID)
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
CREATE TABLE Room (
    RoomID TEXT PRIMARY KEY,
    RoomNo TEXT,
    RoomCapacity INTEGER
);
""")

cursor.execute("""
CREATE TABLE Status (
    StatusID TEXT PRIMARY KEY,
    StatusCode TEXT
);
""")

cursor.execute("""
CREATE TABLE College (
    CollegeID TEXT PRIMARY KEY,
    CollegeName TEXT
);
""")

df = pd.read_csv('sample ClassSched-CS-S25.csv', header=1)
# === College Table ===
college_table = df[
        ['College', 'Acad Org', 'Acad Group']
        ].drop_duplicates().reset_index(drop=True)
college_table.insert(0, 'college_id', range(1, len(college_table) + 1))
df = df.merge(college_table, on=[
    'College', 'Acad Org', 'Acad Group'
    ], how='left')

# === Course Table ===
course_table = df[
        ['Subject', 'Catalog', 'Title', 'Prgrss Unt', 'college_id']
        ].drop_duplicates().reset_index(drop=True)
course_table.insert(0, 'course_id', range(1, len(course_table) + 1))
df = df.merge(
        course_table, on=[
            'Subject', 'Catalog', 'Title', 'Prgrss Unt', 'college_id'
         ], how='left')

# === Meeting Table ===
meeting_table = df[
        ['Class Days',
         'Session',
         'Class Start Time',
         'Class End Time',
         'Start Date',
         'End Date',
         'Room']].drop_duplicates().reset_index(drop=True)
meeting_table.insert(0, 'meeting_id', range(1, len(meeting_table) + 1))
df = df.merge(meeting_table, on=[
    'Class Days', 'Session', 'Class Start Time', 'Class End Time',
    'Start Date', 'End Date', 'Room'
    ], how='left')

# === Course Section Table ===
section_table = df[
        ['Class Nbr', 'Section', 'Instruction Mode', 'Component', 'Class Stat',
         'Combined?', 'course_id', 'meeting_id']
        ].drop_duplicates().reset_index(drop=True)
section_table.rename(columns={'Class Nbr': 'class_nbr'}, inplace=True)

# === Instructor Table ===
instructor_table = df[
        ['Instructor Last Name', 'Instructor First Name']
        ].drop_duplicates().reset_index(drop=True)
instructor_table.insert(
        0, 'instructor_id', range(1, len(instructor_table) + 1))
df = df.merge(instructor_table, on=[
    'Instructor Last Name', 'Instructor First Name'
    ], how='left')

# === Section Instructor Table ===
section_instructor_table = df[
        ['Class Nbr', 'instructor_id']
        ].drop_duplicates().reset_index(drop=True)
section_instructor_table.rename(
        columns={'Class Nbr': 'class_nbr'}, inplace=True)

# === Classroom Table ===
classroom_table = df[
        ['Room', 'Room Capacity']
        ].drop_duplicates().reset_index(drop=True)

# === Enrollment Table ===
enrollment_table = df[
        ['Class Nbr', 'Enrollment Capacity',
         'Current Enrollment', 'Waitlist Capacity',
         'Waitlist Total']].drop_duplicates().reset_index(drop=True)
enrollment_table.rename(columns={'Class Nbr': 'class_nbr'}, inplace=True)

# === Insert into DB ===
college_table.to_sql("college", conn, if_exists="append", index=False)
course_table.to_sql("course", conn, if_exists="append", index=False)
classroom_table.to_sql("classroom", conn, if_exists="append", index=False)
meeting_table.to_sql("meeting", conn, if_exists="append", index=False)
instructor_table.to_sql("instructor", conn, if_exists="append", index=False)
section_table.to_sql("course_section", conn, if_exists="append", index=False)
section_instructor_table.to_sql(
        "section_instructor", conn, if_exists="append", index=False)
enrollment_table.to_sql("enrollment", conn, if_exists="append", index=False)

conn.commit()
conn.close()
