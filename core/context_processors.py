"""
This add context variables that will be appended to each page load.
"""
from .models import EntityType

def entity_options(request):
	return {'entity_options': EntityType.objects.all()}