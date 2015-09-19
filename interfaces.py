from zope.component import Interface
from zope import schema

class ISiteRoot(Interface):
    ''' Marker for the main site root '''
class ISiteIndex(Interface):
    ''' Marker for models which render the site index '''

class ISBNInvalid(schema.ValidationError):
    ''' This does not appear to be a valid ISBN number. '''

def check_isbn(isbn):
    import re
    if re.match(r"[0-9]+[- ][0-9]+[- ][0-9]+[- ][0-9]*[- ]*[xX0-9]", isbn):
        return True
    raise(ISBNInvalid)

class IAuthor(Interface):
    ''' Authors implement this interface '''
    name = schema.TextLine(title=u'Name:', description=u'The name of this author')
    born = schema.Date(title=u'Date of birth:', description=u"This author's birth date",
                       required=False)
    died = schema.Date(title=u'Date of death:', description=u"If deceased, the date",
                       required=False)
    country = schema.Choice(title=u'Country of origin:',
                            description=u"Where is this author from?",
                            vocabulary=u'Countries',
                            required=False)

class IBook(Interface):
    ''' This defines the fields we store for a book '''
    title = schema.TextLine(title=u'Title:', description=u'This book title')
    authors = schema.List(title=u'Authors:', description=u'Authors for this book',
                          value_type=schema.Choice(title=u'Author:', description=u'An author',
                                                   vocabulary=u'BookAuthors'),
                          default=[])
    subject = schema.TextLine(title=u'Subject:', description=u'The subject of this book')
    publisher = schema.TextLine(title=u'Publisher:', description=u'The name of the publisher')
    pub_date = schema.Date(title=u'Publication date:', description=u'The date of publication')
    isbn = schema.TextLine(title=u'ISBN:', description=u'ISBN Number', constraint=check_isbn,
                           required=False)
    notes = schema.Text(title=u'Notes:', description=u'General notes',
                        required=False)

    def authorStrings(): #@NoSelf
        ''' The concatinated list of authors '''

class ISearch(Interface):
    ''' A simple search box '''
    search = schema.TextLine(title=u'Search:', description=u'A search field')

    def do_search(self, **kw):
        ''' Searches for specified field values '''
    def results(self):
        ''' Returns the results of the search '''
