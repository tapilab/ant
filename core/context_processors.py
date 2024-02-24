"""
This add context variables that will be appended to each page load.
"""
from .models import EntityType
from urllib.parse import urlencode

def entity_options(request):
	return {'entity_options': EntityType.objects.all()}
	# print([urlencode(e.name) for e in EntityType.objects.all()])
	# return {'entity_options': [urlencode(e.name) for e in EntityType.objects.all()]}