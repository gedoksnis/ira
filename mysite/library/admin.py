from django.contrib import admin
from . models import Genre, Book, BookInstance, Author, BookReview, Profilis

# Register your models here.

class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'reader', 'due_back', 'uuid')
    # pridėti redaguotinus laukus
    list_filter = ('status', 'due_back')
    list_editable = ('due_back', 'status')
    # pridėti paiešką
    search_fields = ('uuid', 'book__title')

    fieldsets = (
        (None, {'fields': ('uuid', 'book')}),
        ('Availability', {'fields': ('status', 'due_back', 'reader')}),
    )

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    readonly_fields = ('uuid',)
    can_delete = False
    extra = 0 # išjungia placeholder'ius

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'display_books')


class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'reviewer', 'date_created', 'content')


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
admin.site.register(BookReview, BookReviewAdmin)
admin.site.register(Profilis)
