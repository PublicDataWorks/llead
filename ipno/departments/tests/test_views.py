from unittest.mock import patch

import pytz
from datetime import date, datetime
from operator import itemgetter

from django.urls import reverse
from rest_framework import status

from complaints.constants import ALLEGATION_DISPOSITION_SUSTAINED
from news_articles.factories import NewsArticleFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from people.factories import PersonFactory
from test_utils.auth_api_test_case import AuthAPITestCase
from departments.factories import DepartmentFactory, WrglFileFactory
from officers.factories import EventFactory, OfficerFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory
from use_of_forces.factories import UseOfForceFactory
from utils.search_index import rebuild_search_index
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    UOF_INCIDENT,
    UOF_RECEIVE
)


class DepartmentsViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        department_3 = DepartmentFactory()

        department_1_officers = OfficerFactory.create_batch(2)
        department_2_officers = OfficerFactory.create_batch(3)

        for officer in department_1_officers:
            EventFactory.create_batch(2, department=department_1, officer=officer)

        for officer in department_2_officers:
            EventFactory(department=department_2, officer=officer)

        response = self.auth_client.get(reverse('api:departments-list'))
        assert response.status_code == status.HTTP_200_OK

        assert response.data == [{
            'id': department_2.slug,
            'name': department_2.name,
            'city': department_2.city,
            'parish': department_2.parish,
            'location_map_url': department_2.location_map_url,
        }, {
            'id': department_1.slug,
            'name': department_1.name,
            'city': department_1.city,
            'parish': department_1.parish,
            'location_map_url': department_1.location_map_url,
        }, {
            'id': department_3.slug,
            'name': department_3.name,
            'city': department_3.city,
            'parish': department_3.parish,
            'location_map_url': department_3.location_map_url,
        }]

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:departments-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_success(self):
        current_date = datetime.now(pytz.utc)
        department = DepartmentFactory()
        other_department = DepartmentFactory()

        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        officer_2 = OfficerFactory()
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()
        officer_3 = OfficerFactory()
        person_3 = PersonFactory(canonical_officer=officer_3)
        person_3.officers.add(officer_3)
        person_3.save()
        officer_4 = OfficerFactory()
        person_4 = PersonFactory(canonical_officer=officer_4)
        person_4.officers.add(officer_4)
        person_4.save()

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=UOF_INCIDENT,
            year=2018,
            month=8,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=UOF_INCIDENT,
            year=2019,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            kind=OFFICER_HIRE,
            year=2018,
            month=5,
            day=8,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=2,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2020,
            month=10,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=UOF_INCIDENT,
            year=2020,
            month=12,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_4,
            kind=OFFICER_HIRE,
            year=2017,
            month=2,
            day=3,
        )

        documents = DocumentFactory.create_batch(5, incident_date=datetime(2020, 5, 4))
        DocumentFactory(incident_date=datetime(2018, 8, 10))
        for document in documents:
            document.departments.add(department)

        recent_documents = DocumentFactory.create_batch(2, incident_date=current_date)
        for document in recent_documents:
            document.departments.add(department)

        complaints = ComplaintFactory.create_batch(3)
        ComplaintFactory()
        for complaint in complaints:
            complaint.departments.add(department)

        sustained_complaint = ComplaintFactory(disposition=ALLEGATION_DISPOSITION_SUSTAINED)
        sustained_complaint.departments.add(department)

        article_1 = NewsArticleFactory(published_date=current_date)
        matched_sentence_1 = MatchedSentenceFactory(
            article=article_1,
            extracted_keywords=['a']
        )
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_1.save()

        article_2 = NewsArticleFactory()
        matched_sentence_2 = MatchedSentenceFactory(
            article=article_2,
            extracted_keywords=['b']
        )
        matched_sentence_2.officers.add(officer_3)
        matched_sentence_2.save()

        wrfile_1 = WrglFileFactory(department=department, position=1)
        wrfile_1.created_at = current_date
        wrfile_1.save()

        wrgl_file_2 = WrglFileFactory(department=department, position=2)
        wrgl_file_2.created_at = datetime(2018, 8, 10, tzinfo=pytz.utc)
        wrgl_file_2.save()

        wrgl_file_3 = WrglFileFactory(department=department, position=3)
        wrgl_file_3.created_at = datetime(2002, 8, 10, tzinfo=pytz.utc)
        wrgl_file_3.save()

        expected_result = {
            'id': department.slug,
            'name': department.name,
            'city': department.city,
            'parish': department.parish,
            'address': department.address,
            'phone': department.phone,
            'location_map_url': department.location_map_url,
            'officers_count': 3,
            'datasets_count': 3,
            'recent_datasets_count': 1,
            'news_articles_count': 2,
            'recent_news_articles_count': 1,
            'complaints_count': 4,
            'sustained_complaints_count': 1,
            'documents_count': 7,
            'recent_documents_count': 2,
            'incident_force_count': 2,
            'data_period': department.data_period,
        }

        response = self.auth_client.get(
            reverse('api:departments-detail', kwargs={'pk': department.slug})
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_retrieve_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-detail', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-detail', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_documents_success(self):
        department = DepartmentFactory()

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_3 = DocumentFactory(incident_date=date(2019, 11, 6))
        DocumentFactory(incident_date=date(2021, 7, 9))

        for document in [document_1, document_2, document_3]:
            document.departments.add(department)

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.slug}),
            {
                'limit': 2,
            }
        )

        expected_results = [{
            'id': document_1.id,
            'document_type': document_1.document_type,
            'title': document_1.title,
            'url': document_1.url,
            'incident_date': str(document_1.incident_date),
            'text_content': document_1.text_content,
            'preview_image_url': document_1.preview_image_url,
            'pages_count': document_1.pages_count,
            'departments': [
                {
                    'id': department.slug,
                    'name': department.name,
                },
            ],
        }, {
            'id': document_3.id,
            'document_type': document_3.document_type,
            'title': document_3.title,
            'url': document_3.url,
            'incident_date': str(document_3.incident_date),
            'text_content': document_3.text_content,
            'preview_image_url': document_3.preview_image_url,
            'pages_count': document_3.pages_count,
            'departments': [
                {
                    'id': department.slug,
                    'name': department.name,
                },
            ],
        }]

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert response.data['previous'] is None
        assert response.data['next'] == f'http://testserver/api/departments/{department.slug}/documents/?limit=2&offset=2'
        assert response.data['results'] == expected_results

    def test_documents_with_limit_and_offset(self):
        department = DepartmentFactory()

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_3 = DocumentFactory(incident_date=date(2019, 11, 6))
        DocumentFactory(incident_date=date(2021, 7, 9))

        for document in [document_1, document_2, document_3]:
            document.departments.add(department)

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.slug}),
            {
                'limit': 2,
                'offset': 2,
            }
        )

        expected_results = [{
            'id': document_2.id,
            'document_type': document_2.document_type,
            'title': document_2.title,
            'url': document_2.url,
            'incident_date': str(document_2.incident_date),
            'text_content': document_2.text_content,
            'preview_image_url': document_2.preview_image_url,
            'pages_count': document_2.pages_count,
            'departments': [
                {
                    'id': department.slug,
                    'name': department.name,
                },
            ],
        }]

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert response.data['previous'] == f'http://testserver/api/departments/{department.slug}/documents/?limit=2'
        assert response.data['next'] is None
        assert response.data['results'] == expected_results

    def test_search_documents(self):
        department = DepartmentFactory()

        document_1 = DocumentFactory(
            title='Document title 1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 4)
        )
        document_2 = DocumentFactory(
            title='Document title keyword3',
            text_content='Text content 3',
            incident_date=date(2019, 11, 6)
        )
        document_3 = DocumentFactory(
            title='Document title keyword 4',
            text_content='Text content keyword 4',
            incident_date=date(2021, 7, 9)
        )

        DocumentFactory(
            title='Document title keyword2',
            text_content='Text content keyword 2',
            incident_date=date(2017, 12, 5)
        )

        for document in [document_1, document_2, document_3]:
            document.departments.add(department)

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.slug}),
            {'q': 'keyword'}
        )

        expected_results = [
            {
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'incident_date': str(document_2.incident_date),
                'preview_image_url': document_2.preview_image_url,
                'pages_count': document_2.pages_count,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    },
                ],
                'text_content': document_2.text_content,
                'text_content_highlight': None,
            }, {
                'id': document_3.id,
                'document_type': document_3.document_type,
                'title': document_3.title,
                'url': document_3.url,
                'incident_date': str(document_3.incident_date),
                'preview_image_url': document_3.preview_image_url,
                'pages_count': document_3.pages_count,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    },
                ],
                'text_content': document_3.text_content,
                'text_content_highlight': 'Text content <em>keyword</em> 4',
            }
        ]

        results = sorted(response.data['results'], key=itemgetter('id'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert results == expected_results

    def test_search_documents_with_limit_and_offset(self):
        department = DepartmentFactory()

        document_1 = DocumentFactory(
            title='Document title 1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 4)
        )
        document_2 = DocumentFactory(
            title='Document title keyword3',
            text_content='Text content 3',
            incident_date=date(2019, 11, 6)
        )
        document_3 = DocumentFactory(
            title='Document title keyword 4',
            text_content='Text content keyword 4',
            incident_date=date(2021, 7, 9)
        )

        DocumentFactory(
            title='Document title keyword2',
            text_content='Text content keyword 2',
            incident_date=date(2017, 12, 5)
        )

        for document in [document_1, document_2, document_3]:
            document.departments.add(department)

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.slug}),
            {
                'q': 'keyword',
                'offset': 1,
                'limit': 1,
            }
        )

        expected_results = [
            {
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'incident_date': str(document_2.incident_date),
                'preview_image_url': document_2.preview_image_url,
                'pages_count': document_2.pages_count,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    },
                ],
                'text_content': document_2.text_content,
                'text_content_highlight': None,
            },
        ]

        expected_previous = f'http://testserver/api/departments/{department.slug}/documents/?limit=1&q=keyword'

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['previous'] == expected_previous
        assert response.data['next'] is None
        assert response.data['results'] == expected_results

    def test_search_documents_with_empty_results(self):
        department = DepartmentFactory()
        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.slug}),
            {'q': 'keyword'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert response.data['results'] == []

    def test_documents_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_documents_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-documents', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_success_with_related_officer(self):
        current_date = datetime.now(pytz.utc)
        department = DepartmentFactory(
            data_period=['20']
        )
        other_department = DepartmentFactory()

        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        officer_2 = OfficerFactory()
        person_1.officers.add(officer_2)
        person_1.save()
        officer_3 = OfficerFactory()
        person_3 = PersonFactory(canonical_officer=officer_3)
        person_3.officers.add(officer_3)
        person_3.save()
        officer_4 = OfficerFactory()
        person_4 = PersonFactory(canonical_officer=officer_4)
        person_4.officers.add(officer_4)
        person_4.save()

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=UOF_INCIDENT,
            year=2018,
            month=5,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=UOF_INCIDENT,
            year=2019,
            month=5,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=UOF_INCIDENT,
            year=2018,
            month=7,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            kind=OFFICER_HIRE,
            year=2018,
            month=5,
            day=8,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2020,
            month=5,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=UOF_INCIDENT,
            year=2020,
            month=6,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_4,
            kind=OFFICER_HIRE,
            year=2017,
            month=2,
            day=3,
        )

        documents = DocumentFactory.create_batch(5, incident_date=datetime(2020, 5, 4))
        DocumentFactory(incident_date=datetime(2018, 8, 10))
        for document in documents:
            document.departments.add(department)

        recent_documents = DocumentFactory.create_batch(2, incident_date=current_date)
        for document in recent_documents:
            document.departments.add(department)

        complaints = ComplaintFactory.create_batch(3)
        ComplaintFactory()
        for complaint in complaints:
            complaint.departments.add(department)

        sustained_complaint = ComplaintFactory(disposition=ALLEGATION_DISPOSITION_SUSTAINED)
        sustained_complaint.departments.add(department)

        article_1 = NewsArticleFactory(published_date=current_date)
        matched_sentence_1 = MatchedSentenceFactory(
            article=article_1,
            extracted_keywords=['a']
        )
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_1.save()

        article_2 = NewsArticleFactory()
        matched_sentence_2 = MatchedSentenceFactory(
            article=article_2,
            extracted_keywords=['b']
        )
        matched_sentence_2.officers.add(officer_2)
        matched_sentence_2.save()

        wrfile_1 = WrglFileFactory(department=department, position=1)
        wrfile_1.created_at = current_date
        wrfile_1.save()

        wrgl_file_2 = WrglFileFactory(department=department, position=2)
        wrgl_file_2.created_at = datetime(2018, 8, 10, tzinfo=pytz.utc)
        wrgl_file_2.save()

        wrgl_file_3 = WrglFileFactory(department=department, position=3)
        wrgl_file_3.created_at = datetime(2002, 8, 10, tzinfo=pytz.utc)
        wrgl_file_3.save()

        expected_result = {
            'id': department.slug,
            'name': department.name,
            'city': department.city,
            'parish': department.parish,
            'address': department.address,
            'phone': department.phone,
            'location_map_url': department.location_map_url,
            'officers_count': 2,
            'datasets_count': 3,
            'recent_datasets_count': 1,
            'news_articles_count': 2,
            'recent_news_articles_count': 1,
            'complaints_count': 4,
            'sustained_complaints_count': 1,
            'documents_count': 7,
            'recent_documents_count': 2,
            'incident_force_count': 3,
            'data_period': department.data_period,
        }

        response = self.auth_client.get(
            reverse('api:departments-detail', kwargs={'pk': department.slug})
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_datasets_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-datasets', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_datasets_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-datasets', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_datasets_success(self):
        department = DepartmentFactory()

        wrgl_file_1 = WrglFileFactory(department=department, position=2)
        wrgl_file_2 = WrglFileFactory(department=department, position=1)

        response = self.auth_client.get(
            reverse('api:departments-datasets', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': wrgl_file_2.id,
                'name': wrgl_file_2.name,
                'slug': wrgl_file_2.slug,
                'description': wrgl_file_2.description,
                'url': wrgl_file_2.url,
                'download_url': wrgl_file_2.download_url,
                'default_expanded': wrgl_file_2.default_expanded,
            },
            {
                'id': wrgl_file_1.id,
                'name': wrgl_file_1.name,
                'slug': wrgl_file_1.slug,
                'description': wrgl_file_1.description,
                'url': wrgl_file_1.url,
                'download_url': wrgl_file_1.download_url,
                'default_expanded': wrgl_file_1.default_expanded,
            }
        ]

        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_officers_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-officers', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_officers_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-officers', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_officers_success(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_2, all_complaints_count=150)
        person_1.officers.add(officer_1)
        person_1.officers.add(officer_2)
        person_1.save()

        officer_3 = OfficerFactory()
        person_2 = PersonFactory(canonical_officer=officer_3, all_complaints_count=100)
        person_2.officers.add(officer_3)
        person_2.save()

        officer_4 = OfficerFactory()
        person_3 = PersonFactory(canonical_officer=officer_4, all_complaints_count=110)
        person_3.officers.add(officer_4)
        person_3.save()

        department = DepartmentFactory()
        department.starred_officers.add(officer_2)
        department.save()

        use_of_force_1 = UseOfForceFactory(officer=officer_3)
        use_of_force_2 = UseOfForceFactory(officer=officer_2)
        use_of_force_3 = UseOfForceFactory(officer=officer_2)

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="150",
            year=2018,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="100",
            year=2018,
            month=8,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="250",
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="150",
            year=2019,
            month=4,
            day=5,
        )

        uof_receive_event_2 = EventFactory(
            department=department,
            officer=officer_2,
            kind=UOF_RECEIVE,
            badge_no="200",
            year=2018,
            month=8,
            day=20,
        )

        uof_incident_event_2 = EventFactory(
            department=department,
            officer=officer_2,
            kind=UOF_INCIDENT,
            badge_no="200",
            year=2018,
            month=8,
            day=20,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            badge_no="123",
            year=2019,
            month=4,
            day=5,
        )

        uof_receive_event_1 = EventFactory(
            department=department,
            officer=officer_3,
            kind=UOF_RECEIVE,
            year=2018,
            month=8,
            day=20,
        )

        EventFactory(
            department=department,
            officer=officer_4,
            year=2019,
            month=4,
            day=5,
        )

        use_of_force_1.events.add(uof_receive_event_1)
        use_of_force_2.events.add(uof_receive_event_2)
        use_of_force_3.events.add(uof_incident_event_2)

        response = self.auth_client.get(
            reverse('api:departments-officers', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': officer_2.id,
                'name': officer_2.name,
                'is_starred': True,
                'use_of_forces_count': 2,
                'badges': ["150", "200", "250", "100"],
                'complaints_count': officer_2.person.all_complaints_count,
            },
            {
                'id': officer_4.id,
                'name': officer_4.name,
                'is_starred': False,
                'use_of_forces_count': 0,
                'badges': [],
                'complaints_count': officer_4.person.all_complaints_count,
            },
            {
                'id': officer_3.id,
                'name': officer_3.name,
                'is_starred': False,
                'use_of_forces_count': 1,
                'badges': ["123"],
                'complaints_count': officer_3.person.all_complaints_count,
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    @patch('departments.views.DEPARTMENTS_LIMIT', 3)
    def test_officers_with_maximum_starred_officers(self):
        department = DepartmentFactory()
        starred_officers = OfficerFactory.create_batch(3)
        starred_person = PersonFactory(canonical_officer=starred_officers[0])
        for starred_officer in starred_officers:
            department.starred_officers.add(starred_officer)
            starred_person.officers.add(starred_officer)
        department.save()
        starred_person.save()

        featured_officer = OfficerFactory()
        featured_person = PersonFactory(canonical_officer=featured_officer)
        featured_person.officers.add(featured_officer)
        featured_person.save()
        department.officers.add(featured_officer)
        department.save()

        response = self.auth_client.get(
            reverse('api:departments-officers', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': starred_officers[0].id,
                'name': starred_officers[0].name,
                'is_starred': True,
                'use_of_forces_count': 0,
                'badges': [],
                'complaints_count': starred_person.all_complaints_count,
            },
            {
                'id': starred_officers[1].id,
                'name': starred_officers[1].name,
                'is_starred': True,
                'use_of_forces_count': 0,
                'badges': [],
                'complaints_count': starred_person.all_complaints_count,
            },
            {
                'id': starred_officers[2].id,
                'name': starred_officers[2].name,
                'is_starred': True,
                'use_of_forces_count': 0,
                'badges': [],
                'complaints_count': starred_person.all_complaints_count,
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result
