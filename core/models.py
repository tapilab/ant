from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import gzip
import json

# class Tenant(models.Model):
#     name = models.TextField(null=False)
#     slug = models.SlugField(unique=True)  # Used in the URL to identify the tenant

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    security_question = models.CharField(max_length=200, blank=False)
    security_answer = models.CharField(max_length=200, blank=False)

    @receiver(post_save, sender=User)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
        instance.profile.save()


class UserEdits(models.Model):
    title = models.TextField(null=False)
    subtitle = models.TextField(null=True)
    contributors = models.TextField(null=True)
    logoURL = models.TextField(null=True)

    def __str__(self):
        return f"{self.title} - {self.subtitle} - {self.contributors}- {self.logoURL}"

class About(models.Model):
    blurb = models.TextField()

    def __str__(self):
        return self.blurb
    

class EntityType(models.Model):
    name = models.TextField(null=False)
    title_field_name = models.TextField(null=False)
    image_field_name = models.TextField(null=True)
    color = models.TextField(null=True)
    start_date_field_name = models.TextField(null=True)
    end_date_field_name = models.TextField(null=True)


class Field(models.Model):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)    
    name = models.TextField()
    is_image_field = models.BooleanField(null=False, blank=False, default=False)
    is_title_field = models.BooleanField(null=False, blank=False, default=False)

class Value(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, blank=False, null=False)        
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)    
    # FIXME: all values are big strings for now!!
    value = models.TextField(null=True)

class Entity(models.Model):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE, blank=False, null=False)
    key = models.TextField()
    name = models.TextField()    
    image_url = models.TextField(null=True)
    start_date = models.TextField(null=True)
    end_date = models.TextField(null=True)
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
    name = models.TextField()
    symmetric = models.BooleanField(null=False, blank=False, default=False)

class Relationship(models.Model):
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE, blank=False, null=False)        
    source_entity = models.ForeignKey(Entity, related_name='source_relationship_set', on_delete=models.CASCADE, blank=False, null=False)    
    target_entity = models.ForeignKey(Entity, related_name='target_relationship_set', on_delete=models.CASCADE, blank=False, null=False)    


class Location(models.Model):
    key = models.TextField()
    name = models.TextField()
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"



class GoogleSheet(models.Model):
    url = models.TextField()

class Network(models.Model):
    compressed_json = models.BinaryField()

    def get_json(self):
        return json.loads(gzip.decompress(self.compressed_json))

