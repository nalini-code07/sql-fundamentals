import os
import sqlite3
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.sql")


def run_script(conn):
    """Run the SQL file one statement at a time, the way DBeaver's Alt+X does.

    Returns the rows of every statement that produced a result (the SELECTs).
    """
    # utf-8-sig skips a byte-order mark if the editor saved one.
    with open(SCRIPT, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()

    results = []
    statement = ""
    for line in lines:
        statement += line + "\n"
        if sqlite3.complete_statement(statement):
            cur = conn.execute(statement)
            if cur.description is not None:
                columns = [d[0] for d in cur.description]
                results.append((columns, cur.fetchall()))
            statement = ""
    leftover = [l for l in statement.splitlines()
                if l.strip() and not l.strip().startswith("--")]
    if leftover:
        raise AssertionError("statement without a closing semicolon: " + statement)
    return results


class LibraryTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.results = run_script(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_loans_table_has_the_five_columns(self):
        info = self.conn.execute("PRAGMA table_info(loans)").fetchall()
        columns = [(row[1], row[2].upper()) for row in info]
        self.assertEqual(columns, [
            ("loan_id", "INTEGER"),
            ("member_name", "TEXT"),
            ("book_title", "TEXT"),
            ("borrow_date", "TEXT"),
            ("days_borrowed", "INTEGER"),
        ])

    def test_at_least_five_loans_inserted(self):
        count = self.conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
        self.assertGreaterEqual(count, 5)

    def test_script_prints_exactly_two_results(self):
        self.assertEqual(len(self.results), 2)

    def test_first_query_lists_all_loans_highest_days_first(self):
        columns, rows = self.results[0]
        self.assertEqual(columns, ["loan_id", "member_name", "book_title",
                                   "borrow_date", "days_borrowed"])
        all_loans = self.conn.execute("SELECT * FROM loans").fetchall()
        self.assertEqual(sorted(rows), sorted(all_loans))
        days = [row[4] for row in rows]
        self.assertEqual(days, sorted(days, reverse=True))
        self.assertEqual(rows[0], (5, "Emily Ford", "Beloved", "2025-04-10", 30))

    def test_view_has_only_name_and_title(self):
        cur = self.conn.execute("SELECT * FROM long_loans")
        self.assertEqual([d[0] for d in cur.description],
                         ["member_name", "book_title"])

    def test_view_keeps_only_loans_over_14_days(self):
        in_view = set(self.conn.execute("SELECT * FROM long_loans").fetchall())
        expected = set(self.conn.execute(
            "SELECT member_name, book_title FROM loans WHERE days_borrowed > 14"
        ).fetchall())
        self.assertEqual(in_view, expected)
        # 14 days is exactly two weeks: not "greater than 14", so left out.
        self.assertNotIn(("David Evans", "Emma"), in_view)
        self.assertIn(("Bella Chen", "1984"), in_view)

    def test_second_query_reads_the_view_by_member_name(self):
        columns, rows = self.results[1]
        self.assertEqual(columns, ["member_name", "book_title"])
        self.assertEqual(rows, [
            ("Alice Brown", "The Hobbit"),
            ("Bella Chen", "1984"),
            ("Emily Ford", "Beloved"),
        ])

    def test_view_follows_new_rows_in_the_table(self):
        self.conn.execute("INSERT INTO loans VALUES (7, 'Gina Hall', 'Holes', '2025-04-15', 20)")
        self.conn.execute("INSERT INTO loans VALUES (8, 'Hugo Ives', 'Wonder', '2025-04-16', 10)")
        in_view = self.conn.execute("SELECT * FROM long_loans").fetchall()
        self.assertIn(("Gina Hall", "Holes"), in_view)
        self.assertNotIn(("Hugo Ives", "Wonder"), in_view)

    def test_script_can_run_twice(self):
        results = run_script(self.conn)
        self.assertEqual(results, self.results)
        count = self.conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
        self.assertEqual(count, 6)


if __name__ == "__main__":
    unittest.main()

