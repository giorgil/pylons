"""Configuration setup for Myghty, and Paste error middleware

This module supplies pylons_config which handles setting up defaults
for Myghty, Paste errorware, and prefixing Routes if necessary.
"""
import os
from myghty.resolver import *
from paste.deploy.converters import asbool

class Config(object):
    """Pylons configuration object
    
    The Pylons configuration object is a per-application instance object
    that retains the information regarding the global and app conf's as
    well as per-application instance specific data such as the mapper, the
    paths for this instance, and the myghty configuration.
    
    The Config object is available in your application as a Pylons global
    ``pylons_config`` under the ``g`` object. There's several useful
    attributes of the config object most people will be interested in:
    
    ``myghty``
        The myghty configuration dict that was used to initialize Myghty
    ``map``
        Mapper object used for Routing. Yes, it is possible to add routes
        after your application has started running.
    ``paths``
        An array of absolute paths that were defined in the applications
        ``config/environment.py`` module.
    ``global_conf``
        Global configuration passed in from Paste, this corresponds to the
        DEFAULTS section in the config file.
    ``app_conf``
        Application specific configuration directives, passed in via Paste
        from the app section of the config file.
    ``environ_config``
        Dict of environ keys for where in the environ to pickup various
        objects for registering with Pylons. If these are present then
        PylonsApp will use them from environ rather than using default
        middleware from Beaker. Valid keys are: ``session, cache``
    """
    def __init__(self, myghty, map, paths, environ_config={}):
        self.myghty = myghty
        self.map = map
        self.paths = paths
        self.global_conf = {}
        self.app_conf = {}
        self.templating = 'pylonsmyghty'
        self.template_options = None
        self.template_root = None
        self.environ_config = environ_config
    
    def init_app(self, global_conf, app_conf, package):
        """Initialize configuration for the application
        
        ``global_config``
            Several options are expected to be set for a Pylons web application.
            They will be loaded from the global_config which has the main Paste
            options. If ``debug`` is set to ``false`` as a global config option,
            the following option *must* be set:
            
            * error_to - The email address to send the debug error to
            
            The optional config options in this case are:
            
            * smtp_server - The SMTP server to use, defaults to 'localhost'
            * error_log - A logfile to write the error to
            * error_subject_prefix - The prefix of the error email subject
            * from_address - Whom the error email should be from
        ``app_conf``
            Defaults supplied via the [app:main] section from the Paste
            config file. ``load_config`` only cares about whether a 'prefix'
            option is set, if so it will update Routes to ensure URL's take
            that into account.
        ``package``
            The name of the application package, to be stored in the app_conf.
        
        """
        self.global_conf = global_conf
        self.app_conf = app_conf
        self.package = package
        
        app_conf['package'] = package
        
        # Setup the prefix to override the routes if necessary.
        prefix = app_conf.get('prefix')
        if not prefix:
            prefix = global_conf.get('prefix')
        if prefix:
            self.map.prefix = app_conf['prefix']
            self.map._created_regs = False
                
        myghty_defaults = {}
        
        # Raise a complete error for the error middleware to catch
        myghty_defaults['raise_error'] = True
        
        # Standard Pylons configuration directives for Myghty
        myghty_defaults.setdefault('allow_globals', [])
                
        myghty_defaults['allow_globals'].extend(['c', 'h', 'session', 'request', 'params', 'g'])
        myghty_defaults['component_root'] = [{os.path.basename(path): path} for \
                                             path in self.paths['templates']]
        
        errorware = {}
        # Load the errorware configuration from the Paste configuration file
        # These all have defaults, and emails are only sent if configured and
        # if this application is running in production mode
        errorware['debug'] = asbool(global_conf.get('debug', 'true'))
        if not errorware['debug']:
            errorware['debug'] = False
            errorware['error_email'] = global_conf.get('email_to')
            errorware['error_log'] = global_conf.get('error_log', None)
            errorware['smtp_server'] = global_conf.get('smtp_server', 'localhost')
            errorware['error_subject_prefix'] = global_conf.get('error_subject_prefix', 'WebApp Error: ')
            errorware['from_address'] = global_conf.get('from_address', 
                                            global_conf.get('error_email_from', 'pylons@yourapp.com'))
            errorware['error_message'] = global_conf.get('error_message', 'An internal server error occurred')
        
        # Merge in the user-supplied Myghty values
        myghty_defaults.update(self.myghty)
        self.myghty = myghty_defaults
        self.template_options = {}
        for k, v in self.myghty.iteritems():
            self.template_options['myghty.'+k] = v
        
        # Save our errorware values
        self.errorware = errorware
