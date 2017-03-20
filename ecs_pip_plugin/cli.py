
from scanner import *

import sys
import getopt
import json
import requests


def usage():
    print 'usage: ecs_pip_plugin <project folder>'

def main():
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(args, '', [])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    scan_path = os.getcwd()
    if len(args) > 1:
        usage()
        exit(2)
    elif len(args) == 1:
        scan_path = args[0]

    if not os.path.isdir(scan_path):
        print('\'' + scan_path + '\'' + ' is not a folder')
        usage()
        exit(2)

    settings_path = os.path.join(scan_path, 'ecs-plugin.json')
    if not os.path.exists(settings_path) or not os.path.isfile(settings_path):
        print('Cannot find project settings \'ecs-plugin.json\' in \'' + settings_path + '\'')
        exit(2)

    settings = {}
    with open(settings_path) as settings_file:
        try:
            settings = json.load(settings_file)
        except Exception as err:
            print('Cannot read \'ecs-plugin.json\'')
            if err.message != '':
                print(err.message)
            exit(2)

    userName = settings.get('userName', '')
    apiKey = settings.get('apiKey', '')

    if (userName == '') and (apiKey == ''):
        credentials_path = settings.get('credentials', None)
        if credentials_path is not None:
            try:
                with open(os.path.join(scan_path, credentials_path)) as credentials_file:
                    credentials = json.load(credentials_file)
                    userName = credentials.get('userName', '')
                    apiKey = credentials.get('apiKey', '')
            except Exception as err:
                if err.message != '':
                    print(err.message)


    project = settings.get('project', '')
    module = os.path.basename(scan_path.rstrip(os.sep))

    scanner = Scanner(scan_path)
    dependencies = scanner.run()

    scanInfo = {
        'project': project,
        'module': module,
        'moduleId': 'pip:' + module,
        'dependencies': dependencies
    }

    if not settings.get('skipTransfer', False):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'ecs-pip-plugin/0.1.0',
            'X-USER': userName,
            'X-APIKEY': apiKey
        }

        response = requests.post('https://ecs-app.eacg.de/api/v1/scans', json=scanInfo, headers=headers)

        if response.status_code == 201:
            exit(0)
        else:
            print(json.dumps(response.content, indent=2))
            exit(2)
    else:
        print(json.dumps(scanInfo, indent=2))


if __name__ == '__main__':
    main()