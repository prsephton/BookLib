'''  Implements a basic site layout
'''
import grok
from interfaces import ISiteIndex, ISearch
from zope.component import getMultiAdapter

class HeaderMgr(grok.ViewletManager):
    ''' Slot for section headers '''
    grok.context(ISiteIndex)

class ContentMgr(grok.ViewletManager):
    ''' Slot for section content '''
    grok.context(ISiteIndex)

class LeftNavMgr(grok.ViewletManager):
    ''' Slot for left navigation bar '''
    grok.context(ISiteIndex)

class Index(grok.View):
    ''' The site index '''
    grok.context(ISiteIndex)
    deleting = False

class Pager(grok.Viewlet):
    ''' Displays a pager for models implementing ISearch '''
    grok.viewletmanager(ContentMgr)
    grok.context(ISearch)
    grok.order(2)

    def update(self, prevPage = None, nextPage = None):
        search = getMultiAdapter((self.context, self.request), ISearch)
        if prevPage: search.prevPage()
        if nextPage: search.nextPage()
        self.nPages = search.nPages
        self.currPage = search.page()
        self.prevPage = self.currPage > 1
        self.nextPage = self.currPage < self.nPages
