#### About CatEatPad

#### how to Run CatEatPad
##### download mysql
- for this [this link](https://dev.mysql.com/doc/refman/8.0/en/macos-installation-pkg.html) to download mysql in mac
- add `export PATH="/usr/local/mysql-8.0.27-macos11-x86_64/bin/:$PATH"` in `~/.bashrc`
- run `mysql -u root -p` in terminal, create a database named "CatEatPad" by executing `CREATE DATABASE CatEatPad;`

##### run
- **run `. venv/bin/activate` first!!!**
- theoretically every library we need should be contained by `venv`, if you want to pip install something,  please remember to run `. venv/bin/activate` first
- modify `passwd` in `src/flaskr/db.py`  
```bash
cd src
bash start.sh
```

#### Flask
- [Learn Flask for Python(youtube)](https://www.youtube.com/watch?v=Z1RJmh_OqeA)
- 