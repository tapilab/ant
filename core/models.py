from django.db import models



class EntityType(models.Model):
    name = models.CharField(max_length=255)
    image_field_name = models.CharField(max_length=255, null=True)
    title_field_name = models.CharField(max_length=255, null=True)

class Field(models.Model):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)    
    name = models.CharField(max_length=255)
    is_image_field = models.BooleanField(null=False, blank=False, default=False)
    is_title_field = models.BooleanField(null=False, blank=False, default=False)

class Value(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, blank=False, null=False)        
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)    
    # FIXME: all values are big strings for now!!
    value = models.CharField(max_length=2048)

class Entity(models.Model):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=255)    
    key = models.CharField(max_length=255)
    values = models.ManyToManyField(Value)

class RelationshipType(models.Model):
    source_entity_type = models.ForeignKey(EntityType, related_name='source_relationship_type_set', on_delete=models.CASCADE, blank=False, null=False)    
    target_entity_type = models.ForeignKey(EntityType, related_name='target_relationship_type_set', on_delete=models.CASCADE, blank=False, null=False)    
    name = models.CharField(max_length=255)
    symmetric = models.BooleanField(null=False, blank=False, default=False)

class Relationship(models.Model):
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE, blank=False, null=False)        
    source_entity = models.ForeignKey(Entity, related_name='source_relationship_set', on_delete=models.CASCADE, blank=False, null=False)    
    target_entity = models.ForeignKey(Entity, related_name='target_relationship_set', on_delete=models.CASCADE, blank=False, null=False)    
