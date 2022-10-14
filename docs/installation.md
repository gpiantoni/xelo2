# INSTALLATION

`xelo2` consists of an SQL database (referred to as `xelo2db` in the documentation) and Python code (for the API, called `xelo2api` and `xelo2gui`).

## Database
To create `xelo2db`, the SQL database, you need MariaDB or MySQL (refer to the documentation of your server).
You then want to create a user by logging in as root/admin (`mysql -u root -p`):

```SQL
CREATE USER 'giovanni'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON testdb.* TO 'giovanni'@'localhost';
FLUSH PRIVILEGES;
```

> Careful: It creates a user without password `password` and the database is called `testdb`.

Then, as a user, use this code (in bash):

```bash
cd sql
./sql_create.sh giovanni testdb
```
where `giovanni` is the user you created above in `CREATE USER` and `testdb` is the name of the database.

This will create an empty database ready for running `xelo2api` and `xelo2gui` (the Python programs).

## Python Code

`xelo2api` and `xelo2gui` are both contained in the python package called `xelo2`.
`xelo2` is pure python, so it can be installed on every platform if you have the correct dependencies.
Make sure if you have at least python 3.6 installed.
Then you can install it, by typing:

```bash
git clone https://github.com/umcu-ribs/xelo2.git
cd xelo2
pip3 install –-user -e .
```

### Dependencies

Required dependecies are:

* numpy
* scipy
* PyQt5 (including python3-pyqt5.qtsql)
* pandas
* wonambi

## Get Started
To start using the database, see the [tutorials](tutorial.md).
