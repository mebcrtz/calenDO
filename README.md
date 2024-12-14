# CS ELECTIVE 3 Web Development (calenDO)


> [!NOTE]
> Do this on your terminal (command prompt).
### How to setup:
- Go to your Project Folder, type `cmd` here.
![image](/tuts/file_explorer.png)

- Create Virtual Environment
  > type `python -m venv venv`
- Activate Environment
  > type `venv\Scripts\activate`
- Change directory to your project Folder
  > type `cd project`
- Install Dependencies,
  > type `pip install -r requirements.txt` 
          > (if error ERROR: Could not install packages due to an OSError: [WinError 2] )
          > type `pip install --user -r requirements.txt`
- Open project in code editor
  > type `code .` in command prompt

- Create superuser
  > type `python manage.py createsuperuser` in vscdoe terminal

> [!NOTE]
> Go back to your terminal (command prompt).
- Run Migrations
  > type `python manage.py makemigrations`
  > then `python manage.py migrate`
- Run Server
  > type `python manage.py runserver`
- Open the URL `http://127.0.0.1:8000/`


