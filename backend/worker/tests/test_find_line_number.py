"""Line anchoring must not collapse every cur.execute( to the first hit."""

from backend.worker.core.utils import find_line_number

FLASK_APP = '''
def init_db():
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY
        )
    """)

def register():
    cur.execute(
        f"INSERT INTO users (username, password, email, role) VALUES ('{username}', '{pw_hash}', '{email}', '{role}')"
    )

def create_profile():
    cur.execute(
        f"INSERT INTO profiles (user_id, display_name, bio) VALUES ({uid}, '{display_name}', '{bio}')"
    )

def login():
    cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{pw_hash}'")
'''


def test_multiline_insert_does_not_hit_first_execute():
    register_snippet = (
        "cur.execute(\n"
        "        f\"INSERT INTO users (username, password, email, role) VALUES "
        "('{username}', '{pw_hash}', '{email}', '{role}')\"\n"
        "    )"
    )
    line = find_line_number(FLASK_APP, register_snippet, function_name="register")
    assert line == 11, line
    assert line != 4


def test_second_insert_is_create_profile():
    snippet = (
        "cur.execute(\n"
        "        f\"INSERT INTO profiles (user_id, display_name, bio) VALUES "
        "({uid}, '{display_name}', '{bio}')\"\n"
        "    )"
    )
    line = find_line_number(FLASK_APP, snippet, "create_profile")
    assert line == 16, line


def test_single_line_sql_stays_unique():
    snippet = (
        "cur.execute(f\"SELECT * FROM users WHERE username = '{username}' "
        "AND password = '{pw_hash}'\")"
    )
    line = find_line_number(FLASK_APP, snippet)
    assert line == 21, line


def test_ambiguous_execute_falls_back_to_function_def():
    line = find_line_number(FLASK_APP, "cur.execute(", function_name="register")
    assert line == 10, line
    line = find_line_number(FLASK_APP, "cur.execute(", "create_profile")
    assert line == 15, line
