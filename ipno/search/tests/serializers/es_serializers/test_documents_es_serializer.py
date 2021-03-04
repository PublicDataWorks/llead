from operator import itemgetter
from datetime import date

from django.test import TestCase

from mock import Mock
from elasticsearch_dsl.utils import AttrDict

from search.serializers.es_serializers import DocumentsESSerializer
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory


class DocumentsESSerializerTestCase(TestCase):
    def test_serialize(self):
        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory()
        document_3 = DocumentFactory()
        DocumentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()

        OfficerHistoryFactory(
            department=department_1,
            officer=officer_1,
            start_date=date(2018, 2, 3),
            end_date=date(2021, 2, 3),
        )
        OfficerHistoryFactory(
            department=department_2,
            officer=officer_2,
            start_date=date(2019, 4, 5),
            end_date=date(2019, 12, 20),
        )
        OfficerHistoryFactory(
            department=department_2,
            officer=officer_3,
            start_date=date(2019, 12, 21),
            end_date=date(2021, 12, 21),
        )
        document_1.officers.add(officer_1, officer_2, officer_3)

        docs = [
            Mock(id=document_2.id, meta=None),
            Mock(
                id=document_1.id,
                meta=Mock(
                    highlight=AttrDict({'text_content': ['<em>text</em> content']}),
                ),
            ),
            Mock(id=document_3.id, meta=None),
        ]
        expected_result = [
            {
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'incident_date': str(document_2.incident_date),
                'text_content': document_2.text_content,
                'text_content_highlight': None,
                'departments': [],
            },
            {
                'id': document_1.id,
                'document_type': document_1.document_type,
                'title': document_1.title,
                'url': document_1.url,
                'incident_date': str(document_1.incident_date),
                'text_content': document_1.text_content,
                'text_content_highlight': '<em>text</em> content',
                'departments': [
                    {
                        'id': department_1.id,
                        'name': department_1.name,
                    },
                    {
                        'id': department_2.id,
                        'name': department_2.name,
                    },
                ],
            },
            {
                'id': document_3.id,
                'document_type': document_3.document_type,
                'title': document_3.title,
                'url': document_3.url,
                'incident_date': str(document_3.incident_date),
                'text_content': document_3.text_content,
                'text_content_highlight': None,
                'departments': [],
            },
        ]

        result = DocumentsESSerializer().serialize(docs)
        result[1]['departments'] = sorted(result[1]['departments'], key=itemgetter('id'))
        print(result)
        print(expected_result[1])
        assert result == expected_result
