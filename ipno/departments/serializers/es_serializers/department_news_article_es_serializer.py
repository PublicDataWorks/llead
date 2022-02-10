from shared.serializers.es_serializers.base_es_serializer import BaseESSerializer
from news_articles.models import NewsArticle
from shared.serializers import NewsArticleSearchSerializer


class DepartmentNewsArticlesESSerializer(BaseESSerializer):
    serializer = NewsArticleSearchSerializer
    model_klass = NewsArticle

    def get_queryset(self, ids):
        return self.model_klass.objects.select_related(
            'source'
        ).filter(
            id__in=ids
        )
