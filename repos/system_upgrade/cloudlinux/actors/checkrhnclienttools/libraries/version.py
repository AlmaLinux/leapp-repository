from future.utils import raise_from


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
        except Exception as e:
            raise_from(VersionParsingError('failed to parse version: "%s"' % self._raw), e)

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

