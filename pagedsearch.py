import grok
from interfaces import ISearch, Interface
from zope.component import getUtility
from zope.catalog.interfaces import ICatalog #@UnresolvedImport
from zope.session.interfaces import ISession

class PagedSearchAdapter(grok.MultiAdapter):
    ''' An adapter which does searches and returns results '''
    grok.adapts(Interface, grok.IBrowserRequest)
    grok.implements(ISearch)
    grok.baseclass()

    search  = ''  # The search field (unused)
    limit   = 10  # Limits results to this many items
    offset  = 0   # Position from which we display items
    nPages  = 0   # Number of pages in current search result
    catalog = ''  # Override with applicable catalog name

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._getStatus()  # Read session if it exists

    def _calc_nPages(self):
        return 1 + int((len(self.results(noLimits = True))-1)/self.limit)

    def _getStatus(self):
        session = ISession(self.request)['SearchResults']
        if self.__class__ not in session: session[self.__class__] = {}
        status = session[self.__class__]
        self.nPages = status['nPages'] if 'nPages' in status else self._calc_nPages()
        self.offset = status['offset'] if 'offset' in status else 0

    def _setStatus(self, results=None):
        session = ISession(self.request)['SearchResults']
        if self.__class__ not in session: session[self.__class__] = {}
        status = session[self.__class__]
        if results is not None:
            status['results'] = results
            self.nPages = self._calc_nPages()

        status['offset'] = self.offset
        status['nPages'] = self.nPages

    def next_page(self):
        if self.page() < self.nPages: self.offset += self.limit;
        self._setStatus()

    def prev_page(self):
        if self.page() > 1: self.offset -= self.limit;
        self._setStatus()

    def page(self):  # current page #1 = first
        return 1 + int(self.offset/self.limit)

    def do_search(self, **kw):
        try:
            catalog = getUtility(ICatalog, name=self.catalog)
            results = catalog.searchResults(**kw)
            self.offset = 0
        except:
            results = []
        self._setStatus(results=results)

    def results(self, noLimits = False):
        session = ISession(self.request)['SearchResults']
        status = session[self.__class__]
        results = []
        if 'results' in status:
            results = list(status['results'])
        if not len(results):
            results = self.context.values()

        return results if noLimits else results[self.offset:self.offset+self.limit]

