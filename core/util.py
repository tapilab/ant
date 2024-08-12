from collections import defaultdict
from datetime import datetime
from dateutil import parser
from django.apps import apps
from .models import *
import json
import pandas as pd
import re
import traceback

def clear_db():
    # clear all tables in the database.
    for model in apps.get_models():
        if not model.__module__.startswith('django') and model.__qualname__ != 'UserProfile':
            # don't clear user tables.
            model.objects.all().delete()

class DB:
    # dummy class for in-memory db
    def __init__(self):
        pass


def get_about(sheets, warnings):
    about_df = get_sheet_by_name(sheets, 'About')
    abouts = None
    if about_df is not None and about_df.empty == False:
        abouts = About(blurb=about_df.iloc[0,0])
    else:
        abouts = About(blurb='') # if data frame is empty
    abouts.save()

def get_customizations(sheets, warnings):
    """
   Sets user customizations, ie Title, subtitle, etc
    """
    customization_df = get_sheet_by_name(sheets, 'Customizations')
    if customization_df is not None and customization_df.empty == False:
        e = customization_df.iloc[0]
        customizations = UserEdits(title=get_ignore_case(e, 'Title'),
                                   subtitle=get_ignore_case(e, 'Subtitle'),
                                   contributors=get_ignore_case(e, 'Contributors'),
                                   logoURL=get_ignore_case(e, 'Logo URL'))
        # customizations = UserEdits(title=customization_df.iloc[0,0], 
        #                            subtitle=customization_df.iloc[0,1], 
        #                            contributors=customization_df.iloc[0,2],
        #                            logoURL=customization_df.iloc[0,3])    
        customizations.save()

    
        

def validate_entity_type_columns(df):
    cols = [c.lower() for c in df.columns]
    required = ['Type', 'Title Field', 'Image Field', 'Color', 'Start Date Field', 'End Date Field']
    for r in required:
        if r.lower() not in cols:
            raise ValueError('missing %s column in Entity sheet' % r)

def get_ignore_case(row, field):
    if pd.isnull(field) or field.strip()=='':
        return None
    c = [i for i in row.index if i.lower().strip()==field.lower().strip()]
    if len(c) == 0 or c[0] not in row.index or pd.isnull(row[c[0]]):
        return None
    else:
        return str(row[c[0]]).strip()

def create_entity_types(sheets, warnings):
    entity_types_df = get_sheet_by_name(sheets, 'Entities')
    validate_entity_type_columns(entity_types_df)
    entity_types = {}
    for i, e in entity_types_df.iterrows():
        if not pd.isnull(e.Type):
            name = e.Type
            e = EntityType(name=name,
                           color=e.Color,
                           title_field_name=get_ignore_case(e, 'Title Field'),
                           image_field_name=get_ignore_case(e, 'Image Field'),
                           start_date_field_name=get_ignore_case(e, 'Start Date Field'),
                           end_date_field_name=get_ignore_case(e, 'End Date Field')
                           )
            e.save()
            entity_types[name] = e
    return entity_types
    
def create_relationship_types(sheets, db, warnings):
    relationship_types_df = get_sheet_by_name(sheets, 'Relationships')
    relationship_types = defaultdict(lambda: {})
    for i, r in relationship_types_df.iterrows():
        rt = RelationshipType(source_entity_type=db.entity_types[r['Entity 1']],
                             target_entity_type=db.entity_types[r['Entity 2']],
                             name=r['Name'])
        rt.save()
        relationship_types[r['Entity 1']][r.Name] = rt
    return relationship_types

def create_fields(sheets, db, warnings):
    # Add all Fields for each entity
    fields = defaultdict(lambda: {})
    for entity_type_name, entity_type in db.entity_types.items():
        sheet = sheets[entity_type_name]
        for c in sheet.columns:
            if (c in db.relationship_types[entity_type_name]
                or re.match(r'.*\.[0-9]+$', c)): 
                # skip relationship columns. for duplicate columns, pandas appends .1, .2 etc. 
                # We assume these are relationship columns for now.
                # warnings.append('       skipping relationship', c)
                continue
            field = Field(entity_type=entity_type,
                          name=c,
                          is_image_field=c==entity_type.image_field_name,
                          is_title_field=c==entity_type.title_field_name)
            field.save()        
            fields[entity_type_name][c] = field
    return fields




def iter_regular_fields(row, entity_type, db):
    # Iterate over fields that are not special (e.g., key, image_field, etc.)
    for col, val in row.to_dict().items():
        if not (col in db.relationship_types[entity_type.name] or 
                re.match(r'.*\.[0-9]+$', col) or
                col.lower() == 'key' or
                (not pd.isnull(entity_type.image_field_name) and col.lower() == entity_type.image_field_name.lower()) or
                (not pd.isnull(entity_type.title_field_name) and col.lower() == entity_type.title_field_name.lower()) or
                (not pd.isnull(entity_type.start_date_field_name) and col.lower().strip() == entity_type.start_date_field_name.lower().strip()) or
                (not pd.isnull(entity_type.end_date_field_name) and col.lower().strip() == entity_type.end_date_field_name.lower().strip())
                ): 
            yield (col, val)
#  get_ignore_case(col, entity_type.end_date_field_name))
def parse_datetime(value):
    if value is None or pd.isnull(value):
        return None
    # if looks like a year
    if len(value)==4:
        # pd.to_datetime(value, format='%Y') # pandas doesn't recognize years prior to 1677?!?!
        return datetime.strptime(value, "%Y")
    # otherwise, guess
    else:
        return parser.parse(value)


def check_col_ignore_case(col_name, cols):
    for c in cols:
        if col_name is not None and col_name.lower() == c.lower():
            return True
    return False

def check_entity_columns(sheet, entity_type):
    cols = sheet.columns
    # for c in [entity_type.title_field_name, entity_type.image_field_name, entity_type.start_date_field_name, entity_type.end_date_field_name]:
    for c in [entity_type.title_field_name]: # , entity_type.image_field_name, entity_type.start_date_field_name, entity_type.end_date_field_name]:
        if not check_col_ignore_case(c, cols):
            return "cannot find column %s in %s. columns are %s" % (c, entity_type.name, str(cols))
    return None

def create_entities(sheets, db, warnings):
    entities = defaultdict(lambda: {})
    for entity_type_name in db.entity_types:
        sheet = sheets[entity_type_name]    
        entity_type = db.entity_types[entity_type_name]
        # check that required columns exist:
        result = check_entity_columns(sheet, entity_type)
        if result is not None:
            # return False, result
            raise ValueError('Missing columns for %s: %s' % (entity_type_name, result))
        for ri, row in sheet.iterrows():
            key = get_ignore_case(row, 'key')
            if pd.isnull(key):
                # raise ValueError('In sheet %s, cannot find Key field for row %s' % (entity_type_name, str(row)))
                warnings.append('In sheet %s, cannot find Key field for row %d' % (entity_type_name,ri+2))
                continue
            name = get_ignore_case(row, entity_type.title_field_name)
            if pd.isnull(name):
                name = key # default to key for name
                warnings.append('In sheet %s, cannot find Title Field %s for row %d (%s). Defaulting to Key' % (entity_type_name, entity_type.title_field_name, ri+2, row.Key))
            values = []
            for col, val in iter_regular_fields(row, entity_type, db):
                if not pd.isnull(val):
                    v = Value(field=db.fields[entity_type_name][col], 
                              entity_type=entity_type,
                              value=str(val) if not pd.isnull(val) else None)
                    v.save()
                    values.append(v)
            entity = Entity(entity_type=entity_type, 
                            key=key,
                            name=name,
                            image_url=get_ignore_case(row, entity_type.image_field_name),
                            start_date=get_ignore_case(row, entity_type.start_date_field_name),
                            end_date=get_ignore_case(row, entity_type.end_date_field_name)
                            )
            entity.save()
            entity.values.set(values)
            entity.save()
            entities[entity_type_name][key.lower()] = entity    
    return entities

def create_relationships(sheets, db, warnings):
    relationships = defaultdict(lambda: [])
    for entity_type_name in db.entity_types:
        sheet = sheets[entity_type_name]    
        for ri, row in sheet.iterrows():
            keyval = get_ignore_case(row, 'key')
            if keyval is not None:
                for col, val in row.to_dict().items():     
                    if pd.isnull(val): # nothing to add
                        continue
                    # drop any added .1, .2 etc string added for duplicate rows
                    col = re.sub(r'\.[0-9]+$', '', col)
                    if col in db.relationship_types[entity_type_name]:
                        try:
                            relationship_type = db.relationship_types[entity_type_name][col]
                            entity1 = db.entities[entity_type_name][row.Key.lower()]
                            entity2_type = relationship_type.target_entity_type.name.strip()
                            entity2 = db.entities[entity2_type][val.lower()]
                            r = Relationship(relationship_type=relationship_type,
                                             source_entity=entity1,
                                             target_entity=entity2).save()    
                            relationships[col] = r
                        except Exception as e:
                            warnings.append('Cannot add relationship for %s from row %d (%s)\n%s' % (entity_type_name, ri, row.Key, str(e)))
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

def node2jsonid(n):
    return n.entity_type.name + '__' + n.key

def none2str(v):
    if v is None:
        return ''
    else:
        return v

def db2json():
    nodes = []
    for e in Entity.objects.all():
        nodes.append({
            'id': node2jsonid(e),#e.entity_type.name + '__' + e.key,#e.pk,
            'key': e.key,
            'name': e.name,
            'entity_type': e.entity_type.name,
            'color': none2str(e.entity_type.color),
            'image_url': none2str(e.image_url),
            'start_date': none2str(e.start_date),
            'end_date': none2str(e.end_date),
        })
    links = []
    for r in Relationship.objects.all():
        links.append({
            'source': node2jsonid(r.source_entity),
            'target': node2jsonid(r.target_entity),#r.target_entity.pk,
            'relationship_type': r.relationship_type.name,
            'value': 1
        })
    return json.dumps({'nodes': nodes, 'links': links}).encode('utf-8')


def import_from_google_sheet(url):
    """
    Import all data from the google sheet at the provided url.
    """
    print('importing data from google sheet')
    clear_db()
    try:
        sheets = pd.read_excel(id2export_url(url2doc_id(url)), sheet_name=None, dtype=str)
        # remove all leading/trailing spaces everywhere.
        for s, df in sheets.items():
            sheets[s] = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    except Exception as e:
        return False, "Cannot find a sheet at that URL. Please navigate to the page of the Google sheet and copy the URL in your browser's address bar.\n" + str(traceback.format_exc())
    
    try:      
        warnings = []
        db = DB()
        db.entity_types = create_entity_types(sheets, warnings)
        db.relationship_types = create_relationship_types(sheets, db, warnings)
        # db.relationship_types
        db.fields = create_fields(sheets, db, warnings)
        db.entities = create_entities(sheets, db, warnings)
        db.relationships = create_relationships(sheets, db, warnings)
        print('entities')

        get_customizations(sheets, warnings)
        get_about(sheets, warnings)
        Network(compressed_json=gzip.compress(db2json())).save()
        return True, "Success! " + '<br>Warnings:<br>>>>' + '<br>>>> '.join(warnings) if len(warnings) > 0 else ''
    except Exception as e:
        return False, str(e) + '\n' + str(traceback.format_exc())
