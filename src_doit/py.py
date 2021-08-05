from pathlib import Path

import packaging.requirements

from hat import json

from . import common


__all__ = ['task_py_build',
           'task_py_json_schema_repo']


build_dir = Path('build')
src_py_dir = Path('src_py')
schemas_json_dir = Path('schemas_json')
requirements_path = Path('requirements.pip.runtime.txt')

json_schema_repo_path = src_py_dir / 'restlog/json_schema_repo.json'


def task_py_build():
    """Python - build"""

    def build():
        common.rm_rf(build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)

        common.cp_r(src_py_dir, build_dir)
        common.rm_rf(*build_dir.rglob('__pycache__'))

        manifest_path = build_dir / 'MANIFEST.in'
        paths = [path for path in build_dir.rglob('*') if not path.is_dir()]
        with open(manifest_path, 'w', encoding='utf-8') as f:
            for path in paths:
                f.write(f"include {path.relative_to(manifest_path.parent)}\n")

        readme = Path('README.rst').read_text()
        requirements = list(_get_requirements(requirements_path))
        setup_py = _setup_py.format(readme=repr(readme),
                                    requirements=repr(requirements))
        (build_dir / 'setup.py').write_text(setup_py)

    return {'actions': [build],
            'task_dep': ['py_json_schema_repo',
                         'js_build']}


def task_py_json_schema_repo():
    """Python - JSON schema repo"""
    src_paths = list(schemas_json_dir.rglob('*.yaml'))

    def generate():
        repo = json.SchemaRepository(*src_paths)
        data = repo.to_json()
        json.encode_file(data, json_schema_repo_path, indent=None)

    return {'actions': [generate],
            'file_dep': src_paths,
            'targets': [json_schema_repo_path]}


def _get_requirements(path):
    # TODO: implement full format
    #       https://pip.pypa.io/en/stable/cli/pip_install/
    for i in path.read_text().split('\n'):
        i = i.strip()
        if not i or i.startswith('#'):
            continue
        requirement = packaging.requirements.Requirement(i)
        yield str(requirement)


_setup_py = r"""
from setuptools import setup

readme = {readme}
requirements = {requirements}

setup(
    name='restlog',
    version='0.0.1',
    description='JSON log-structured data storage with REST API',
    long_description=readme,
    long_description_content_type='text/x-rst',
    url='https://github.com/bozokopic/restlog',
    license='GPLv3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
    packages=['restlog'],
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8',
    zip_safe=False,
    entry_points={{
        'console_scripts': ['restlog = restlog.main:main']
    }})
"""  # NOQA
