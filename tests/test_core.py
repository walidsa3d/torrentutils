import unittest

from torrentutils import core


class CoreTest(unittest.TestCase):

    def test_parse(self):
        magnet_uri = 'magnet:?xt=urn:btih:E8BB36B5199EB989D49828460CF90019958A3F4C&dn=san+andreas+2015+1080p+brrip+x264+yify&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'
        data = core.parse(magnet_uri)
        self.assertEqual(
            data['name'], 'san.andreas.2015.1080p.brrip.x264.yify')
        self.assertEqual(data['infoHash'], 'E8BB36B5199EB989D49828460CF90019958A3F4C')
