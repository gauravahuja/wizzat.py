from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
from future.utils import iteritems, itervalues

import collections
import contextlib
import errno
import functools
import inspect
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
import types

__all__ = [
    'Host',
    'OfflineError',
    'UnsafeTarError',
    'assert_online',
    'carp',
    'chdir',
    'chunks',
    'extract_tarfile',
    'filter_keys',
    'first_existing_path',
    'funcs',
    'get_open_port',
    'import_class',
    'invert_dict',
    'is_online',
    'json_copy',
    'json_path',
    'listdirs',
    'load_paths',
    'merge_dicts',
    'mkdirp',
    'parse_host',
    'parse_hosts',
    'reset_online',
    'set_defaults',
    'set_online',
    'set_strict_defaults',
    'slurp',
    'swallow',
    'tmpdir',
    'touch',
    'umask',
    'unique',
    'update_env',
]

@contextlib.contextmanager
def update_env(**kwargs):
    """
        Temporarily update os.environ for the duration of the context.

        Modified from from https://github.com/bennoleslie/pyutil
    """
    purge_values = [ k for k in kwargs if k not in os.environ.keys() ]
    orig_values = { k : os.environ[k] for k in kwargs if k in os.environ }
    os.environ.update(kwargs)

    yield

    os.environ.update(orig_values)
    for k in purge_values:
        os.environ.pop(k)

@contextlib.contextmanager
def tmpdir(*args, **kwargs):
    """
        Call tempfile.mkdtemp and remove the temp dir after the context.

        Modified from from https://github.com/bennoleslie/pyutil
    """
    tmpdir = tempfile.mkdtemp(*args, **kwargs)
    yield tmpdir
    shutil.rmtree(tmpdir)

@contextlib.contextmanager
def umask(new_mask):
    """
        umask context manager.

        Makes `new_mask` the current mask, and restores the previous umask
        after the context closes.

        Modified from from https://github.com/bennoleslie/pyutil
    """

    prev_mask = os.umask(new_mask)
    yield
    os.umask(prev_mask)

@contextlib.contextmanager
def chdir(new_path):
    """
        Current-working directory context manager.

        Makes the current working directory the specified `path` for the
        duration of the context.

        Example:

        with chdir("newdir"):
            # Do stuff in the new directory
            pass

        Modified from from https://github.com/bennoleslie/pyutil
    """

    cwd = os.getcwd()
    os.chdir(os.path.expanduser(new_path))
    yield
    os.chdir(cwd)

def invert_dict(d, many = False):
    """
        Returns the inversion of keys and values in dictionary d. The default case
        allows overriding of values pointed to by multiple keys.  Passing many=True
        will make each value a key for the list of values pointing to it.

        Examples:
        invert_dict({ 1 : 2, 3 : 4 })
        { 2 : 1, 4 : 3 }

        invert_dict({ 1 : 2, 2 : 2, 3 : 2 })
        { 2 : 3 }

        invert_dict({ 1 : 2, 2 : 2, 3 : 2 }, many=True)
        { 2 : [ 1, 2, 3 ] }
    """
    if not many:
        return { v : k for k, v in iteritems(d) }

    output = collections.defaultdict(list)

    for k, v in iteritems(d):
        output[v].append(k)

    return dict(output)

def touch(path):
    """
        Ensures that a specified file (and directory path) exists.

        Analogous to mkdir -p && touch
    """
    mkdirp(os.path.dirname(path))
    with open(path, 'a') as fp:
        pass

def listdirs(paths, regex = None):
    for path in paths:
        for filename in os.listdir(os.path.expanduser(path)):
            if not regex or re.match(regex, filename):
                yield os.path.join(path, filename)

def mkdirp(path):
    """
        Ensure that directory path exists.
        Analogous to mkdir -p

        See http://stackoverflow.com/questions/10539823/python-os-makedirs-to-recreate-path
    """
    try:
        os.makedirs(os.path.expanduser(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def first_existing_path(*paths):
    """
        Finds and returns the first existing file path.
        Calls os.path.expanduser on each path.
    """
    for path in paths:
        if path:
            path = os.path.expanduser(path)
            if os.path.exists(path):
                return path
    return None

def load_paths(func, *paths):
    if not func:
        func = lambda x: x

    path = first_existing_path(*paths)
    if not path:
        raise ValueError()

    with open(path, 'r') as fp:
        return func(fp.read())

def json_path(obj, *args):
    if not obj:
        return None

    try:
        for arg in args:
            obj = obj[arg]
        return obj
    except (KeyError, IndexError) as e:
        return None

def merge_dicts(*iterable):
    """
        Merge a list of dictionaries.
        Successive keys are updated.

        See http://dietbuddha.blogspot.com/2013/04/python-expression-idiom-merging.html
    """
    return functools.reduce(lambda a, b: a.update(b) or a, iterable, {})

def swallow(err_type, func, *args, **kwargs):
    """
        Swallow an exception.

        swallow(KeyError, lambda: dictionary[x])

        vs

        try:
            dictionary[x]
        except KeyError:
            pass
    """
    try:
        return func(*args, **kwargs)
    except err_type:
        pass

def carp(msg, file_obj = None):
    """
        Python's equivalent of Perl's carp

        http://stackoverflow.com/questions/8275745/warnings-from-callers-perspective-aka-python-equivalent-of-perls-carp
    """

    # grab the current call stack, and remove the stuff we don't want
    file_obj = file_obj or sys.stderr

    stack = inspect.stack()
    stack = stack[1:]

    caller_func = stack[0][1]
    caller_line = stack[0][2]
    file_obj.write('%s at %s line %d\n' % (msg, caller_func, caller_line))

    for idx, frame in enumerate(stack[1:]):
        # The frame, one up from `frame`
        upframe = stack[idx]
        upframe_record = upframe[0]
        upframe_func   = upframe[3]
        upframe_module = inspect.getmodule(upframe_record).__name__

        # The stuff we need from the current frame
        frame_file = frame[1]
        frame_line = frame[2]

        file_obj.write('\t%s.%s ' % (upframe_module, upframe_func))
        file_obj.write('called at %s line %d\n' % (frame_file, frame_line))

def import_class(name):
    """
        Import a class a string and return a reference to it.
        THIS IS A GIANT SECURITY VULNERABILITY.

        See: http://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
    """
    if not isinstance(name, str):
        return name

    package    = ".".join(name.split(".")[: - 1])
    class_name = name.split(".")[  - 1]

    mod = __import__(package, fromlist=[class_name])
    return getattr(mod, class_name)

def chunks(iterable, chunk_size):
    """
        Iterate across iterable in chunks of chunk_size

        Example:
        for chunk in chunks(some_long_iterable, 500):
            for element in chunk:
                element.perform_operation()
    """
    for chunk_no in range(0, len(iterable), chunk_size):
        yield iterable[chunk_no:chunk_no+chunk_size]

def set_defaults(kwargs, defaults = {}, **default_values):
    """
    Returns kwargs with defaults set.
    Has two forms:
    kwargs = set_defaults(kwargs, { 'value1' : 'value1', 'value2' : 'value2' })
    kwargs = set_defaults(kwargs,
        value1 = 'value1',
        value2 = 'value2',
    )
    """
    if defaults:
        default_values = dict(defaults)

    default_values.update(kwargs)
    return default_values

def set_strict_defaults(kwargs, defaults = {}, **default_values):
    """
    Returns kwargs with defaults set. Throws a TypeError if parameters exist
    in kwargs that do not have default values.
    Has two forms:
    kwargs = set_defaults(kwargs, { 'value1' : 'value1', 'value2' : 'value2' })
    kwargs = set_defaults(kwargs,
        value1 = 'value1',
        value2 = 'value2',
    )
    """
    if defaults:
        default_values = dict(defaults)

    for k, v in iteritems(kwargs):
        if k not in default_values:
            raise TypeError("Unexpected paramter: " + k)
        default_values[k] = v

    return default_values

def slurp(filename, must_exist=True):
    """
        Find the named file, read it into memory, and return it as a string.
    """
    if not must_exist and not os.path.exists(filename):
        return ''

    with open(filename, 'r') as fp:
        return fp.read()

def funcs(obj):
    """
        Returns the functions on object (or, callables)
    """
    return filter(callable, itervalues(obj.__dict__))

def filter_keys(keys, dictionary, error = True):
    """
        Returns a dictionary filtered to the specific keys.  If error is True, the keys must be present.

    """
    if error:
        return { k : dictionary[k] for k in keys }
    else:
        return { k : dictionary[k] for k in keys if k in dictionary }

def json_copy(obj):
    if isinstance(obj, dict):
        return { k : (json_copy(v) if isinstance(v, (dict, list, tuple)) else v) for k, v in iteritems(obj) }
    elif isinstance(obj, (list, tuple)):
        return [ (json_copy(v) if isinstance(v, (dict, list, tuple)) else v) for v in obj ]
    else:
        return obj

def unique(iterable):
    """
        Returns the unique items while preserving order.
    """
    d = collections.OrderedDict()
    for x in iterable:
        d[x] = 1
    return list(d.keys())

Host = collections.namedtuple('Host', 'host port')
Host.combined = lambda self: '{}:{}'.format(self.host, self.port)

def parse_host(host_string, default_port = ''):
    try:
        return Host(*(x.strip() for x in host_string.split(':')))
    except (TypeError, ValueError) as e:
        return Host(host_string, str(default_port))

def parse_hosts(host_list, default_port):
    return [ parse_host(x) for x in host_list.split(',') ]

def get_open_port():
    """
        Gets an open port on the system
    """
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()

    return port

def download_file(url, dest_path = None, dest_dir = None, skip_if_exists = True):
    if not dest_path and not dest_dir:
        raise TypeError('Either dest_path or dest_dir must be passed in')

    if not dest_path:
        dest_path = os.path.join(dest_dir, os.path.basename(url))

    if not os.path.exists(dest_path) or not skip_if_exists:
        response = urllib.request.urlopen(url)
        with open(dest_path, 'wb') as fp:
            fp.write(response.read())

    return dest_path

class UnsafeTarError(Exception): pass

def extract_tarfile(filename, dest_dir, validate = True, gz = None):
    """
    Sanity checks the tar file to ensure there are no paths which escape.
    In particular, looks for relative and absolute paths.

    Params:
    validate checks for unsafe tar files (member paths beginning with .. or /)
    gz allows overriding the automatic detection of .tar.gz files

    Returns the path to the extracted tar file (including the root paths)
    """
    if gz == False or not filename.endswith('.gz'):
        mode = 'r'
    else:
        mode = 'r:gz'

    mkdirp(dest_dir)
    with tarfile.open(filename, mode) as fp:
        # We make the bold assertion that the first file is the "root directory".
        # This should hold if it is a substring of all member paths.
        extract_dir = fp.getmembers()[0].name

        for member in fp.getmembers():
            if extract_dir and not member.name.startswith(extract_dir):
                extract_dir = ''

            if validate and member.name.startswith('/') or member.name.startswith('..'):
                raise UnsafeTarError(member)

        if len(fp.getmembers()) == 1:
            extract_dir = ''

        fp.extractall(dest_dir)

    return os.path.join(dest_dir, extract_dir)

class OfflineError(Exception): pass

def assert_online():
    """
        This method tests the OFFLINE environment variable and throws OfflineError().  This directly
        hooks into @skip_offline, but can be used in other situations as well.
    """
    if not is_online():
        raise OfflineError()

# Initial value for _offline set from environment
_offline = None
def is_online():
    """
        This method tests the OFFLINE environment variable and the global offline state.
    """
    global _offline
    return _offline

def set_online(value):
    """
        Sets the global offline state
    """
    global _offline
    _offline = value

def reset_online():
    """
        Resets the global offline state
    """
    global _offline
    _offline = os.environ.get('OFFLINE', False) == False
reset_online()
