# 🎮 FLang: The Fun Language Manual
**Written for Kids, Code Crackers, and Future Programmers!**

Welcome to FLang! This is a special coding language designed to be easy to read and write. Think of it like giving instructions to a robot, but using words that make sense to humans.

Let’s start your adventure!

---

## 📦 Variables (Keeping Track of Things)

In coding, we often need to remember information. We use **Variables** to store this info. Think of a variable like a labeled box where you can keep a number, a piece of text, or a list of items.

**How to create a variable:**
Use the command `SET`.

```sql
SET my_name TO "Robot"
SET score TO 100
SET is_fun TO true
```

Now, the computer knows:
*   `my_name` is "Robot"
*   `score` is 100

---

## 🖨️ Showing Stuff on Screen

If you want to see what is inside your variables, or just say "Hello", use `DISP` (short for Display).

```sql
DISP "Hello, World!"
DISP score
```
*Tip: You can print text and variables together!*

---

## 🤔 Making Decisions (Conditionals)

Sometimes you want the computer to do different things based on the situation. For this, we use `IF`, `ELIF` (Else If), and `ELSE`.

```sql
SET age TO 10

IF age > 12:
    DISP "You are a teenager!"
ELIF age < 5:
    DISP "You are a toddler!"
ELSE:
    DISP "You are just right!"
```
*Translation: If the age is bigger than 12, print the first thing. Otherwise, if it is smaller than 5, print the second thing. If none of those are true, print the last thing!*

---

## 🔄 Loops (Doing Things Over and Over)

Computers are great at doing boring tasks repeatedly. We call these **Loops**.

### The `FOR` Loop
Use this when you know how many times you want to do something.

```sql
-- This will print numbers 1, 2, 3, 4, 5
FOR range(1, 6) AS i:
    DISP i
```

### The `WHILE` Loop
Use this when you want to keep going until a certain condition changes.

```sql
SET counter TO 0
WHILE counter < 3:
    DISP "Still going!"
    SET counter TO counter + 1
```

### Controlling Loops
*   **`NEXT`**: Skip the rest of the code right now and jump to the next round of the loop.
*   **`END`**: Stop the loop completely immediately.

---

## 🎒 Lists (Lists of Things)

What if you want to store many numbers? You use an **List**, which is just a list!

```sql
SET my_list TO [10, 20, 30, 40]
DISP my_list[0] -- This gets the first item (10)
```

You can loop through a list easily:
```sql
FOR my_list AS item:
    DISP item
```

---

## ⚡ Special Powers (Functions)

You can create your own commands using `DEF`. This helps you organize your code.

```sql
DEF say_hello(name):
    DISP "Hello " + name + "!"

say_hello("Sam")
```

---

## 🛠️ Fun Built-in Tools

FLang comes with a toolbox full of helpers. You don't need to write the math for these; just use them!

### String Tools (Text)
*   `strlower("HELLO")` → turns text to lowercase ("hello").
*   `strupper("hello")` → turns text to UPPERCASE ("HELLO").
*   `strlen("abc")` → counts the letters (3).
*   `strreplace("abc", "a", "z")` → swaps letters ("zbc").
*   `strcontains("apple", "p")` → checks if text is inside (True).
*   `strstarts("hello", "he")` → checks if it starts with something (True).
*   `strjoin(["apple", "banana", "orange"], ", ")` → joins strings in an List with specified joiner (", ") (output: "apply, banana, orange").

### Math Tools
*   `abs(-10)` → makes negative numbers positive (10).
*   `round(4.7)` → rounds to the nearest whole number (5).
*   `floor(4.9)` → rounds down (4).
*   `ceil(4.1)` → rounds up (5).
*   `max(5, 10)` → finds the biggest number (10).
*   `min(5, 10)` → finds the smallest number (5).
*   `sum([1, 2, 3])` → adds up a list (6).
*   `random()` → gives you a random number between 0 and 1.
*   `randint(1, 10)` → gives you a random whole number between 1 and 10.

### List Tools
*   `len([1, 2, 3])` → tells you how many items are in the list (3).
*   `sort([3, 1, 2])` → organizes the list ([1, 2, 3]).
*   `reverse([1, 2, 3])` → flips the list backwards ([3, 2, 1]).
*   `append(my_list, 4)` → adds an item to the end of a list.
*   `pop(my_list)` → removes the last item from a list.
*   `index(my_list, 2)` → returns item at index 2.
*   `slice(my_list, 1, 3)` → return sub-list from item 1 to 3 (ending exclusive).

### Conversion Tools
*   `tostr(123)` → turns a number into text ("123").
*   `toint("123")` → turns text into a number (123).
*   `tofloat("1.5")` → turns text into a decimal number (1.5).
*   `typeof(x)` → tells you what "type" of variable x is (like "int" or "str").

### Asking the User
*   `ASK INT "Guess a number: "` — Asks the user for a whole number.
*   `ASK STR "What is your name? "` — Asks the user for text.

---

# RUN by
```cmd
python -m flang your_file.fun
```

---

## 🚀 Ready to Code?
Now you know the basics! Just remember: computers do exactly what you tell them. If something goes wrong, check your spelling and your colons `:`. Have fun!

***