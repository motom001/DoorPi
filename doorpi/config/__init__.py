"""The configuration module handles all things application config.

DoorPi's configuration file uses the `TOML format`__.  For the most
part, it looks very similar to MS-DOS style ``.ini`` files, but it also
brings built-in support for more advanced data structures.

__ https://toml.io/en/

The ``Configuration`` object acts as a gateway between ``DoorPi`` and
the on-disk configuration file.  When a configuration value is
requested, the gateway object first tries to look the value up in the
user configuration file.  If the requested value is not found there,
it will instead be read from the shipped "defaults" file.  If the value
is not defined there either, an exception will be raised.  This decision
is intended to help with debugging new modules, to ensure that every
configuration key has an explicit default value set for it.

Configuration defaults
======================

The configuration "defaults" files live inside this module below the
``defaults`` directory.  When the configuration is first loaded, all
defaults files will be read into a dictionary.  Defaults files are
loaded in alphabetical order.  While the mechanism does allow for later
files to override the defaults from an earlier file, this feature is not
recommended to be used in practice.  Each module should define exactly
the keys it uses, and -- to avoid name clashes -- should define its keys
below a namespace named after the module itself.  This also allows to
more easily associate keys and the module that uses them.

Flat namespaces that only consist of a single level of nesting look in
the configuration file just like plain old ``.ini`` file sections.  Each
namespace can be associated with a description, but namespaces cannot
have default values on their own.

Each configuration key is associated with a table in the defaults file.
This allows to easily define auxiliary information along with the actual
value, as well as being a future-proof and easily extensible format.

Entries in the definition table that describe the key or namespace
instead of opening a subkey are prefixed with an underscore to make them
unambiguous.  Whether a table in the defaults file describes a namespace
or a key is determined by the presence of a ``_default`` or ``_type``
key in the table.

The following keys are always defined in the config key table:

*   ``_type``: The value type.  See below for more details.
*   ``_default``: The default value for the key.  Used for inferring the
    ``_type`` if not explicitly given.
*   ``_description``: A human-readable description for this key.

Some types define additional keys.  See below for an explanation of
those.  Keys in the defaults table that are not used are ignored.

Value types
===========

Configuration values are strongly typed.  If not explicitly given by the
``type`` table key, the type is inferred from the default value.  The
following types can be automatically inferred:

*   ``int``: Integer numbers.  This type is used when a number without a
    floating point is the default value.  It accepts any integer number
    that Python can handle.

    ``int`` types accept the following additional keys in their defaults
    table:

    *   ``_min``, ``_max``: The minimum and maximum allowed value.  If the
        provided value lies outside of this range, an exception will be
        raised during startup.
*   ``float``: Floating point numbers.  This type is used when a number
    is used that does contain a floating point (e.g. ``1.0``, ``2.5``).

    Values of type ``int`` will be automatically upcast into ``float``.

    ``float`` types accept the same additional keys as ``int`` types.
*   ``bool``: A boolean value (true/false).  Note that you must not
    enclose the default value with quotes, or it will be recognized as
    string instead.

    The integer values 0 and 1 are automatically converted to False and
    True respectively.  The string values "on/off", "yes/no" and
    "true/false" will each be automatically converted to True/False.
*   ``string``: An arbitrary string of characters.  This type is used if
    the default value is a string constant.

    This type will automatically cast from int, float and bool using the
    built-in ``str`` function.  Date, Time and DateTime objects will be
    automatically formatted according to RFC3339.

    This type does not do any input validation.  See below for more
    specific types that do.
*   ``date``: A date (without a time).  This is represented as instance
    of :class:`datetime.date`.  Note that you must not enclose the
    default value in quotes, or it will be recognized as string instead.
*   ``time``: A time (without a date).  This is represented as instance
    of :class:`datetime.time`.  Note that you must not enclose the
    default value in quotes, or it will be recognized as string instead.
*   ``datetime``: A date and time.  This is represented as instance of
    :class:`datetime.datetime`.  If a timezone was given in the
    configuration, the corresponding :module:`pytz` timezone will be
    added to the ``datetime`` object.  Note that you must not enclose
    the default value in quotes, or it will be recognized as string
    instead.
*   ``list``: A list of values.  Accepts the following additional key in
    the defaults table:

    *   ``_membertype``: If given, the type that each list member has.
        If the member type defines additional defaults table keys, they
        will be honored as well.  This cannot be set to ``list``.  The
        member type cannot be inferred from the default value.

The following types cannot be inferred and must be explicitly given:

*   ``enum``: An enumeration value.

    The possible values can be defined in one of two ways.  The first
    way is to define them in the defaults table itself with the
    ``_values`` key.  The configuration system will create an
    :class:`enum.Enum` with the same name as the configuration key in
    the module named by the first component of the namespace path (e.g.
    if the key is defined as ``mymod.submod.key``, the Enum will be
    created in the module ``mymod``).  The Enum keys are the possible
    values given in the defaults file, and the Enum values are numbers
    starting with 1.  This method keeps the possible values next to the
    default value and is thus preferred.

    The second way is to define an :class:`enum.Enum` at the mentioned
    place yourself.  The config module will import that Enum and use it
    instead of creating its own.  This allows to associate more data
    with each configuration value, but also splits the information into
    two different places.
*   ``path``: A filesystem path.

    Paths are always returned as :class:`pathlib.Path` instances.  If a
    path is given that is not valid on the platform DoorPi is running
    on, an exception will be raised during loading.  This will make the
    administrator aware of the configuration problem early, so that he
    can provide a correct path in the user configuration.

    ``path`` types accept the following additional keys in their
    defaults table:

    *   ``_create``: Either ``true``, ``false`` or the string
        ``"parent"`` (note the absence of quotes on the former two).  If
        ``true``, a directory will be created at the given path during
        startup.  Leading path components are automatically created as
        needed.  If ``"parent"``, all path components except for the
        last one will be created as directories as needed.  If directory
        creation fails for any path component, startup will be aborted
        with an exception.
    *   ``_delete``: If ``_create`` is not ``false`` and this is
        ``true``, the path configured here will be automatically deleted
        during application shutdown.  Parent directories that are left
        empty are automatically cleaned up as well.  If the configured
        path points to a directory, it will be removed recursively.
"""

from .configuration import Configuration
