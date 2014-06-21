import os
import urllib2

import logger


def clone_status(target_file):
    """
    Backup Vatsim status.txt file that contains data necessary to launch Vatsinator.
    @param target_file: name of the target file.
    """
    url = 'http://status.vatsim.net/status.txt'
    logger.info('Downloading %s to %s...' % (url, target_file))
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Vatsinator Buildbot/1.0')
    response = urllib2.urlopen(request)
    content = response.read()

    bak_file = target_file + '.bak'
    if os.path.isfile(target_file):
        os.rename(target_file, bak_file)

    f = open(target_file, 'w')
    f.write(content)
    f.close()

    if os.path.isfile(bak_file):
        os.remove(bak_file)

    logger.info('clone_status done.')
