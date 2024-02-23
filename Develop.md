

## Jupyter notebooks

`heroku local notebook`

To configure the notebook to be able to access the Django models:

```
import sys
sys.path.append('../')  # Assuming your notebook is in the nbs/ folder, we add the ant root project to the path.
import django
django.setup()
```


## Migrations

Whenever you change the models, you'll need to migrate the database to reflect those changes.

- make migrations: `heroku local:run python manage.py makemigrations` : This will write `.py` files to `docketdashboard/migrations`
- migrate: `heroku local:run python manage.py migrate` : This will run those `.py` files to actually update the database.