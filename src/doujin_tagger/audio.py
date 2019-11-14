from collections.abc import MutableMapping


class DictMixin(MutableMapping):
    """Dict Mixin for Convenient audio's info process with mutagen"""

    def __init__(self, *args, **kwargs):
        self._data = {}
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        dict_ = args[0] if args else None
        if dict_ is not None:
            self.update(dict_)
        for k, v in kwargs.items():
            self.add(k, v)  # 如果key在dict_里存在，这里是add进去而不是覆盖

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            return ""

    def get(self, key, default=None):
        # pass __getitem__
        try:
            return self._data[key]
        except KeyError:
            return default

    def __contains__(self, key):
        # pass __getitem__
        return key in self._data

    def __setitem__(self, key, value):
        self._data[key] = self._list2str(value)

    def __len__(self):
        return len(self._data)

    def _list2str(self, value):
        if not isinstance(value, str) and hasattr(value, "__iter__"):
            it = (str(each) for each in value)
            return '\n'.join(it)
        else:
            return str(value)

    def add(self, key, value):
        if key not in self:
            self[key] = self._list2str(value)
        else:
            self[key] = self._data[key] + "\n" + self._list2str(value)

    def __iter__(self):
        return iter(self._data)

    def __delitem__(self, key):
        del self._data[key]

    def tolist(self, key):
        """return value in list"""
        val = self._data.get(key)
        return val.strip().split("\n") if val else []

    def remove(self, key, value=None):
        # multi-value is stored by str separated by \n. e.g. '1\n2'
        # but you can both remove(key,'1\n2') or remove(key,['1','2'])
        # yet not remove(key,[1,2])
        if key not in self:
            pass
        elif value is None or self[key] == value or self.tolist(key) == value:
            del self[key]
        else:
            try:
                parts = self.tolist(key)
                parts.remove(value)
                self._data[key] = "\n".join(parts)
            except ValueError:
                pass

    def __repr__(self):
        return repr(self._data)

    def list_repr(self):
        """repr variant where value is a list"""
        return {k: self.tolist(k) for k in self}


class AudioFile(DictMixin):
    _registry = {}
    exclude = ("filename", "image_url", "cover")
    @classmethod
    def __init_subclass__(cls, ext=None, **kwargs):
        super().__init_subclass__(**kwargs)
        # subclass have sub-subclass, so don"t need to register
        if ext is None:
            return

        if isinstance(ext, str):
            cls._registry[ext] = cls
        elif hasattr(ext, "__iter__"):
            for each in ext:
                cls._registry[each] = cls

    def __new__(cls, filename):
        if cls is not AudioFile:
            return super().__new__(cls)

        for fmt, class_ in cls._registry.items():
            if fmt in filename:
                Klass = class_
                break

        return Klass(filename)

    def realkeys(self):
        return (k for k in self if k not in self.exclude)

    def feed(self, info):
        self.update(info)

    def save(self):
        raise NotImplementedError

    def set_image(self, image):
        """Replaces all embedded images by the passed image

        do not save the change immediately. use .save() instead"""
        raise NotImplementedError

    def delete_all_tags(self):
        raise NotImplementedError


class AudioFileError(Exception):
    """Base error for AudioFile, mostly IO/parsing related operations"""


class MutagenBug(AudioFileError):
    """Raised in is caused by a mutagen bug, so we can highlight it"""
