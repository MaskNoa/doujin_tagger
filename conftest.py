import pytest
from testfixtures import TempDirectory

# dir:
# music/
#     RJ23232/
#         test.mp3
#     sub/
#         RJ45454/
#             title/
#                 test2.mp3
#     RJ67676/
#         title/
#             test3.mp3
#         another/
#             test4.mp4


@pytest.fixture(scope='module')
def dir():
    with TempDirectory() as dir:
        dir.write('music/RJ23232/test.mp3', b'this is test.mp3 file')
        dir.write('music/sub/RJ45454/title/test2.mp3', b'this is test2.mp3')
        dir.write('music/RJ67676/title/test3.mp3', b'this is test3.mp3')
        dir.write('music/RJ67676/another/test4.mp3', b'this is test4.mp3')
        yield dir
