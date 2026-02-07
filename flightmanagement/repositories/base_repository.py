import sqlite3
from flightmanagement.error import RepositoryError, ForeignKeyInvalidViolation, UniqueConstraintViolation, CheckConstraintViolation, MissingNotNullViolation, ForeignKeyDependencyViolation

class BaseRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _execute(self, sql: str, params=None):
        try:
            return self.conn.execute(sql, params or ())
        except sqlite3.IntegrityError as e:
            self._handle_integrity_error(e)
        except sqlite3.DatabaseError as e:
            raise RepositoryError("Database operation failed.") from e

    def _execute_fetchone(self, sql: str, params=None):
        cursor = self._execute(sql, params)
        return cursor.fetchone()

    def _execute_fetchall(self, sql: str, params=None):
        cursor = self._execute(sql, params)
        return cursor.fetchall()

    def _handle_integrity_error(self, e: sqlite3.IntegrityError):
        code = getattr(e, "sqlite_errorcode", None)

        if code == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise UniqueConstraintViolation(e) from e
        elif code == sqlite3.SQLITE_CONSTRAINT_FOREIGNKEY:
            raise ForeignKeyInvalidViolation(e) from e
        elif code == sqlite3.SQLITE_CONSTRAINT_TRIGGER:
            raise ForeignKeyDependencyViolation(e) from e
        elif code == sqlite3.SQLITE_CONSTRAINT_CHECK:
            raise CheckConstraintViolation(e) from e
        elif code == sqlite3.SQLITE_CONSTRAINT_NOTNULL:
            raise MissingNotNullViolation(e) from e
        else:
            raise RepositoryError("Integrity constraint violated.") from e