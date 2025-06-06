from collections import defaultdict
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import django_rq

import time
from .forms import ConfigForm, SetEmailAndPasswordForm, UserResetForm
from .models import *
from .tasks import import_data
from .util import import_from_google_sheet


def register(request):
    if User.objects.exists():
        return HttpResponse("Registration not allowed. A user already exists.", status=403)

    if request.method == 'POST':
        form = SetEmailAndPasswordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('config')  # Redirect to a login page, for example
    else:
        form = SetEmailAndPasswordForm()
    return render(request, 'register.html', {'form': form})

def user_reset(request):
    error_msg = ''
    if request.method == 'POST':
        form = UserResetForm(request.POST)
        if form.is_valid():            
            # check that security answer matches
            if form.cleaned_data['answer'] == UserProfile.objects.first().security_answer.lower():
                User.objects.all().delete()
                UserProfile.objects.all().delete()
                return redirect('register')
            else:
                error_msg = 'invalid answer'
    else:
        form = UserResetForm()
    return render(request, 'reset_user.html', {
        'form': form, 
        'error_msg': error_msg,
        'security_question': UserProfile.objects.first().security_question if UserProfile.objects.count() > 0 else ''})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('config')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def about(request):
    try:
        about = About.objects.latest('id')
    except About.DoesNotExist:
        about = None
    return render(request, 'about.html', {'about': about})

def get_customizations():
    try:
        customizations = UserEdits.objects.latest('id')  # Retrieve the latest UserEdits object from the database
    except UserEdits.DoesNotExist:
        customizations = UserEdits(title="ANT", 
                   subtitle="Artistic Network Toolkit", 
                   contributors=None,
                   logoURL="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Raphael_-_Fire_in_the_Borgo.jpg/639px-Raphael_-_Fire_in_the_Borgo.jpg")
        customizations.save()
    return customizations

def get_sheet_url():
    try:
        sheet_url = GoogleSheet.objects.latest('id')  # Retrieve the latest GoogleSheet object from the database
    except GoogleSheet.DoesNotExist as e:
        sheet_url, _ = GoogleSheet.objects.update_or_create(id=1, defaults={'url': 'https://docs.google.com/spreadsheets/'})
        sheet_url.save()
    return sheet_url.url

def index(request):  
    customizations = get_customizations()
    context = {
        'customizations': customizations,  # Pass customizations object to the template context
        'sheet_url': get_sheet_url(),
    }  
    return render(request, 'index.html', context)

def check_job_status(request, job_id):
    queue = django_rq.get_queue('default')
    job = queue.fetch_job(job_id)
    if job is None:
        return JsonResponse({'status': 'No such job.', 'result': ''})
    return JsonResponse({'status': job.get_status(), 'result': job.result})

def foo():
    pass


def config(request):
    # if request.user.is_authenticated:
    if True:
        if request.method == 'POST':
            config_form = ConfigForm(request.POST)
            if config_form.is_valid():
                url = config_form.cleaned_data['google_sheet_url']
                queue = django_rq.get_queue('default')
                # strange bug where only second job was run. tmpfix: adding dummy job.
                job = queue.enqueue(foo)
                job = queue.enqueue(import_from_google_sheet, url)
                return render(request, 'config.html', {'job_id': job.id, 'config_form': config_form, 'customizations': get_customizations()})                
        else:
            config_form = ConfigForm()
            return render(request, 'config.html', {'config_form': config_form, 'job_id': None, 'customizations': get_customizations()})
    elif not User.objects.exists():
        return redirect('register')
    else:
        return redirect('user_login')


def entities(request):
    entity_type = request.GET.get('type', '')  # Default to '' if 'name' is not provided

    return render(request, 'entities.html', {
                  'entity_type': entity_type,
                  'entities': Entity.objects.filter(entity_type__name=entity_type),
                  'customizations': get_customizations(),
                  }) 

def entity(request):
    entity_type = request.GET.get('type', '')
    key = request.GET.get('key', '')
    entity = Entity.objects.filter(key=key).prefetch_related('values').first()
    # FIXME: could have a name clash if a field name matches a variable already in this object (e.g., if there's a field name "values")
    for v in entity.values.all():
        if v.field.name == 'Image URL': # FIXME: generalize
            entity.image_url = v.value
        elif v.field.name.lower() in ['notes', 'note']:
            entity.notes = v.value
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
                     'images': entity.image_urls,
                     'relationships': relationships,
                     'customizations': get_customizations()}) 

def network(request):
    obj = Network.objects.first()
    return render(request, 'network.html',
        {'network_json': obj.get_json() if obj else '{}',
         'customizations': get_customizations()})
