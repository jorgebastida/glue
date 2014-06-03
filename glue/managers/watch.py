import os
import sys
import time
import signal
import hashlib


class WatchManager(object):

    def __init__(self, manager_cls, options):
        self.manager_cls = manager_cls
        self.options = options
        self.last_hash = self.manager = None
        signal.signal(signal.SIGINT, self.signal_handler)

    def process(self):
        while True:
            current_hash = self.generate_hash()
            if self.last_hash != current_hash:
                self.manager = self.manager_cls(**self.options)
                self.manager.process()
            self.last_hash = current_hash
            time.sleep(0.2)

    def generate_hash(self):
        """ Return a hash of files and modification times to determine if a
        change has occourred."""

        hash_list = []
        for root, dirs, files in os.walk(self.options['source']):
            for f in sorted([f for f in files if not f.startswith('.')]):
                hash_list.append(os.path.join(root, f))
                hash_list.append(str(os.path.getmtime(os.path.join(root, f))))
        hash_list = ''.join(hash_list)

        if sys.version < '3':
            return hashlib.sha1(hash_list).hexdigest()
        return hashlib.sha1(hash_list.encode('utf-8')).hexdigest()

    def signal_handler(self, signal, frame):
        """ Gracefully close the app if Ctrl+C is pressed."""
        print 'You pressed Ctrl+C!'
        sys.exit(0)
