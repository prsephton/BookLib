'''  Authors list and editor
'''
import grok

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.fieldproperty import FieldProperty
from zope.component import getMultiAdapter

from interfaces import IAuthor, ISiteIndex, ISiteRoot, ISearch
from layout import HeaderMgr, ContentMgr, LeftNavMgr
from pagedsearch import PagedSearchAdapter

class AuthorVocabulary(grok.GlobalUtility):
    ''' A vocabulary of all the authors we know about '''
    grok.implements(IVocabularyFactory)
    grok.name(u'BookAuthors')

    def __call__(self, _context):
        terms = []
        app = grok.getApplication()
        authors = app['authors']
        for author in authors.values():
            title = author.mkTitle()
            token = author.key()
            terms.append(SimpleVocabulary.createTerm(author, token, title))
        return SimpleVocabulary(terms)

class Author(grok.Model):
    ''' An author implements the IAuthor interface '''
    grok.implements(IAuthor, ISiteIndex)
    name    = FieldProperty(IAuthor['name'])
    born    = FieldProperty(IAuthor['born'])
    died    = FieldProperty(IAuthor['died'])
    country = FieldProperty(IAuthor['country'])

    _key = None
    def key(self, val=None):
        if val: self._key = int(val)
        return str(self._key)

    def __init__(self, name=None, born=None, died=None, country=None):
        super(Author, self).__init__()
        if name: self.name = name
        if born: self.born = born
        if died: self.died = died
        if country: self.country = country

    def mkTitle(self):
        title = self.name
        if self.born:
            title = title + '({}'.format(self.born.year)
            if self.died:
                title = title + '-{})'.format(self.died.year)
            else:
                title += ')'
            if self.country:
                title = title + '[{}]'.format(self.country)
        return title


class Authors(grok.Container):
    ''' All of our authors are part of this collection '''
    grok.implements(ISiteIndex, ISearch)
    site_title = u'Authors'
    search = FieldProperty(ISearch['search'])
    grok.traversable('new')

    _seq = 0
    def next_seq(self):
        self._seq += 1
        return self._seq
    def new(self):
        return Author()
    def delete(self, key):
        if key in self.keys(): del self[key]

class AuthorIndex(grok.Indexes):
    ''' This catalogues and indexes all of our authors '''
    grok.site(ISiteRoot)
    grok.context(IAuthor)
    grok.name('authorindex')

    name = grok.index.Text()     #@UndefinedVariable
    born = grok.index.Field()    #@UndefinedVariable
    died = grok.index.Field()    #@UndefinedVariable
    country = grok.index.Text()  #@UndefinedVariable

class AuthorSearch(PagedSearchAdapter):
    ''' An adapter which does library searches and returns results '''
    grok.adapts(Authors, grok.IBrowserRequest)
    catalog = 'authorindex'

class EditAuthor(grok.EditForm):
    ''' A form letting us define an author '''
    grok.context(IAuthor)

    def author_registered(self, act=None):
        author = self.context
        container = self.context.__parent__
        if author.key() in container: return True

    @grok.action(u'Update')
    def update_author(self, **data):
        author = self.context
        container = self.context.__parent__
        self.applyData(author, **data)
        key = author.key()
        if key not in container:
            key = str(container.next_seq())
            author = container[key] = Author(**data)
            author.key(key)
            self.redirect(grok.url(self.request, author))

    @grok.action(u'Delete', condition=author_registered)
    def delete_author(self, **data):
        author = self.context
        self.redirect(grok.url(self.request, author, 'delete'))

class Delete(grok.View):
    ''' A view to delete an author '''
    grok.context(Author)
    def render(self):
        index = getMultiAdapter((self.context, self.request), name=u'index')
        index.deleting = True
        return index()

class DelAuthor(grok.EditForm):
    ''' An author deletion confirmation '''
    grok.context(IAuthor)
    form_fields = grok.Fields(IAuthor, for_display=True)

    @grok.action(u'Confirm Delete')
    def delete_author(self, **data):
        author = self.context
        container = self.context.__parent__
        container.delete(author.key())
        self.redirect(grok.url(self.request, container))

    @grok.action(u"Don't delete", validator=lambda *a, **k: {})
    def cancel(self, **data):
        author = self.context
        self.redirect(grok.url(self.request, author))

class SearchForm(grok.EditForm):
    ''' This form performs a search and returns a list of authors '''
    grok.context(Authors)
    form_fields = grok.Fields(ISearch)
    search = None
    def update(self):
        self.search = getMultiAdapter((self.context, self.request), ISearch).do_search

    @grok.action('Name')
    def find_name(self, **data):
        self.search(name=data['search'])
    @grok.action('Born')
    def find_born(self, **data):
        self.search(born=data['search'])
    @grok.action('Died')
    def find_died(self, **data):
        self.search(died=data['search'])
    @grok.action('Country')
    def find_country(self, **data):
        self.search(country=data['search'])

class Header(grok.Viewlet):
    ''' Authors section header '''
    grok.viewletmanager(HeaderMgr)
    grok.context(Authors)

class Content(grok.Viewlet):
    ''' Authors section content '''
    grok.viewletmanager(ContentMgr)
    grok.context(Authors)
    search = None

    def update(self):
        search = self.search = getMultiAdapter((self.context, self.request), ISearch)
        if 'prevPage' in self.request: search.prevPage()
        if 'nextPage' in self.request: search.nextPage()

    def auth_results(self):
        return self.search.results()

class LeftNav(grok.Viewlet):
    ''' Authors section navigation '''
    grok.viewletmanager(LeftNavMgr)
    grok.context(Authors)

class Author_Header(grok.Viewlet):
    ''' Author editor header '''
    grok.viewletmanager(HeaderMgr)
    grok.context(Author)

class Author_Content(grok.Viewlet):
    ''' Author editor content '''
    grok.viewletmanager(ContentMgr)
    grok.context(Author)

class Author_LeftNav(grok.Viewlet):
    ''' Author editor navigation '''
    grok.viewletmanager(LeftNavMgr)
    grok.context(Author)


