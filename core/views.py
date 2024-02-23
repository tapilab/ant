from django.shortcuts import render

from .forms import ConfigForm
from .models import *
from .util import import_from_google_sheet

# Create your views here.


def index(request):
    return render(request, "index.html")


def db(request):
    # If you encounter errors visiting the `/db/` page on the example app, check that:
    #
    # When running the app on Heroku:
    #   1. You have added the Postgres database to your app.
    #   2. You have uncommented the `psycopg` dependency in `requirements.txt`, and the `release`
    #      process entry in `Procfile`, git committed your changes and re-deployed the app.
    #
    # When running the app locally:
    #   1. You have run `./manage.py migrate` to create the `hello_greeting` database table.

    # greeting = Greeting()
    # greeting.save()

    # greetings = Greeting.objects.all()
    entity_types = EntityType.objects.all()
    relationship_types = RelationshipType.objects.all()
    entities = Entity.objects.all()
    return render(request, "db.html",
        {"entity_types": entity_types, 
         "relationship_types": relationship_types,
         "entities": entities})
    # return render(request, "db.html", {"greetings": greetings})

def config(request):
    if request.method == 'POST':
        config_form = ConfigForm(request.POST)
        if config_form.is_valid():
            # Here, you can process the form data
            # For now, we'll just redirect to the same page as a simple example
            url = config_form.cleaned_data['google_sheet_url']
            success, message = import_from_google_sheet(url)
            return render(request, 'config.html',
                {'config_form': config_form, 'success': success, 'message': message})
    else:
        config_form = ConfigForm()
    return render(request, 'config.html', {'config_form': config_form})