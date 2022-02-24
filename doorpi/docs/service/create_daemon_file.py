import doorpi.metadata as metadata
import os
import urllib.request
import urllib.error
import urllib.parse


def parse_string(raw_string):
    for meta_key in dir(metadata):
        if not meta_key.startswith('__'):
            raw_string = raw_string.replace(('!!{}!!').format(
                meta_key),  str(getattr(metadata, meta_key)))
    return raw_string


def create_daemon_file():
    print('start to create daemon file now...')
    print('start download and parse new daemon file:')
    print(('URL:  ' + metadata.daemon_online_template))
    print(('FILE: ' + metadata.daemon_file))
    with open(metadata.daemon_file, 'w') as daemon_file:
        for line in urllib.request.urlopen(metadata.daemon_online_template):
            daemon_file.write(parse_string(line))
        print('download successfully - change chmod to 0755 now')
        os.chmod(metadata.daemon_file, 0o755)
        print('finished')


if __name__ == '__main__':
    create_daemon_file()
