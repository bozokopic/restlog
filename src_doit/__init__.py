from pathlib import Path
import subprocess
import sys

from . import common

from .js import *  # NOQA
from .py import *  # NOQA
from . import js
from . import py


__all__ = ['task_clean_all',
           'task_build',
           'task_test',
           *js.__all__,
           *py.__all__]


build_dir = Path('build')
pytest_dir = Path('test_pytest')


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [build_dir,
                                        js.dst_dir,
                                        py.json_schema_repo_path])]}


def task_build():
    """Build"""

    def build():
        subprocess.run([sys.executable, 'setup.py', '-q', 'bdist_wheel'],
                       cwd=str(build_dir),
                       check=True)

    return {'actions': [build],
            'task_dep': ['py_build']}


def task_test():
    """Test"""

    def run(args):
        js.dst_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, '-m', 'pytest',
                        '-s', '-p', 'no:cacheprovider',
                        *(args or [])],
                       cwd=str(pytest_dir),
                       check=True)

    return {'actions': [run],
            'pos_arg': 'args',
            'task_dep': ['py_json_schema_repo']}
