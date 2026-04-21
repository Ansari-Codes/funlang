Builtins = {
    "strlower": "fun_strlower",
    "strupper": "fun_strupper",
    "strlen": "fun_strlen",
    "strreplace": "fun_strreplace",
    "strsplit": "fun_strsplit",
    "strcontains": "fun_strcontains",
    "strstarts": "fun_strstarts",
    "strends": "fun_strends",
    "strjoin": "fun_strjoin",
    "abs": "fun_abs",
    "round": "fun_round",
    "floor": "fun_floor",
    "ceil": "fun_ceil",
    "max": "fun_max",
    "min": "fun_min",
    "sum": "fun_sum",
    "len": "fun_len",
    "range": "fun_range",
    "sort": "fun_sort",
    "reverse": "fun_reverse",
    "append": "fun_append",
    "pop": "fun_pop",
    "index": "fun_index",
    "slice": "fun_slice",
    "typeof": "fun_typeof",
    "tostr": "fun_tostr",
    "toint": "fun_toint",
    "tofloat": "fun_tofloat",
    "random": "fun_random",
    "randint": "fun_randint",
}

BUILTIN_IMPLEMENTATIONS = '''
import math as _math
import random as _random

def fun_strlower(s): return str(s).lower()
def fun_strupper(s): return str(s).upper()
def fun_strlen(s): return len(str(s))
def fun_strreplace(s, old, new): return str(s).replace(str(old), str(new))
def fun_strsplit(s, sep=" "): return str(s).split(str(sep))
def fun_strcontains(s, sub): return str(sub) in str(s)
def fun_strstarts(s, pre): return str(s).startswith(str(pre))
def fun_strends(s, suf): return str(s).endswith(str(suf))
def fun_strjoin(lst, joiner=""): return joiner.join(lst)
def fun_abs(n): return abs(n)
def fun_round(n, d=0): return round(n, int(d))
def fun_floor(n): return _math.floor(n)
def fun_ceil(n): return _math.ceil(n)
def fun_max(*args): return max(*args) if len(args) > 1 else max(args[0])
def fun_min(*args): return min(*args) if len(args) > 1 else min(args[0])
def fun_sum(lst): return sum(lst)
def fun_len(lst): return len(lst)
def fun_range(*args): return list(range(*[int(a) for a in args]))
def fun_sort(lst): return sorted(lst)
def fun_reverse(lst): return list(reversed(lst))
def fun_append(lst, item): return lst + [item]
def fun_pop(lst): return lst[:-1]
def fun_index(lst, ind): return lst[ind]
def fun_slice(lst, start, end=None, step=None): return lst[start:end:step]
def fun_typeof(v): return type(v).__name__
def fun_tostr(v): return str(v)
def fun_toint(v): return int(v)
def fun_tofloat(v): return float(v)
def fun_random(): return _random.random()
def fun_randint(a, b): return _random.randint(int(a), int(b))
fun_true = True
fun_false = False
'''
