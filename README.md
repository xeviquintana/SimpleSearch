# DATA ENGINEER TEST

This project aims to solve the challenge described in [problem description](PROBLEM_DESCRIPTION.md)

## Building and running this code

This code has been successfully tested to run in `Python 3.9`, current release at the time of writing this doc is 3.9.6.

```shell
python3 -V
```
If it's not 3.9.6 or above, get it from [python.org](https://www.python.org/downloads/release/python-396/)

Make sure `pip` is available as a package manager, otherwise follow
[these instructions](https://pip.pypa.io/en/stable/installation/) to get it up.

You should use `virtualenv` module to install required packages. Let's install it:
```
python3 -m pip install virtualenv
```

After having python 3.9.6 and having virtualenv module installed, next steps are as follow:

1. Create a new virtual environment, let's call it `mypython`:
   ```shell
   python3 -m pip virtualenv mypython
   ```
   
   It will create a folder in our current directory, named `mypython`.


2. Time to activate it.
    - In Mac OS / Linux
      ```shell
      source mypython/bin/activate
      ```
    - In Windows
      ```shell
      mypthon\Scripts\activate
      ```

3. You should see the name of your virtual environment in brackets on your terminal line e.g. `(mypython)`.

4. Install required packages. First, check you are in SimpleSearch project root folder:
   - In Mac OS / Linux run a `pwd`
   - In Windows run a `echo %cd%`

   Install dependencies from requirements file:
   ```shell
   python3 -m pip install -r requirements.txt
   ```

5. Finally, run the code! In case of doubts run it using `-h` flag option to display a help message.

   Remember to use `\` if you're in Windows as directory separator...
   ```shell
   python3 src/simple_search.py --path samples
   ```

6. When you're done, remember to deactivate the virtualenv `mypython`:
   ```shell
   deactivate
   ```
   Additionally, you can delete the virtualenv resources for `mypython` by removing the folder that got created.

## Technical documentation

First let's give an explanation of things considered in this implementation:

1. ### What constitutes a word

A word is, by default, an alphanumeric string that additionally can contain special symbols '-' and '_'.

If a word is made by other symbols, they will be split using the word delimiter configured.

This is essentially what Tokenizer class does: it holds as attributes:
- `_regex` that defines how to convert a word into a `token`,
- `_word_delimiter` that will be used to convert a multi-word string into multi tokens.

A RegexCatalog has been provided as a utility to have identified what `regex` can be used by Tokenizer.

In order to improve the user experience and make it easy to find words, searches are case-insensitive. So the token
returned by typing `hello` will be the same returned by typing `HeLlO`.

In the Scanner, the class that holds the input of query strings by the user, multiple words can be provided. It will be
the Tokenizer who will treat each of the words and *clean* them, so different words can become the same `token`.

A few examples of what will be return when Tokenizing different words:
- `hello` `hello?` `!hello` all will return the token `hello`
- `hello-worlD?` will return the token `hello-world`
- `"hello there" how are you? I'm great!` will return tokens  `hello` `there` `how` `are` `you` `i` `m` `great`


2. ### What constitutes two words being equal (and matching)

We consider two words when the string:
- is separated by the `_word_delimiter` property in Tokenizer, or
- includes a symbol out of `_regex` property in Tokenizer. For example, if using RegexCatalog.ALPHANUMERIC_EXTENDED, a
dot '.' will make the string be split in two: the string up to the dot '.', and the string after the dot '.'.

In the first case it is the desired behavior. You can set the word delimiter when creating a Tokenizer instance.

In the second case, it is meant to be greedy and try to find as many tokens as possible. An alternative could be to
just remove the unknown characters and join the words to become one `token`. So `hello?I'm here` would become tokens
`helloim` and `here`.

3. ### Data structure design: the in memory representation to search against

To build an efficient lookup system we should be aiming at having `O(1)` queries.

The current data structure, encapsulated in `Database` class, consists of a `dict[str, set[str]]`:
- A key is a `token`
- A value is a `set` of files containing that token

This representation enables fast lookup at the cost of memory. It is focused on the main usage of the script, which is
to query tokens and ranking results.

An alternative structure considered was to store this data in a Tree.
The downside of a Tree is it needs to be balanced to have O(log(N)) (N being the number of tokens).
This was a big concern, but the upside is it needs less memory than a dict.

Since both approaches focus on fast query access, it's hard to know what files are loaded in the Database.
If the objective was to build a system to know what tokens a file holds, a different approach should be used.

Current solution has as `keys` every token for a file. If we rather had as `keys` file names scanned, and their
`value` being a set of tokens that the file holds, a simple `keys()` would return all files loaded in the Database.

We'd have two major issues in that situation though:
- Unnecessary memory being used to hold repeated tokens across files
- Query response time to check what files hold a certain token would become O(N) being N number of files.

Hence, to keep the original desing for faster lookups, the `SimpleSearch` holds a `_database_list` that contains all
files loaded in the `_database` of tokens. This means the space cost increases, but will make it easier to convert
search results into a pandas Dataframe.

Check `get_search_hits_as_dataframe` [docstring in simple_search.py](src/simple_search.py#L101) for more
information on how the chosen data structure is converted to a pandas Dataframe.

4. ### Ranking score design

The code performs a simple count of words matched for each file, and it divides it by the number of tokens processed.

5. ### Testability

In `tests` folder there are provided a suite of tests to be run by `unittest` module.
Some static resources are kept in `tests/samples` that are related to the tests being run.

To run all the tests in it, from the root folder you can just run:
```shell
pwd # check you are in `[...]/SimpleSearch` path
python3 -m unittest -b  # use `-v` instead of `-b` for a more verbose output
```

## Improvement areas

Keeping the same goals of this project, some functionalities can be improved.

By goals, it's understood to improve the ranking system, the query lookup, or even the scalability, so it can analyse
higher volumes of data.
Nevertheless, recursively processing the `--path` was not part of the main functionality of this project.

### Tokenizer
1. Handle compound words like "I'm" (currently would become two tokens: `i` and `m`)
   
2. Handle multi-word strings to become one token. Would be great to be able to look up by just quoting every
word of the query string.
   
3. Handle binary operations. Start by adding 'AND', 'OR' support, and adding complex operations later: 'IN',
'BEGINS WITH', 'ENDS WITH'...

### Ranking score design
1. Convert a binary design (has/doesn't have the word) to a real count of hits. A file that has more than one time a
   word should have higher rank than a file that doesn't.
   
2. In addition to previous point, a feature to rank *word diversity* should be put in place. A file having only one
   word many times should have lower rank than one  having a lot of diverse words in it.
   
3. Give less score to very frequent words for a given vocabulary. In English "I" is a very used word, but in Spanish
   it is not.

### Data structure design

A simple improvement that can save some memory is to have a numeric representation of each file.

This way values in Dictionary would be a `set[int]` instead of a `set[str]`.

For example `_database_files` property in SimpleSearch could be a `dict[str, int]`, and the `_dictionary` property in
Database would be then a `dict[str, set[int]]`, so DictionaryValue would be an `int` in that case.

### Performance
Put a data structure design that enables "map", "group by" and "reduce" in Spark to perform both the lookup and ranking
the results. This way it will be able to process larger volumes of data much more efficiently than today.
