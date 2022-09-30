from six import reraise as raise_
import sys


class VersionException(Exception):
    pass


class VersionParsingError(VersionException):
    pass


class Version(object):
    def __init__(self, version):
        self._raw = version
        try:
            self.value = tuple(
                map(lambda x: int(x), version.split('.'))
            )
        except Exception:
            tb = sys.exc_info()[2]
            raise_(VersionParsingError, 'failed to parse version: "%s"' % self._raw, tb)

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return any(
            [v[0] > v[1] for v in zip(self.value, other.value)]
        )

    def __ge__(self, other):
        return all(
            [v[0] >= v[1] for v in zip(self.value, other.value)]
        )

    def __lt__(self, other):
        return any(
            [v[0] < v[1] for v in zip(self.value, other.value)]
        )

    def __le__(self, other):
        return all(
            [v[0] <= v[1] for v in zip(self.value, other.value)]
        )

