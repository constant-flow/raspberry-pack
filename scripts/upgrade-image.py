#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# This script alters the disto-image, by changing the '/etc/rc.local'
#
# It replaces one comment by a line that starts the raspberry-pack process
# on the first boot.
#
# This is based on: 
#   https://www.raspberrypi.org/forums/viewtopic.php?t=197052#p1231634
# -----------------------------------------------------------------------------

import re
import os

IO_FILE = "raspberry-pack.img"
BLOCK_SIZE = 64 * (1 << 20)

# This 'SEARCH_REPLACEMENT' string must be of exact same length!
SEARCH_ORIGINAL     = b'# By default this script does nothing.'
SEARCH_REPLACEMENT  = b'sudo bash /boot/script-starter.sh #new'

injectionSuccessful  = False
injectionAlreadyDone = False

with open(IO_FILE, 'rb+') as f:    
    f.seek(0)
    while True:
        block = f.read(BLOCK_SIZE) # Read 64 MB at a time; big, but not memory busting
        if not block:  # Reached EOF
            break
        
        match = re.search(SEARCH_ORIGINAL, block)
        if match:
            #movecursor to beginning of block
            f.seek(-BLOCK_SIZE, os.SEEK_CUR)
            changedBlock = re.sub(SEARCH_ORIGINAL, SEARCH_REPLACEMENT, block)
            f.write(changedBlock)
            print("Success: Raspberry-pack autostart script injected!")
            f.close()
            injectionSuccessful = True
            break

        match = re.search(SEARCH_REPLACEMENT, block)
        if match:
            injectionAlreadyDone = True

if not injectionSuccessful:
    if not injectionAlreadyDone:
        print("Failed: /etc/rc.local didn't contain expected content !!!")
    else:
        print("Success: Nothing to do, you ran this already.")

f.close()

        
        
