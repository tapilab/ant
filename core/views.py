from django.shortcuts import render
from collections import defaultdict

from .forms import ConfigForm
from .models import *
from .util import import_from_google_sheet


#def index(request):
    #return render(request, "index.html")

def about(request):
    try:
        about = About.objects.latest('id')

    except About.DoesNotExist:
        about = None
    print('About:', about)   
    context = {
        'about': about, 
               }
    return render(request, 'about.html', context)

def index(request):  
    try:
        customizations = UserEdits.objects.latest('id')  # Retrieve the latest UserEdits object from the database
    except UserEdits.DoesNotExist:
        customizations = None

    context = {
        'customizations': customizations,  # Pass customizations object to the template context
    }  
    return render(request, 'index.html', context)


def db(request):
    # If you encounter errors visiting the `/db/` page on the example app, check that:
    #
    # When running the app on Heroku:
    #   1. You have added the Postgres database to your app.
    #   2. You have uncommented the `psycopg` dependency in `requirements.txt`, and the `release`
    #      process entry in `Procfile`, git committed your changes and re-deployed the app.
    #
    # When running the app locally:
    #   1. You have run `./manage.py migrate` to create the database tables.

    entity_types = EntityType.objects.all()
    relationship_types = RelationshipType.objects.all()
    entities = Entity.objects.all().prefetch_related('values')
    return render(request, "db.html",
        {"entity_types": entity_types, 
         "relationship_types": relationship_types,
         "entities": entities,
         "values": Value.objects.all()})
    # return render(request, "db.html", {"greetings": greetings})

def config(request):
    if request.method == 'POST':
        config_form = ConfigForm(request.POST)
        if config_form.is_valid():
            url = config_form.cleaned_data['google_sheet_url']
            success, message = import_from_google_sheet(url)
            return render(request, 'config.html',
                {'config_form': config_form, 'success': success, 'message': message})
    else:
        config_form = ConfigForm()
    return render(request, 'config.html', {'config_form': config_form})


def entities(request):
    entity_type = request.GET.get('type', '')  # Default to '' if 'name' is not provided

    return render(request, 'entities.html', {'entity_type': entity_type,
                  'entities': Entity.objects.filter(entity_type__name=entity_type)}) 

def entity(request):
    entity_type = request.GET.get('type', '')
    key = request.GET.get('key', '')
    entity = Entity.objects.filter(key=key).prefetch_related('values').first()
    # FIXME: could have a name clash if a field name matches a variable already in this object (e.g., if there's a field name "values")
    for v in entity.values.all():
        if v.field.name == 'Image URL': # FIXME: generalize
            entity.image_url = v.value
        else:
            setattr(entity, v.field.name, v.value)

    # get all related entities.
    relationships = []
    rel_types = RelationshipType.objects.filter(source_entity_type__name=entity_type)#.values_list('name', flat=True)
    for rel_type in rel_types:
        relationships.append((rel_type.name + " " + rel_type.target_entity_type.name, 
            [{'name': r.target_entity.name,
              'key': r.target_entity.key,
              'entity_type': r.target_entity.entity_type}
              for r in 
                    Relationship.objects.filter(source_entity=entity, relationship_type=rel_type)]))
    # get reverse relationships
    rel_types = RelationshipType.objects.filter(target_entity_type__name=entity_type)#.values_list('name', flat=True)
    for rel_type in rel_types:    
        relationships.append((rel_type.source_entity_type.name + " " + rel_type.name + " " + entity.name,
            [{'name': r.source_entity.name,
              'key': r.source_entity.key,
              'entity_type': r.source_entity.entity_type}
              for r in 
                    Relationship.objects.filter(target_entity=entity, relationship_type=rel_type)]))

    return render(request, 'entity.html',
                    {'entity_type': entity_type,
                     'entity': entity,
                     'relationships': relationships}) 

def network(request):
    return render(request, 'network.html',
        {'network_json': Network.objects.first().get_json()})
