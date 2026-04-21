DEF fact(x):
    IF x = 0 | x = 1:
        RETURN x
    ELSE:
        RETURN x * fact(x - 1)

SET x TO ASK INT "Number to find its factorial: "
DISP fact(x)