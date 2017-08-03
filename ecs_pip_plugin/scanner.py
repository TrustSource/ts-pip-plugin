import os
import re

import pip
import pip.commands.show


class Scanner:
    def __init__(self, client):
        self._client = client

        self._found_packages = set()
        self._import_statement_regex = re.compile(r'(?:from|import) ([a-zA-Z0-9]+)(?:.*)')


    def run(self):
        scanPath = self._client.scanPath
        path = os.path.expanduser(scanPath)
        path = os.path.expandvars(path)
        os.path.walk(path, Scanner._scan_dir, self)

        mod = os.path.basename(scanPath.rstrip(os.sep))

        scanInfo = {
            'project': self._client.projectName,
            'module': mod,
            'moduleId': 'pip:' + mod,
            'dependencies': create_dependencies(self._found_packages)
        }

        return scanInfo


    def _scan_dir(self, dir_path, names):
        for n in names:
            name = os.path.join(dir_path, n)
            if os.path.isfile(name) and os.path.splitext(name)[-1].lower() == '.py':
                self._extract_imports(name)

    def _extract_imports(self, src_file):
        with open(src_file, "r") as src:
            imports = self._import_statement_regex.findall(src.read())
            self._found_packages |= set(imports)


def create_dependencies(packages):

    processed_packages = set()

    def do_create_dependencies(pkgs):
        packages_info = pip.commands.show.search_packages_info(pkgs)
        for info in packages_info:
            name = info.get('name', '')
            key = 'pip:' + name.lower()

            version = info.get('version', None)
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
                licence = info.get('license', None)
                if licence is None:
                    licenses = []
                else:
                    licenses = [{'name': licence}]

                dep['description'] = info.get('summary', '')
                dep['private']  = False
                dep['homepageUrl'] = info.get('home-page', '')
                dep['repoUrl'] = ''
                dep['checksum'] = ''
                dep['licenses'] = licenses
                dep['dependencies'] = [d for d in do_create_dependencies(info.get('requires', []))]

            yield dep

    return [dep for dep in do_create_dependencies(packages)]