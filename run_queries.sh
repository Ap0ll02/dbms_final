DB="unr_schedule.db"
OUTFILE="output.txt"

rm -f "$DB" "$OUTFILE"

python3 database.py 

sqlite3 "$DB" <<EOF >> "$OUTFILE"
.headers on
.mode box

-- Class Search View
CREATE VIEW [Class Search] AS
SELECT
  cl.Subject || ' ' || cl.Catalog AS Course,
  cl.Subject AS Subject,
  cl.Catalog AS Catalog,
  s.SectionClassID AS [Class Nbr],
  cl.Section,
  s.ClassDays || ' ' || s.StartTime || ' - ' || s.EndTime AS [Days & Times],
  r.RoomNo AS Room,
  i.InstructorFirstName || ' ' || i.InstructorLastName AS Instructor,
  s.StartDate || ' - ' || s.EndDate AS [Meeting Dates],
  st.StatusCode AS [Class Stat],
  s.Term
FROM SectionInstructor si
JOIN Instructor i ON si.InstructorID = i.InstructorID
JOIN Section s ON si.SectionClassID = s.SectionClassID
JOIN Class cl ON s.SectionClassID = cl.ClassID
LEFT JOIN Room r ON s.Room = r.RoomID
LEFT JOIN Status st ON s.StatusID = st.StatusID;

-- Class search for all spring courses
SELECT Course, [Class Nbr], Section, [Days & Times], Room, Instructor, [Meeting Dates], [Class Stat]
FROM [Class Search]
WHERE Term = 1;

-- Lower Division Comp Sci Courses
SELECT Course, [Class Nbr], Section, [Days & Times], Room, Instructor, [Meeting Dates], [Class Stat]
FROM [Class Search]
WHERE Catalog < 300;

-- All CS 135 Sections
SELECT Course, [Class Nbr], Section, [Days & Times], Room, Instructor, [Meeting Dates], [Class Stat]
FROM [Class Search]
WHERE Course = 'CS 135';

-- All upper division CS Courses
SELECT Course, [Class Nbr], Section, [Days & Times], Room, Instructor, [Meeting Dates], [Class Stat]
FROM [Class Search]
WHERE Catalog >= 300;

-- Hastings and Keith taught courses
SELECT Course, [Class Nbr], Section, [Days & Times], Room, Instructor, [Meeting Dates], [Class Stat]
FROM [Class Search]
WHERE Course LIKE 'CS%' AND (
  Instructor LIKE '%Keith%' OR
  Instructor LIKE '%Hastings%'
);

EOF

echo "output saved to $OUTFILE"
