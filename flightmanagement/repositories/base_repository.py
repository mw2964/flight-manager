import sqlite3
from flightmanagement.error import RepositoryError, ForeignKeyInvalidViolation, UniqueConstraintViolation, CheckConstraintViolation, MissingNotNullViolation, ForeignKeyDependencyViolation

class BaseRepository:
    """
    Base class for all repository implementations.

    This class encapsulates the common SQLite execution logic and translates
    sqlite3 errors into repository exceptions for handling higher up the stack.

    SQLite-specific dependencies should be restricted to this class,
    enabling easier migration to other database technology options in the future.
    """

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def _execute(self, sql: str, params=None) -> sqlite3.Cursor:
        """
        Execute a SQL statement (with optional parameters) against the database connection.

        Catches sqlite exceptions and raises them as repository exceptions.
        Returns an sqlite cursor object.
        """

        try:
            return self._conn.execute(sql, params or ())
        except sqlite3.IntegrityError as e:
            self._handle_integrity_error(e)
        except sqlite3.DatabaseError as e:
            raise RepositoryError("Database operation failed.") from e

    def _execute_fetchone(self, sql: str, params=None) -> dict | None:
        """
        Execute a query against the database and return the first row of data as a dictionary.

        Returns None if no rows are returned by the query.
        """
        cursor = self._execute(sql, params)

        result = cursor.fetchone()
        if result is None:
            return None

        return dict(result)

    def _execute_fetchall(self, sql: str, params=None) -> list[dict]:
        """
        Execute a query against the database and return all matching rows as a list of dictionaries.

        Returns an empty list if no rows are returned by the query.
        """
        cursor = self._execute(sql, params)
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]

        return results

    def _handle_integrity_error(self, e: sqlite3.IntegrityError):
        """
        Catch any sqlite exceptions raised by the execution functions
        and translate them into repository exceptions for upstream handling. 
        """
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