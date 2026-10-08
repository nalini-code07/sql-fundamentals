-- Library borrowing records
-- Run the whole script in DBeaver with Alt+X (Execute SQL Script).

-- Start clean so the script can be run again and again.
-- The view depends on the table, so it is dropped first.
DROP VIEW IF EXISTS long_loans;
DROP TABLE IF EXISTS loans;

CREATE TABLE loans (
    loan_id       INTEGER,
    member_name   TEXT,
    book_title    TEXT,
    borrow_date   TEXT,
    days_borrowed INTEGER
);

INSERT INTO loans (loan_id, member_name, book_title, borrow_date, days_borrowed) VALUES
    (1, 'Alice Brown', 'The Hobbit', '2025-04-01', 21),
    (2, 'Carlos Diaz', 'Dune',       '2025-04-03', 7),
    (3, 'Bella Chen',  '1984',       '2025-04-05', 15),
    (4, 'David Evans', 'Emma',       '2025-04-08', 14),
    (5, 'Emily Ford',  'Beloved',    '2025-04-10', 30),
    (6, 'Frank Green', 'Matilda',    '2025-04-12', 10);

-- Query 1: every loan, longest first.
SELECT loan_id, member_name, book_title, borrow_date, days_borrowed
FROM loans
ORDER BY days_borrowed DESC;

-- A view of the loans kept longer than two weeks.
CREATE VIEW long_loans AS
SELECT member_name, book_title
FROM loans
WHERE days_borrowed > 14;

-- Query 2: everything in the view, alphabetical by member.
SELECT *
FROM long_loans
ORDER BY member_name;

