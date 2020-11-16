import os
import re

from importlib_metadata import metadata, PackageNotFoundError

class Scanner:
    def __init__(self, client):
        self._client = client

        self._found_packages = set()
        self._import_statement_regex = re.compile(r'(?:from|import) ([a-zA-Z0-9_]+)(?:.*)')


    def _extract_imports(self, src_file):
        with open(src_file, "r") as src:
            imports = self._import_statement_regex.findall(src.read())
            self._found_packages |= set(imports)


    def run(self):
        scanPath = self._client.scanPath
        path = os.path.expanduser(scanPath)
        path = os.path.expandvars(path)

        for dirpath, _, filenames in os.walk(path):
            for n in filenames:
                name = os.path.join(dirpath, n)
                if os.path.isfile(name) and os.path.splitext(name)[-1].lower() == '.py':
                    self._extract_imports(name)

        mod = os.path.basename(scanPath.rstrip(os.sep))

        scanInfo = {
            'project': self._client.projectName,
            'module': mod,
            'moduleId': 'pip:' + mod,
            'dependencies': create_dependencies(self._found_packages)
        }

        return scanInfo


def create_dependencies(packages):

    processed_packages = set()

    def do_create_dependencies(pkgs):
        packages_info = []
        for pkg in pkgs:
            try:
                packages_info.append(metadata(pkg))
            except  PackageNotFoundError as err:
                continue

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