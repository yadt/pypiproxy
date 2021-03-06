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

__author__ = "Alexander Metzner"

import StringIO

from pyfix import test, given, Fixture
from pyfix.fixtures import TemporaryDirectoryFixture
from pyassert import assert_that


from pypiproxy.packageindex import PackageIndex, _guess_name_and_version


class PackageData(Fixture):
    def provide(self):
        data_buffer = StringIO.StringIO()
        data_buffer.write("some package data")
        return [data_buffer.getvalue()]


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
def guess_name_and_version_should_understand_version_without_numbers_and_dots():
    assert_that(_guess_name_and_version("spam-and-eggs.tar.gz")).is_equal_to(("spam-and", "eggs"))


@test
def guess_name_and_version_should_understand_file_name_without_dash():
    def callback():
        _guess_name_and_version("spam.tar.gz")

    assert_that(callback).raises(ValueError)


@test
@given(temp_dir=TemporaryDirectoryFixture)
def ensure_that_constructor_creates_directory_if_it_does_not_exist(temp_dir):
    package_dir = temp_dir.join("packages")
    PackageIndex("any_name", package_dir)

    assert_that(package_dir).is_a_directory()


@test
@given(temp_dir=TemporaryDirectoryFixture)
def list_available_package_names_should_return_single_package_when_directory_contains_single_package_file(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    names = [name for name in index.list_available_package_names()]

    assert_that(names).is_equal_to(["spam"])


@test
@given(temp_dir=TemporaryDirectoryFixture)
def list_available_package_names_should_return_two_packages_when_directory_contains_two_package_files(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")
    temp_dir.touch("packages", "eggs-0.1.2.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    names = sorted([name for name in index.list_available_package_names()])

    assert_that(names).is_equal_to(["eggs", "spam"])


@test
@given(temp_dir=TemporaryDirectoryFixture)
def list_available_package_names_should_return_single_package_when_directory_contains_two_package_files_for_the_same_package_name(
        temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")
    temp_dir.touch("packages", "spam-0.1.3.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    names = [name for name in index.list_available_package_names()]

    assert_that(names).is_equal_to(["spam"])


@test
@given(temp_dir=TemporaryDirectoryFixture)
def list_versions_should_return_empty_list_when_no_package_files_are_found(temp_dir):
    temp_dir.create_directory("packages")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    versions = [v for v in index.list_versions("spam")]

    assert_that(versions).is_empty()


@test
@given(temp_dir=TemporaryDirectoryFixture)
def list_versions_should_return_single_version_when_single_package_file_matches_package_name(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    versions = [v for v in index.list_versions("spam")]

    assert_that(versions).is_equal_to(["0.1.2"])


@test
@given(temp_dir=TemporaryDirectoryFixture)
def list_versions_should_return_two_versions_when_two_package_files_match_package_name(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")
    temp_dir.touch("packages", "spam-0.1.3.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    versions = sorted([v for v in index.list_versions("spam")])

    assert_that(versions).is_equal_to(["0.1.2", "0.1.3"])


@test
@given(temp_dir=TemporaryDirectoryFixture)
def list_versions_should_ignore_package_files_when_name_does_not_match_wanted_name(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "eggs-0.1.2.tar.gz")
    temp_dir.touch("packages", "eggs-0.1.3.tar.gz")

    index = PackageIndex("any_name", temp_dir.join("packages"))
    versions = [v for v in index.list_versions("spam")]

    assert_that(versions).is_empty()


@test
@given(temp_dir=TemporaryDirectoryFixture)
def get_package_content_should_return_file_content_when_file_exists(temp_dir):
    content = "spam and eggs"
    temp_dir.create_directory("packages")
    temp_dir.create_file(["packages", "eggs-0.1.2.tar.gz"], content, binary=True)

    index = PackageIndex("any_name", temp_dir.join("packages"))

    actual_content = index.get_package_content("eggs", "0.1.2")

    assert_that(actual_content).is_equal_to(content)


@test
@given(temp_dir=TemporaryDirectoryFixture)
def get_package_content_should_return_none_when_file_does_not_exist(temp_dir):
    temp_dir.create_directory("packages")

    index = PackageIndex("any_name", temp_dir.join("packages"))

    actual_content = index.get_package_content("eggs", "0.1.2")

    assert_that(actual_content).is_none()


@test
@given(temp_dir=TemporaryDirectoryFixture, package_data=PackageData)
def add_package_should_write_package_file(temp_dir, package_data):
    index = PackageIndex("any_name", temp_dir.join("packages"))
    index.add_package("spam", "version", package_data)

    expected_file_name = temp_dir.join("packages", "spam-version.tar.gz")
    assert_that(expected_file_name).is_a_file()
    assert_that(expected_file_name).has_file_length_of(17)


@test
@given(temp_dir=TemporaryDirectoryFixture)
def count_packages_should_return_zero_when_directory_is_empty(temp_dir):
    index = PackageIndex("any_name", temp_dir.join("packages"))

    assert_that(index.count_packages()).is_equal_to(0)


@test
@given(temp_dir=TemporaryDirectoryFixture)
def count_packages_should_return_one_when_directory_is_empty(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-eggs.tar.gz")
    index = PackageIndex("any_name", temp_dir.join("packages"))

    assert_that(index.count_packages()).is_equal_to(1)


@test
@given(temp_dir=TemporaryDirectoryFixture)
def contains_should_return_false_if_package_not_available(temp_dir):
    temp_dir.create_directory("packages")
    index = PackageIndex("any_name", temp_dir.join("packages"))

    assert_that(index.contains("egg", "0.1.2")).is_equal_to(False)


@test
@given(temp_dir=TemporaryDirectoryFixture)
def contains_should_return_true_if_package_available(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.5.tar.gz")
    index = PackageIndex("any_name", temp_dir.join("packages"))

    assert_that(index.contains("spam")).is_equal_to(True)

@test
@given(temp_dir=TemporaryDirectoryFixture)
def contains_should_return_true_if_package_in_specific_version_available(temp_dir):
    temp_dir.create_directory("packages")
    temp_dir.touch("packages", "spam-0.1.2.tar.gz")
    index = PackageIndex("any_name", temp_dir.join("packages"))

    assert_that(index.contains("spam", "0.1.2")).is_equal_to(True)


if __name__ == "__main__":
    from pyfix import run_tests

    run_tests()
