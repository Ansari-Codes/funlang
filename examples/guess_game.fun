SET x TO round(random(), 2)*100
SET guess TO -1

WHILE !(guess = x):
    SET guess TO ASK INT "Guess (0 - 100): "
    IF guess > x:
        DISP "Too High!"
    ELIF guess < x:
        DISP "Too low!"
    ELSE:
        DISP "You made it!"
        END
