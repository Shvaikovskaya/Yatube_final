from .forms import SearchForm


def search_form(request):
    ''' Добавляет форму поиска.'''
    search_form = SearchForm()
    return {'search_form': search_form}
