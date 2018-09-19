from ecs_python_client import *
from scanner import *

def main():
    tool = ECSClient('ecs_pip_plugin', Scanner)
    tool.run(sys.argv[1:])

if __name__ == '__main__':
    main()