### Err Vars #######################
FLOATERROR = 'error: not a float or int'
DIVBYZEROERROR = 'error: can not divide by zero'
####################################


### SQA Utils ######################

def _checkType(num):
    def tryInt(n):
        try:
            return int(n)
        except (ValueError, TypeError) as e:
            return -1
    
    def tryFloat(n):
        try:
            return float(n)
        except (ValueError, TypeError) as e:
            return FLOATERROR
    
    RESULT = tryInt(num)

    if RESULT != -1: # it is an integer
        return RESULT
    
    return tryFloat(num)


def _checkZeroDivErr(num1, num2):
    try:
        return (num1 / num2)
    except ZeroDivisionError as e:
        return 'error: can not divide by zero'

####################################


### Calculator Functions Below ###

def performSub(a, b):
    a = _checkType(a)
    b = _checkType(b)
    if a == FLOATERROR or b == FLOATERROR:
        return FLOATERROR
    return a-b

def performAdd(a, b):
    a = _checkType(a)
    b = _checkType(b)
    if a == FLOATERROR or b == FLOATERROR:
        return FLOATERROR
    return a+b

def performSquareRoot(a):
    a = _checkType(a)
    if a == FLOATERROR:
        return FLOATERROR
    return a ** 0.5

def performMultiply(a, b):
    a = _checkType(a)
    b = _checkType(b)
    if a == FLOATERROR or b == FLOATERROR:
        return FLOATERROR
    return a * b

def performDivide(a, b):
    a = _checkType(a)
    b = _checkType(b)
    if a == FLOATERROR or b == FLOATERROR:
        return FLOATERROR
    return _checkZeroDivErr(a, b)

####################################