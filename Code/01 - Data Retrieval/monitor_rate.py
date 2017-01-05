
from utils import *

def monitor_rate(gh = None, resource='core', delay=5):
    if gh is None:
        gh = github_login()

    while True:
        show_rate_limit(gh, [resource], oneline=True)
        time.sleep(delay)

if __name__ == '__main__':
    monitor_rate()

