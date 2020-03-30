# Copyright 2019-2020 maybeRainH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os
import re

from doujin_tagger.common import find_inner_most, match_path


def test_match_path(dir):
    rjpat = re.compile(r"(RJ\d+)", flags=re.IGNORECASE)
    rj23_path = os.path.join(dir.path, 'music', 'RJ23232')
    rj45_path = os.path.join(dir.path, 'music', 'sub', 'RJ45454')
    rj67_path = os.path.join(dir.path, 'music', 'RJ67676')
    res = [('RJ23232', rj23_path), ('RJ45454',
                                    rj45_path), ('RJ67676', rj67_path)]
    for i in res:
        assert i in list(match_path(dir.path, rjpat))


def test_find_inner_most(dir):
    rj23_path = os.path.join(dir.path, 'music', 'RJ23232')
    rj45_path = os.path.join(dir.path, 'music', 'sub', 'RJ45454')
    rj10_path = os.path.join(dir.path, 'music', 'RJ67676')
    assert rj23_path == str(find_inner_most(rj23_path))
    assert os.path.join(rj45_path, 'title') == str(find_inner_most(rj45_path))
    assert rj10_path == str(find_inner_most(rj10_path))
