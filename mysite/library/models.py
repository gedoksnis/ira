import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from tinymce.models import HTMLField
from PIL import Image
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Genre(models.Model):
    name = models.CharField('Pavadinimas', max_length=100, help_text='Nurodykite žanro pavadinimą (pvz. detektyvas)')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Žanras'
        verbose_name_plural = 'Žanrai'

class Book(models.Model):
    """Modelis reprezentuojantis knygą"""
    title = models.CharField(_('Title'), max_length=200)
    author = models.ForeignKey('Author', max_length=200, null=True, on_delete=models.SET_NULL, related_name='books')
    summary = models.TextField(_('Summary'), max_length=1000, help_text=_('A short book description'))
    isbn = models.CharField('ISBN', max_length=13, help_text=_('A unique 13 digits ISBN number'))
    genre = models.ManyToManyField(Genre, help_text=_("Please select book's genre(s)"))
    cover = models.ImageField(_('Cover'), upload_to='covers', null=True)

    def __str__(self):
        return self.title

    def display_genre(self):
        return ','.join(genre.name for genre in self.genre.all()[:3])

class BookInstance(models.Model):
    """Modelis aprašantis konkrečios knygos kopijos būseną"""
    uuid = models.UUIDField(default=uuid.uuid4, help_text='Unikalus ID knygos kopijai')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    due_back = models.DateField('Bus prieinama', null=True, blank=True)
    reader = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    LOAN_STATUS = (
        ('a', 'Administruojama'),
        ('p', 'Paimta'),
        ('g', 'Galima paimti'),
        ('r', 'Rezervuota')
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, default='p', help_text='Statusas', blank=True)

    class Meta:
        ordering = ['due_back']

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    def __str__(self):
        return f'{self.id} {self.book.title}'

    # def get_absolute_url(self):
    #     return reverse('book_detail', args=[str(self.id)])

class Author(models.Model):
    """Modelis reprezentuojantis knygos autorių."""
    first_name = models.CharField('Vardas', max_length=80)
    last_name = models.CharField('Pavardė', max_length=80)
    description = HTMLField()
    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Nurodo konkretaus autoriaus galutinį adresą"""
        return reverse('author', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    def display_books(self):
        return ', '.join(book.title for book in self.books.all()[:3])

    display_books.short_description = 'Knygos'

class BookReview(models.Model):
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField('Atsiliepimas', max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)


class Profilis(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nuotrauka = models.ImageField(default='default.png', upload_to='profile_pics')

    class Meta:
        verbose_name = 'Profilis'
        verbose_name_plural = 'Profiliai'
    def __str__(self):
        return f"{self.user.username} profilis"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.nuotrauka.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.nuotrauka.path)

