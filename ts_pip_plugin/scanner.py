# SPDX-FileCopyrightText: 2020 EACG GmbH
#
# SPDX-License-Identifier: Apache-2.0

import os
import re

from pathlib import Path
from importlib_metadata import distribution, Distribution, PackageNotFoundError
from typing import List


class Scanner:
    def __init__(self, client):
        self._client = client

        self._found_packages = set()
        self._import_statement_regex = re.compile(r'(?:from|import) ([a-zA-Z0-9_]+)(?:.*)')


    def _extract_imports(self, src_file: Path):
        with src_file.open('r') as src:
            try:
                imports = self._import_statement_regex.findall(src.read())
                self._found_packages |= set(imports)
            except:
                pass


    def run(self, settings=None):
        path = os.path.expandvars(self._client.scanPath)
        path = Path(path).expanduser().resolve()

        ignore_list = settings.get('ignore', []) if settings else []

        def walk(dirpath: Path):
            for p in dirpath.iterdir():
                # Improve checks to support wildcards etc.
                if p.name in ignore_list:
                   continue

                if p.is_file() and p.suffix == '.py':
                    self._extract_imports(p)
                elif p.is_dir():
                    walk(p)

        walk(path)
        mod = path.name

        scanInfo = {
            'module': mod,
            'moduleId': 'pip:' + mod,
            'dependencies': create_dependencies(self._found_packages)
        }

        return scanInfo


def create_dependencies(packages):
    processed_packages = set()
    pkg_require_expr_regex = re.compile(r'([a-zA-Z0-9_\-]+)(?:.*)')

    def parse_requires(requires):
        if requires:
            for req in requires:
                for pkg in pkg_require_expr_regex.findall(req):
                    yield pkg

    def do_create_dependencies(pkgs):
        packages_info: List[Distribution] = []
        for pkg in pkgs:
            try:
                packages_info.append(distribution(pkg))
            except  PackageNotFoundError as err:
                continue

        for info in packages_info:
            metadata = info.metadata

            name =  metadata.get('Name', '')
            key = 'pip:' + name.lower()

            version = metadata.get('Version', None)
            if version is None:
                versions = []
            else:
                versions = [version]

            dep = {
                'name': name,
                'key': key,
                'versions': versions
            }

            if name not in processed_packages:
                processed_packages.add(name)
                licence = metadata.get('License', None)
                if licence is None:
                    licenses = []
                else:
                    licenses = [{'name': licence}]

                dep['description'] = metadata.get('Summary', '')
                dep['private']  = False
                dep['homepageUrl'] = metadata.get('Home-page', '')
                dep['repoUrl'] = metadata.get('Download-URL', '')
                dep['checksum'] = ''
                dep['licenses'] = licenses

                deps = [pkg for pkg in parse_requires(info.requires)]
                dep['dependencies'] = [d for d in do_create_dependencies(deps)]

            yield dep

    return [dep for dep in do_create_dependencies(packages)]