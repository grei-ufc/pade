import sys

sys.path.insert(1, '/home/lucas/Dropbox/workspace/Twisted_Agents/')

from misc.common import set_ams, start_loop

if __name__ == '__main__':
    set_ams('localhost', 8000)
    start_loop(list(), gui=True)
