import re
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name('tickets.db')


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            solution TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')


def save_ticket(description, category, priority, solution):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            'INSERT INTO tickets (description, category, priority, solution) VALUES (?, ?, ?, ?)',
            (description, category, priority, solution),
        )
        return cur.lastrowid


def list_tickets(limit=50):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT * FROM tickets ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        return [dict(row) for row in rows]


STOPWORDS = {
    'the', 'and', 'with', 'after', 'from', 'this', 'that', 'have', 'cannot',
    'can', 'not', 'my', 'our', 'are', 'for', 'but', 'other', 'devices',
    'company', 'problem', 'issue', 'please', 'work', 'working', 'does',
}


def _keywords(text):
    text = text.lower().replace('wi-fi', 'wifi').replace('wi fi', 'wifi')
    return {word for word in re.findall(r'[a-z0-9]+', text)
            if len(word) >= 3 and word not in STOPWORDS}


def search_tickets(query: str, limit: int = 3) -> list[dict]:
    """Find earlier IT tickets that share keywords with the problem description.

    Args:
        query: Description of the IT problem to search for.
        limit: Maximum number of matching tickets to return.
    """
    words = _keywords(query[:3000])
    if not words:
        return []

    # A simple local keyword search is sufficient for this portfolio MVP.
    # All data are stored locally; we do not send the entire DB to the model.
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT * FROM tickets ORDER BY id DESC LIMIT 200').fetchall()

    matches = []
    for row in rows:
        ticket = dict(row)
        score = len(words & _keywords(ticket['description']))
        if score:
            matches.append((score, ticket['id'], {
                'id': ticket['id'],
                'description': ticket['description'],
                'category': ticket['category'],
                'priority': ticket['priority'],
                'solution': ticket['solution'],
            }))
    matches.sort(key=lambda item: (-item[0], -item[1]))
    return [item[2] for item in matches[:max(1, min(limit, 5))]]
