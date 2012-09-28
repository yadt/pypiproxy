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

from pyfix import test, after
from pyassert import assert_that
from mockito import mock, verify, unstub, when

import pypiproxy.services

@test
@after(unstub)
def ensure_that_list_available_package_names_delegates_to_hosted_packages_index():
    pypiproxy.services._hosted_packages_index = mock()

    pypiproxy.services.list_available_package_names()

    verify(pypiproxy.services._hosted_packages_index).list_available_package_names()


@test
@after(unstub)
def ensure_that_list_versions_delegates_to_hosted_packages_index():
    pypiproxy.services._hosted_packages_index = mock()

    pypiproxy.services.list_versions("spam")

    verify(pypiproxy.services._hosted_packages_index).list_versions("spam")


@test
@after(unstub)
def ensure_that_get_package_content_delegates_to_hosted_packages_index():
    pypiproxy.services._hosted_packages_index = mock()

    pypiproxy.services.get_package_content("spam", "0.1.1")

    verify(pypiproxy.services._hosted_packages_index).get_package_content("spam", "0.1.1")


@test
@after(unstub)
def ensure_that_add_package_delegates_to_hosted_packages_index():
    pypiproxy.services._hosted_packages_index = mock()

    pypiproxy.services.add_package("spam", "0.1.1", "any_buffer")

    verify(pypiproxy.services._hosted_packages_index).add_package("spam", "0.1.1", "any_buffer")


@test
@after(unstub)
def ensure_that_get_package_statistics_delegates_to_hosted_packages_index():
    pypiproxy.services._hosted_packages_index = mock()
    when(pypiproxy.services._hosted_packages_index).count_packages().thenReturn(0)

    actual = pypiproxy.services.get_package_statistics()

    assert_that(actual).is_equal_to((0, 0))

    verify(pypiproxy.services._hosted_packages_index).list_available_package_names()
    verify(pypiproxy.services._hosted_packages_index).count_packages()
