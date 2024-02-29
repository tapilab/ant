## Setup

1. Clone the repo
`git clone https://github.com/tapilab/ant.git`
2. Create and enter a virtual environment
```
virtualenv ant-v
source ant-v/bin/activate
```
3. Install requirements
```
cd ant
pip install -r requirements.txt
```

## Deploying locally

```
python manage.py migrate
python manage.py runserver 8089
```

This will run the server locally at port 8089 http://0.0.0.0:8089/

## Loading data

On first run, there will be no data. Go to the config page and enter the URL of a public-viewable Google Sheet in the ANT format. This will populate the database.

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


