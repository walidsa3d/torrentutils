import requests

import base64
import bencode
import hashlib
import math

from collections import defaultdict


def parse_magnet(magnet_uri):
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
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}
    response = requests.get(torrent_link, headers=headers, timeout=20)
    with open('/tmp/tempfile.torrent', 'w') as out_file:
        out_file.write(response.content)
    torrent = open('/tmp/tempfile.torrent', 'r').read()
    metadata = bencode.bdecode(torrent)
    hashcontents = bencode.bencode(metadata['info'])
    digest = hashlib.sha1(hashcontents).digest()
    b32hash = base64.b32encode(digest)
    magneturi = 'magnet:?xt=urn:btih:%s' % b32hash
    return magneturi


def hsize(bytes):
    """converts a bytes to human-readable format"""
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if bytes == 0:
        return "0 Byte"
    i = int(math.floor(math.log(bytes) / math.log(1024)))
    r = round(bytes / math.pow(1024, i), 2)
    return str(r) + '' + sizes[i]


def ratio(leechs, seeds):
    """ computes the torrent ratio"""
    return seeds / leechs if leechs != 0 else float('inf')
