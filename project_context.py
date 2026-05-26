"""ProjectContext — управление путями и рабочей областью проекта (.arm/)"""

from pathlib import Path
from dataclasses import dataclass, field
import sys
import os
import tempfile


@dataclass
class ProjectContext:
    """Контекст проекта: хранит пути к корню проекта и рабочей области .arm/"""
    
    project_root: Path
    arm_dir_name: str = ".arm"
    _is_fallback: bool = field(default=False, init=False)
    _fallback_dir: Path = field(default=None, init=False)
    
    def __post_init__(self):
        """Нормализует путь после создания"""
        self.project_root = self.project_root.resolve()
        self._check_permissions()
    
    def _check_permissions(self):
        """Проверяет права на запись в проект и определяет режим работы"""
        arm_path = self.project_root / self.arm_dir_name
        if arm_path.exists():
            can_write = os.access(arm_path, os.W_OK)
        else:
            can_write = os.access(self.project_root, os.W_OK)
        
        if not can_write:
            self._is_fallback = True
            self._fallback_dir = Path(tempfile.gettempdir()) / f".arm_{self.project_root.name}"
            self._fallback_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def is_fallback_mode(self) -> bool:
        """Возвращает True, если используется временная папка вместо .arm/"""
        return self._is_fallback
    
    @property
    def arm_dir(self) -> Path:
        """Папка .arm/ внутри проекта (или временная папка при fallback)"""
        if self._is_fallback:
            return self._fallback_dir
        return self.project_root / self.arm_dir_name
    
    @property
    def reports_dir(self) -> Path:
        """Папка для HTML-отчётов"""
        return self.arm_dir / "reports"
    
    @property
    def cache_dir(self) -> Path:
        """Папка для временных файлов (JSON-отчёты pytest, кеш)"""
        return self.arm_dir / "cache"
    
    @property
    def configs_dir(self) -> Path:
        """Папка для конфигураций запусков (Repeat)"""
        return self.arm_dir / "configs"
    
    @property
    def screenshots_dir(self) -> Path:
        """Папка для скриншотов (задел)"""
        return self.arm_dir / "screenshots"
    
    @property
    def logs_dir(self) -> Path:
        """Папка для логов (задел)"""
        return self.arm_dir / "logs"
    
    @property
    def db_path(self) -> Path:
        """Путь к базе данных SQLite внутри .arm/"""
        return self.arm_dir / "arm_testing.db"
    
    @property
    def current_project_id(self) -> int:
        """В локальной БД проекта всегда 1"""
        return 1
    
    @property
    def python_path(self) -> Path:
        """Путь к Python интерпретатору проекта (venv или системный)"""
        candidates = [
            self.project_root / "venv" / "bin" / "python",
            self.project_root / ".venv" / "bin" / "python",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        # Fallback на Python, которым запущен АРМ
        return Path(sys.executable)
    
    def ensure_dirs(self) -> None:
        """Создаёт все директории .arm/ и добавляет .gitignore"""
        if self._is_fallback:
            return
        
        dirs = [
            self.arm_dir,
            self.reports_dir,
            self.cache_dir,
            self.configs_dir,
            self.screenshots_dir,
            self.logs_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        # Защита от коммита .arm/ в git
        gitignore_path = self.arm_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("# Автоматически создано АРМ тестировщика\n*\n!.gitignore\n")
        
        # Создаём базу данных, если её нет
        if not self.db_path.exists():
            from db.database import Database
            Database(str(self.db_path), include_projects=False)
    
    def get_run_config_path(self, run_id: int) -> Path:
        """Возвращает путь к файлу конфигурации запуска для Repeat"""
        return self.configs_dir / f"run_{run_id}.json"