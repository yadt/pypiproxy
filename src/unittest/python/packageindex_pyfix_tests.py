__author__ = "Alexander Metzner"

import os
import shutil
import tempfile

from pyfix import test, given, Fixture
from pyassert import assert_that

import filesystem_matchers

from pypiproxy.packageindex import PackageIndex, _guess_name_and_version

class TempDirHandle(object):
    def __init__(self):
        self.basedir = tempfile.mkdtemp(prefix=__name__)

    def __del__(self):
        if os.path.exists(self.basedir):
            shutil.rmtree(self.basedir)

    def join(self, *path_elements):
        path_elements = [self.basedir] + list(path_elements)
        return os.path.join(*path_elements)

    def touch(self, *path_elements):
        f = open(self.join(*path_elements), "w")
        try:
            f.write("")
        finally:
            f.close()

    def create_directory(self, *path_elements):
        os.makedirs(self.join(*path_elements))


class TempDirFixture(Fixture):
    def reclaim(self, temp_dir_handle):
        del temp_dir_handle

    def provide(self):
        return [TempDirHandle()]


@test
def guess_name_and_version_should_understand_single_digit_version():
    assert_that(_guess_name_and_version("spam-1.tar.gz")).is_equal_to(("spam", "1"))


@test
def guess_name_and_version_should_understand_simple_version():
    assert_that(_guess_name_and_version("spam-1.2.tar.gz")).is_equal_to(("spam", "1.2"))


@test
def guess_name_and_version_should_understand_simple_version_with_suffix():
    assert_that(_guess_name_and_version("spam-1.2-rc1.tar.gz")).is_equal_to(("spam", "1.2-rc1"))


@test
def guess_name_and_version_should_understand_dashed_package_name_with_simple_version_with_suffix():
    assert_that(_guess_name_and_version("spam-and-eggs-1.2-rc1.tar.gz")).is_equal_to(("spam-and-eggs", "1.2-rc1"))


@test
@given(temp_dir=TempDirFixture)
def ensure_that_constructor_creates_directory_if_it_does_not_exist(temp_dir):
    package_dir = temp_dir.join("packages")
    PackageIndex("any_name", package_dir)

    assert_that(package_dir).is_a_directory()


@test
@given(temp_dir=TempDirFixture)
def list_available_package_names_should_return_single_package_when_directory_contains_single_package_file(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    names = [name for name in index.list_available_package_names()]

    assert_that(names).is_equal_to(["spam"])


@test
@given(temp_dir=TempDirFixture)
def list_available_package_names_should_return_two_packages_when_directory_contains_two_package_files(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")
    temp_dir.touch("packages", "eggs-0.1.2.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    names = [name for name in index.list_available_package_names()]

    assert_that(names).is_equal_to(["eggs", "spam"])


@test
@given(temp_dir=TempDirFixture)
def list_available_package_names_should_return_single_package_when_directory_contains_two_package_files_for_the_same_package_name(
        temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")
    temp_dir.touch("packages", "spam-0.1.3.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    names = [name for name in index.list_available_package_names()]

    assert_that(names).is_equal_to(["spam"])


@test
@given(temp_dir=TempDirFixture)
def list_versions_should_return_empty_list_when_no_package_files_are_found(temp_dir):
    temp_dir.create_directory("packages")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    versions = [v for v in index.list_versions("spam")]

    assert_that(versions).is_empty()


@test
@given(temp_dir=TempDirFixture)
def list_versions_should_return_single_version_when_single_package_file_matches_package_name(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    versions = [v for v in index.list_versions("spam")]

    assert_that(versions).is_equal_to(["0.1.2"])


@test
@given(temp_dir=TempDirFixture)
def list_versions_should_return_two_versions_when_two_package_files_match_package_name(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")
    temp_dir.touch("packages", "spam-0.1.3.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    versions = [v for v in index.list_versions("spam")]

    assert_that(versions).is_equal_to(["0.1.3", "0.1.2"])


@test
@given(temp_dir=TempDirFixture)
def list_versions_should_ignore_package_files_when_name_does_not_match_wanted_name_(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "eggs-0.1.2.tar.gz")
    temp_dir.touch("packages", "eggs-0.1.3.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    versions = [v for v in index.list_versions("spam")]

    assert_that(versions).is_empty()
