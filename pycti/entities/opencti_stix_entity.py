# coding: utf-8

import json


class StixEntity:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            stix_id_key
            entity_type
            parent_types
            name
            description
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
            externalReferences {
                edges {
                    node {
                        id
                        entity_type
                        stix_id_key
                        source_name
                        description
                        url
                        hash
                        external_id
                        created
                        modified
                    }
                    relation {
                        id
                    }
                }
            }
            ... on AttackPattern {
                killChainPhases {
                    edges {
                        node {
                            id
                            entity_type
                            stix_id_key
                            kill_chain_name
                            phase_name
                            phase_order
                            created
                            modified
                        }
                        relation {
                            id
                        }
                    }
                }
            }
            ... on Malware {
                killChainPhases {
                    edges {
                        node {
                            id
                            entity_type
                            stix_id_key
                            kill_chain_name
                            phase_name
                            phase_order
                            created
                            modified
                        }
                        relation {
                            id
                        }
                    }
                }                
            }
            ... on StixRelation {
                killChainPhases {
                    edges {
                        node {
                            id
                            entity_type
                            stix_id_key
                            kill_chain_name
                            phase_name
                            phase_order
                            created
                            modified
                        }
                        relation {
                            id
                        }
                    }
                }                
            } 
        """

    """
        Read a Stix-Entity object

        :param id: the id of the Stix-Entity
        :return Stix-Entity object
    """

    def read(self, **kwargs):
        id = kwargs.get('id', None)
        if id is not None:
            self.opencti.log('info', 'Reading Stix-Entity {' + id + '}.')
            query = """
                query StixEntity($id: String!) {
                    stixEntity(id: $id) {
                        """ + self.properties + """
                    }
                }
             """
            result = self.opencti.query(query, {'id': id})
            return self.opencti.process_multiple_fields(result['data']['stixEntity'])
        else:
            self.opencti.log('error', 'Missing parameters: id or filters')
            return None

    """
        Update the Identity author of a Stix-Entity object (created_by_ref)

        :param id: the id of the Stix-Entity
        :param identity_id: the id of the Identity
        :return Boolean
    """

    def update_created_by_ref(self, **kwargs):
        id = kwargs.get('id', None)
        identity_id = kwargs.get('identity_id', None)
        if id is not None and identity_id is not None:
            self.opencti.log('info',
                             'Updating author of Stix-Entity {' + id + '} with Identity {' + identity_id + '}')
            stix_entity = self.read(id=id)
            current_identity_id = None
            current_relation_id = None
            if stix_entity['createdByRef'] is not None:
                current_identity_id = stix_entity['createdByRef']['id']
                current_relation_id = stix_entity['createdByRef']['remote_relation_id']

            # Current identity is the same
            if current_identity_id == identity_id:
                return True
            else:
                # Current identity is different, delete the old relation
                if current_relation_id is not None:
                    query = """
                        mutation StixEntityEdit($id: ID!, $relationId: ID!) {
                            stixEntityEdit(id: $id) {
                                relationDelete(relationId: $relationId) {
                                    id
                                }
                            }
                        }
                    """
                    self.opencti.query(query, {'id': id, 'relationId': current_relation_id})
                # Add the new relation
                query = """
                   mutation StixEntityEdit($id: ID!, $input: RelationAddInput) {
                       stixEntityEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                       }
                   }
                """
                variables = {
                    'id': id,
                    'input': {
                        'fromRole': 'so',
                        'toId': identity_id,
                        'toRole': 'creator',
                        'through': 'created_by_ref'
                    }
                }
                self.opencti.query(query, variables)

        else:
            self.opencti.log('error', 'Missing parameters: id and identity_id')
            return False

    """
        Add a Marking-Definition object to Stix-Entity object (object_marking_refs)

        :param id: the id of the Stix-Entity
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def add_marking_definition(self, **kwargs):
        id = kwargs.get('id', None)
        marking_definition_id = kwargs.get('marking_definition_id', None)
        if id is not None and marking_definition_id is not None:
            self.opencti.log('info',
                             'Adding Marking-Definition {' + marking_definition_id + '} to Stix-Entity {' + id + '}')
            stix_entity = self.read(id=id)
            markings_ids = []
            for marking in stix_entity['markingDefinitions']:
                markings_ids.append(marking['id'])
            if marking_definition_id in markings_ids:
                return True
            else:
                query = """
                   mutation StixEntityAddRelation($id: ID!, $input: RelationAddInput) {
                       stixEntityEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                       }
                   }
                """
                self.opencti.query(query, {
                    'id': id,
                    'input': {
                        'fromRole': 'so',
                        'toId': marking_definition_id,
                        'toRole': 'marking',
                        'through': 'object_marking_refs'
                    }
                })
                return True
        else:
            self.opencti.log('error', 'Missing parameters: id and marking_definition_id')
            return False

    """
        Add a External-Reference object to Stix-Entity object (object_marking_refs)

        :param id: the id of the Stix-Entity
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def add_external_reference(self, **kwargs):
        id = kwargs.get('id', None)
        external_reference_id = kwargs.get('external_reference_id', None)
        if id is not None and external_reference_id is not None:
            self.opencti.log('info',
                             'Adding External-Reference {' + external_reference_id + '} to Stix-Entity {' + id + '}')
            stix_entity = self.read(id=id)
            external_references_ids = []
            for external_reference in stix_entity['externalReferences']:
                external_references_ids.append(external_reference['id'])
            if external_reference_id in external_references_ids:
                return True
            else:
                query = """
                   mutation StixEntityAddRelation($id: ID!, $input: RelationAddInput) {
                       stixEntityEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                       }
                   }
                """
                self.opencti.query(query, {
                    'id': id,
                    'input': {
                        'fromRole': 'so',
                        'toId': external_reference_id,
                        'toRole': 'external_reference',
                        'through': 'external_references'
                    }
                })
                return True
        else:
            self.opencti.log('error', 'Missing parameters: id and external_reference_id')
            return False

    """
        Add a Kill-Chain-Phase object to Stix-Entity object (kill_chain_phases)

        :param id: the id of the Stix-Entity
        :param kill_chain_phase_id: the id of the Kill-Chain-Phase
        :return Boolean
    """

    def add_kill_chain_phase(self, **kwargs):
        id = kwargs.get('id', None)
        kill_chain_phase_id = kwargs.get('kill_chain_phase_id', None)
        if id is not None and kill_chain_phase_id is not None:
            self.opencti.log('info',
                             'Adding Kill-Chain-Phase {' + kill_chain_phase_id + '} to Stix-Entity {' + id + '}')
            stix_entity = self.read(id=id)
            kill_chain_phases_ids = []
            for kill_chain_phase in stix_entity['killChainPhases']:
                kill_chain_phases_ids.append(kill_chain_phase['id'])
            if kill_chain_phase_id in kill_chain_phases_ids:
                return True
            else:
                query = """
                   mutation StixEntityAddRelation($id: ID!, $input: RelationAddInput) {
                       stixEntityEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                       }
                   }
                """
                self.opencti.query(query, {
                    'id': id,
                    'input': {
                        'fromRole': 'phase_belonging',
                        'toId': kill_chain_phase_id,
                        'toRole': 'kill_chain_phase',
                        'through': 'kill_chain_phases'
                    }
                })
                return True
        else:
            self.opencti.log('error', 'Missing parameters: id and kill_chain_phase_id')
            return False

    """
        Get the reports about a Stix-Entity object

        :param id: the id of the Stix-Entity
        :return Stix-Entity object
    """

    def reports(self, **kwargs):
        id = kwargs.get('id', None)
        if id is not None:
            self.opencti.log('info', 'Getting reports of the Stix-Entity {' + id + '}.')
            query = """
                query StixEntity($id: String!) {
                    stixEntity(id: $id) {
                        reports {
                            edges {
                                node {
                                    id
                                    stix_id_key
                                    entity_type
                                    stix_label
                                    name
                                    alias
                                    description
                                    report_class
                                    published
                                    object_status
                                    source_confidence_level
                                    graph_data
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
                                    externalReferences {
                                        edges {
                                            node {
                                                id
                                                entity_type
                                                stix_id_key
                                                source_name
                                                description
                                                url
                                                hash
                                                external_id
                                                created
                                                modified
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                    objectRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id_key
                                                entity_type
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                    observableRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id_key
                                                entity_type
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                    relationRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id_key
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                }
                                relation {
                                    id
                                }
                            }
                        }
                    }
                }
             """
            result = self.opencti.query(query, {'id': id})
            processed_result = self.opencti.process_multiple_fields(result['data']['stixEntity'])
            return processed_result['reports']
        else:
            self.opencti.log('error', 'Missing parameters: id')
            return None
