from datetime import date

from django.test import TestCase

from news_articles.factories import NewsArticleFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.queries import OfficerTimelineQuery
from officers.factories import OfficerFactory, EventFactory
from complaints.factories import ComplaintFactory
from people.factories import PersonFactory
from use_of_forces.factories import UseOfForceFactory
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from officers.constants import (
    JOINED_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    UOF_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND,
    UNIT_CHANGE_TIMELINE_KIND,
    NEWS_ARTICLE_TIMELINE_KIND,
    UOF_INCIDENT,
    UOF_ASSIGNED,
    UOF_COMPLETED,
    UOF_CREATED,
    UOF_DUE,
    COMPLAINT_INCIDENT,
    ALLEGATION_CREATE,
    INVESTIGATION_COMPLETE,
    SUSPENSION_START,
    SUSPENSION_END,
)
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    COMPLAINT_RECEIVE,
    OFFICER_DEPT,
    UOF_RECEIVE,
)


class OfficerTimelineQueryTestCase(TestCase):
    def test_query(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=8,
        )
        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=4,
            day=8,
        )
        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='57000',
            salary_freq='yearly',
            year=2019,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            department=department_2,
            kind=OFFICER_HIRE,
            year=2020,
            month=5,
            day=9,
        )
        EventFactory(
            officer=officer,
            department=department_2,
            kind=OFFICER_RANK,
            rank_desc='senior police office',
            rank_code=3,
            year=2017,
            month=7,
            day=13,
        )
        complaint_receive_event = EventFactory(
            officer=officer,
            department=department_1,
            kind=COMPLAINT_RECEIVE,
            year=2019,
            month=5,
            day=4,
        )
        complaint_1.events.add(complaint_receive_event)

        EventFactory(
            kind=OFFICER_DEPT,
            officer=officer,
            department=department_1,
            department_code='193',
            department_desc='Gang Investigation Division',
            year=2017,
            month=7,
            day=14,
        )
        EventFactory(
            kind=OFFICER_DEPT,
            officer=officer,
            department=department_1,
            department_code='610',
            department_desc='Detective Area - Central',
            year=2018,
            month=8,
            day=10,
        )

        document_1 = DocumentFactory(incident_date=date(2018, 6, 5))
        document_2 = DocumentFactory(incident_date=date(2021, 2, 1))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_1.departments.add(department_1)

        news_article_1 = NewsArticleFactory(published_date=date(2018, 6, 6))
        news_article_2 = NewsArticleFactory(published_date=date(2021, 2, 2))

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)

        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)

        use_of_force = UseOfForceFactory(officer=officer)
        EventFactory(
            kind=UOF_RECEIVE,
            year=2019,
            month=5,
            day=5,
            use_of_force=use_of_force,
        )

        expected_result = [
            {
                'id': complaint_2.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': None,
                'year': None,
                'rule_code': complaint_2.rule_code,
                'rule_violation': complaint_2.rule_violation,
                'paragraph_code': complaint_2.paragraph_code,
                'paragraph_violation': complaint_2.paragraph_violation,
                'disposition': complaint_2.disposition,
                'action': complaint_2.action,
                'tracking_number': complaint_2.tracking_number,
                'allegation_desc': complaint_2.allegation_desc,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_code': '3',
                'rank_desc': 'senior police office',
                'date': str(date(2017, 7, 13)),
                'year': 2017,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '193',
                'department_desc': 'Gang Investigation Division',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': str(date(2017, 7, 14)),
                'year': 2017,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2018, 4, 8)),
                'year': 2018,
                'department': department_1.name,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_1.incident_date),
                'year': document_1.incident_date.year,
                'id': document_1.id,
                'document_type': document_1.document_type,
                'title': document_1.title,
                'url': document_1.url,
                'preview_image_url': document_1.preview_image_url,
                'incident_date': str(document_1.incident_date),
                'pages_count': document_1.pages_count,
                'departments': [
                    {
                        'id': department_1.slug,
                        'name': department_1.name,
                    },
                ],
            },
            {
                'kind': NEWS_ARTICLE_TIMELINE_KIND,
                'date': str(news_article_1.published_date),
                'year': news_article_1.published_date.year,
                'id': news_article_1.id,
                'source_name': news_article_1.source.source_display_name,
                'title': news_article_1.title,
                'url': news_article_1.url,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '610',
                'department_desc': 'Detective Area - Central',
                'prev_department_code': '193',
                'prev_department_desc': 'Gang Investigation Division',
                'date': str(date(2018, 8, 10)),
                'year': 2018,
            },
            {
                'id': complaint_1.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': str(date(2019, 5, 4)),
                'year': 2019,
                'rule_code': complaint_1.rule_code,
                'rule_violation': complaint_1.rule_violation,
                'paragraph_code': complaint_1.paragraph_code,
                'paragraph_violation': complaint_1.paragraph_violation,
                'disposition': complaint_1.disposition,
                'action': complaint_1.action,
                'tracking_number': complaint_1.tracking_number,
                'allegation_desc': complaint_1.allegation_desc,
            },
            {
                'id': use_of_force.id,
                'kind': UOF_TIMELINE_KIND,
                'date': str(date(2019, 5, 5)),
                'year': 2019,
                'force_type': use_of_force.force_type,
                'force_description': use_of_force.force_description,
                'force_reason': use_of_force.force_reason,
                'disposition': use_of_force.disposition,
                'service_type': use_of_force.service_type,
                'citizen_involvement': use_of_force.citizen_involvement,
                'citizen_age': use_of_force.citizen_age,
                'citizen_race': use_of_force.citizen_race,
                'citizen_sex': use_of_force.citizen_sex,
                'uof_tracking_number': use_of_force.uof_tracking_number,
                'citizen_arrested': use_of_force.citizen_arrested,
                'citizen_injured': use_of_force.citizen_injured,
                'citizen_hospitalized': use_of_force.citizen_hospitalized,
                'officer_injured': use_of_force.officer_injured,
                'traffic_stop': use_of_force.traffic_stop,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '57000.00',
                'salary_freq': 'yearly',
                'date': str(date(2019, 12, 1)),
                'year': 2019,
            },
            {
                'kind': LEFT_TIMELINE_KIND,
                'date': str(date(2020, 4, 8)),
                'year': 2020,
                'department': department_1.name,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2020, 5, 9)),
                'year': 2020,
                'department': department_2.name,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_2.incident_date),
                'year': document_2.incident_date.year,
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'preview_image_url': document_2.preview_image_url,
                'incident_date': str(document_2.incident_date),
                'pages_count': document_2.pages_count,
                'departments': [],
            },
            {
                'kind': NEWS_ARTICLE_TIMELINE_KIND,
                'date': str(news_article_2.published_date),
                'year': news_article_2.published_date.year,
                'id': news_article_2.id,
                'source_name': news_article_2.source.source_display_name,
                'title': news_article_2.title,
                'url': news_article_2.url,
            },
        ]

        officer_timeline_data = OfficerTimelineQuery(officer).query()

        timeline = sorted(
            officer_timeline_data['timeline'],
            key=lambda item: str(item['date']) if item['date'] else ''
        )

        assert timeline == expected_result
        assert officer_timeline_data['timeline_period'] == ['2019']

    def test_salary_change(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='57000',
            salary_freq='yearly',
            year=2015,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='65000',
            salary_freq='yearly',
            year=2019,
            month=3,
            day=7,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='57000',
            salary_freq='yearly',
            year=2017,
            month=5,
            day=6,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='45000',
            salary_freq='yearly',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='45000',
            salary_freq='yearly',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='60000',
            salary_freq='yearly',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='45000',
            salary_freq='yearly',
            year=2019,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='26.14',
            salary_freq='hourly',
            year=2017,
            month=8,
            day=12,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='16.15',
            salary_freq='hourly',
            year=None,
            month=None,
            day=None,
        )

        expected_result = [
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '57000.00',
                'salary_freq': 'yearly',
                'date': str(date(2015, 12, 1)),
                'year': 2015,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '26.14',
                'salary_freq': 'hourly',
                'date': str(date(2017, 8, 12)),
                'year': 2017,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '65000.00',
                'salary_freq': 'yearly',
                'date': str(date(2019, 3, 7)),
                'year': 2019,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '45000.00',
                'salary_freq': 'yearly',
                'date': None,
                'year': 2019,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '16.15',
                'salary_freq': 'hourly',
                'date': None,
                'year': None,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '45000.00',
                'salary_freq': 'yearly',
                'date': None,
                'year': None,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '60000.00',
                'salary_freq': 'yearly',
                'date': None,
                'year': None,
            },
        ]

        officer_timeline_data = OfficerTimelineQuery(officer).query()

        assert officer_timeline_data['timeline'] == expected_result

    def test_rank_change(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Fresh Officer',
            rank_code='1',
            year=2015,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Senior Officer',
            rank_code='3',
            year=2019,
            month=3,
            day=7,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Fresh Officer',
            rank_code='1',
            year=2017,
            month=5,
            day=6,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Junior Officer',
            rank_code='2',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Junior Officer',
            rank_code='2',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Senior Officer',
            rank_code='3',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Junior Officer',
            rank_code='2',
            year=2019,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='police recruit',
            rank_code=None,
            year=2017,
            month=8,
            day=12,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='police technical specialist',
            rank_code=None,
            year=None,
            month=None,
            day=None,
        )

        expected_result = [
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Fresh Officer',
                'rank_code': '1',
                'date': str(date(2015, 12, 1)),
                'year': 2015,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'police recruit',
                'rank_code': None,
                'date': str(date(2017, 8, 12)),
                'year': 2017,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Senior Officer',
                'rank_code': '3',
                'date': str(date(2019, 3, 7)),
                'year': 2019,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Junior Officer',
                'rank_code': '2',
                'date': None,
                'year': 2019,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Junior Officer',
                'rank_code': '2',
                'date': None,
                'year': None,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Senior Officer',
                'rank_code': '3',
                'date': None,
                'year': None,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'police technical specialist',
                'rank_code': None,
                'date': None,
                'year': None,
            },
        ]

        officer_timeline_data = OfficerTimelineQuery(officer).query()

        assert officer_timeline_data['timeline'] == expected_result

    def test_unit_change(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='193',
            department_desc='Gang Investigation Division',
            year=2015,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='610',
            department_desc='Detective Area - Central',
            year=2019,
            month=3,
            day=7,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='193',
            department_desc='Gang Investigation Division',
            year=2017,
            month=5,
            day=6,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='5020',
            department_desc='police-uniform patrol bureau',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='5020',
            department_desc='police-uniform patrol bureau',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='610',
            department_desc='Detective Area - Central',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='5020',
            department_desc='police-uniform patrol bureau',
            year=2019,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code=None,
            department_desc='fob - field operations bureau',
            year=2017,
            month=8,
            day=12,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code=None,
            department_desc='msb - management service bureau',
            year=None,
            month=None,
            day=None,
        )

        expected_result = [
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '193',
                'department_desc': 'Gang Investigation Division',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': str(date(2015, 12, 1)),
                'year': 2015,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': None,
                'department_desc': 'fob - field operations bureau',
                'prev_department_code': '193',
                'prev_department_desc': 'Gang Investigation Division',
                'date': str(date(2017, 8, 12)),
                'year': 2017,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '610',
                'department_desc': 'Detective Area - Central',
                'prev_department_code': None,
                'prev_department_desc': 'fob - field operations bureau',
                'date': str(date(2019, 3, 7)),
                'year': 2019,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '5020',
                'department_desc': 'police-uniform patrol bureau',
                'prev_department_code': '610',
                'prev_department_desc': 'Detective Area - Central',
                'date': None,
                'year': 2019,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '5020',
                'department_desc': 'police-uniform patrol bureau',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': None,
                'year': None,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '610',
                'department_desc': 'Detective Area - Central',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': None,
                'year': None,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': None,
                'department_desc': 'msb - management service bureau',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': None,
                'year': None,
            },
        ]

        officer_timeline_data = OfficerTimelineQuery(officer).query()

        assert officer_timeline_data['timeline'] == expected_result

    def test_query_with_related_officer(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        related_officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_1.officers.add(officer)
        complaint_2.officers.add(related_officer)

        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=8,
        )
        EventFactory(
            officer=related_officer,
            department=department_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=4,
            day=8,
        )
        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='57000',
            salary_freq='yearly',
            year=2019,
            month=12,
            day=1,
        )
        EventFactory(
            officer=related_officer,
            department=department_2,
            kind=OFFICER_HIRE,
            year=2020,
            month=5,
            day=9,
        )
        EventFactory(
            officer=related_officer,
            department=department_2,
            kind=OFFICER_RANK,
            rank_desc='senior police office',
            rank_code=3,
            year=2017,
            month=7,
            day=13,
        )
        complaint_receive_event = EventFactory(
            officer=officer,
            department=department_1,
            kind=COMPLAINT_RECEIVE,
            year=2019,
            month=5,
            day=4,
        )
        complaint_1.events.add(complaint_receive_event)

        EventFactory(
            kind=OFFICER_DEPT,
            officer=officer,
            department=department_1,
            department_code='193',
            department_desc='Gang Investigation Division',
            year=2017,
            month=7,
            day=14,
        )
        EventFactory(
            kind=OFFICER_DEPT,
            officer=officer,
            department=department_1,
            department_code='610',
            department_desc='Detective Area - Central',
            year=2018,
            month=8,
            day=10,
        )

        document_1 = DocumentFactory(incident_date=date(2018, 6, 5))
        document_2 = DocumentFactory(incident_date=date(2021, 2, 1))

        document_1.officers.add(officer)
        document_2.officers.add(related_officer)
        document_1.departments.add(department_1)

        news_article_1 = NewsArticleFactory(published_date=date(2018, 6, 6))
        news_article_2 = NewsArticleFactory(published_date=date(2021, 2, 2))

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)

        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)

        use_of_force = UseOfForceFactory(officer=officer)
        EventFactory(
            kind=UOF_RECEIVE,
            year=2019,
            month=5,
            day=5,
            use_of_force=use_of_force,
        )

        expected_result = [
            {
                'id': complaint_2.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': None,
                'year': None,
                'rule_code': complaint_2.rule_code,
                'rule_violation': complaint_2.rule_violation,
                'paragraph_code': complaint_2.paragraph_code,
                'paragraph_violation': complaint_2.paragraph_violation,
                'disposition': complaint_2.disposition,
                'action': complaint_2.action,
                'tracking_number': complaint_2.tracking_number,
                'allegation_desc': complaint_2.allegation_desc,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_code': '3',
                'rank_desc': 'senior police office',
                'date': str(date(2017, 7, 13)),
                'year': 2017,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '193',
                'department_desc': 'Gang Investigation Division',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': str(date(2017, 7, 14)),
                'year': 2017,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2018, 4, 8)),
                'year': 2018,
                'department': department_1.name,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_1.incident_date),
                'year': document_1.incident_date.year,
                'id': document_1.id,
                'document_type': document_1.document_type,
                'title': document_1.title,
                'url': document_1.url,
                'preview_image_url': document_1.preview_image_url,
                'incident_date': str(document_1.incident_date),
                'pages_count': document_1.pages_count,
                'departments': [
                    {
                        'id': department_1.slug,
                        'name': department_1.name,
                    },
                ],
            },
            {
                'kind': NEWS_ARTICLE_TIMELINE_KIND,
                'date': str(news_article_1.published_date),
                'year': news_article_1.published_date.year,
                'id': news_article_1.id,
                'source_name': news_article_1.source.source_display_name,
                'title': news_article_1.title,
                'url': news_article_1.url,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '610',
                'department_desc': 'Detective Area - Central',
                'prev_department_code': '193',
                'prev_department_desc': 'Gang Investigation Division',
                'date': str(date(2018, 8, 10)),
                'year': 2018,
            },
            {
                'id': complaint_1.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': str(date(2019, 5, 4)),
                'year': 2019,
                'rule_code': complaint_1.rule_code,
                'rule_violation': complaint_1.rule_violation,
                'paragraph_code': complaint_1.paragraph_code,
                'paragraph_violation': complaint_1.paragraph_violation,
                'disposition': complaint_1.disposition,
                'action': complaint_1.action,
                'tracking_number': complaint_1.tracking_number,
                'allegation_desc': complaint_1.allegation_desc,
            },
            {
                'id': use_of_force.id,
                'kind': UOF_TIMELINE_KIND,
                'date': str(date(2019, 5, 5)),
                'year': 2019,
                'force_type': use_of_force.force_type,
                'force_description': use_of_force.force_description,
                'force_reason': use_of_force.force_reason,
                'disposition': use_of_force.disposition,
                'service_type': use_of_force.service_type,
                'citizen_involvement': use_of_force.citizen_involvement,
                'citizen_age': use_of_force.citizen_age,
                'citizen_race': use_of_force.citizen_race,
                'citizen_sex': use_of_force.citizen_sex,
                'uof_tracking_number': use_of_force.uof_tracking_number,
                'citizen_arrested': use_of_force.citizen_arrested,
                'citizen_injured': use_of_force.citizen_injured,
                'citizen_hospitalized': use_of_force.citizen_hospitalized,
                'officer_injured': use_of_force.officer_injured,
                'traffic_stop': use_of_force.traffic_stop,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '57000.00',
                'salary_freq': 'yearly',
                'date': str(date(2019, 12, 1)),
                'year': 2019,
            },
            {
                'kind': LEFT_TIMELINE_KIND,
                'date': str(date(2020, 4, 8)),
                'year': 2020,
                'department': department_1.name,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2020, 5, 9)),
                'year': 2020,
                'department': department_2.name,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_2.incident_date),
                'year': document_2.incident_date.year,
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'preview_image_url': document_2.preview_image_url,
                'incident_date': str(document_2.incident_date),
                'pages_count': document_2.pages_count,
                'departments': [],
            },
            {
                'kind': NEWS_ARTICLE_TIMELINE_KIND,
                'date': str(news_article_2.published_date),
                'year': news_article_2.published_date.year,
                'id': news_article_2.id,
                'source_name': news_article_2.source.source_display_name,
                'title': news_article_2.title,
                'url': news_article_2.url,
            },
        ]

        officer_timeline_data = OfficerTimelineQuery(officer).query()

        timeline = sorted(
            officer_timeline_data['timeline'],
            key=lambda item: str(item['date']) if item['date'] else ''
        )

        assert timeline == expected_result
        assert officer_timeline_data['timeline_period'] == ['2019']

    def test_get_timeline_period(self):
        department = DepartmentFactory()

        officer = OfficerFactory()

        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_3 = ComplaintFactory()
        complaint_4 = ComplaintFactory()
        complaint_5 = ComplaintFactory()
        complaint_6 = ComplaintFactory()
        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)
        complaint_3.officers.add(officer)
        complaint_4.officers.add(officer)
        complaint_5.officers.add(officer)
        complaint_6.officers.add(officer)

        uof_1 = UseOfForceFactory(officer=officer)
        uof_2 = UseOfForceFactory(officer=officer)
        uof_3 = UseOfForceFactory(officer=officer)
        uof_4 = UseOfForceFactory(officer=officer)
        uof_5 = UseOfForceFactory(officer=officer)
        uof_6 = UseOfForceFactory(officer=officer)

        uof_receive_event = EventFactory(
            kind=UOF_RECEIVE,
            officer=officer,
            department=department,
            year=2009,
        )

        uof_incident_event = EventFactory(
            kind=UOF_INCIDENT,
            officer=officer,
            department=department,
            year=2010,
        )

        uof_assigned_event = EventFactory(
            kind=UOF_ASSIGNED,
            officer=officer,
            department=department,
            year=2011,
        )

        uof_completed_event = EventFactory(
            kind=UOF_COMPLETED,
            officer=officer,
            department=department,
            year=2011,
        )

        uof_created_event = EventFactory(
            kind=UOF_CREATED,
            officer=officer,
            department=department,
            year=2012,
        )

        uof_due_event = EventFactory(
            kind=UOF_DUE,
            officer=officer,
            department=department,
            year=2014,
        )

        complaint_incident_event = EventFactory(
            kind=COMPLAINT_INCIDENT,
            officer=officer,
            department=department,
            year=2013,
        )

        complaint_receive_event = EventFactory(
            kind=COMPLAINT_RECEIVE,
            officer=officer,
            department=department,
            year=2017,
        )

        complaint_allegation_event = EventFactory(
            kind=ALLEGATION_CREATE,
            officer=officer,
            department=department,
            year=2010,
        )

        complaint_investigation_event = EventFactory(
            kind=INVESTIGATION_COMPLETE,
            officer=officer,
            department=department,
            year=2011,
        )

        complaint_suspension_start_event = EventFactory(
            kind=SUSPENSION_START,
            officer=officer,
            department=department,
            year=2015,
        )

        complaint_suspension_end_event = EventFactory(
            kind=SUSPENSION_END,
            officer=officer,
            department=department,
            year=2017,
        )

        uof_1.events.add(uof_receive_event)
        uof_2.events.add(uof_incident_event)
        uof_3.events.add(uof_assigned_event)
        uof_4.events.add(uof_completed_event)
        uof_5.events.add(uof_created_event)
        uof_6.events.add(uof_due_event)

        complaint_1.events.add(complaint_incident_event)
        complaint_2.events.add(complaint_receive_event)
        complaint_3.events.add(complaint_allegation_event)
        complaint_4.events.add(complaint_investigation_event)
        complaint_5.events.add(complaint_suspension_start_event)
        complaint_6.events.add(complaint_suspension_end_event)

        result = OfficerTimelineQuery(officer).query()

        assert result.get('timeline_period') == ["2009-2012", "2014", "2017"]

    def test_get_timeline_period_with_data_period_of_deparment(self):
        department = DepartmentFactory(data_period=[2007, 2008, 2009, 2015, 2016, 2017, 2018, 2019])

        officer = OfficerFactory()

        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_3 = ComplaintFactory()
        complaint_4 = ComplaintFactory()
        complaint_5 = ComplaintFactory()
        complaint_6 = ComplaintFactory()
        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)
        complaint_3.officers.add(officer)
        complaint_4.officers.add(officer)
        complaint_5.officers.add(officer)
        complaint_6.officers.add(officer)

        uof_1 = UseOfForceFactory(officer=officer)
        uof_2 = UseOfForceFactory(officer=officer)
        uof_3 = UseOfForceFactory(officer=officer)
        uof_4 = UseOfForceFactory(officer=officer)
        uof_5 = UseOfForceFactory(officer=officer)
        uof_6 = UseOfForceFactory(officer=officer)

        uof_receive_event = EventFactory(
            kind=UOF_RECEIVE,
            officer=officer,
            department=department,
            year=2009,
        )

        uof_incident_event = EventFactory(
            kind=UOF_INCIDENT,
            officer=officer,
            department=department,
            year=2010,
        )

        uof_assigned_event = EventFactory(
            kind=UOF_ASSIGNED,
            officer=officer,
            department=department,
            year=2011,
        )

        uof_completed_event = EventFactory(
            kind=UOF_COMPLETED,
            officer=officer,
            department=department,
            year=2012,
        )

        uof_created_event = EventFactory(
            kind=UOF_CREATED,
            officer=officer,
            department=department,
            year=2013,
        )

        uof_due_event = EventFactory(
            kind=UOF_DUE,
            officer=officer,
            department=department,
            year=2014,
        )

        complaint_incident_event = EventFactory(
            kind=COMPLAINT_INCIDENT,
            officer=officer,
            department=department,
            year=2013,
        )

        complaint_receive_event = EventFactory(
            kind=COMPLAINT_RECEIVE,
            officer=officer,
            department=department,
            year=2017,
        )

        complaint_allegation_event = EventFactory(
            kind=ALLEGATION_CREATE,
            officer=officer,
            department=department,
            year=2010,
        )

        complaint_investigation_event = EventFactory(
            kind=INVESTIGATION_COMPLETE,
            officer=officer,
            department=department,
            year=2011,
        )

        complaint_suspension_start_event = EventFactory(
            kind=SUSPENSION_START,
            officer=officer,
            department=department,
            year=2015,
        )

        complaint_suspension_end_event = EventFactory(
            kind=SUSPENSION_END,
            officer=officer,
            department=department,
            year=2017,
        )

        uof_1.events.add(uof_receive_event)
        uof_2.events.add(uof_incident_event)
        uof_3.events.add(uof_assigned_event)
        uof_4.events.add(uof_completed_event)
        uof_5.events.add(uof_created_event)
        uof_6.events.add(uof_due_event)

        complaint_1.events.add(complaint_incident_event)
        complaint_2.events.add(complaint_receive_event)
        complaint_3.events.add(complaint_allegation_event)
        complaint_4.events.add(complaint_investigation_event)
        complaint_5.events.add(complaint_suspension_start_event)
        complaint_6.events.add(complaint_suspension_end_event)

        result = OfficerTimelineQuery(officer).query()

        assert result.get('timeline_period') == ["2009-2017"]

    def test_get_timeline_period_with_one_event(self):
        department = DepartmentFactory(data_period=[2015, 2016, 2017, 2018, 2019])

        officer = OfficerFactory()

        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        complaint = ComplaintFactory()
        complaint.officers.add(officer)

        complaint_receive_event = EventFactory(
            kind=COMPLAINT_RECEIVE,
            officer=officer,
            department=department,
            year=2017,
        )

        complaint.events.add(complaint_receive_event)

        result = OfficerTimelineQuery(officer).query()

        assert result.get('timeline_period') == ["2017"]
