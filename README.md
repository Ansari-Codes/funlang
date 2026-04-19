# Fun Language or FLang

- This is just a fun DSL (domain sepcific language).
- For me, just a python coding practice.
- But great for kids to start simple programming.

Syntax:

```SQL
-- Comment

-- VARIABLES
SET x TO 10
DISP x

-- CONDITIONALS
IF x > 0:
    DISP "x is greater than 10 with value {x}"
ELIF x < 0:
    DISP "x is smaller than 10 with value {x}"
ELSE:
    DISP "x is equal to 10"

-- FOR LOOP
FOR RANGE 1 TO 2 AS x:
    DISP x

FOR RANGE 1 TO 2 STEP 6 AS x:
    DISP x

FOR RANGE 3 AS x:
    DISP x

-- WHILE LOOP
SET y TO 0
WHILE y < 10:
    DISP y
    SET y TO y + 1

-- END keyword and NEXT keyword
SET z TO 0
-- this loop runs infinte, so, avoid this
-- this is just demostration
WHILE z < 10:
    SET z TO z + 1
    IF z%2 = 0:
        DISP z
    ELIF z%3 = 0:
        NEXT
    ELIF z%4 = 0:
        END

-- ARRAYS
SET arr TO [1, 2, 3, 4]
DISP arr

FOR arr AS i:
    DISP i

SET arr[3] TO 5
DISP arr

DEF square(n):
    RETURN n**2

DISP square(10)

SET input TO ASK INT "Number? "
DISP square(input)

```

types:
int
float
str
bool
arr (array)

OPERATORS:
```+ : adding, string concatenation
- : sub
* : mul
** : pow
/ : div
// : fdiv
% : mod
= : eq
> : gt
< : st
>= : geq
<= : seq
& : and
| : or
! : not
```
