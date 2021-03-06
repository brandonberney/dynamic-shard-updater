import glob
import os
import sys
import threading
import time

from shard import constants

class Follow(threading.Thread):
    def __init__(self, directory, interval):
        threading.Thread.__init__(self)

        self.directory = directory
        self.interval = int(interval)

        newest = max(glob.iglob(self.directory + '*.log'), key=os.path.getctime)
        print(constants.READING_LOG % newest)
        self.logfile = open(newest)
        loglines = self.follow()

        for line in loglines:
            if constants.OTP_ENTERING_SHARD in line:
                shard_line = line.split(constants.COMMAND_SPACE)
                shard_id = shard_line[-1].rstrip()
                shard_name = constants.SHARDS[shard_id]

                print(constants.NEW_SHARD % (int(shard_id), shard_name))
                self.write(int(shard_id), shard_name)

    def follow(self):
        self.logfile.seek(0, 2)
        while True:
            line = self.logfile.readline()
            if not line:
                time.sleep(self.interval)
                continue
            yield line

    def write(self, shard, shard_name):
        # We're going to make two files. One with District Name: {{ name }},
        # and the other with simply the name of the shard.

        district_full = open(constants.DISTRICT_FILE, 'w')
        district_name = open(constants.DISTRICT_NAME_FILE, 'w')

        if shard_name is None:
            district_full.write(constants.CURRENT_DISTRICT %
                           constants.DISTRICT_UNKNOWN)
            district_name.write(constants.DISTRICT_UNKNOWN)
        else:
            district_full.write(constants.CURRENT_DISTRICT % shard_name)
            district_name.write(shard_name)

        # We need to ensure we close these files, or we'll run into problems.
        district_full.close()
        district_name.close()
