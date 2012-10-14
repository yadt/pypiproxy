#   pypiproxy
#   Copyright 2012 Michael Gruber, Alexander Metzner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

__author__ = "Alexander Metzner, Michael Gruber"

import itertools
import logging
import glob
import os
import re
import urllib2

LOGGER = logging.getLogger("pypiproxy.packageindex")

_PACKAGE_NAME_AND_VERSION_PATTERN = re.compile(r"^(.*?)(-([0-9.]+.*)).tar.gz$")

def _guess_name_and_version(filename):
    result = _PACKAGE_NAME_AND_VERSION_PATTERN.match(filename)
    if result:
        return result.group(1), result.group(3)

    filename = filename.replace(r".tar.gz", "")

    if "-" in filename:
        split_index = filename.rfind("-")
        return filename[0:split_index], filename[split_index + 1:]

    raise ValueError("Invalid package file name: '{0}'".format(filename))


class PackageIndex(object):
    FILE_SUFFIX = ".tar.gz"

    def __init__(self, name, directory):
        self._name = name
        self._directory = directory
        LOGGER.info("Creating packageindex '%s' serving directory '%s'", name, self._directory)

        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

    @property
    def directory(self):
        return self._directory

    def add_package(self, name, version, content_stream):
        filename = self._filename_from_name_and_version(name, version)

        LOGGER.info("Adding package '%s %s' to file '%s'", name, version, filename)

        with open(filename, "wb") as package_file:
            package_file.write(content_stream)

    def contains(self, name, version="*"):
        filename = self._filename_from_name_and_version(name, version)
        list_of_files = glob.glob(filename)
        return len(list_of_files) > 0

    def count_packages(self):
        return len([p for p in self._read_packages()])

    def get_package_content(self, package, version):
        filename = os.path.join(self._directory, package + "-" + version + PackageIndex.FILE_SUFFIX)
        if not self.contains(package, version):
            return None

        with open(filename, "rb") as f:
            return f.read()

    def list_available_package_names(self):
        package_names = [p for p in itertools.imap(lambda name_and_version: name_and_version[0], self._read_packages())]
        package_names = sorted(package_names)
        return UniqueIterator(package_names.__iter__())

    def list_versions(self, name):
        LOGGER.info("Listing versions for '{0}'".format(name))

        return itertools.imap(lambda name_and_version: name_and_version[1],
            itertools.ifilter(lambda name_and_version: name_and_version[0] == name, self._read_packages()))

    def _filename_from_name_and_version(self, name, version):
        return os.path.join(self._directory, "{0}-{1}{2}".format(name, version, PackageIndex.FILE_SUFFIX))

    def _read_files(self):
        return itertools.ifilter(lambda f: f.endswith(PackageIndex.FILE_SUFFIX), os.listdir(self._directory))

    def _read_packages(self):
        return itertools.imap(_guess_name_and_version, self._read_files())


class ProxyPackageIndex(object):
    """
    Retrieves the packages from another pypi and stores them in a package index. 
    """
    def __init__(self, name, directory, pypi_url):
        self._package_index = PackageIndex(name, directory)
        self._pypi_url = pypi_url

    def get_package_content(self, name, version):
        if not self._package_index.contains(name, version):
            filename = "{0}-{1}{2}".format(name, version, PackageIndex.FILE_SUFFIX)
            package_url = "{0}/packages/source/{1}/{2}/{3}".format(self._pypi_url, name[0], name, filename)
            package_stream = urllib2.urlopen(package_url)

            self._package_index.add_package(name, version, package_stream)

        return self._package_index.get_package_content(name, version)

    def list_available_package_names(self):
        raise NotImplementedError()

    def list_versions(self, name):
        return self._package_index.list_versions(name)


class UniqueIterator(object):
    """
    Iterator that only yields a value if it differs from the value returned before.
    """

    def __init__(self, base_iterator):
        self._base_iterator = base_iterator
        self._last_value = None
        self._started = False

    def __iter__(self):
        return self

    def next(self):
        candidate = self._base_iterator.next()
        if not self._started:
            self._started = True
            self._last_value = candidate
            return candidate

        if self._last_value == candidate:
            return self.next()
        self._last_value = candidate
        return candidate

