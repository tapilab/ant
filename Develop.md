## Deploying locally

`python manage.py runserver 8089`

This will run the server locally at port 8089 http://0.0.0.0:8089/


## Migrations

Whenever you change the models, you'll need to migrate the database to reflect those changes.

- make migrations: `heroku local:run python manage.py makemigrations` : This will write `.py` files to `docketdashboard/migrations`
- migrate: `heroku local:run python manage.py migrate` : This will run those `.py` files to actually update the database.



## Jupyter notebooks

`heroku local notebook`

To configure the notebook to be able to access the Django models:

```
import sys
sys.path.append('../')  # Assuming your notebook is in the nbs/ folder, we add the ant root project to the path.
import django
django.setup()
```


