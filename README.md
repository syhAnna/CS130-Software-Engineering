#### About CatEatPad
#### TODOList
- show the display picture
- search function

#### how to Run CatEatPad
##### download mysql
- for this [this link](https://dev.mysql.com/doc/refman/8.0/en/macos-installation-pkg.html) to download mysql in mac
- add `export PATH="/usr/local/mysql-8.0.27-macos11-x86_64/bin/:$PATH"` in `~/.bashrc`
- run `mysql -u root -p` in terminal, create a database named "CatEatPad" by executing `CREATE DATABASE CatEatPad;`

##### run
- **run `. venv/bin/activate` first!!!**
- theoretically every library we need should be contained by `venv`, if you want to pip install something,  please remember to run `. venv/bin/activate` first
- add `dbConfig.json` under `src/flaskr/` 
```json
{
    "host": "127.0.0.1",
    "user": "root",
    "passwd": "YourPassWord",
    "database": "CatEatPad"
}
```
```bash
cd src
bash start.sh
```

#### how to generate docs
Before generating the docs, need to replace reading dbConfig from file in db.py with direct dictionary assignment.
```bash
cd src/docs
make clean
make html
```
Then, the doc is availble in `src/docs/buiild/html/index.html`.

#### Flask
- [Learn Flask for Python(youtube)](https://www.youtube.com/watch?v=Z1RJmh_OqeA)
- 

##### test
- run `pytest` in `src` to test. more more details, see [testing in Flask](https://flask.palletsprojects.com/en/2.0.x/testing/)

##### How to run on Windows:
- First, install the required packages as indicated before, using   `py -m pip install *`
- Then, use the cmd command:
```
set FLASK_ENV=development
set FLASK_DEBUG=1
set FLASK_APP=flaskr
py -m flask run
```
