'''  A library is a container which holds a set of books
'''
import grok
from interfaces import IBook, ISearch, ISiteIndex, ISiteRoot
from layout import HeaderMgr, ContentMgr, LeftNavMgr
from pagedsearch import PagedSearchAdapter
from zope.schema.fieldproperty import FieldProperty
from zope.session.interfaces import ISession
from zope.component import getMultiAdapter

class Book(grok.Model):
    ''' A book is defined by an IBook interface '''
    grok.implements(IBook, ISiteIndex)
    site_title = u'Book Detail'

    authors = FieldProperty(IBook['authors'])
    title = FieldProperty(IBook['title'])
    subject = FieldProperty(IBook['subject'])
    publisher = FieldProperty(IBook['publisher'])
    pub_date = FieldProperty(IBook['pub_date'])
    isbn = FieldProperty(IBook['isbn'])
    notes = FieldProperty(IBook['notes'])

    _key = None
    def key(self, val=None):
        if val: self._key = int(val)
        if self._key: return str(self._key)

    def __init__(self, authors=None, title=None, subject=None, publisher=None,
                 pub_date=None, isbn=None, notes=None):
        super(Book, self).__init__()
        if authors: self.authors = authors;
        if title: self.title = title;
        if subject: self.subject = subject
        if publisher: self.publisher = publisher
        if pub_date: self.pub_date = pub_date
        if isbn: self.isbn = isbn
        if notes: self.notes = notes

    def authorStrings(self):
        if self.authors and len(self.authors): return "|".join([a.name for a in self.authors])
        return ""

class Library(grok.Container):
    ''' A library is a collection of books '''
    grok.implements(ISearch, ISiteIndex)
    site_title = u'Library'
    search = FieldProperty(ISearch['search'])

    _seq = 0
    def next_seq(self):
        self._seq += 1
        return self._seq

    grok.traversable('new')
    def new(self):
        return Book()

class BookIndex(grok.Indexes):
    ''' A catalogue of books in our library '''
    grok.site(ISiteRoot)
    grok.context(IBook)
    grok.name('bookindex')

    title         = grok.index.Text() #@UndefinedVariable
    subject       = grok.index.Text() #@UndefinedVariable
    publisher     = grok.index.Text() #@UndefinedVariable
    pub_date      = grok.index.Field() #@UndefinedVariable
    isbn          = grok.index.Text() #@UndefinedVariable
    authorStrings = grok.index.Text() #@UndefinedVariable

class LibrarySearch(PagedSearchAdapter):
    ''' An adapter which does library searches and returns results '''
    grok.adapts(Library, grok.IBrowserRequest)
    catalog = 'bookindex'

class EditBook(grok.EditForm):
    ''' A book editor '''
    grok.context(Book)

    form_fields = grok.Fields(IBook)
    def book_in_library(self, _act=None):
        book = self.context
        library = book.__parent__
        return book.key() in library

    @grok.action(u'Update')
    def update_book(self, **data):
        if not self.book_in_library():
            library = self.context.__parent__
            key = str(library.next_seq())
            book = library[key] = Book(**data)
            book.key(key)
            self.redirect(grok.url(self.request, book))
        self.applyData(self.context, **data)

    @grok.action(u'Delete', condition=book_in_library)
    def delete_book(self, **data):
        book = self.context
        self.redirect(grok.url(self.request, book, 'delete'))

class Delete(grok.View):
    ''' A view to delete a book '''
    grok.context(Book)
    def render(self):
        index = getMultiAdapter((self.context, self.request), name=u'index')
        index.deleting = True
        return index()

class DeleteBook(grok.EditForm):
    ''' A book deletion confirmation '''
    grok.context(Book)

    form_fields = grok.Fields(IBook, for_display=True)
    @grok.action(u"Confirm Delete")
    def delete(self, **data):
        library = self.context.__parent__
        key = self.context.key()
        if key in library:
            self.context.authors = []
            del library[key]
        self.redirect(grok.url(self.request, library))

    @grok.action(u"Don't delete this book!", validator=lambda *a, **k: {})
    def cancel(self, **data):
        book = self.context
        self.redirect(grok.url(self.request, book))

class SearchForm(grok.EditForm):
    ''' Searches our book catalogue '''
    grok.context(Library)
    form_fields = grok.Fields(ISearch)
    search = None

    def update(self):
        self.search = getMultiAdapter((self.context, self.request), ISearch).do_search

    @grok.action('Title')
    def find_title(self, **data):
        self.search(title=data['search'])
    @grok.action('Subject')
    def find_subject(self, **data):
        self.search(subject=data['search'])
    @grok.action('Authors')
    def find_authors(self, **data):
        self.search(authorList=data['search'])
    @grok.action('Publisher')
    def find_publishers(self, **data):
        self.search(publisher=data['search'])
    @grok.action('ISBN')
    def find_isbn(self, **data):
        self.search(isbn=data['search'])

class Header(grok.Viewlet):
    ''' Library section header '''
    grok.viewletmanager(HeaderMgr)
    grok.context(Library)

class Content(grok.Viewlet):
    ''' Library section content '''
    grok.viewletmanager(ContentMgr)
    grok.context(Library)

    def update(self):
        search = self.search = getMultiAdapter((self.context, self.request), ISearch)
        if 'prevPage' in self.request: search.prevPage()
        if 'nextPage' in self.request: search.nextPage()

    def book_results(self):
        return self.search.results()

class LeftNav(grok.Viewlet):
    ''' Library section navigation '''
    grok.viewletmanager(LeftNavMgr)
    grok.context(Library)

class Book_Header(grok.Viewlet):
    ''' Book editor header '''
    grok.viewletmanager(HeaderMgr)
    grok.context(Book)

class Book_Content(grok.Viewlet):
    ''' Book editor content '''
    grok.viewletmanager(ContentMgr)
    grok.context(Book)

class Book_LeftNav(grok.Viewlet):
    ''' Book editor navigation '''
    grok.viewletmanager(LeftNavMgr)
    grok.context(Book)

