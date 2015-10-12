from __future__ import division

import requests

import base64
import bencode
import hashlib
import math

from collections import defaultdict
from datetime import datetime

HEADERS = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}


def parse_magnet(magnet_uri):
    """returns a dictionary of parameters contained in the uri"""
    data = defaultdict(list)
    if not magnet_uri.startswith('magnet:'):
        return data
    else:
        magnet_uri = magnet_uri.strip('magnet:?')
        for segment in magnet_uri.split('&'):
            key, value = segment.split('=')
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
    md = parse_torrent(torrent_link)
    if md:
        magneturi = 'magnet:?xt=urn:btih:%s' % md['infoHash']
        return magneturi
    return None


def parse_remote_torrent(torrent_link):
    """converts a remote torrent file to a magnet link"""
    response = requests.get(torrent_link, headers=HEADERS, timeout=20)
    return parse_torrent(response.content)


def parse_local_torrent(torrent_file):
    """converts a local torrent file to a magnet link"""
    with open(torrent_file, 'rb') as f:
        data = parse_torrent(f.read())
    return data


def parse_torrent(torrent):
    """parse a torrent buffer"""
    md = {}
    try:
        metadata = bencode.bdecode(torrent)
    except bencode.BTL.BTFailure:
        print 'Not a valid encoded torrent'
        return None
    if 'announce-list' in metadata:
        md['trackers'] = []
        for tracker in metadata['announce-list']:
            md['trackers'].append(tracker[0])
    if 'announce' in metadata:
        md['trackers'].append(metadata['announce'])
    md['trackers'] = list(set(md['trackers']))
    if 'name' in metadata['info']:
        md['name'] = metadata['info']['name']
    webseeds = []
    if 'httpseeds' in metadata:
        webseeds = metadata['httpseeds']
    if 'url-list' in metadata:
        webseeds += md['url-list']
    if webseeds:
        md['webseeds'] = webseeds
    if 'created by' in metadata:
        md['creator'] = metadata['created by']
    if 'creation date' in metadata:
        utc_dt = datetime.utcfromtimestamp(metadata['creation date'])
        md['created'] = utc_dt.strftime('%Y-%m-%d %H:%M:%S')
    if 'comment' in metadata:
        md['comment'] = metadata['comment']
    md['piece_size'] = metadata['info']['piece length']
    if 'files' in metadata['info']:
        md['files'] = []
        for item in metadata['info']['files']:
            md['files'].append({'path': item['path'][0], 'length': item['length']})
    hashcontents = bencode.bencode(metadata['info'])
    digest = hashlib.sha1(hashcontents).digest()
    md['infoHash'] = hashlib.sha1(hashcontents).hexdigest()
    b32hash = base64.b32encode(digest)
    md['infoHash_b32'] = b32hash
    md['pieces'] = _split_pieces(metadata['info']['pieces'])
    return md


def _split_pieces(buf):
    pieces = []
    i = 0
    while i < len(buf):
        byte_str = buf[i:i + 20]
        hex_str = ''.join(["%02X" % ord(x) for x in byte_str]).strip()
        pieces.append(hex_str)
        i = i+20
    return pieces


def hsize(bytes):
    """converts a bytes to human-readable format"""
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    if bytes == 0:
        return '0 Byte'
    i = int(math.floor(math.log(bytes) / math.log(1024)))
    r = round(bytes / math.pow(1024, i), 2)
    return str(r) + '' + sizes[i]


def ratio(leechs, seeds):
    """ computes the torrent ratio"""
    try:
        ratio = float(seeds) / float(leechs)
    except ZeroDivisionError:
        ratio = int(seeds)
    return ratio


def make_torrent():
    pass
