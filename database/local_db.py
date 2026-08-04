import sqlite3
from datetime import datetime
from config.settings import Settings


class Database:
    def __init__(self):
        self.db_path = Settings.DATABASE_PATH
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_url TEXT UNIQUE,
                    author_name TEXT,
                    content TEXT,
                    likes INTEGER DEFAULT 0,
                    comments_count INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    impressions INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_url TEXT,
                    author_name TEXT,
                    author_profile TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT 0,
                    ai_response TEXT,
                    response_sent BOOLEAN DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_name TEXT,
                    sender_profile TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT 0,
                    ai_response TEXT,
                    response_sent BOOLEAN DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS actions_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT,
                    target_url TEXT,
                    content TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_post(self, post_url, author_name, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO posts (post_url, author_name, content) VALUES (?, ?, ?)",
                (post_url, author_name, content),
            )
            conn.commit()

    def update_post_metrics(self, post_url, likes, comments_count, shares, impressions):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE posts SET likes=?, comments_count=?, shares=?, impressions=?, updated_at=?
                   WHERE post_url=?""",
                (likes, comments_count, shares, impressions, datetime.now(), post_url),
            )
            conn.commit()

    def get_all_posts(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()]

    def save_comment(self, post_url, author_name, author_profile, content, timestamp=None):
        with sqlite3.connect(self.db_path) as conn:
            exists = conn.execute(
                "SELECT 1 FROM comments WHERE post_url=? AND author_name=? AND content=?",
                (post_url, author_name, content),
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO comments (post_url, author_name, author_profile, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (post_url, author_name, author_profile, content, timestamp or datetime.now()),
                )
                conn.commit()
                return True
            return False

    def get_unprocessed_comments(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(
                "SELECT * FROM comments WHERE processed=0 ORDER BY timestamp DESC"
            ).fetchall()]

    def mark_comment_processed(self, comment_id, ai_response=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE comments SET processed=1, ai_response=? WHERE id=?",
                (ai_response, comment_id),
            )
            conn.commit()

    def mark_comment_responded(self, comment_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE comments SET response_sent=1 WHERE id=?", (comment_id,))
            conn.commit()

    def save_message(self, sender_name, sender_profile, content, timestamp=None):
        with sqlite3.connect(self.db_path) as conn:
            exists = conn.execute(
                "SELECT 1 FROM messages WHERE sender_name=? AND content=?",
                (sender_name, content),
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO messages (sender_name, sender_profile, content, timestamp) VALUES (?, ?, ?, ?)",
                    (sender_name, sender_profile, content, timestamp or datetime.now()),
                )
                conn.commit()
                return True
            return False

    def get_unprocessed_messages(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(
                "SELECT * FROM messages WHERE processed=0 ORDER BY timestamp DESC"
            ).fetchall()]

    def mark_message_processed(self, message_id, ai_response=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE messages SET processed=1, ai_response=? WHERE id=?",
                (ai_response, message_id),
            )
            conn.commit()

    def mark_message_responded(self, message_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE messages SET response_sent=1 WHERE id=?", (message_id,))
            conn.commit()

    def log_action(self, action_type, target_url, content, status):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO actions_log (action_type, target_url, content, status) VALUES (?, ?, ?, ?)",
                (action_type, target_url, content, status),
            )
            conn.commit()

    def get_actions_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(
                "SELECT * FROM actions_log WHERE date(created_at)=?", (today,)
            ).fetchall()]

    def get_pending_comments_count(self):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM comments WHERE processed=0").fetchone()[0]

    def get_pending_messages_count(self):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM messages WHERE processed=0").fetchone()[0]
