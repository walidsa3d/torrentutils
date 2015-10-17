from __future__ import division

import requests

import base64
import bencode
import hashlib
import math
import os
import re

from collections import defaultdict
from datetime import datetime

HEADERS = {'User-Agent':
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}


def parse_magnet(magnet_uri):
    """returns a dictionary of parameters contained in a magnet uri"""
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
    md = parse_torrent_buffer(torrent_link)
    if md:
        magneturi = 'magnet:?xt=urn:btih:%s' % md['infoHash']
        return magneturi
    return None


def parse_torrent_file(torrent):
    """parse local or remote torrent file"""
    link_re = re.compile(r'^(http?s|ftp)')
    if link_re.match(torrent):
        response = requests.get(torrent, headers=HEADERS, timeout=20)
        data = parse_torrent_buffer(response.content)
    elif os.path.isfile(torrent):
        with open(torrent, 'rb') as f:
            data = parse_torrent_buffer(f.read())
    else:
        data = None
    return data


def parse_torrent_buffer(torrent):
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
    if 'length' in metadata['info']:
        md['file'] = {'path': metadata['info']['name'],
                      'length': metadata['info']['length']}
    if 'files' in metadata['info']:
        md['files'] = []
        for item in metadata['info']['files']:
            md['files'].append(
                {'path': item['path'][0], 'length': item['length']})
    # TODO check if torrent is private and encoding
    hashcontents = bencode.bencode(metadata['info'])
    digest = hashlib.sha1(hashcontents).digest()
    md['infoHash'] = hashlib.sha1(hashcontents).hexdigest()
    b32hash = base64.b32encode(digest)
    md['infoHash_b32'] = b32hash
    md['pieces'] = _split_pieces(metadata['info']['pieces'])
    md['total_size'] = hsize(sum([x['length'] for x in md['files']]))
    return md


def _split_pieces(buf):
    to_hex = lambda byte_str: ''.join(
        ['%02X' % ord(x) for x in byte_str]).strip()
    pieces = [to_hex(buf[i:i + 20]) for i in xrange(0, len(buf), 20)]
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


def to_torrent(magnet_link):
    """turn a magnet link to a link to a torrent file"""
    infoHash = parse_magnet(magnet_link)['infoHash']
    torcache = 'http://torcache.net/torrent/' + infoHash + '.torrent'
    torrage = 'https://torrage.com/torrent/' + infoHash + '.torrent'
    reflektor = 'http://reflektor.karmorra.info/torrent/' + \
        infoHash + '.torrent'
    thetorrent = 'http://TheTorrent.org/'+infoHash
    btcache = 'http://www.btcache.me/torrent/'+infoHash
    for link in [torcache, torrage, reflektor, btcache, thetorrent]:
        try:
            print "Checking "+link
            response = requests.head(link, headers=HEADERS)
            if response.headers['content-type'] in ['application/x-bittorrent',
                                                    'application/octet-stream']:
                return link
        except requests.exceptions.ConnectionError:
            pass
    return


def make_torrent():
    pass
