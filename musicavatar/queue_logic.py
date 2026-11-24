"""Cola de reproducción e historial real, independiente de PySide6.

Diseño sencillo y comprobable mediante unittest.
"""
from __future__ import annotations
import random


class PlaybackQueue:
    def __init__(self):
        self.items: list[int] = []
        self.current_index: int | None = None
        self.history: list[tuple[int,int|None]] = []
        self.history_cursor = -1
        self.shuffle_visited: set[int] = set()

    def replace(self, track_ids: list[int]):
        self.items = list(track_ids)
        self.current_index = None
        self.shuffle_visited.clear()

    def extend(self, track_ids: list[int]):
        self.items.extend(track_ids)

    def clear(self):
        self.items.clear()
        self.current_index = None
        self.shuffle_visited.clear()

    def remove(self, index: int):
        if index < 0 or index >= len(self.items):
            return
        self.items.pop(index)
        self.shuffle_visited = {i-(i>index) for i in self.shuffle_visited if i != index}
        if self.current_index == index:
            self.current_index = None
        elif self.current_index is not None and index < self.current_index:
            self.current_index -= 1

    def select(self, tid: int, queue_index: int | None = None, history_cursor: int | None = None):
        if queue_index is None or queue_index >= len(self.items) or self.items[queue_index] != tid:
            try:
                queue_index = self.items.index(tid)
            except ValueError:
                queue_index = len(self.items)
                self.items.append(tid)
        self.current_index = queue_index
        if queue_index is not None:
            self.shuffle_visited.add(queue_index)
        if history_cursor is not None and 0 <= history_cursor < len(self.history):
            self.history_cursor = history_cursor
        else:
            self.history = self.history[:self.history_cursor + 1]
            self.history.append((tid, queue_index))
            self.history_cursor = len(self.history) - 1

    def _valid_history_entry(self, cursor: int) -> tuple[int,int|None,int]:
        tid, idx = self.history[cursor]
        if idx is None or idx >= len(self.items) or self.items[idx] != tid:
            idx = self.items.index(tid) if tid in self.items else None
        return (tid, idx, cursor)

    def next_target(self, shuffle: bool = False, repeat: bool = False) -> tuple[int,int|None,int|None] | None:
        if not self.items:
            return None
        if shuffle and self.history_cursor + 1 < len(self.history):
            return self._valid_history_entry(self.history_cursor + 1)
        if shuffle:
            candidates = [i for i in range(len(self.items)) if i not in self.shuffle_visited]
            if not candidates and repeat:
                # Una vuelta de aleatorio terminó; comienza otra sin repetir
                # inmediatamente la canción actual cuando hay alternativas.
                self.shuffle_visited = {self.current_index} if self.current_index is not None else set()
                candidates = [i for i in range(len(self.items)) if i not in self.shuffle_visited]
                if not candidates and self.items:
                    self.shuffle_visited.clear()
                    candidates = list(range(len(self.items)))
            if not candidates:
                return None
            index = random.choice(candidates)
            return self.items[index], index, None
        index = (self.current_index + 1) if self.current_index is not None else 0
        if index >= len(self.items):
            if not repeat:
                return None
            index = 0
        return self.items[index], index, None

    def previous_target(self, shuffle: bool = False, repeat: bool = False) -> tuple[int,int|None,int|None] | None:
        if self.history_cursor > 0:
            return self._valid_history_entry(self.history_cursor - 1)
        if shuffle or not self.items:
            return None
        index = (self.current_index or 0) - 1
        if index < 0:
            if not repeat:
                return None
            index = len(self.items) - 1
        return self.items[index], index, None

    def prune(self, existing: set[int]):
        self.items = [tid for tid in self.items if tid in existing]
        self.shuffle_visited.clear()
        current = self.history[self.history_cursor][0] if 0 <= self.history_cursor < len(self.history) else None
        self.current_index = self.items.index(current) if current in self.items else None
        before_cursor = self.history[:self.history_cursor + 1]
        self.history_cursor = sum(tid in existing for tid, _ in before_cursor) - 1
        self.history = [(tid, None) for tid, _ in self.history if tid in existing]
