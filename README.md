# README #

## Overview ##

This is a tool that downloads twitter user information and tweets to a SQLite
database.

## Installation ##

You need to have Python (it was developed with 3.x, but it should run on 2.x
too), pip and virutalenv installed. You can follow this
blog post [(osx)](http://hackercodex.com/guide/python-development-environment-on-mac-osx/),
[(windows)](http://www.tylerbutler.com/2012/05/how-to-install-python-pip-and-virtualenv-on-windows-with-powershell/).

When you're ready with the requirements, go to the the repository root and
create a new virtualenv:

```bash
virtualenv env/ -p /usr/local/bin/python3
```

`/usr/local/bin/python3` is the path to your python 3 executable. It should
be this one if you followed the instructions from the blog post.

When you have created your virutalenv, you have to activate it. This is done
by running:

```bash
source env/bin/activate
```

You will notice that you will have `(env)` in front of your prompt. This means
the virutalenv is activated successfully. You need to do this every time you
need to install/run something related to the script.

Then you need to install packages dependencies:

```bash
pip install -r requirements.txt
```

## Configuring ##

Copy `config.py.example` to `config.py` and fill in application keys. You can
obtain them from [here](https://apps.twitter.com/).

## Running ##

It requires a CSV file with 2 columns and a header. Example:

```csv
source,user
source1,twitter_user1
source2,twitter_user2
source3,twitter_user3
```

Make sure you've activated your virtualenv (you will see `(env)` in front of
you command prompt) and then run:

```bash
python twitter-digger.py path-to-csv-file.csv
```
