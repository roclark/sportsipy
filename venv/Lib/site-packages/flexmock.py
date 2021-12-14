"""Copyright 2011-2015 Herman Sheremetyev, Slavek Kabrda. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


# from flexmock import * is evil, keep it from doing any damage
__all__ = ['flexmock']
__version__ = '0.10.4'


import inspect
import re
import sys
import types


AT_LEAST = 'at least'
AT_MOST = 'at most'
EXACTLY = 'exactly'
UPDATED_ATTRS = ['should_receive', 'should_call', 'new_instances']
DEFAULT_CLASS_ATTRIBUTES = [attr for attr in dir(type)
                            if attr not in dir(type('', (object,), {}))]
RE_TYPE = re.compile('')
SPECIAL_METHODS = (classmethod, staticmethod)


class FlexmockError(Exception):
    pass


class MockBuiltinError(Exception):
    pass


class MethodSignatureError(FlexmockError):
    pass


class ExceptionClassError(FlexmockError):
    pass


class ExceptionMessageError(FlexmockError):
    pass


class StateError(FlexmockError):
    pass


class MethodCallError(FlexmockError):
    pass


class CallOrderError(FlexmockError):
    pass


class ReturnValue(object):
    def __init__(self, value=None, raises=None):
        self.value = value
        self.raises = raises

    def __str__(self):
        if self.raises:
            return '%s(%s)' % (self.raises, _arg_to_str(self.value))
        else:
            if not isinstance(self.value, tuple):
                return '%s' % _arg_to_str(self.value)
            elif len(self.value) == 1:
                return '%s' % _arg_to_str(self.value[0])
            else:
                return '(%s)' % ', '.join([_arg_to_str(x) for x in self.value])


class FullArgSpec(object):
    """Silly hack for inpsect.getargspec return a tuple on python <2.6"""
    def __init__(self, spec):
        if len(spec) == 4:  # python2 => getargspec was used
            spec += ([], None, {})
        (self.args, self.varargs, self.keywords, self.defaults, self.kwonlyargs,
         self.kwonlydefaults, self.annotations) = spec


class FlexmockContainer(object):
    """Holds global hash of object/expectation mappings."""
    flexmock_objects = {}
    properties = {}
    ordered = []
    last = None

    @classmethod
    def reset(cls):
        cls.ordered = []
        cls.last = None
        cls.flexmock_objects = {}
        cls.properties = {}

    @classmethod
    def get_flexmock_expectation(cls, obj, name=None, args=None):
        """Retrieves an existing matching expectation."""
        if args is None:
            args = {'kargs': (), 'kwargs': {}}
        if not isinstance(args, dict):
            args = {'kargs': args, 'kwargs': {}}
        if not isinstance(args['kargs'], tuple):
            args['kargs'] = (args['kargs'],)
        if name and obj in cls.flexmock_objects:
            found = None
            for e in reversed(cls.flexmock_objects[obj]):
                if e.name == name and e.match_args(args):
                    if e in cls.ordered or not e._ordered and not found:
                        found = e
            if found and found._ordered:
                cls._verify_call_order(found, args)
            return found

    @classmethod
    def _verify_call_order(cls, expectation, args):
        if not cls.ordered:
            next_method = cls.last
        else:
            next_method = cls.ordered.pop(0)
            cls.last = next_method
        if expectation is not next_method:
            raise CallOrderError(
                '%s called before %s' %
                (_format_args(expectation.name, args),
                 _format_args(next_method.name, next_method.args)))

    @classmethod
    def add_expectation(cls, obj, expectation):
        if obj in cls.flexmock_objects:
            cls.flexmock_objects[obj].append(expectation)
        else:
            cls.flexmock_objects[obj] = [expectation]

    @classmethod
    def add_teardown_property(cls, obj, name):
        if obj in cls.properties:
            cls.properties[obj].append(name)
        else:
            cls.properties[obj] = [name]

    @classmethod
    def teardown_properties(cls):
        for obj, names in cls.properties.items():
            for name in names:
                delattr(obj, name)


class Expectation(object):
    """Holds expectations about methods.

    The information contained in the Expectation object includes method name,
    its argument list, return values, and any exceptions that the method might
    raise.
    """

    def __init__(self, mock, name=None, return_value=None, original=None):
        self.name = name
        self.modifier = EXACTLY
        if original is not None:
            self.original = original
        self.args = None
        self.method_type = types.MethodType
        self.argspec = None
        value = ReturnValue(return_value)
        self.return_values = return_values = []
        self._replace_with = None
        if return_value is not None:
            return_values.append(value)
        self.times_called = 0
        self.expected_calls = {
            EXACTLY: None,
            AT_LEAST: None,
            AT_MOST: None}
        self.runnable = lambda: True
        self._mock = mock
        self._pass_thru = False
        self._ordered = False
        self._one_by_one = False
        self._verified = False
        self._callable = True
        self._local_override = False

    def __str__(self):
        return '%s -> (%s)' % (_format_args(self.name, self.args),
                               ', '.join(['%s' % x for x in self.return_values]))

    def __call__(self):
        return self

    def __getattribute__(self, name):
        if name == 'once':
            return _getattr(self, 'times')(1)
        elif name == 'twice':
            return _getattr(self, 'times')(2)
        elif name == 'never':
            return _getattr(self, 'times')(0)
        elif name in ('at_least', 'at_most', 'ordered', 'one_by_one'):
            return _getattr(self, name)()
        elif name == 'mock':
            return _getattr(self, 'mock')()
        else:
            return _getattr(self, name)

    def __getattr__(self, name):
        self.__raise(
            AttributeError,
            "'%s' object has not attribute '%s'" % (self.__class__.__name__, name))

    def _get_runnable(self):
        """Ugly hack to get the name of when() condition from the source code."""
        name = 'condition'
        try:
            source = inspect.getsource(self.runnable)
            if 'when(' in source:
                name = source.split('when(')[1].split(')')[0]
            elif 'def ' in source:
                name = source.split('def ')[1].split('(')[0]
        except:  # couldn't get the source, oh well
            pass
        return name

    def _verify_signature_match(self, *kargs, **kwargs):
        if isinstance(self._mock, Mock):
            return  # no sense in enforcing this for fake objects
        allowed = self.argspec
        # we consider object a method for purposes or not counting "self"/"cls" as argument if:
        #  - one of inspect.ismethod, inspect.isfunction, _isclass return True
        #    (in Python 3 it's sometimes impossible to tell whether callable is method or not,
        #     so we try both inspect.ismethod and inspect.isfunction; classes are callable too -
        #     they have __init__)
        #  - it's not a static method
        #  - the mocked object is a module - module "methods" are in fact plain functions;
        #    unless they're classes, which means they still have __init__
        is_method = ((inspect.ismethod(self.original) or inspect.isfunction(self.original)
                      or _isclass(self.original)) and
                     self.method_type is not staticmethod and
                     (not isinstance(self._mock, types.ModuleType) or
                      _isclass(self.original)))
        args_len = len(allowed.args)
        if is_method:
            args_len -= 1
        minimum = args_len - (allowed.defaults and len(allowed.defaults) or 0)
        maximum = None
        if allowed.varargs is None and allowed.keywords is None:
            maximum = args_len
        total_positional = len(
            kargs + tuple(a for a in kwargs if a in allowed.args))
        named_optionals = [a for a in kwargs
                           if allowed.defaults
                           if a in allowed.args[len(allowed.args) - len(allowed.defaults):]]
        if allowed.defaults and total_positional == minimum and named_optionals:
            minimum += len(named_optionals)
        if total_positional < minimum:
            raise MethodSignatureError(
                '%s requires at least %s arguments, expectation provided %s' %
                (self.name, minimum, total_positional))
        if maximum is not None and total_positional > maximum:
            raise MethodSignatureError(
                '%s requires at most %s arguments, expectation provided %s' %
                (self.name, maximum, total_positional))
        if args_len == len(kargs) and any(a for a in kwargs if a in allowed.args):
            raise MethodSignatureError(
                '%s already given as positional arguments to %s' %
                ([a for a in kwargs if a in allowed.args], self.name))
        if (not allowed.keywords and
                any(a for a in kwargs if a not in allowed.args + allowed.kwonlyargs)):
            raise MethodSignatureError(
                '%s is not a valid keyword argument to %s' %
                ([a for a in kwargs
                  if a not in (allowed.args + allowed.kwonlyargs)][0], self.name))
        # check that kwonlyargs that don't have default value specified are provided
        required_kwonlyargs = [a for a in allowed.kwonlyargs
                               if a not in (allowed.kwonlydefaults or {})]
        missing_kwonlyargs = [a for a in required_kwonlyargs if a not in kwargs]
        if missing_kwonlyargs:
            raise MethodSignatureError(
                '%s requires keyword-only argument(s) "%s"' %
                (self.name, '", "'.join(missing_kwonlyargs)))

    def _update_original(self, name, obj):
        if hasattr(obj, '__dict__') and name in obj.__dict__:
            self.original = obj.__dict__[name]
        else:
            self.original = getattr(obj, name)
        self._update_argspec()

    def _update_argspec(self):
        original = self.__dict__.get('original')
        if original:
            try:
                if sys.version_info < (3, 0):
                    self.argspec = FullArgSpec(inspect.getargspec(original))
                else:
                    self.argspec = FullArgSpec(inspect.getfullargspec(original))
            except TypeError:
                # built-in function: fall back to stupid processing and hope the
                # builtins don't change signature
                pass

    def _normalize_named_args(self, *kargs, **kwargs):
        argspec = self.argspec
        default = {'kargs': kargs, 'kwargs': kwargs}
        if not argspec:
            return default
        ret = {'kargs': (), 'kwargs': kwargs}
        if inspect.ismethod(self.original):
            args = argspec.args[1:]
        else:
            args = argspec.args
        for i, arg in enumerate(kargs):
            if len(args) <= i:
                return default
            ret['kwargs'][args[i]] = arg
        return ret

    def __raise(self, exception, message):
        """Safe internal raise implementation.

        In case we're patching builtins, it's important to reset the
        expectation before raising any exceptions or else things like
        open() might be stubbed out and the resulting runner errors are very
        difficult to diagnose.
        """
        self.reset()
        raise exception(message)

    def match_args(self, given_args):
        """Check if the set of given arguments matches this expectation."""
        expected_args = self.args
        given_args = self._normalize_named_args(
            *given_args['kargs'], **given_args['kwargs'])
        if (expected_args == given_args or expected_args is None):
            return True
        if (len(given_args['kargs']) != len(expected_args['kargs']) or
            len(given_args['kwargs']) != len(expected_args['kwargs']) or
            (sorted(given_args['kwargs'].keys()) !=
             sorted(expected_args['kwargs'].keys()))):
            return False
        for i, arg in enumerate(given_args['kargs']):
            if not _arguments_match(arg, expected_args['kargs'][i]):
                return False
        for k, v in given_args['kwargs'].items():
            if not _arguments_match(v, expected_args['kwargs'][k]):
                return False
        return True

    def mock(self):
        """Return the mock associated with this expectation."""
        return self._mock

    def with_args(self, *kargs, **kwargs):
        """Override the arguments used to match this expectation's method.

        Args:
          - kargs: optional keyword arguments
          - kwargs: optional named arguments

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use with_args() with attribute stubs")
        self._update_argspec()
        if self.argspec:
            # do this outside try block as TypeError is way too general and catches
            # unrelated errors in the verify signature code
            self._verify_signature_match(*kargs, **kwargs)
            self.args = self._normalize_named_args(*kargs, **kwargs)
        else:
            self.args = {'kargs': kargs, 'kwargs': kwargs}
        return self

    def and_return(self, *values):
        """Override the return value of this expectation's method.

        When and_return is given multiple times, each value provided is returned
        on successive invocations of the method. It is also possible to mix
        and_return with and_raise in the same manner to alternate between returning
        a value and raising and exception on different method invocations.

        When combined with the one_by_one property, value is treated as a list of
        values to be returned in the order specified by successive calls to this
        method rather than a single list to be returned each time.

        Args:
          - values: optional list of return values, defaults to None if not given

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not values:
            value = None
        elif len(values) == 1:
            value = values[0]
        else:
            value = values

        if not self._callable:
            _setattr(self._mock, self.name, value)
            return self

        return_values = _getattr(self, 'return_values')
        if not _getattr(self, '_one_by_one'):
            value = ReturnValue(value)
            return_values.append(value)
        else:
            try:
                return_values.extend([ReturnValue(v) for v in value])
            except TypeError:
                return_values.append(ReturnValue(value))
        return self

    def times(self, number):
        """Number of times this expectation's method is expected to be called.

        There are also 3 aliases for the times() method:

          - once() -> times(1)
          - twice() -> times(2)
          - never() -> times(0)

        Args:
          - number: int

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use times() with attribute stubs")
        expected_calls = _getattr(self, 'expected_calls')
        modifier = _getattr(self, 'modifier')
        expected_calls[modifier] = number
        return self

    def one_by_one(self):
        """Modifies the return value to be treated as a list of return values.

        Each value in the list is returned on successive invocations of the method.

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use one_by_one() with attribute stubs")
        if not self._one_by_one:
            self._one_by_one = True
            return_values = _getattr(self, 'return_values')
            saved_values = return_values[:]
            self.return_values = return_values = []
            for value in saved_values:
                try:
                    for val in value.value:
                        return_values.append(ReturnValue(val))
                except TypeError:
                    return_values.append(value)
        return self

    def at_least(self):
        """Modifies the associated times() expectation.

        When given, an exception will only be raised if the method is called less
        than times() specified. Does nothing if times() is not given.

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use at_least() with attribute stubs")
        expected_calls = _getattr(self, 'expected_calls')
        modifier = _getattr(self, 'modifier')
        if expected_calls[AT_LEAST] is not None or modifier == AT_LEAST:
            self.__raise(FlexmockError, 'cannot use at_least modifier twice')
        if modifier == AT_MOST and expected_calls[AT_MOST] is None:
            self.__raise(FlexmockError, 'cannot use at_least with at_most unset')
        self.modifier = AT_LEAST
        return self

    def at_most(self):
        """Modifies the associated "times" expectation.

        When given, an exception will only be raised if the method is called more
        than times() specified. Does nothing if times() is not given.

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use at_most() with attribute stubs")
        expected_calls = _getattr(self, 'expected_calls')
        modifier = _getattr(self, 'modifier')
        if expected_calls[AT_MOST] is not None or modifier == AT_MOST:
            self.__raise(FlexmockError, 'cannot use at_most modifier twice')
        if modifier == AT_LEAST and expected_calls[AT_LEAST] is None:
            self.__raise(FlexmockError, 'cannot use at_most with at_least unset')
        self.modifier = AT_MOST
        return self

    def ordered(self):
        """Makes the expectation respect the order of should_receive statements.

        An exception will be raised if methods are called out of order, determined
        by order of should_receive calls in the test.

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use ordered() with attribute stubs")
        self._ordered = True
        FlexmockContainer.ordered.append(self)
        return self

    def when(self, func):
        """Sets an outside resource to be checked before executing the method.

        Args:
          - func: function to call to check if the method should be executed

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use when() with attribute stubs")
        if not hasattr(func, '__call__'):
            self.__raise(FlexmockError, 'when() parameter must be callable')
        self.runnable = func
        return self

    def and_raise(self, exception, *kargs, **kwargs):
        """Specifies the exception to be raised when this expectation is met.

        Args:
          - exception: class or instance of the exception
          - kargs: optional keyword arguments to pass to the exception
          - kwargs: optional named arguments to pass to the exception

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use and_raise() with attribute stubs")
        args = {'kargs': kargs, 'kwargs': kwargs}
        return_values = _getattr(self, 'return_values')
        return_values.append(ReturnValue(raises=exception, value=args))
        return self

    def replace_with(self, function):
        """Gives a function to run instead of the mocked out one.

        Args:
          - function: callable

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(FlexmockError, "can't use replace_with() with attribute/property stubs")
        replace_with = _getattr(self, '_replace_with')
        original = self.__dict__.get('original')
        if replace_with:
            self.__raise(FlexmockError, 'replace_with cannot be specified twice')
        if function == original:
            self._pass_thru = True
        self._replace_with = function
        return self

    def and_yield(self, *kargs):
        """Specifies the list of items to be yielded on successive method calls.

        In effect, the mocked object becomes a generator.

        Returns:
          - self, i.e. can be chained with other Expectation methods
        """
        if not self._callable:
            self.__raise(
                FlexmockError, "can't use and_yield() with attribute stubs")
        return self.and_return(iter(kargs))

    def verify(self, final=True):
        """Verify that this expectation has been met.

        Args:
          final: boolean, True if no further calls to this method expected
                 (skip checking at_least expectations when False)

        Raises:
          MethodCallError Exception
        """
        failed, message = self._verify_number_of_calls(final)
        if failed and not self._verified:
            self._verified = True
            self.__raise(
                MethodCallError,
                '%s expected to be called %s times, called %s times' %
                (_format_args(self.name, self.args), message, self.times_called))

    def _verify_number_of_calls(self, final):
        failed = False
        message = ''
        expected_calls = _getattr(self, 'expected_calls')
        times_called = _getattr(self, 'times_called')
        if expected_calls[EXACTLY] is not None:
            message = 'exactly %s' % expected_calls[EXACTLY]
            if final:
                if times_called != expected_calls[EXACTLY]:
                    failed = True
            else:
                if times_called > expected_calls[EXACTLY]:
                    failed = True
        else:
            if final and expected_calls[AT_LEAST] is not None:
                message = 'at least %s' % expected_calls[AT_LEAST]
                if times_called < expected_calls[AT_LEAST]:
                    failed = True
            if expected_calls[AT_MOST] is not None:
                if message:
                    message += ' and '
                message += 'at most %s' % expected_calls[AT_MOST]
                if times_called > expected_calls[AT_MOST]:
                    failed = True
        return failed, message

    def reset(self):
        """Returns the methods overriden by this expectation to their originals."""
        _mock = _getattr(self, '_mock')
        if not isinstance(_mock, Mock):
            original = self.__dict__.get('original')
            if original:
                # name may be unicode but pypy demands dict keys to be str
                name = str(_getattr(self, 'name'))
                if (hasattr(_mock, '__dict__') and
                        name in _mock.__dict__ and
                        self._local_override):
                    del _mock.__dict__[name]
                elif (hasattr(_mock, '__dict__') and
                        name in _mock.__dict__ and
                        type(_mock.__dict__) is dict):
                    _mock.__dict__[name] = original
                else:
                    if self.method_type == staticmethod and sys.version_info < (3, 0):
                        # on some Python 2 implementations (e.g. pypy), just assigning
                        # the original staticmethod would make it a normal method,
                        # thus an additional "self" argument would be passed to it,
                        # we need to explicitly cast it to staticmethod
                        setattr(_mock, name, staticmethod(original))
                    else:
                        setattr(_mock, name, original)
        del self


class Mock(object):
    """Fake object class returned by the flexmock() function."""

    def __init__(self, **kwargs):
        """Mock constructor.

        Args:
          - kwargs: dict of attribute/value pairs used to initialize the mock object
        """
        self._object = self
        for attr, value in kwargs.items():
            if type(value) is property:
                setattr(self.__class__, attr, value)
            else:
                setattr(self, attr, value)

    def __enter__(self):
        return self._object

    def __exit__(self, type, value, traceback):
        pass

    def __call__(self, *kargs, **kwargs):
        """Hack to make Expectation.mock() work with parens."""
        return self

    def __iter__(self):
        """Makes the mock object iterable.

        Call the instance's version of __iter__ if available, otherwise yield self.
        """
        if (hasattr(self, '__dict__') and type(self.__dict__) is dict and
                '__iter__' in self.__dict__):
            for item in self.__dict__['__iter__'](self):
                yield item
        else:
            yield self

    def should_receive(self, name):
        """Replaces the specified attribute with a fake.

        Args:
          - name: string name of the attribute to replace

        Returns:
          - Expectation object which can be used to modify the expectations
            on the fake attribute
        """
        if name in UPDATED_ATTRS:
            raise FlexmockError('unable to replace flexmock methods')
        chained_methods = None
        obj = _getattr(self, '_object')
        if '.' in name:
            name, chained_methods = name.split('.', 1)
        name = _update_name_if_private(obj, name)
        _ensure_object_has_named_attribute(obj, name)
        if chained_methods:
            if (not isinstance(obj, Mock) and not hasattr(getattr(obj, name), '__call__')):
                return_value = _create_partial_mock(getattr(obj, name))
            else:
                return_value = Mock()
            self._create_expectation(obj, name, return_value)
            return return_value.should_receive(chained_methods)
        else:
            return self._create_expectation(obj, name)

    def should_call(self, name):
        """Creates a spy.

        This means that the original method will be called rather than the fake
        version. However, we can still keep track of how many times it's called and
        with what arguments, and apply expectations accordingly.

        should_call is meaningless/not allowed for non-callable attributes.

        Args:
          - name: string name of the method

        Returns:
          - Expectation object
        """
        expectation = self.should_receive(name)
        return expectation.replace_with(expectation.__dict__.get('original'))

    def new_instances(self, *kargs):
        """Overrides __new__ method on the class to return custom objects.

        Alias for should_receive('__new__').and_return(kargs).one_by_one

        Args:
          - kargs: objects to return on each successive call to __new__

        Returns:
          - Expectation object
        """
        if _isclass(self._object):
            return self.should_receive('__new__').and_return(kargs).one_by_one
        else:
            raise FlexmockError('new_instances can only be called on a class mock')

    def _create_expectation(self, obj, name, return_value=None):
        if self not in FlexmockContainer.flexmock_objects:
            FlexmockContainer.flexmock_objects[self] = []
        expectation = self._save_expectation(name, return_value)
        FlexmockContainer.add_expectation(self, expectation)
        if _isproperty(obj, name):
            self._update_property(expectation, name, return_value)
        elif (isinstance(obj, Mock) or
              hasattr(getattr(obj, name), '__call__') or
              _isclass(getattr(obj, name))):
            self._update_method(expectation, name)
        else:
            self._update_attribute(expectation, name, return_value)
        return expectation

    def _save_expectation(self, name, return_value=None):
        if name in [x.name for x in
                    FlexmockContainer.flexmock_objects[self]]:
            expectation = [x for x in FlexmockContainer.flexmock_objects[self]
                           if x.name == name][0]
            expectation = Expectation(
                self._object, name=name, return_value=return_value,
                original=expectation.__dict__.get('original'))
        else:
            expectation = Expectation(
                self._object, name=name, return_value=return_value)
        return expectation

    def _update_class_for_magic_builtins(self, obj, name):
        """Fixes MRO for builtin methods on new-style objects.

        On 2.7+ and 3.2+, replacing magic builtins on instances of new-style
        classes has no effect as the one attached to the class takes precedence.
        To work around it, we update the class' method to check if the instance
        in question has one in its own __dict__ and call that instead.
        """
        if not (name.startswith('__') and name.endswith('__') and len(name) > 4):
            return
        original = getattr(obj.__class__, name)

        def updated(self, *kargs, **kwargs):
            if (hasattr(self, '__dict__') and type(self.__dict__) is dict and
                    name in self.__dict__):
                return self.__dict__[name](*kargs, **kwargs)
            else:
                return original(self, *kargs, **kwargs)
        setattr(obj.__class__, name, updated)
        if _get_code(updated) != _get_code(original):
            self._create_placeholder_mock_for_proper_teardown(
                obj.__class__, name, original)

    def _create_placeholder_mock_for_proper_teardown(self, obj, name, original):
        """Ensures that the given function is replaced on teardown."""
        mock = Mock()
        mock._object = obj
        expectation = Expectation(obj, name=name, original=original)
        FlexmockContainer.add_expectation(mock, expectation)

    def _update_method(self, expectation, name):
        method_instance = self._create_mock_method(name)
        obj = self._object
        if _hasattr(obj, name) and not hasattr(expectation, 'original'):
            expectation._update_original(name, obj)
            method_type = type(_getattr(expectation, 'original'))
            try:
                # TODO(herman): this is awful, fix this properly.
                # When a class/static method is mocked out on an *instance*
                # we need to fetch the type from the class
                method_type = type(_getattr(obj.__class__, name))
            except:
                pass
            if method_type in SPECIAL_METHODS:
                expectation.original_function = getattr(obj, name)
            expectation.method_type = method_type
        override = _setattr(obj, name, types.MethodType(method_instance, obj))
        expectation._local_override = override
        if (override and not _isclass(obj) and not isinstance(obj, Mock) and
                hasattr(obj.__class__, name)):
            self._update_class_for_magic_builtins(obj, name)

    def _update_attribute(self, expectation, name, return_value=None):
        obj = self._object
        expectation._callable = False
        if _hasattr(obj, name) and not hasattr(expectation, 'original'):
            expectation._update_original(name, obj)
        override = _setattr(obj, name, return_value)
        expectation._local_override = override

    def _update_property(self, expectation, name, return_value=None):
        new_name = '_flexmock__%s' % name
        obj = self._object
        if not _isclass(obj):
            obj = obj.__class__
        expectation._callable = False
        original = getattr(obj, name)

        @property
        def updated(self):
            if (hasattr(self, '__dict__') and type(self.__dict__) is dict and
                    name in self.__dict__):
                return self.__dict__[name]
            else:
                return getattr(self, new_name)
        setattr(obj, name, updated)
        if not hasattr(obj, new_name):
            # don't try to double update
            FlexmockContainer.add_teardown_property(obj, new_name)
            setattr(obj, new_name, original)
            self._create_placeholder_mock_for_proper_teardown(obj, name, original)

    def _create_mock_method(self, name):
        def _handle_exception_matching(expectation):
            return_values = _getattr(expectation, 'return_values')
            if return_values:
                raised, instance = sys.exc_info()[:2]
                message = '%s' % instance
                expected = return_values[0].raises
                if not expected:
                    raise
                args = return_values[0].value
                expected_instance = expected(*args['kargs'], **args['kwargs'])
                expected_message = '%s' % expected_instance
                if _isclass(expected):
                    if expected is not raised and expected not in raised.__bases__:
                        raise (ExceptionClassError('expected %s, raised %s' %
                               (expected, raised)))
                    if args['kargs'] and type(RE_TYPE) is type(args['kargs'][0]):
                        if not args['kargs'][0].search(message):
                            raise (ExceptionMessageError('expected /%s/, raised "%s"' %
                                   (args['kargs'][0].pattern, message)))
                    elif expected_message and expected_message != message:
                        raise (ExceptionMessageError('expected "%s", raised "%s"' %
                               (expected_message, message)))
                elif expected is not raised:
                    raise (ExceptionClassError('expected "%s", raised "%s"' %
                           (expected, raised)))
            else:
                raise

        def match_return_values(expected, received):
            if not isinstance(expected, tuple):
                expected = (expected,)
            if not isinstance(received, tuple):
                received = (received,)
            if len(received) != len(expected):
                return False
            for i, val in enumerate(received):
                if not _arguments_match(val, expected[i]):
                    return False
            return True

        def pass_thru(expectation, runtime_self, *kargs, **kwargs):
            return_values = None
            try:
                original = _getattr(expectation, 'original')
                _mock = _getattr(expectation, '_mock')
                if _isclass(_mock):
                    if type(original) in SPECIAL_METHODS:
                        original = _getattr(expectation, 'original_function')
                        return_values = original(*kargs, **kwargs)
                    else:
                        return_values = original(runtime_self, *kargs, **kwargs)
                else:
                    return_values = original(*kargs, **kwargs)
            except:
                return _handle_exception_matching(expectation)
            expected_values = _getattr(expectation, 'return_values')
            if (expected_values and
                    not match_return_values(expected_values[0].value, return_values)):
                raise (MethodSignatureError('expected to return %s, returned %s' %
                       (expected_values[0].value, return_values)))
            return return_values

        def mock_method(runtime_self, *kargs, **kwargs):
            arguments = {'kargs': kargs, 'kwargs': kwargs}
            expectation = FlexmockContainer.get_flexmock_expectation(
                self, name, arguments)
            if expectation:
                if not expectation.runnable():
                    raise StateError('%s expected to be called when %s is True' %
                                     (name, expectation._get_runnable()))
                expectation.times_called += 1
                expectation.verify(final=False)
                _pass_thru = _getattr(expectation, '_pass_thru')
                _replace_with = _getattr(expectation, '_replace_with')
                if _pass_thru:
                    return pass_thru(expectation, runtime_self, *kargs, **kwargs)
                elif _replace_with:
                    return _replace_with(*kargs, **kwargs)
                return_values = _getattr(expectation, 'return_values')
                if return_values:
                    return_value = return_values[0]
                    del return_values[0]
                    return_values.append(return_value)
                else:
                    return_value = ReturnValue()
                if return_value.raises:
                    if _isclass(return_value.raises):
                        raise return_value.raises(
                            *return_value.value['kargs'], **return_value.value['kwargs'])
                    else:
                        raise return_value.raises
                else:
                    return return_value.value
            else:
                # make sure to clean up expectations to ensure none of them
                # interfere with the runner's error reporing mechanism
                # e.g. open()
                for _, expectations in FlexmockContainer.flexmock_objects.items():
                    for expectation in expectations:
                        _getattr(expectation, 'reset')()
                raise MethodSignatureError(_format_args(name, arguments))

        return mock_method


def _arg_to_str(arg):
    if type(RE_TYPE) is type(arg):
        return '/%s/' % arg.pattern
    if sys.version_info < (3, 0):
        # prior to 3.0 unicode strings are type unicode that inherits
        # from basestring along with str, in 3.0 both unicode and basestring
        # go away and str handles everything properly
        if isinstance(arg, basestring):
            return '"%s"' % (arg,)
        else:
            return '%s' % (arg,)
    else:
        if isinstance(arg, str):
            return '"%s"' % (arg,)
        else:
            return '%s' % (arg,)


def _format_args(name, arguments):
    if arguments is None:
        arguments = {'kargs': (), 'kwargs': {}}
    kargs = ', '.join(_arg_to_str(arg) for arg in arguments['kargs'])
    kwargs = ', '.join('%s=%s' % (k, _arg_to_str(v)) for k, v in arguments['kwargs'].items())
    if kargs and kwargs:
        args = '%s, %s' % (kargs, kwargs)
    else:
        args = '%s%s' % (kargs, kwargs)
    return '%s(%s)' % (name, args)


def _create_partial_mock(obj_or_class, **kwargs):
    matches = [x for x in FlexmockContainer.flexmock_objects
               if x._object is obj_or_class]
    if matches:
        mock = matches[0]
    else:
        mock = Mock()
        mock._object = obj_or_class
    for name, return_value in kwargs.items():
        if hasattr(return_value, '__call__'):
            mock.should_receive(name).replace_with(return_value)
        else:
            mock.should_receive(name).and_return(return_value)
    if not matches:
        FlexmockContainer.add_expectation(mock, Expectation(obj_or_class))
    if (_attach_flexmock_methods(mock, Mock, obj_or_class) and not _isclass(mock._object)):
        mock = mock._object
    return mock


def _attach_flexmock_methods(mock, flexmock_class, obj):
    try:
        for attr in UPDATED_ATTRS:
            if hasattr(obj, attr):
                if (_get_code(getattr(obj, attr)) is not _get_code(getattr(flexmock_class, attr))):
                    return False
        for attr in UPDATED_ATTRS:
            _setattr(obj, attr, getattr(mock, attr))
    except TypeError:
        raise MockBuiltinError(
            'Python does not allow you to mock builtin objects or modules. '
            'Consider wrapping it in a class you can mock instead')
    except AttributeError:
        raise MockBuiltinError(
            'Python does not allow you to mock instances of builtin objects. '
            'Consider wrapping it in a class you can mock instead')
    return True


def _get_code(func):
    if hasattr(func, 'func_code'):
        code = 'func_code'
    elif hasattr(func, 'im_func'):
        func = func.im_func
        code = 'func_code'
    else:
        code = '__code__'
    return getattr(func, code)


def _arguments_match(arg, expected_arg):
    if expected_arg == arg:
        return True
    elif _isclass(expected_arg) and isinstance(arg, expected_arg):
        return True
    elif (type(RE_TYPE) is type(expected_arg) and
          expected_arg.search(arg)):
        return True
    else:
        return False


def _getattr(obj, name):
    """Convenience wrapper to work around custom __getattribute__."""
    return object.__getattribute__(obj, name)


def _setattr(obj, name, value):
    """Ensure we use local __dict__ where possible."""
    name = str(name)  # name may be unicode but pypy demands dict keys to be str
    local_override = False
    if hasattr(obj, '__dict__') and type(obj.__dict__) is dict:
        if name not in obj.__dict__:
            local_override = True
        obj.__dict__[name] = value
    else:
        setattr(obj, name, value)
    return local_override


def _hasattr(obj, name):
    """Ensure hasattr checks don't create side-effects for properties."""
    if (not _isclass(obj) and hasattr(obj, '__dict__') and name not in obj.__dict__):
        if name in DEFAULT_CLASS_ATTRIBUTES:
            return False  # avoid false positives for things like __call__
        else:
            return hasattr(obj.__class__, name)
    else:
        return hasattr(obj, name)


def _isclass(obj):
    """Fixes stupid bug in inspect.isclass from < 2.7."""
    if sys.version_info < (2, 7):
        return isinstance(obj, (type, types.ClassType))
    else:
        return inspect.isclass(obj)


def _isproperty(obj, name):
    if isinstance(obj, Mock):
        return False
    if not _isclass(obj) and hasattr(obj, '__dict__') and name not in obj.__dict__:
        attr = getattr(obj.__class__, name)
        if type(attr) is property:
            return True
    elif _isclass(obj):
        attr = getattr(obj, name)
        if type(attr) is property:
            return True
    return False


def _update_name_if_private(obj, name):
    if (name.startswith('__') and not name.endswith('__') and not inspect.ismodule(obj)):
        if _isclass(obj):
            class_name = obj.__name__
        else:
            class_name = obj.__class__.__name__
        name = '_%s__%s' % (class_name.lstrip('_'), name.lstrip('_'))
    return name


def _ensure_object_has_named_attribute(obj, name):
    if not isinstance(obj, Mock) and not _hasattr(obj, name):
        exc_msg = '%s does not have attribute %s' % (obj, name)
        if name == '__new__':
            exc_msg = 'old-style classes do not have a __new__() method'
        raise FlexmockError(exc_msg)


def flexmock_teardown():
    """Performs lexmock-specific teardown tasks."""
    saved = {}
    instances = []
    classes = []
    for mock_object, expectations in FlexmockContainer.flexmock_objects.items():
        saved[mock_object] = expectations[:]
        for expectation in expectations:
            _getattr(expectation, 'reset')()
    for mock in saved.keys():
        obj = mock._object
        if not isinstance(obj, Mock) and not _isclass(obj):
            instances.append(obj)
        if _isclass(obj):
            classes.append(obj)
    for obj in instances + classes:
        for attr in UPDATED_ATTRS:
            try:
                obj_dict = obj.__dict__
                if _get_code(obj_dict[attr]) is _get_code(Mock.__dict__[attr]):
                    del obj_dict[attr]
            except:
                try:
                    if _get_code(getattr(obj, attr)) is _get_code(Mock.__dict__[attr]):
                        delattr(obj, attr)
                except AttributeError:
                    pass
    FlexmockContainer.teardown_properties()
    FlexmockContainer.reset()

    # make sure this is done last to keep exceptions here from breaking
    # any of the previous steps that cleanup all the changes
    for mock_object, expectations in saved.items():
        for expectation in expectations:
            _getattr(expectation, 'verify')()


def flexmock(spec=None, **kwargs):
    """Main entry point into the flexmock API.

    This function is used to either generate a new fake object or take
    an existing object (or class or module) and use it as a basis for
    a partial mock. In case of a partial mock, the passed in object
    is modified to support basic Mock class functionality making
    it unnecessary to make successive flexmock() calls on the same
    objects to generate new expectations.

    Examples:
      >>> flexmock(SomeClass)
      >>> SomeClass.should_receive('some_method')

    NOTE: it's safe to call flexmock() on the same object, it will detect
    when an object has already been partially mocked and return it each time.

    Args:
      - spec: object (or class or module) to mock
      - kwargs: method/return_value pairs to attach to the object

    Returns:
      Mock object if no spec is provided. Otherwise return the spec object.
    """
    if spec is not None:
        return _create_partial_mock(spec, **kwargs)
    else:
        # use this intermediate class to attach properties
        klass = type('MockClass', (Mock,), {})
        return klass(**kwargs)


# RUNNER INTEGRATION


def _hook_into_pytest():
    try:
        from _pytest import runner
        saved = runner.call_runtest_hook

        def call_runtest_hook(item, when, **kwargs):
            ret = saved(item, when, **kwargs)
            if when != 'call' and ret.excinfo is None:
                return ret
            if hasattr(runner.CallInfo, "from_call"):
                teardown = runner.CallInfo.from_call(flexmock_teardown, when=when)
            else:
                teardown = runner.CallInfo(flexmock_teardown, when=when)
                teardown.result = None
            if ret.excinfo is not None:
                teardown.excinfo = ret.excinfo
            return teardown
        runner.call_runtest_hook = call_runtest_hook

    except ImportError:
        pass
_hook_into_pytest()


def _hook_into_doctest():
    try:
        from doctest import DocTestRunner
        saved = DocTestRunner.run

        def run(self, test, compileflags=None, out=None, clear_globs=True):
            try:
                return saved(self, test, compileflags, out, clear_globs)
            finally:
                flexmock_teardown()
        DocTestRunner.run = run
    except ImportError:
        pass
_hook_into_doctest()


def _patch_test_result(klass):
    """Patches flexmock into any class that inherits unittest.TestResult.

    This seems to work well for majority of test runners. In the case of nose
    it's not even necessary as it doesn't override unittest.TestResults's
    addSuccess and addFailure methods so simply patching unittest works
    out of the box for nose.

    For those that do inherit from unittest.TestResult and override its
    stopTest and addSuccess methods, patching is pretty straightforward
    (numerous examples below).

    The reason we don't simply patch unittest's parent TestResult class
    is stopTest and addSuccess in the child classes tend to add messages
    into the output that we want to override in case flexmock generates
    its own failures.
    """

    saved_addSuccess = klass.addSuccess
    saved_stopTest = klass.stopTest

    def addSuccess(self, test):
        self._pre_flexmock_success = True

    def stopTest(self, test):
        if _get_code(saved_stopTest) is not _get_code(stopTest):
            # if parent class was for some reason patched, avoid calling
            # flexmock_teardown() twice and delegate up the class hierarchy
            # this doesn't help if there is a gap and only the parent's
            # parent class was patched, but should cover most screw-ups
            try:
                flexmock_teardown()
                saved_addSuccess(self, test)
            except:
                if hasattr(self, '_pre_flexmock_success'):
                    self.addFailure(test, sys.exc_info())
            if hasattr(self, '_pre_flexmock_success'):
                del self._pre_flexmock_success
        return saved_stopTest(self, test)

    if klass.stopTest is not stopTest:
        klass.stopTest = stopTest

    if klass.addSuccess is not addSuccess:
        klass.addSuccess = addSuccess


def _hook_into_unittest():
    import unittest
    try:
        try:
            # only valid TestResult class for unittest is TextTestResult
            _patch_test_result(unittest.TextTestResult)
        except AttributeError:
            # ugh, python2.4
            _patch_test_result(unittest._TextTestResult)
    except:  # let's not take any chances
        pass
_hook_into_unittest()


def _hook_into_unittest2():
    try:
        try:
            from unittest2 import TextTestResult
        except ImportError:
            # Django has its own copy of unittest2 it uses as fallback
            from django.utils.unittest import TextTestResult
        _patch_test_result(TextTestResult)
    except:
        pass
_hook_into_unittest2()


def _hook_into_twisted():
    try:
        from twisted.trial import reporter
        _patch_test_result(reporter.MinimalReporter)
        _patch_test_result(reporter.TextReporter)
        _patch_test_result(reporter.VerboseTextReporter)
        _patch_test_result(reporter.TreeReporter)
    except:
        pass
_hook_into_twisted()


def _hook_into_subunit():
    try:
        import subunit
        _patch_test_result(subunit.TestProtocolClient)
    except:
        pass
_hook_into_subunit()


def _hook_into_zope():
    try:
        from zope import testrunner
        _patch_test_result(testrunner.runner.TestResult)
    except:
        pass
_hook_into_zope()


def _hook_into_testtools():
    try:
        from testtools import testresult
        _patch_test_result(testresult.TestResult)
    except:
        pass
_hook_into_testtools()


def _hook_into_teamcity_unittest():
    try:
        from tcunittest import TeamcityTestResult
        _patch_test_result(TeamcityTestResult)
    except:
        pass
_hook_into_teamcity_unittest()


# Dark magic to make the flexmock module itself callable.
# So that you can say:
#   import flexmock
# instead of:
#   from flexmock import flexmock
class _CallableModule(types.ModuleType):
    def __init__(self):
        super(_CallableModule, self).__init__('flexmock')
        self._realmod = sys.modules['flexmock']
        sys.modules['flexmock'] = self
        self.__doc__ = flexmock.__doc__

    def __dir__(self):
        return dir(self._realmod)

    def __call__(self, *args, **kw):
        return self._realmod.flexmock(*args, **kw)

    def __getattr__(self, attr):
        return getattr(self._realmod, attr)

_CallableModule()
