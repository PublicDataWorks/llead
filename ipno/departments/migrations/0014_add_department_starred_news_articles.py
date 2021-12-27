# Generated by Django 3.1.13 on 2021-12-24 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_articles', '0022_rename_field_custom_matching_name'),
        ('departments', '0013_add_department_starred_officers'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='starred_news_articles',
            field=models.ManyToManyField(blank=True, related_name='starred_departments', to='news_articles.NewsArticle'),
        ),
    ]
