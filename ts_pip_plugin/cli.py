import sys

from ts_python_client.client import TSClient
from .scanner import *

def main():
    tool = TSClient('ts_pip_plugin', Scanner)
    tool.run(sys.argv[1:])

if __name__ == '__main__':
    main()