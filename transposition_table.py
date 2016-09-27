# -*- coding: utf-8 -*-

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
