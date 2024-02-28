from django.db import models
import gzip
import json


class EntityType(models.Model):
    name = models.CharField(max_length=255, null=False)
    title_field_name = models.CharField(max_length=255, null=False)
    image_field_name = models.CharField(max_length=255, null=True)
    color = models.CharField(max_length=255, null=True)
    start_date_field_name = models.CharField(max_length=255, null=True)
    end_date_field_name = models.CharField(max_length=255, null=True)


class Field(models.Model):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)    
    name = models.CharField(max_length=255)
    is_image_field = models.BooleanField(null=False, blank=False, default=False)
    is_title_field = models.BooleanField(null=False, blank=False, default=False)

class Value(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, blank=False, null=False)        
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)    
    # FIXME: all values are big strings for now!!
    value = models.CharField(max_length=2048, null=True)

class Entity(models.Model):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)
    key = models.CharField(max_length=255)
    name = models.CharField(max_length=255)    
    image_url = models.CharField(max_length=255, null=True)
    start_date = models.CharField(max_length=255, null=True)
    end_date = models.CharField(max_length=255, null=True)
    values = models.ManyToManyField(Value)

    def get_value(self, field_name):
        vs = self.get_values(field_name)
        if len(vs) > 0 and vs[0] is not None:
            return vs[0]
        else:
            return ''

    def get_values(self, field_name):
        return self.values.filter(field__name=field_name).values_list('value', flat=True)        

class RelationshipType(models.Model):
    source_entity_type = models.ForeignKey(EntityType, related_name='source_relationship_type_set', on_delete=models.CASCADE, blank=False, null=False)    
    target_entity_type = models.ForeignKey(EntityType, related_name='target_relationship_type_set', on_delete=models.CASCADE, blank=False, null=False)    
    name = models.CharField(max_length=255)
    symmetric = models.BooleanField(null=False, blank=False, default=False)

class Relationship(models.Model):
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE, blank=False, null=False)        
    source_entity = models.ForeignKey(Entity, related_name='source_relationship_set', on_delete=models.CASCADE, blank=False, null=False)    
    target_entity = models.ForeignKey(Entity, related_name='target_relationship_set', on_delete=models.CASCADE, blank=False, null=False)    


class Network(models.Model):
    compressed_json = models.BinaryField()

    def get_json(self):
        return json.loads(gzip.decompress(self.compressed_json))

