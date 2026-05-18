"""Тесты для ProjectContext (после реализации)"""

import pytest
import tempfile
from pathlib import Path
import sys

from project_context import ProjectContext


def test_project_context_creation():
    """Тест: создание контекста с корректным путём"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        assert context.project_root == Path(tmpdir).resolve()


def test_arm_dir_property():
    """Тест: свойство arm_dir возвращает .arm внутри проекта"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        assert context.arm_dir == Path(tmpdir).resolve() / ".arm"


def test_ensure_dirs_creates_structure():
    """Тест: ensure_dirs() создаёт все поддиректории .arm/"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        context.ensure_dirs()
        
        assert context.arm_dir.exists()
        assert context.reports_dir.exists()
        assert context.cache_dir.exists()
        assert context.configs_dir.exists()
        assert context.screenshots_dir.exists()
        assert context.logs_dir.exists()


def test_arm_dir_gitignore_created():
    """Тест: ensure_dirs() создаёт .gitignore внутри .arm/"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        context.ensure_dirs()
        
        gitignore = context.arm_dir / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert "arm_testing" not in content  # .gitignore не должен содержать имя АРМ
        assert "*" in content  # игнорировать всё


def test_python_path_finds_venv():
    """Тест: python_path находит venv/bin/python в проекте"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        # Создаём имитацию venv
        venv_bin = project_path / "venv" / "bin"
        venv_bin.mkdir(parents=True)
        fake_python = venv_bin / "python"
        fake_python.touch()
        
        context = ProjectContext(project_path)
        assert context.python_path == fake_python


def test_python_path_fallback():
    """Тест: python_path возвращает sys.executable если venv не найден"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        # Нет venv, должен вернуть sys.executable
        assert context.python_path == Path(sys.executable)


def test_db_path_property():
    """Тест: db_path указывает на arm_testing.db внутри .arm/"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        assert context.db_path == context.arm_dir / "arm_testing.db"


def test_cache_dir_property():
    """Тест: cache_dir существует и доступен"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        assert context.cache_dir == context.arm_dir / "cache"


def test_reports_dir_property():
    """Тест: reports_dir существует и доступен"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        assert context.reports_dir == context.arm_dir / "reports"


def test_get_run_config_path():
    """Тест: get_run_config_path(run_id) возвращает корректный путь"""
    with tempfile.TemporaryDirectory() as tmpdir:
        context = ProjectContext(Path(tmpdir))
        run_id = 42
        expected = context.configs_dir / "run_42.json"
        assert context.get_run_config_path(run_id) == expected