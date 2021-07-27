from pathlib import Path
import subprocess
import tempfile

from . import common


__all__ = ['task_js_build',
           'task_js_deps',
           'task_js_deps_clean']


src_py_dir = Path('src_py')
src_js_dir = Path('src_js')
src_scss_dir = Path('src_scss')
node_modules_dir = Path('node_modules')
openapi_dir = Path('schemas_openapi')

dst_dir = src_py_dir / 'restlog/ui'


def task_js_build():
    """JavaScript - build"""

    def build(args):
        args = args or []
        entry = src_js_dir / 'main.js'
        conf = _webpack_conf.format(
            entry=entry.resolve(),
            dst_dir=dst_dir.resolve(),
            src_js_dir=src_js_dir.resolve(),
            src_scss_dir=src_scss_dir.resolve(),
            node_modules_dir=node_modules_dir.resolve())

        common.rm_rf(dst_dir)
        dst_dir.mkdir(parents=True, exist_ok=True)

        common.cp_r(openapi_dir / 'main.yaml', dst_dir / 'openapi.yaml')
        (dst_dir / 'index.html').write_text(_index_html)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            config_path = tmpdir / 'webpack.config.js'
            config_path.write_text(conf)
            subprocess.run([str(node_modules_dir / '.bin/webpack'),
                            '--config', str(config_path),
                            *args],
                           check=True)

    return {'actions': [(common.rm_rf, [dst_dir]),
                        build],
            'pos_arg': 'args',
            'task_dep': ['js_deps']}


def task_js_deps():
    """JavaScript - install dependencies"""
    return {'actions': ['yarn install --silent']}


def task_js_deps_clean():
    """JavaScript - remove dependencies"""
    return {'actions': [(common.rm_rf, [node_modules_dir,
                                        Path('yarn.lock')])]}


_index_html = r"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>restlog</title>
    <script src="index.js"></script>
</head>
<body>
</body>
</html>
"""


_webpack_conf = r"""
module.exports = {{
    mode: 'none',
    entry: '{entry}',
    output: {{
        filename: 'index.js',
        path: '{dst_dir}'
    }},
    module: {{
        rules: [
            {{
                test: /\.scss$/,
                use: [
                    "style-loader",
                    "css-loader",
                    "resolve-url-loader",
                    {{
                        loader: "sass-loader",
                        options: {{ sourceMap: true }}
                    }}
                ]
            }}
        ]
    }},
    resolve: {{
        modules: [
            '{src_js_dir}',
            '{src_scss_dir}',
            '{node_modules_dir}'
        ]
    }},
    watchOptions: {{
        ignored: /node_modules/
    }},
    devtool: 'source-map',
    stats: 'errors-only'
}};
"""
