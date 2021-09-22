`xelo2` is pure python, so it can be installed on every platform if you have the correct dependencies.
Make sure if you have at least python 3.6 installed.
Then you can install it, by typing:

```bash
git pull https://github.com/umcu-ribs/xelo2.git
pip install -e xelo2
```

## Dependencies

Required dependecies are:

* numpy
* scipy
* PyQt5 (including python3-pyqt5.qtsql)
* pandas
* wonambi

## Connect to database
To connect to a SQL database, you can do:

```bash
xelo2
```
and then log in with the prompt screen. Or you can pass the credentials directly (in plain text...):

```bash
xelo2 --mysql DATABASE_NAME -U USERNAME -P PASSWORD
```
