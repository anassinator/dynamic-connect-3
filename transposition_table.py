# -*- coding: utf-8 -*-

import sqlite3
from threading import Lock
from abc import ABCMeta, abstractmethod


class TranspositionTable(object, metaclass=ABCMeta):

    """Transposition table."""

    @abstractmethod
    def __contains__(self, key):
        """Returns whether a key is contained in the table or not.

        Args:
            key: Key.

        Returns:
            Whether the key is stored in the table or not.
        """
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key):
        """Returns the value in the table corresponding to a given key.

        Args:
            key: Key.

        Returns:
            The corresponding value.
        """
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key, value):
        """Sets value in the table to given key.

        Args:
            key: Key.
            value: Value.
        """
        raise NotImplementedError


class TemporaryTranspositionTable(object, metaclass=ABCMeta):

    """Transposition table stored in memory."""

    def __init__(self):
        """Constructs a TemporaryTranspositionTable."""
        self._table = dict()

    def __contains__(self, key):
        """Returns whether a key is contained in the table or not.

        Args:
            key: Key.

        Returns:
            Whether the key is stored in the table or not.
        """
        return key in self._table

    def __getitem__(self, key):
        """Returns the value in the table corresponding to a given key.

        Args:
            key: Key.

        Returns:
            The corresponding value.
        """
        return self._table[key]

    def __setitem__(self, key, value):
        """Sets value in the table to given key.

        Args:
            key: Key.
            value: Value.
        """
        self._table[key] = value


class PermanentTranspositionTable(object, metaclass=ABCMeta):

    """Transposition table stored in database."""

    def __init__(self, filename):
        """Constructs a PermanentTranspositionTable.

        Args:
            filename: Filename of SQLite database.
        """
        self._lock = Lock()
        self._conn = sqlite3.connect(filename)
        self.__setup()

    def __contains__(self, key):
        """Returns whether a key is contained in the table or not.

        Args:
            key: Key.

        Returns:
            Whether the key is stored in the table or not.
        """
        return self[key] is not None

    def __getitem__(self, key):
        """Returns the value in the table corresponding to a given key.

        Args:
            key: Key.

        Returns:
            The corresponding value.
        """
        state, depth_searched = key
        s = """
        SELECT heuristic FROM transposition_table
            WHERE
                white_pieces=:white AND
                black_pieces=:black AND
                turn=:turn AND
                depth_searched>=:depth;
        """
        parameters = {
            "white": state.board._white_pieces,
            "black": state.board._black_pieces,
            "turn": state.turn.value,
            "depth": depth_searched
        }

        c = self._conn.cursor()
        with self._lock:
            c.execute(s, parameters)
            result = c.fetchone()
            c.close()
            
        return result[0] if result is not None else None

    def __setitem__(self, key, value):
        """Sets value in the table to given key.

        Args:
            key: Game state.
            value: Value.
        """
        state, depth_searched = key

        c = self._conn.cursor()
        parameters = {
            "white": state.board._white_pieces,
            "black": state.board._black_pieces,
            "turn": state.turn.value,
            "depth": depth_searched,
            "heuristic": value
        }

        update = """
        UPDATE transposition_table
            SET
                depth_searched=:depth,
                heuristic=:heuristic
            WHERE
                white_pieces=:white AND
                black_pieces=:black AND
                turn=:turn;
        """

        insert = """
        INSERT INTO transposition_table
            (white_pieces, black_pieces, turn, depth_searched, heuristic)
            SELECT :white, :black, :turn, :depth, :heuristic
            WHERE (SELECT CHANGES()=0);
        """

        with self._lock:
            # Update existing item if exists.
            c.execute(update, parameters)

            # Insert if no update occurred.
            c.execute(insert, parameters)

            self._conn.commit()
            c.close()

    def __setup(self):
        """Sets up the database if it doesn't exist yet."""
        c = self._conn.cursor()

        check_command = """
        SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='transposition_table';
        """

        with self._lock:
            c.execute(check_command)
            created = c.fetchone()

            if not created:
                creation_command = """
                CREATE TABLE transposition_table
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     white_pieces INTEGER NOT NULL,
                     black_pieces INTEGER NOT NULL,
                     turn INTEGER NOT NULL,
                     depth_searched INTEGER,
                     heuristic REAL);
                """
                c.execute(creation_command)
                self._conn.commit()

            c.close()
