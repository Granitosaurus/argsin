# argsin
ArgsIn is an argument manager for user input. It's a simple module that provides ability to find arguments for python's `input()`(or any other stream) and act upon them.

### Example   

    argsin = ArgsIn()
    argsin.add_action(['name', 'nickname'],  # these are argument identifiers
                      lambda *args, **kwargs: print(kwargs))  # these are actions to execute
    value = argsin('Find user: ')
    print(value)
    
Outcome:

    >>>Find user: hello --name Guido  # input
    >>>{'value': 'Guido', 'text': 'hello'} # action executed
    >>>(hello,[None],{'name': 'Guido'})  # that's print(value)
    # ^ (user input without arguments, what action returns, {arg: value,..} dict)
    
We can also use user input to resolve some code, example number guessing game:

    <...>
    STOP = 0
    argsin.add_action('stop', STOP)
    while True:
        number = random.randint(0, 10)
        value = argsin('guess number between 1 and 10: ')
        if STOP in value[1]:
            print('you gave up :(')
            break
        if value[0] == str(number):
            print('you won!')
            break
        else:
            print('wrong, it was: {}'.format(number))
            
Outcome:

      guess number between 1 and 10: 2
      wrong, it was: 4
      guess number between 1 and 10: 9
      wrong, it was: 5
      guess number between 1 and 10: --stop
      you gave up :(
        
