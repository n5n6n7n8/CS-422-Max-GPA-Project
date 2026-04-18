--
-- Table structure for table `degree`
--

CREATE TABLE IF NOT EXISTS degree (
  degree_id INTEGER PRIMARY KEY AUTOINCREMENT,
  degree_title TEXT NOT NULL
);

-- --------------------------------------------------------

--
-- Table structure for table `degree_courses`
--

CREATE TABLE IF NOT EXISTS degree_courses (
  degree_id INTEGER NOT NULL,
  course_key TEXT NOT NULL,
  course_title TEXT NOT NULL,
  year INTEGER NOT NULL,
  term INTEGER NOT NULL,
  PRIMARY KEY (degree_id, course_key)
);

-- --------------------------------------------------------

--
-- Table structure for table `grade_history`
--

CREATE TABLE IF NOT EXISTS grade_history (
  term_code TEXT NOT NULL,
  course_key TEXT NOT NULL,
  instructor_name TEXT NOT NULL,
  academic_year TEXT NOT NULL,
  crn TEXT NOT NULL,
  a_count INTEGER NOT NULL DEFAULT 0,
  b_count INTEGER NOT NULL DEFAULT 0,
  c_count INTEGER NOT NULL DEFAULT 0,
  dnf_count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (term_code, course_key, instructor_name)
);
