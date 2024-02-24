from collections import defaultdict
from django.apps import apps
from .models import *
import pandas as pd
import re

def clear_db():
    # clear all tables in the database.
    for model in apps.get_models():
        model.objects.all().delete()

class DB:
    # dummy class for in-memory db
    def __init__(self):
        pass

def create_entity_types(sheets):
    entity_types_df = get_sheet_by_name(sheets, 'Entities')
    entity_types = {}
    for i, e in entity_types_df.iterrows():
        name = e.Type
        e = EntityType(name=name)
        e.save()
        entity_types[name] = e
        print('Added Entity Type', name)
    return entity_types
    
def create_relationship_types(sheets, db):
    relationship_types_df = get_sheet_by_name(sheets, 'Relationships')
    relationship_types = defaultdict(lambda: {})
    for i, r in relationship_types_df.iterrows():
        print(r)
        rt = RelationshipType(source_entity_type=db.entity_types[r['Entity 1']],
                             target_entity_type=db.entity_types[r['Entity 2']],
                             name=r['Name'])
        rt.save()
        relationship_types[r['Entity 1']][r.Name] = rt
        print('Added Relationship Type', r['Entity 1'], r.Name)
    return relationship_types

def create_fields(sheets, db):
    # Add all Fields for each entity
    fields = defaultdict(lambda: {})
    for entity_type_name, entity_type in db.entity_types.items():
        sheet = sheets[entity_type_name]
        print('Adding Fields for entity', entity_type_name)
        for c in sheet.columns:
            print('  Field', c)
            if (c in db.relationship_types[entity_type_name] or 
                re.match(r'.*\.[0-9]+$', c)): 
                # skip relationship columns. for duplicate columns, pandas appends .1, .2 etc. 
                # We assume these are relationship columns for now.
                print('       skipping relationship', c)
                continue
            field = Field(entity_type=entity_type,
                          name=c,
                          is_image_field=c==entity_type.image_field_name,
                          is_title_field=c==entity_type.title_field_name)
            field.save()        
            fields[entity_type_name][c] = field
    return fields

def create_entities(sheets, db):
    entities = defaultdict(lambda: {})
    for entity_type_name in db.entity_types:
        sheet = sheets[entity_type_name]    
        entity_type = db.entity_types[entity_type_name]
        for _, row in sheet.iterrows():
            key = None
            values = []
            for col, val in row.to_dict().items():
                if (col in db.relationship_types[entity_type_name] or 
                    re.match(r'.*\.[0-9]+$', col) or col.lower()=='name'): 
                    continue
                v = Value(field=db.fields[entity_type_name][col], 
                          entity_type=entity_type,
                          value=str(val))
                v.save()
                values.append(v)
                if col.strip().lower() == 'key':
                    key = str(val)
            entity = Entity(entity_type=entity_type, key=key, name=row['Name'])
            entity.save()
            entity.values.set(values)
            entity.save()
            entities[entity_type_name][key] = entity    
    return entities

def create_relationships(sheets, db):
    relationships = defaultdict(lambda: [])
    for entity_type_name in db.entity_types:
        sheet = sheets[entity_type_name]    
        for _, row in sheet.iterrows():
            for col, val in row.to_dict().items():     
                if pd.isnull(val): # nothing to add
                    continue
                # drop any added .1, .2 etc string added for duplicate rows
                col = re.sub(r'\.[0-9]+$', '', col)
                if col in db.relationship_types[entity_type_name]:
                    relationship_type = db.relationship_types[entity_type_name][col]
                    entity1 = db.entities[entity_type_name][row.Key]
                    entity2_type = relationship_type.target_entity_type.name
                    print(col, relationship_type.name, entity1.key, entity2_type, val)
                    entity2 = db.entities[entity2_type][val]
                    r = Relationship(relationship_type=relationship_type,
                                     source_entity=entity1,
                                     target_entity=entity2).save()    
                    relationships[col] = r
    return relationships
    


def url2doc_id(u):
    """
    Given a URL to a google sheet, return the id. E.g.:
    https://docs.google.com/spreadsheets/d/xxxx/edit#gid=0
    returns xxxx
    """
    r = re.findall(r'\/d\/(.+?)\/', u)
    if len(r) == 0:
        return None
    else:
        return r[0]

def id2export_url(id_):
    """
    Given a google sheet id, return a url that exports the .xlsx version of the sheet.
    """
    return 'https://docs.google.com/spreadsheets/d/%s/export?format=xlsx&id=%s' % (id_, id_)

def get_sheet_by_name(sheets, name):
    """
    Return a sheet DataFrame with the given name, ignoring case.
    sheets...dict from sheet name -> DataFrame
    name.....string for sheet name to return
    """ 
    for sheet_name, sheet in sheets.items():
        if sheet_name.lower() == name.lower():            
            return sheet
    return None

def import_from_google_sheet(url):
    """
    Import all data from the google sheet at the provided url.
    """
    clear_db()
    try:
        sheets = pd.read_excel(id2export_url(url2doc_id(url)), sheet_name=None)
    except:
        return False, "Cannot find a sheet at that URL. Please navigate to the page of the Google sheet and copy the URL in your browser's address bar."
    db = DB()
    db.entity_types = create_entity_types(sheets)
    db.relationship_types = create_relationship_types(sheets, db)
    # db.relationship_types
    db.fields = create_fields(sheets, db)
    db.entities = create_entities(sheets, db)
    db.relationships = create_relationships(sheets, db)
    print('entities')
    # for etype in db.entities:
    #     print(etype, 'entities')
    #     for e in db.entities[etype]:
    #         print(e.key)
    #         for v in e.values:
    #             print(v.field.name, v.field.value)
    # print(db.entities)
    # print('relationships')
    # print(db.relationships)
    return True, "Success!"





