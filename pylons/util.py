"""Paste Template and Pylons utility functions

PylonsTemplate is a Paste Template sub-class that configures the source
directory and default plug-ins for a new Pylons project. The minimal template
provides a more minimal template with less additional directories and layout.
"""
import warnings

from paste.script.appinstall import Installer
from paste.script.templates import Template

import pylons
import pylons.helpers
import pylons.i18n

def func_move(name, moved_to='pylons.i18n'):
    return ("The %s function has moved to %s, please update your import "
            "statements to reflect the move." % (name, moved_to))

def deprecated(func, message):
    def deprecated_method(*args, **kargs):        
        warnings.warn(message, DeprecationWarning, 2)
        return func(*args, **kargs)
    try:
        deprecated_method.__name__ = func.__name__
    except TypeError: # Python < 2.4
        pass
    deprecated_method.__doc__ = message + "\n\n" + func.__doc__
    return deprecated_method

get_lang = deprecated(pylons.i18n.get_lang, func_move('get_lang'))
set_lang = deprecated(pylons.i18n.set_lang, func_move('set_lang'))
_ = deprecated(pylons.i18n._, func_move('_'))
log = deprecated(pylons.helpers.log, func_move('log',
                                               moved_to='pylons.helpers'))
    
def get_prefix(environ):
    if 'paste.config' in environ:
        prefix = environ['paste.config']['app_conf'].get('prefix', '')
    else:
        # Not ideal but if the error occurs before the paste.config is
        # available not a lot we can do
        prefix = ''
    if not prefix:
        if environ.get('SCRIPT_NAME', '') != '':
            prefix = environ['SCRIPT_NAME']
    return prefix

def class_name_from_module_name(module_name):
    """Takes a module name and returns the name of the class it defines.

    If the module name contains dashes, they are replaced with underscores.
    
    Example::
    
        >>> class_name_from_module_name('with-dashes')
        'WithDashes'
        >>> class_name_from_module_name('with_underscores')
        'WithUnderscores'
        >>> class_name_from_module_name('oneword')
        'Oneword'
    """
    words = module_name.replace('-', '_').split('_')
    return ''.join([w.title() for w in words])


def config_get(key, default=None):
    """Return a value from ``CONFIG``. Supports both ``paste.config.CONFIG``
    and the older ``paste.deploy.CONFIG``.

    This is for Pylons internal use only; to support both versions of the
    ``CONFIG`` objects, depending on which is used by the current Pylons
    web app."""
    try:
        # environ['paste.config'] is assured to be the correct CONFIG
        # during requests
        CONFIG = pylons.request.environ['paste.config']
        value = CONFIG['app_conf'].get(key, default)
    except TypeError:
        # TypeError: pylons.request isn't registered (this function call was
        # made outside of a web request). fall back to paste.config.CONFIG
        # directly, and finally paste.deploy.CONFIG
        try:
            from paste.config import CONFIG
            value = CONFIG['app_conf'].get(key, default)
        except AttributeError:
            from paste.deploy import CONFIG
            value = CONFIG['app_conf'].get(key, default)
    return value


class ContextObj(object):
    """ The 'c' object, with strict attribute access (raises an Exception when
    the attribute does not exist) """
    def __repr__(self):
        attrs = [(name, value)
                 for name, value in self.__dict__.items()
                 if not name.startswith('_')]
        attrs.sort()
        parts = []
        for name, value in attrs:
            value_repr = repr(value)
            if len(value_repr) > 70:
                value_repr = value_repr[:60] + '...' + value_repr[-5:]
            parts.append(' %s=%s' % (name, value_repr))
        return '<%s.%s at %s%s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self)),
            ','.join(parts))

class AttribSafeContextObj(ContextObj):
    """ The 'c' object, with lax attribute access (returns '' when the
    attribute does not exist) """
    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return ''

class PylonsTemplate(Template):
    _template_dir = 'templates/default_project'
    summary = 'Pylons application template'
    egg_plugins = ['Pylons', 'WebHelpers']

class MinimalPylonsTemplate(Template):
    _template_dir = 'templates/minimal_project'
    summary = 'Pylons minimal application template'
    egg_plugins = ['Pylons', 'WebHelpers']

class PylonsInstaller(Installer):
    use_cheetah = False

__all__ = ['AttribSafeContextObj', 'ContextObj', 'Helpers',
           'class_name_from_module_name', 'log', '_', 'set_lang', 'get_lang']
__pudge_all__ = __all__ + ['MinimalPylonsTemplate', 'PylonsTemplate']
