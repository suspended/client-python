# coding: utf-8

import json

from pycti.utils.constants import CustomProperties


class IntrusionSet:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            stix_id_key
            stix_label
            entity_type
            parent_types
            name
            alias
            description
            graph_data
            first_seen
            last_seen
            goal
            sophistication
            resource_level
            primary_motivation
            secondary_motivation
            created
            modified
            created_at
            updated_at
            createdByRef {
                node {
                    id
                    entity_type
                    stix_id_key
                    stix_label
                    name
                    alias
                    description
                    created
                    modified
                }
                relation {
                    id
                }
            }            
            markingDefinitions {
                edges {
                    node {
                        id
                        entity_type
                        stix_id_key
                        definition_type
                        definition
                        level
                        color
                        created
                        modified
                    }
                    relation {
                        id
                    }
                }
            }
            tags {
                edges {
                    node {
                        id
                        tag_type
                        value
                        color
                    }
                    relation {
                        id
                    }
                }
            }            
        """

    """
        List Intrusion-Set objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Intrusion-Set objects
    """

    def list(self, **kwargs):
        filters = kwargs.get('filters', None)
        search = kwargs.get('search', None)
        first = kwargs.get('first', 500)
        after = kwargs.get('after', None)
        order_by = kwargs.get('orderBy', None)
        order_mode = kwargs.get('orderMode', None)
        self.opencti.log('info', 'Listing Intrusion-Sets with filters ' + json.dumps(filters) + '.')
        query = """
            query IntrusionSets($filters: [IntrusionSetsFiltering], $search: String, $first: Int, $after: ID, $orderBy: IntrusionSetsOrdering, $orderMode: OrderingMode) {
                intrusionSets(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                    edges {
                        node {
                            """ + self.properties + """
                        }
                    }
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                        hasPreviousPage
                        globalCount
                    }
                }
            }
        """
        result = self.opencti.query(query, {
            'filters': filters,
            'search': search,
            'first': first,
            'after': after,
            'orderBy': order_by,
            'orderMode': order_mode
        })
        return self.opencti.process_multiple(result['data']['intrusionSets'])

    """
        Read a Intrusion-Set object
        
        :param id: the id of the Intrusion-Set
        :param filters: the filters to apply if no id provided
        :return Intrusion-Set object
    """

    def read(self, **kwargs):
        id = kwargs.get('id', None)
        filters = kwargs.get('filters', None)
        if id is not None:
            self.opencti.log('info', 'Reading Intrusion-Set {' + id + '}.')
            query = """
                query IntrusionSet($id: String!) {
                    intrusionSet(id: $id) {
                        """ + self.properties + """
                    }
                }
             """
            result = self.opencti.query(query, {'id': id})
            return self.opencti.process_multiple_fields(result['data']['intrusionSet'])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log('error', 'Missing parameters: id or filters')
            return None

    """
        Create a Intrusion-Set object

        :param name: the name of the Intrusion Set
        :return Intrusion-Set object
    """

    def create_raw(self, **kwargs):
        name = kwargs.get('name', None)
        description = kwargs.get('description', None)
        alias = kwargs.get('alias', None)
        first_seen = kwargs.get('first_seen', None)
        last_seen = kwargs.get('last_seen', None)
        goal = kwargs.get('goal', None)
        sophistication = kwargs.get('sophistication', None)
        resource_level = kwargs.get('resource_level', None)
        primary_motivation = kwargs.get('primary_motivation', None)
        secondary_motivation = kwargs.get('secondary_motivation', None)
        id = kwargs.get('id', None)
        stix_id_key = kwargs.get('stix_id_key', None)
        created = kwargs.get('created', None)
        modified = kwargs.get('modified', None)

        if name is not None and description is not None:
            self.opencti.log('info', 'Creating Intrusion-Set {' + name + '}.')
            query = """
                mutation IntrusionSetAdd($input: IntrusionSetAddInput) {
                    intrusionSetAdd(input: $input) {
                        """ + self.properties + """
                    }
                }
            """
            result = self.opencti.query(query, {
                'input': {
                    'name': name,
                    'description': description,
                    'alias': alias,
                    'first_seen': first_seen,
                    'last_seen': last_seen,
                    'goal': goal,
                    'sophistication': sophistication,
                    'resource_level': resource_level,
                    'primary_motivation': primary_motivation,
                    'secondary_motivation': secondary_motivation,
                    'internal_id_key': id,
                    'stix_id_key': stix_id_key,
                    'created': created,
                    'modified': modified
                }
            })
            return self.opencti.process_multiple_fields(result['data']['intrusionSetAdd'])
        else:
            self.opencti.log('error', 'Missing parameters: name and description')

    """
        Create a Intrusion-Set object only if it not exists, update it on request

        :param name: the name of the Intrusion Set
        :return Intrusion-Set object
    """

    def create(self, **kwargs):
        name = kwargs.get('name', None)
        description = kwargs.get('description', None)
        alias = kwargs.get('alias', None)
        first_seen = kwargs.get('first_seen', None)
        last_seen = kwargs.get('last_seen', None)
        goal = kwargs.get('goal', None)
        sophistication = kwargs.get('sophistication', None)
        resource_level = kwargs.get('resource_level', None)
        primary_motivation = kwargs.get('primary_motivation', None)
        secondary_motivation = kwargs.get('secondary_motivation', None)
        id = kwargs.get('id', None)
        stix_id_key = kwargs.get('stix_id_key', None)
        created = kwargs.get('created', None)
        modified = kwargs.get('modified', None)
        update = kwargs.get('update', False)

        object_result = self.opencti.stix_domain_entity.get_by_stix_id_or_name(
            types=['Intrusion-Set'],
            stix_id_key=stix_id_key,
            name=name
        )
        if object_result is not None:
            if update:
                self.opencti.stix_domain_entity.update_field(id=object_result['id'], key='name', value=name)
                object_result['name'] = name
                self.opencti.stix_domain_entity.update_field(
                    id=object_result['id'],
                    key='description',
                    value=description
                )
                object_result['description'] = description
                if alias is not None:
                    if 'alias' in object_result:
                        new_aliases = object_result['alias'] + list(set(alias) - set(object_result['alias']))
                    else:
                        new_aliases = alias
                    self.opencti.stix_domain_entity.update_field(id=object_result['id'], key='alias', value=new_aliases)
                    object_result['alias'] = new_aliases
                if first_seen is not None:
                    self.opencti.stix_domain_entity.update_field(
                        id=object_result['id'],
                        key='first_seen',
                        value=first_seen
                    )
                    object_result['first_seen'] = first_seen
                if last_seen is not None:
                    self.opencti.stix_domain_entity.update_field(
                        id=object_result['id'],
                        key='last_seen',
                        value=last_seen
                    )
                    object_result['last_seen'] = last_seen
                if goal is not None:
                    self.opencti.stix_domain_entity.update_field(
                        id=object_result['id'],
                        key='goal',
                        value=goal
                    )
                    object_result['goal'] = goal
            return object_result
        else:
            return self.create_raw(
                name=name,
                description=description,
                alias=alias,
                first_seen=first_seen,
                last_seen=last_seen,
                goal=goal,
                sophistication=sophistication,
                resource_level=resource_level,
                primary_motivation=primary_motivation,
                secondary_motivation=secondary_motivation,
                id=id,
                stix_id_key=stix_id_key,
                created=created,
                modified=modified
            )

    """
        Export an Intrusion-Set object in STIX2
    
        :param id: the id of the Intrusion-Set
        :return Intrusion-Set object
    """

    def to_stix2(self, **kwargs):
        id = kwargs.get('id', None)
        mode = kwargs.get('mode', 'simple')
        max_marking_definition_entity = kwargs.get('max_marking_definition_entity', None)
        entity = kwargs.get('entity', None)
        if id is not None and entity is None:
            entity = self.read(id=id)
        if entity is not None:
            intrusion_set = dict()
            intrusion_set['id'] = entity['stix_id_key']
            intrusion_set['type'] = 'intrusion-set'
            intrusion_set['name'] = entity['name']
            if self.opencti.not_empty(entity['stix_label']):
                intrusion_set['labels'] = entity['stix_label']
            else:
                intrusion_set['labels'] = ['intrusion-set']
            if self.opencti.not_empty(entity['alias']): intrusion_set['aliases'] = entity['alias']
            if self.opencti.not_empty(entity['description']): intrusion_set['description'] = entity['description']
            if self.opencti.not_empty(entity['goal']): intrusion_set['goals'] = entity['goal']
            if self.opencti.not_empty(entity['sophistication']): intrusion_set['sophistication'] = entity[
                'sophistication']
            if self.opencti.not_empty(entity['resource_level']): intrusion_set['resource_level'] = entity[
                'resource_level']
            if self.opencti.not_empty(entity['primary_motivation']): intrusion_set['primary_motivation'] = entity[
                'primary_motivation']
            if self.opencti.not_empty(entity['secondary_motivation']): intrusion_set['secondary_motivations'] = entity[
                'secondary_motivation']
            if self.opencti.not_empty(entity['first_seen']): intrusion_set[
                CustomProperties.FIRST_SEEN] = self.opencti.stix2.format_date(
                entity['first_seen'])
            if self.opencti.not_empty(entity['last_seen']): intrusion_set[
                CustomProperties.LAST_SEEN] = self.opencti.stix2.format_date(
                entity['last_seen'])
            intrusion_set['created'] = self.opencti.stix2.format_date(entity['created'])
            intrusion_set['modified'] = self.opencti.stix2.format_date(entity['modified'])
            intrusion_set[CustomProperties.ID] = entity['id']
            return self.opencti.stix2.prepare_export(entity, intrusion_set, mode, max_marking_definition_entity)
        else:
            self.opencti.log('error', 'Missing parameters: id or entity')
