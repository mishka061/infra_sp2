from csv import DictReader

from django.core.management.base import BaseCommand

from api_yamdb.reviews.models import (Category,
                                      Genre,
                                      User,
                                      Title,
                                      Review,
                                      Comment,
                                      GenreTitle)


class Command(BaseCommand):
    help = 'Загрузка данных из директории data.'

    def handle(self, *args, **options):
        for row in DictReader(open('static/data/category.csv')):
            Category(id=row['id'], name=row['name'], slug=row['slug']).save()

        for row in DictReader(open('static/data/genre.csv')):
            Genre(id=row['id'], name=row['name'], slug=row['slug']).save()

        for row in DictReader(open('static/data/users.csv')):
            User(id=row['id'], username=row['username'], role=row['role'],
                 bio=row['bio'], first_name=row['first_name'],
                 last_name=row['last_name']).save()

        for row in DictReader(open('static/data/titles.csv')):
            category = Category.objects.get(pk=row['category'])
            Title(id=row['id'], name=row['name'],
                  year=row['year'], category=category).save()

        for row in DictReader(open('static/data/review.csv')):
            title = Title.objects.get(pk=row['title_id'])
            author = User.objects.get(pk=row['author'])
            Review(id=row['id'], title=title,
                   text=row['text'], author=author,
                   score=row['score'], pub_date=row['pub_date']).save()

        for row in DictReader(open('static/data/comments.csv')):
            review = Review.objects.get(pk=row['review_id'])
            author = User.objects.get(pk=row['author'])
            Comment(id=row['id'], review=review,
                    text=row['text'], author=author,
                    pub_date=row['pub_date']).save()

        for row in DictReader(open('static/data/genre_title.csv')):
            genre = Genre.objects.get(pk=row['genre_id'])
            title = Title.objects.get(pk=row['title_id'])
            GenreTitle(id=row['id'], title=title, genre=genre).save()

        self.stdout.write(self.style.SUCCESS('Импорт успешно завершен.'))
