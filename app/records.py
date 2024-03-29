import datetime
import os
import socket
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Optional, Sequence

from typing_extensions import override

from app.globals import BackupMode


class ScarabRecord(ABC):
    @abstractmethod
    def to_dict(self) -> Mapping[str, str | Sequence[str] | int]:
        ...


@dataclass
class ScarabDataclass(ScarabRecord):
    @override
    def to_dict(self) -> Mapping[str, str | Sequence[str] | int]:
        return asdict(self)


@dataclass(init=True)
class Message(ScarabDataclass):
    message: str


@dataclass
class BackupParams(ScarabDataclass):
    backup_mode: str
    source: str
    target: str
    existing_backup: Optional[str]
    backup_name: Optional[str]

    def __init__(
        self,
        *,
        backup_mode: BackupMode,
        source: Path,
        target: Path,
        existing_backup: Optional[Path],
        backup_name: Optional[str],
    ) -> None:
        self.backup_mode = backup_mode
        self.source = str(source)
        self.target = str(target)
        self.existing_backup = str(existing_backup.name) if existing_backup else None
        self.backup_name = backup_name


@dataclass
class TargetContent(ScarabDataclass):
    target_content: list[str]
    source: Optional[str]
    target: Optional[str]

    def __init__(
        self,
        *,
        target_content: list[str],
        source: Optional[Path] = None,
        target: Optional[Path] = None,
    ) -> None:
        self.target_content = target_content
        self.source = str(source)
        self.target = str(target)


class NameFormats(ScarabRecord):
    _source: str

    def __init__(
        self,
        source: str,
    ) -> None:
        self._source = source

    @override
    def to_dict(self) -> dict[str, Sequence[str]]:
        return {"name_formats": self.name_formats}

    @property
    def name_formats(self) -> Sequence[str]:
        return self._print_templates()

    def select(self, option: int) -> str:
        return self._render_templates()[option - 1]

    def _print_templates(self) -> Sequence[str]:
        return self._make_templates("<source-dir>", "<user>", "<host>", "<date>", "<time>")

    def _render_templates(self) -> Sequence[str]:
        user: str = os.environ["USER"]
        host: str = socket.gethostname()
        date: str = datetime.datetime.today().strftime("%Y-%m-%d")
        time: str = datetime.datetime.today().strftime("%H-%M-%S")

        return self._make_templates(self._source, user, host, date, time)

    def _make_templates(
        self, source: str, user: str, host: str, date: str, time: str
    ) -> Sequence[str]:
        return (
            f"{source}",
            f"{source}_{date}",
            f"{source}_{date}-{time}",
            f"{user}@{host}_{source}",
            f"{user}@{host}_{source}_{date}",
            f"{user}@{host}_{source}_{date}-{time}",
        )
