# coding: utf-8
"""
Helper functions for filename and URL generation.
"""
import sys
import os
import subprocess
import urllib.request
import urllib.error
import logging
import tarfile

from io import BytesIO


__author__ = 'Yeongbin Jo <yeongbin.jo@pylab.co>'


def get_geckodriver_filename():
    """
    Returns the filename of the binary for the current platform.
    :return: Binary filename
    """
    if sys.platform.startswith('win'):
        return 'geckodriver.exe'
    return 'geckodriver'


def get_variable_separator():
    """
    Returns the environment variable separator for the current platform.
    :return: Environment variable separator
    """
    if sys.platform.startswith('win'):
        return ';'
    return ':'


def get_platform_architecture():
    if sys.platform.startswith('linux') and sys.maxsize > 2 ** 32:
        platform = 'linux'
        architecture = '64'
    elif sys.platform == 'darwin':
        platform = 'mac'
        architecture = 'os'
    elif sys.platform.startswith('win'):
        platform = 'win'
        architecture = '32'
    else:
        raise RuntimeError('Could not determine geckodriver download URL for this platform.')
    return platform, architecture


def get_geckodriver_url(version):
    """
    Generates the download URL for current platform , architecture and the given version.
    Supports Linux, MacOS and Windows.
    :param version: the version of geckodriver
    :return: Download URL for geckodriver
    """
    platform, architecture = get_platform_architecture()
    return f'https://github.com/mozilla/geckodriver/releases/download/{version}' \
           f'/geckodriver-{version}-{platform}{architecture}.tar.gz'


def find_binary_in_path(filename):
    """
    Searches for a binary named `filename` in the current PATH. If an executable is found, its absolute path is returned
    else None.
    :param filename: Filename of the binary
    :return: Absolute path or None
    """
    if 'PATH' not in os.environ:
        return None
    for directory in os.environ['PATH'].split(get_variable_separator()):
        binary = os.path.abspath(os.path.join(directory, filename))
        if os.path.isfile(binary) and os.access(binary, os.X_OK):
            return binary
    return None


def get_firefox_version():
    """
    :return: the version of firefox installed on client
    """
    platform, _ = get_platform_architecture()
    if platform == 'linux':
        with subprocess.Popen(['firefox', '--version'], stdout=subprocess.PIPE) as proc:
            version = proc.stdout.read().decode('utf-8').replace('Mozilla Firefox', '').strip()
    elif platform == 'mac':
        process = subprocess.Popen(['/Applications/Firefox.app/Contents/MacOS/firefox', '--version'], stdout=subprocess.PIPE)
        version = process.communicate()[0].decode('UTF-8').replace('Mozilla Firefox', '').strip()
    elif platform == 'win':
        path1 = 'C:\\PROGRA~1\\Mozilla Firefox\\firefox.exe'
        path2 = 'C:\\PROGRA~2\\Mozilla Firefox\\firefox.exe'
        if os.path.exists(path1):
            process = subprocess.Popen([path1, '-v', '|', 'more'], stdout=subprocess.PIPE)
        elif os.path.exists(path2):
            process = subprocess.Popen([path2, '-v', '|', 'more'], stdout=subprocess.PIPE)
        else:
            return
        version = process.communicate()[0].decode('UTF-8').replace('Mozilla Firefox', '').strip()
    else:
        return
    return version


def get_major_version(version):
    """
    :param version: the version of firefox
    :return: the major version of firefox
    """
    return version.split('.')[0]


def get_latest_geckodriver_version():
    """
    :return: the latest version of geckodriver
    """
    url = urllib.request.urlopen('https://github.com/mozilla/geckodriver/releases/latest').geturl()
    if '/tag/' not in url:
        return
    return url.split('/')[-1]


def get_geckodriver_path():
    """
    :return: path of the geckodriver binary
    """
    return os.path.abspath(os.path.dirname(__file__))


def print_geckodriver_path():
    """
    Print the path of the geckodriver binary.
    """
    print(get_geckodriver_path())


def download_geckodriver(cwd=False):
    """
    Downloads, unzips and installs geckodriver.
    If a geckodriver binary is found in PATH it will be copied, otherwise downloaded.

    :param cwd: Flag indicating whether to download to current working directory
    :return: The file path of geckodriver
    """
    firefox_version = get_firefox_version()
    if not firefox_version:
        logging.debug('Firefox is not installed.')
        return
    geckodriver_version = get_latest_geckodriver_version()
    if not geckodriver_version:
        logging.debug('Can not find latest version of geckodriver.')
        return

    if cwd:
        geckodriver_dir = os.path.join(
            os.path.abspath(os.getcwd()),
            geckodriver_version
        )
    else:
        geckodriver_dir = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            geckodriver_version
        )
    geckodriver_filename = get_geckodriver_filename()
    geckodriver_filepath = os.path.join(geckodriver_dir, geckodriver_filename)
    if not os.path.isfile(geckodriver_filepath):
        logging.debug(f'Downloading geckodriver ({geckodriver_version})...')
        if not os.path.isdir(geckodriver_dir):
            os.mkdir(geckodriver_dir)
        url = get_geckodriver_url(geckodriver_version)
        try:
            response = urllib.request.urlopen(url)
            if response.getcode() != 200:
                raise urllib.error.URLError('Not Found')
        except urllib.error.URLError:
            raise RuntimeError(f'Failed to download geckodriver archive: {url}')
        archive = BytesIO(response.read())

        tar = tarfile.open(fileobj=archive, mode='r:gz')
        tar.extractall(geckodriver_dir)
        tar.close()
    else:
        logging.debug('geckodriver is already installed.')
    if not os.access(geckodriver_filepath, os.X_OK):
        os.chmod(geckodriver_filepath, 0o744)
    return geckodriver_filepath


if __name__ == '__main__':
    print(get_firefox_version())
    print(download_geckodriver())
