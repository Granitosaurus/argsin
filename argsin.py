"""
ArgsIn is an argument manager for user input. It's a simple module
that provides ability to find arguments for python's input()
(or any other stream) and act upon them.

example:
    argsin = ArgsIn()
    argsin.add_action(['name', 'nickname'],  # these are argument identifiers
                      # these are actions to execute
                      lambda *args, **kwargs: print("Looking for: {}...".format(kwargs['value'])))
    value = argsin('Find user: ')
    Find user: bdfl --name Guido
    Looking for: Guido...
"""
import logging
import re

# Set up logger
argsin_logger = logging.getLogger('argsin')
argsin_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(message)s')
ch.setFormatter(formatter)
argsin_logger.addHandler(ch)


class Input:
    """Class for storing ArgsIn input returns"""
    def __init__(self, text, action_returns, args):
        self.text = text
        self.action_returns = action_returns
        self.args = args

    def __repr__(self):
        return '({},{},{})'.format(self.text, self.action_returns, self.args)

    def __getitem__(self, item):
        if item == 0:
            return self.text
        if item == 1:
            return self.action_returns
        if item == 2:
            return self.args
        raise IndexError("ArgsIn Input only has 3 values(text,[action_returns],[args])")


class ArgsIn:
    arg_value_regex = re.compile('\B-{1,2}([^\b|^\s]+)(?:\s|)(?:"|)([^-]+|-\d+|)')
    arg_regex = re.compile('(\B-{1,2}[^\b|^\s]+(?:\s|)(?:"|))')

    def __init__(self, default_input_manager=input, action_map=None):
        self.action_map = action_map or []
        if self.action_map:
            self._validate_action_map()
        self.default_input_manager = default_input_manager

    def find_arguments(self, text):
        """Finds arguments in text
        :param text: text where to look for arguments
        :return a list of tuples of (argument, value)
        """
        args = self.arg_value_regex.findall(text)
        args = {k.strip(''' '"'''): v.strip(''' '"''') for k, v in args}
        clean_text = self.arg_regex.split(text)[0].strip()
        return clean_text, args

    def argsin(self, msg, *args, **kwargs):
        """
        Smart input for question answers which reads the answer for arguments (i.e. --hint)
        :param msg: message to pass to input manager
        # kwargs
        :param input_manager[self.default_input_manager]: manager that takes the input (i.e. builtins.input())
        :param recursion_on_invalid[True]: whether to recur on invalid argument
        :param single_action[False]: whether to run 1 argument only
        :param squelch[False]: whether to silence logging

        # any extra kwargs will be passed to actions
        :return: Input(user input without arguments, what action returns, {arg: value,..} dict)
        """
        local_kwargs = ('recursion_on_invalid', 'single_action', 'squelch')
        recursion_on_invalid = kwargs.get('recursion_on_invalid', True)
        single_action = kwargs.get('single_action', False)
        squelch = kwargs.get('squelch', False)
        input_manager = kwargs.get('input_manager', self.default_input_manager)
        if not callable(input_manager) and recursion_on_invalid:
            raise ValueError('recursion on valid cannot be true if input_manager is not callable(infinite recursion)')

        text, t_args = self.find_arguments(input_manager(msg))
        func_returns = []
        # Iterate through found (argument, value) and
        # execute action if argument matches action identifiers
        for arg, value in t_args.items():
            action_kwargs = {k: v for k, v in kwargs.items() if k not in local_kwargs}
            action_kwargs['value'] = value
            action_kwargs['text'] = text
            # handle unknown/invalid arguments
            invalid = not any(arg in action[0] for action in self.action_map)
            if invalid:
                if not squelch:
                    argsin_logger.info('Unknown arg: "{}"'.format(arg))
                if recursion_on_invalid:
                    return self.argsin(msg, input_manager, recursion_on_invalid, single_action, squelch)
            # handle actions
            for action in self.action_map:
                identifiers, actions, recursive = action
                if arg in identifiers:
                    for item in actions:
                        # is callable
                        try:
                            func_returns.append(item(*args, **action_kwargs))
                            continue
                        except TypeError:
                            pass
                        # is callable with no arg intake
                        try:
                            func_returns.append(item())
                            continue
                        except TypeError:
                            pass
                        # is callable but failed to call
                        if callable(item):
                            argsin_logger.error('Action {} is callable but intakes unexpected arguments'
                                                '(should take *args, **kwargs or nothing)'.format(action))
                        # is not a callable
                        func_returns.append(item)
                    if recursive:
                        return self.argsin(msg, *args, **kwargs)
                    if single_action:
                        Input(text, func_returns, t_args)
        return Input(text, func_returns, t_args)

    def add_action(self, identifiers, *actions, **kwargs):
        """
        Add action to the action_map
        :param identifiers: possible valid arguments
        :param actions: function to execute, must be able to receive 1 argument value
        :keyword recursive: [False] whether action is recursive or not
        """
        if isinstance(identifiers, str):
            identifiers = (identifiers,)
        action = (identifiers, actions, kwargs.get('recursive', False))
        self._validate_action(action)
        self.action_map.append(action)

    @staticmethod
    def _validate_action(action):
        if len(action) != 3:
            raise ValueError('arg map "{}" should have length of two (arg, action)'.format(action))
        if isinstance(action[0], str):
            raise ValueError('arg map arg value "{}" string found, expected iterator'.format(action[0]))
        try:
            iter(action[0])
        except TypeError:
            raise ValueError('arg map arg value "{}" is not iterable, expected iterator'.format(action[0]))

    def _validate_action_map(self):
        for action in self.action_map:
            self._validate_action(action)

    def __call__(self, msg, *args, **kwargs):
        return self.argsin(msg, *args, **kwargs)
