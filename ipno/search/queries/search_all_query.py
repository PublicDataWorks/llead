from search.queries.departments_search_query import DepartmentsSearchQuery
from search.queries.officers_search_query import OfficersSearchQuery
from search.queries.documents_search_query import DocumentsSearchQuery
from search.serializers.es_serializers import DepartmentsESSerializer, OfficersESSerializer
from shared.serializers.es_serializers import DocumentsESSerializer

SEARCH_MAPPINGS = {
    'DEPARTMENTS': {
        'search_query': DepartmentsSearchQuery,
        'serializer': DepartmentsESSerializer
    },
    'OFFICERS': {
        'search_query': OfficersSearchQuery,
        'serializer': OfficersESSerializer
    },
    'DOCUMENTS': {
        'search_query': DocumentsSearchQuery,
        'serializer': DocumentsESSerializer
    }
}


class SearchAllQuery(object):
    def search(self, query):
        results = {}
        for search_key, search_mapping in SEARCH_MAPPINGS.items():
            search_result = search_mapping['search_query'](query).search()
            results[search_key] = search_mapping['serializer'](search_result).data
        return results
