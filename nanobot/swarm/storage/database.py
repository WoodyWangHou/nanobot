# SQLite database layer for swarm experiments
import sqlite3
import uuid
from datetime import datetime
from typing import Optional, List
from .models import Experiment, Iteration, BudgetPolicy

# Static in-memory database for testing
_in_memory_db = None


class Database:
    def __init__(self, db_path: str = "swarm.db"):
        self.db_path = db_path
        if db_path == ":memory:":
            global _in_memory_db
            if _in_memory_db is None:
                _in_memory_db = sqlite3.connect(":memory:", check_same_thread=False)
                self._create_tables(_in_memory_db)
            self._conn = _in_memory_db
        else:
            self._conn = None
            self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        if self._conn:
            return self._conn
        return sqlite3.connect(self._db_ref if hasattr(self, '_db_ref') else self.db_path)

    def _create_tables(self, conn):
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                success_criteria TEXT,
                status TEXT DEFAULT 'running',
                budget_max_tokens INTEGER,
                budget_window TEXT,
                budget_auto_pause INTEGER,
                budget_warning_percent INTEGER,
                tokens_used INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS iterations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT,
                agent_type TEXT,
                task TEXT,
                result TEXT,
                learnings TEXT,
                feedback TEXT,
                tokens_used INTEGER DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id)
            );
        """)

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        self._create_tables(conn)
        conn.close()

    def create_experiment(self, goal: str, success_criteria: str, budget_policy: BudgetPolicy) -> Experiment:
        exp_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        conn = self._get_connection()
        conn.execute(
            """INSERT INTO experiments
               (id, goal, success_criteria, status, budget_max_tokens, budget_window,
                budget_auto_pause, budget_warning_percent, tokens_used, created_at, updated_at)
               VALUES (?, ?, ?, 'running', ?, ?, ?, ?, 0, ?, ?)""",
            (exp_id, goal, success_criteria, budget_policy.max_tokens_per_window,
             budget_policy.window_duration, int(budget_policy.auto_pause),
             budget_policy.warning_at_percent, now, now)
        )
        conn.commit()
        return Experiment(
            id=exp_id, goal=goal, success_criteria=success_criteria,
            status="running", budget_policy=budget_policy, tokens_used=0,
            created_at=datetime.fromisoformat(now), updated_at=datetime.fromisoformat(now)
        )

    def add_iteration(self, experiment_id: str, agent_type: str, task: str, result: str,
                      learnings: List[str] = None, feedback: str = None, tokens_used: int = 0) -> Iteration:
        now = datetime.utcnow().isoformat()
        conn = self._get_connection()
        cursor = conn.execute(
            """INSERT INTO iterations (experiment_id, agent_type, task, result, learnings, feedback, tokens_used, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (experiment_id, agent_type, task, result, str(learnings or []), feedback, tokens_used, now)
        )
        iteration_id = cursor.lastrowid
        conn.commit()
        return Iteration(
            id=iteration_id, experiment_id=experiment_id, agent_type=agent_type,
            task=task, result=result, learnings=learnings or [], feedback=feedback,
            tokens_used=tokens_used, created_at=datetime.fromisoformat(now)
        )

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_experiment(row)

    def get_iterations(self, experiment_id: str) -> List[Iteration]:
        conn = self._get_connection()
        cursor = conn.execute("SELECT * FROM iterations WHERE experiment_id = ? ORDER BY created_at", (experiment_id,))
        rows = cursor.fetchall()
        return [self._row_to_iteration(row) for row in rows]

    def update_experiment_status(self, experiment_id: str, status: str):
        now = datetime.utcnow().isoformat()
        conn = self._get_connection()
        conn.execute("UPDATE experiments SET status = ?, updated_at = ? WHERE id = ?", (status, now, experiment_id))
        conn.commit()

    def _row_to_experiment(self, row) -> Experiment:
        return Experiment(
            id=row[0], goal=row[1], success_criteria=row[2], status=row[3],
            budget_policy=BudgetPolicy(
                max_tokens_per_window=row[4] or 0,
                window_duration=row[5] or "1h",
                auto_pause=bool(row[6]),
                warning_at_percent=row[7] or 80
            ),
            tokens_used=row[8] or 0,
            created_at=datetime.fromisoformat(row[9]),
            updated_at=datetime.fromisoformat(row[10])
        )

    def _row_to_iteration(self, row) -> Iteration:
        import ast
        learnings = []
        if row[5]:
            try:
                learnings = ast.literal_eval(row[5])
            except:
                learnings = []
        return Iteration(
            id=row[0], experiment_id=row[1], agent_type=row[2], task=row[3],
            result=row[4], learnings=learnings, feedback=row[6],
            tokens_used=row[7] or 0, created_at=datetime.fromisoformat(row[8])
        )
