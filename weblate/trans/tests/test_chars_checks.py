# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2013 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <http://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Tests for quality checks.
"""

from weblate.trans.checks.chars import (
    BeginNewlineCheck, EndNewlineCheck,
    BeginSpaceCheck, EndSpaceCheck,
    EndStopCheck, EndColonCheck,
    EndQuestionCheck, EndExclamationCheck,
    EndEllipsisCheck,
    NewlineCountingCheck,
    ZeroWidthSpaceCheck,
)
from weblate.trans.tests.test_checks import CheckTestCase


class BeginNewlineCheckTest(CheckTestCase):
    def setUp(self):
        super(BeginNewlineCheckTest, self).setUp()
        self.check = BeginNewlineCheck()
        self.test_good_matching = ('\nstring', '\nstring', '')
        self.test_failure_1 = ('\nstring', ' \nstring', '')
        self.test_failure_2 = ('string', '\nstring', '')


class EndNewlineCheckTest(CheckTestCase):
    def setUp(self):
        super(EndNewlineCheckTest, self).setUp()
        self.check = EndNewlineCheck()
        self.test_good_matching = ('string\n', 'string\n', '')
        self.test_failure_1 = ('string\n', 'string', '')
        self.test_failure_2 = ('string', 'string\n', '')


class BeginSpaceCheckTest(CheckTestCase):
    def setUp(self):
        super(BeginSpaceCheckTest, self).setUp()
        self.check = BeginSpaceCheck()
        self.test_good_matching = ('   string', '   string', '')
        self.test_failure_1 = ('  string', '    string', '')
        self.test_failure_2 = ('    string', '  string', '')


class EndSpaceCheckTest(CheckTestCase):
    def setUp(self):
        super(EndSpaceCheckTest, self).setUp()
        self.check = EndSpaceCheck()
        self.test_good_matching = ('string  ', 'string  ', '')
        self.test_failure_1 = ('string  ', 'string', '')
        self.test_failure_2 = ('string', 'string ', '')


class EndStopCheckTest(CheckTestCase):
    def setUp(self):
        super(EndStopCheckTest, self).setUp()
        self.check = EndStopCheck()
        self.test_good_matching = ('string.', 'string.', '')
        self.test_failure_1 = ('string.', 'string', '')
        self.test_failure_2 = ('string', 'string.', '')


class EndColonCheckTest(CheckTestCase):
    def setUp(self):
        super(EndColonCheckTest, self).setUp()
        self.check = EndColonCheck()
        self.test_good_matching = ('string:', 'string:', '')
        self.test_failure_1 = ('string:', 'string', '')
        self.test_failure_2 = ('string', 'string:', '')


class EndQuestionCheckTest(CheckTestCase):
    def setUp(self):
        super(EndQuestionCheckTest, self).setUp()
        self.check = EndQuestionCheck()
        self.test_good_matching = ('string?', 'string?', '')
        self.test_failure_1 = ('string?', 'string', '')
        self.test_failure_2 = ('string', 'string?', '')


class EndExclamationCheckTest(CheckTestCase):
    def setUp(self):
        super(EndExclamationCheckTest, self).setUp()
        self.check = EndExclamationCheck()
        self.test_good_matching = ('string!', 'string!', '')
        self.test_failure_1 = ('string!', 'string', '')
        self.test_failure_2 = ('string', 'string!', '')


class EndEllipsisCheckTest(CheckTestCase):
    def setUp(self):
        super(EndEllipsisCheckTest, self).setUp()
        self.check = EndEllipsisCheck()
        self.test_good_matching = (u'string…', u'string…', '')
        self.test_failure_1 = (u'string…', 'string...', '')
        self.test_failure_2 = ('string...', u'string…', '')


class NewlineCountingCheckTest(CheckTestCase):
    def setUp(self):
        super(NewlineCountingCheckTest, self).setUp()
        self.check = NewlineCountingCheck()
        self.test_good_matching = ('string\\nstring', 'string\\nstring', '')
        self.test_failure_1 = ('string\\nstring', 'string\\n\\nstring', '')
        self.test_failure_2 = ('string\\n\\nstring', 'string\\nstring', '')


class ZeroWidthSpaceCheckTest(CheckTestCase):
    def setUp(self):
        super(ZeroWidthSpaceCheckTest, self).setUp()
        self.check = ZeroWidthSpaceCheck()
        self.test_good_matching = (u'str\u200bing', u'str\u200bing', '')
        self.test_failure_1 = (u'str\u200bing', 'string', '')
        self.test_failure_2 = ('string', u'str\u200bing', '')