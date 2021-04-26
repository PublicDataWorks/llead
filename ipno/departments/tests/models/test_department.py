from datetime import date
from django.test.testcases import TestCase

from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory


class DepartmentTestCase(TestCase):
    def test_str(self):
        department = DepartmentFactory()
        assert str(department) == f"{department.name} - {department.id}"

    def test_document_years(self):
        department = DepartmentFactory()

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2019, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.departments.add(department)
        document_2.departments.add(department)
        document_3.departments.add(department)

        assert sorted(department.document_years) == [2016, 2018, 2019]
