'''
    Implements a book library
'''
import grok

from authors import Authors
from library import Library
from layout import HeaderMgr, ContentMgr, LeftNavMgr
from interfaces import ISiteIndex, ISiteRoot

class PAT(grok.Application, grok.Container):
    ''' Putting it All Together: A book library'''
    grok.implements(ISiteRoot, ISiteIndex)
    site_title = u'Publication Archiving Tool'

    def __init__(self):
        super(PAT, self).__init__()
        self['authors'] = Authors()
        self['library'] = Library()

    def authCount(self):
        return len(self['authors'])

    def bookCount(self):
        return len(self['library'])

class Header(grok.Viewlet):
    ''' Fills the slot for the dashboard header '''
    grok.viewletmanager(HeaderMgr)
    grok.context(PAT)

class Content(grok.Viewlet):
    ''' Fills the dashboard content slot '''
    grok.viewletmanager(ContentMgr)
    grok.context(PAT)

class LeftNav(grok.Viewlet):
    ''' Fills the left navigation slot '''
    grok.viewletmanager(LeftNavMgr)
    grok.context(PAT)

