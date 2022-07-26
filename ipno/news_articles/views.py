from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from news_articles.models import NewsArticle
from shared.serializers import NewsArticleSerializer
from news_articles.constants import NEWS_ARTICLES_LIMIT


class NewsArticlesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        news_articles = NewsArticle.objects.select_related('source').filter(
            matched_sentences__officers__isnull=False,
            is_hidden=False
        ).order_by(
            '-published_date',
        ).distinct()[:NEWS_ARTICLES_LIMIT]

        serializer = NewsArticleSerializer(news_articles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def hide(self, request, pk=None):
        queryset = NewsArticle.objects.all()
        news_article = get_object_or_404(queryset, pk=pk)

        news_article.is_hidden = True
        news_article.save()
        return Response({
            'detail': 'the news articles is hidden'
        })
