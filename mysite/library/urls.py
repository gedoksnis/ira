from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authors/', views.authors, name='authors'),
    path('authors/<int:author_id>', views.author, name='author'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('books/<int:pk>', views.BookDetailView.as_view(), name='book_detail'),
    path('search/', views.search, name='search'),
    path('mybooks/', views.LoanBooksListView.as_view(), name='my-borrowed'),
    path('mybooks/<int:pk>', views.BookByUserDetailView.as_view(), name='mybook'),
    path('mybooks/<int:pk>/update', views.BookByUserUpdateView.as_view(), name='my-book-update'),
    path('mybooks/<int:pk>/delete', views.BookByUserDeleteView.as_view(), name='my-book-delete'),
    path('mybooks/new', views.BookByUserCreateView.as_view(), name='my-new-book'),
    path('register/', views.register, name='register'),
    path('profile/', views.profilis, name='profile'),
]
