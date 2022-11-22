from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin
from .forms import BookReviewForm, UserUpdateForm, ProfilisUpdateForm, UserBookInstanceCreateForm
from .models import Book, BookInstance, Author
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

# Create your views here.

def index(request):

    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # laisvos knygos
    num_instances_available = BookInstance.objects.filter(status__exact='g').count()

    num_authors = Author.objects.all().count()
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books':num_books,
        'num_instances':num_instances,
        'num_instances_available':num_instances_available,
        'num_authors':num_authors,
        'num_visits':num_visits
    }

    return render(request, 'library/index.html', context=context)


def authors(request):
    paginator = Paginator(Author.objects.all(), 3)
    page_number = request.GET.get('page')
    paged_authors = paginator.get_page(page_number)
    context = {
        'authors': paged_authors
    }
    return render(request, 'library/authors.html', context=context)


# def books(request):
#     books = Book.objects.all()
#     context = {
#         'books': books
#     }
#     return render(request, 'library/books.html', context=context)


class BookListView(generic.ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'my_book_list'
    paginate_by = 2


class BookDetailView(FormMixin, generic.DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    form_class = BookReviewForm

    class Meta:
        ordering = ['title']

    def get_success_url(self):
        return reverse('book_detail', kwargs={'pk': self.object.id})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super(BookDetailView, self).form_valid(form)


def author(request, author_id):
    single_author = get_object_or_404(Author, pk=author_id)
    return render(request, 'library/author.html', {'author': single_author})

def search(request):
    query = request.GET.get('query')
    lt_letters = {'ž': 'z', 'š': 's', 'į':'i'}
    for raide in query:
       if raide in lt_letters.keys():
           print(lt_letters[raide])
    search_results = Book.objects.filter(Q(title__icontains=query) | Q(summary__icontains = query))
    return render(request, 'library/search.html', {'books': search_results, 'query': query})

class LoanBooksListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'library/user_books.html'
    context_object_name = 'mybooks'

    def get_queryset(self):
        return BookInstance.objects.filter(reader=self.request.user).filter(status__exact='p').order_by('due_back')
class BookByUserDetailView(LoginRequiredMixin, generic.DetailView):
    model = BookInstance
    template_name = 'library/user_book.html'

class BookByUserCreateView(LoginRequiredMixin, generic.CreateView):
    model = BookInstance
    # fields = ['book', 'due_back']
    success_url = '/mybooks/'
    template_name = 'library/user_book_form.html'
    form_class = UserBookInstanceCreateForm

    def form_valid(self, form):
        form.instance.reader = self.request.user
        form.instance.status = 'p'
        form.save()
        return super().form_valid(form)

@csrf_protect
def register(request):
    if request.method == 'POST':
        #pasiimti duomenis iš formos
        username = request.POST['username']
        email = request.POST ['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, _('Username %s already exists!') % username)
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, _('Username with %s already exists!') % email)
                    return redirect('register')
                else:
                    User.objects.create_user(username=username, email=email, password=password)
                    return render(request, 'library/welcome.html')
        else:
            messages.error(request, _('Passwords do no match!'))
            return redirect('register')
    return render(request, 'library/register.html')


@login_required
def profilis(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfilisUpdateForm(request.POST, request.FILES, instance=request.user.profilis)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Profilis atnaujintas')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfilisUpdateForm(instance=request.user.profilis)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'library/profilis.html', context)

class BookByUserUpdateView(LoginRequiredMixin, generic.UpdateView, UserPassesTestMixin):
    model = BookInstance
    fields = ['book', 'due_back']
    success_url = '/mybooks/'
    template_name = 'library/user_book_form.html'

    def form_valid(self, form):
        form.instance.reader = self.request.user
        form.save()
        return super().form_valid(form)
    def test_func(self):
        book = self.get_object()
        return self.request.user == book.reader

class BookByUserDeleteView(generic.DeleteView, LoginRequiredMixin, UserPassesTestMixin):
    model = BookInstance
    success_url = '/mybooks/'
    template_name = 'library/userbook_delete.html'
    context_object_name = 'instance'

    def test_func(self):
        book_instance = self.get_object()
        return book_instance.reader == self.request.user