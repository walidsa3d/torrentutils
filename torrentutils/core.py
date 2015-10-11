import requests

import base64
import bencode
import hashlib

from collections import defaultdict

def parse(magnet_uri):
    """returns a dictionary of parameters contained in the uri"""
    data = defaultdict(list)
    if not magnet_uri.startswith('magnet:'):
        return data
    else:
        magnet_uri = magnet_uri.strip("magnet:?")
        for segment in magnet_uri.split('&'):
            key, value = segment.split("=")
            if key == 'dn':
                data['name'] = requests.utils.unquote(value).replace('+', '.')
            elif key == 'xt':
                data['infoHash'] = value.strip('urn:btih:')
            elif key == 'tr':
                data['trackers'].append(requests.utils.unquote(value))
            else:
                data[key] = value
    return data

def to_magnet(torrent_link):
    """converts a torrent file to a magnet link"""
    response = requests.get(torrent_link, timeout=20)
    print response
    with open('/tmp/tempfile.torrent', 'w') as out_file:
        out_file.write(response.content)
    torrent = open('/tmp/tempfile.torrent', 'r').read()
    metadata = bencode.bdecode(torrent)
    hashcontents = bencode.bencode(metadata['info'])
    digest = hashlib.sha1(hashcontents).digest()
    b32hash = base64.b32encode(digest)
    magneturi = 'magnet:?xt=urn:btih:%s' % b32hash
    return magneturi
