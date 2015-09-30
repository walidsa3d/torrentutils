from collections import defaultdict
from requests.utils import unquote


def magnet_info(magnet_uri):
    """returns a dictionary of parameters contained in the uri"""
    data = defaultdict(list)
    if not magnet_uri.startswith('magnet:'):
        return data
    else:
        magnet_uri = magnet_uri.strip("magnet:?")
        trackers = []
        for segment in magnet_uri.split('&'):
            key, value = segment.split("=")
            if key == 'dn':
                data['name'] = unquote(value).replace('+', '.')
            elif key == 'xt':
                data['infoHash'] = value.strip('urn:btih:')
            elif key == 'tr':
                data['trackers'].append(unquote(value))
            else:
                data[key] = value
    return data


mag = "magnet:?xt=urn:btih:93E545F95354D90539C51BC3A59AC685B613C75C&dn=cinderella+2015+1080p+brrip+x264+yify&tr=udp%3A%2F%2Ftracker.publicbt.com%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.com%3A1337"
print magnet_info(mag)
