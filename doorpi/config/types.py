"""Classes that handle different configuration value types"""
# pylint: disable=missing-function-docstring, too-few-public-methods
from __future__ import annotations

import abc
import collections.abc
import datetime
import enum
import importlib
import math
import pathlib
import re
from typing import Any, Dict, Mapping, Sequence, Tuple, Type


def gettype(typename: str) -> Type[ValueType]:
    return _types[typename]


def infertype(default: Any) -> Type[ValueType]:
    # pylint: disable=too-many-return-statements
    if isinstance(default, bool):
        return Bool
    elif isinstance(default, int):
        return Int
    elif isinstance(default, float):
        return Float
    elif isinstance(default, str):
        return String
    elif isinstance(default, datetime.datetime):
        return DateTime
    elif isinstance(default, datetime.date):
        return Date
    elif isinstance(default, datetime.time):
        return Time
    elif isinstance(default, collections.abc.Sequence):
        return List
    else:
        raise TypeError(f"Cannot infer from type {type(default).__name__}")


class ValueType(metaclass=abc.ABCMeta):
    """ABC for value types"""

    __slots__ = ()

    def __init__(self, name: Sequence[str], keydef: Mapping[str, Any]) -> None:
        del self, name, keydef

    @abc.abstractmethod
    def insertcast(self, value: Any) -> Any:
        """Cast ``value`` so it can be inserted into the configuration dict"""

    def querycast(self, value: Any) -> Any:
        """Cast ``value`` after retrieving it from the configuration dict"""
        del self
        return value


class Anything(ValueType):
    """Any value"""

    __slots__ = ()

    @staticmethod
    def insertcast(value: Any) -> Any:
        return value


class Int(ValueType):
    """An integer number (1, 2, -5, etc.)"""

    __slots__ = ("_Int__min", "_Int__max")

    def __init__(self, name: Sequence[str], keydef: Mapping[str, Any]) -> None:
        # pylint: disable=assigning-non-slot
        super().__init__(name, keydef)
        self.__min = keydef.get("_min", -math.inf)
        self.__max = keydef.get("_max", math.inf)

    def insertcast(self, value: Any) -> int:
        # pylint: disable=no-member
        if isinstance(value, int):
            if self.__min <= value <= self.__max:
                return value
            raise ValueError(f"Integer out of range: {value!r}")
        raise TypeError(f"Needed an integer, got {value!r}")


class Float(ValueType):
    """A floating point number (1.2, -7.9, etc.)"""

    __slots__ = ("_Float__min", "_Float__max")

    def __init__(self, name: Sequence[str], keydef: Mapping[str, Any]) -> None:
        # pylint: disable=assigning-non-slot
        super().__init__(name, keydef)
        self.__min = keydef.get("_min", -math.inf)
        self.__max = keydef.get("_max", math.inf)

    def insertcast(self, value: Any) -> float:
        # pylint: disable=no-member
        if isinstance(value, (int, float)):
            if self.__min <= value <= self.__max:
                return float(value)
            raise ValueError(f"Number out of range: {value!r}")
        raise TypeError(f"Needed a number, got {value!r}")


class Bool(ValueType):
    """A boolean value, i.e. true/false, on/off, 1/0 etc."""

    __true_values = {"true", "yes", "on", "1", 1}
    __false_values = {"false", "no", "off", "0", 0}
    __slots__ = ()

    @classmethod
    def insertcast(cls, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if hasattr(value, "lower"):
            value = value.lower()
        if isinstance(value, collections.abc.Hashable):
            if value in cls.__true_values:
                return True
            if value in cls.__false_values:
                return False
            raise ValueError(f"Not a boolean value: {value!r}")
        raise TypeError(f"Cannot cast {value!r} to boolean")


class String(ValueType):
    """A string of characters"""

    __slots__ = ()

    @staticmethod
    def insertcast(value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(
            value,
            (
                int,
                float,
                bool,
                datetime.date,
                datetime.datetime,
                datetime.time,
            ),
        ):
            return str(value)
        raise ValueError(f"Expected string, got {value!r}")


class Password(String):
    """A string of characters that should not be shown to the user"""


class Date(ValueType):
    """A date (without time)"""

    __slots__ = ()

    @staticmethod
    def insertcast(value: Any) -> datetime.date:
        if isinstance(value, datetime.datetime):
            return datetime.date(value.year, value.month, value.day)
        if isinstance(value, datetime.date):
            return value
        raise TypeError(f"Expected date, got {value!r}")


class Time(ValueType):
    """A time, with or without timezone"""

    __slots__ = ()

    @staticmethod
    def insertcast(value: Any) -> datetime.time:
        if isinstance(value, datetime.time):
            return value
        if isinstance(value, datetime.datetime):
            return datetime.time(
                value.hour,
                value.minute,
                value.second,
                value.microsecond,
                tzinfo=value.tzinfo,
            )
        raise TypeError(f"Expected time, got {value!r}")


class DateTime(ValueType):
    """A date and time, with or without timezone"""

    __slots__ = ()

    @staticmethod
    def insertcast(value: Any) -> datetime.datetime:
        if isinstance(value, datetime.datetime):
            return value
        raise TypeError(f"Expected date and time, got {value!r}")


class List(ValueType):
    """A list of values"""

    __slots__ = ("_List__membertype",)

    def __init__(self, name: Sequence[str], keydef: Mapping[str, Any]) -> None:
        # pylint: disable=assigning-non-slot
        super().__init__(name, keydef)
        membertype = keydef.get("_membertype", "any")
        if membertype == "list":  # pragma: no cover
            raise ValueError("Cannot define a list of lists")
        self.__membertype = gettype(membertype)(name, keydef)

    def insertcast(self, value: Any) -> Tuple[Any, ...]:
        # pylint: disable=no-member
        if not isinstance(value, collections.abc.Iterable) or isinstance(
            value, str
        ):
            value = (value,)
        return tuple(self.__membertype.insertcast(v) for v in value)

    def querycast(self, value: Sequence[Any]) -> Tuple[Any, ...]:
        # pylint: disable=no-member
        return tuple(self.__membertype.querycast(v) for v in value)


class Enum(ValueType):
    """One of a set of values"""

    __slots__ = ("_Enum__enum",)

    def __init__(self, name: Sequence[str], keydef: Mapping[str, Any]) -> None:
        # pylint: disable=assigning-non-slot, no-member
        assert len(name) >= 2, f"Key path too short: {name}"
        super().__init__(name, keydef)
        modulename = f"{__name__.split('.')[0]}.{name[0]}"
        module = importlib.import_module(modulename)
        enumname = re.sub(
            r"(^|_+)[a-z]", lambda match: match.group(0)[-1].upper(), name[-1]
        )
        try:
            self.__enum = getattr(module, enumname)
        except AttributeError:
            vals = keydef["_values"]
            self.__enum = enum.unique(
                enum.Enum(enumname, vals, module=modulename)
            )
            setattr(module, enumname, self.__enum)

    def insertcast(self, value: Any) -> enum.Enum:
        # pylint: disable=no-member
        if isinstance(value, self.__enum):
            return value

        try:
            return self.__enum[value]
        except KeyError:
            pass

        try:
            return self.__enum(value)
        except KeyError:
            pass

        raise ValueError(f"{value!r} is no member or value of {self.__enum}")


class Path(ValueType):
    """A path in the filesystem"""

    __slots__ = ()

    @staticmethod
    def insertcast(value: Any) -> pathlib.Path:
        if isinstance(value, pathlib.Path):
            return value
        if isinstance(value, str):
            return pathlib.Path(value)
        raise TypeError(f"Expected a path, got {value!r}")

    @staticmethod
    def querycast(value: pathlib.Path) -> pathlib.Path:
        return value.expanduser()


_types: Dict[str, Type[ValueType]] = {
    "any": Anything,
    "int": Int,
    "float": Float,
    "bool": Bool,
    "string": String,
    "password": Password,
    "date": Date,
    "time": Time,
    "datetime": DateTime,
    "list": List,
    "enum": Enum,
    "path": Path,
}
