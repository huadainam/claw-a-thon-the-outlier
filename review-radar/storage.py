import json
import os
from abc import ABC, abstractmethod

class Store(ABC):
    @abstractmethod
    def load_config(self) -> dict: ...
    @abstractmethod
    def save_config(self, cfg: dict): ...
    @abstractmethod
    def load_processed_ids(self) -> set: ...
    @abstractmethod
    def save_processed_ids(self, ids: set): ...
    @abstractmethod
    def load_reviews(self) -> list: ...
    @abstractmethod
    def append_reviews(self, reviews: list): ...
    @abstractmethod
    def load_todos(self) -> list: ...
    @abstractmethod
    def save_todos(self, todos: list): ...
    @abstractmethod
    def reset(self): ...

class LocalStore(Store):
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _path(self, name: str) -> str:
        return os.path.join(self.data_dir, name)

    def _read(self, name: str, default):
        path = self._path(name)
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return default

    def _write(self, name: str, value):
        with open(self._path(name), "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)

    def load_config(self) -> dict:
        return self._read("config.json", {})

    def save_config(self, cfg: dict):
        self._write("config.json", cfg)

    def load_processed_ids(self) -> set:
        return set(self._read("processed_ids.json", []))

    def save_processed_ids(self, ids: set):
        self._write("processed_ids.json", sorted(ids))

    def load_reviews(self) -> list:
        return self._read("reviews.json", [])

    def append_reviews(self, reviews: list):
        existing = self.load_reviews()
        existing.extend(reviews)
        self._write("reviews.json", existing)

    def load_todos(self) -> list:
        return self._read("todos.json", [])

    def save_todos(self, todos: list):
        self._write("todos.json", todos)

    def reset(self):
        for name in ("processed_ids.json", "reviews.json", "todos.json"):
            path = self._path(name)
            if os.path.exists(path):
                os.remove(path)
