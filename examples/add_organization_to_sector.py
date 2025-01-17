# coding: utf-8

import datetime

from pycti import OpenCTIApiClient

# Variables
api_url = 'http://localhost:4000'
api_token = '22566f94-9091-49ba-b583-efd76cf8b29c'

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

# Get the sector
sector = opencti_api_client.identity.read(filters=[{'key': 'name', 'values': ['Banking institutions']}])

# Create the organization
organization = opencti_api_client.identity.create(
    type='Organization',
    name='BNP Paribas',
    description='A french bank.'
)

# Create the relation
relation = opencti_api_client.stix_relation.create(
    fromType='Organization',
    fromId=organization['id'],
    toType='Sector',
    toId=sector['id'],
    relationship_type='gathering',
    description='BNP Paribas is part of the sector Banking institutions.',
    first_seen=datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ'),
    last_seen=datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ'),
    ignore_dates=True
)

# Print
print(relation)
