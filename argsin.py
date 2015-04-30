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
            self._validate_args_map()
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

    def argsin(self,
               msg,
               input_manager=None,
               recursion_on_invalid=True,
               single_action=False,
               squelch=False):
        """
        Smart input for question answers which reads the answer for arguments (i.e. --hint)
        :param msg:
        :param input_manager:
        :param recursion_on_invalid:
        :param single_action:
        :param squelch:
        :return:
        """
        if not input_manager:
            input_manager = self.default_input_manager
        elif not callable(input_manager) and recursion_on_invalid:
            raise ValueError('recursion on valid cannot be true if input_manager is not callable(infinite recursion)')
        text, args = self.find_arguments(input_manager(msg))
        func_returns = []
        for arg, value in args.items():
            invalid = not any(arg in action[0] for action in self.action_map)
            if invalid:
                if not squelch:
                    argsin_logger.info('Unknown arg: "{}"'.format(arg))
                if recursion_on_invalid:
                    return self.argsin(msg, input_manager, recursion_on_invalid, single_action, squelch)
            for identifiers, actions in self.action_map:
                if arg in identifiers:
                    for item in actions:
                        # is callable
                        try:
                            func_returns.append(item(value))
                            continue
                        except TypeError:
                            pass
                        # is callable with no arg intake
                        try:
                            func_returns.append(item())
                            continue
                        except TypeError:
                            pass
                        # is not a callable
                        func_returns.append(item)
                if single_action:
                    return Input(text, func_returns, args)
        return Input(text, func_returns, args)

    def add_action(self, identifiers, *actions):
        """
        Add action to the action_map
        :param identifiers: possible valid arguments
        :param actions: function to execute, must be able to receive 1 argument value
        """
        if isinstance(identifiers, str):
            identifiers = (identifiers,)
        action = (identifiers, actions,)
        self._validate_action(action)
        self.action_map.append(action)

    @staticmethod
    def _validate_action(action):
        if len(action) != 2:
            raise ValueError('arg map "{}" should have length of two (arg, action)'.format(action))
        if isinstance(action[0], str):
            raise ValueError('arg map arg value "{}" string found, expected iterator'.format(action[0]))
        try:
            iter(action[0])
        except TypeError:
            raise ValueError('arg map arg value "{}" is not iterable, expected iterator'.format(action[0]))

    
    def _validate_args_map(self):
        for action in self.action_map:
            self._validate_action(action)

    def __call__(self, msg, input_manager=None, recursion_on_invalid=True, single_action=False, squelch=False):
        return self.argsin(msg,
                           input_manager=input_manager,
                           recursion_on_invalid=recursion_on_invalid,
                           single_action=single_action,
                           squelch=squelch)
            

if __name__ == '__main__':
    argsin = ArgsIn()
    argsin.add_action(['name', 'nickname'],
                      lambda user_input: print("Looking for: {}...".format(user_input)))
    value = argsin('Find user:')
    print(value[3])