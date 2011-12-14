"""Guardian Search web application

A small, simple web application which allows a user to search for
articles on the Guardian's website (http://www.guardian.co.uk) using
simple queries.

The aim of this project is primarily to learn about the Guardian's
Open Platform Content API (http://www.guardian.co.uk/open-platform)
and Google's App Engine infrastructure and webapp2 framework.  The
focus is on back end development, so the front end interface is bare.

"""

import os
import urllib
import webapp2
import jinja2
import json

from google.appengine.api import urlfetch
from aux import generate_nav_urls
from errors import HTTPError

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):
    """Front page of the search interface."""
    def get(self):
        template_values = {}
        template = jinja_environment.get_template('index.html')
        self.response.write(template.render(template_values))

class Search(webapp2.RequestHandler):
    """Searches for the phrase as specified by an encoded
    URL. Displays results."""
    def get(self):
        q = self.request.get('q') # query
        page = self.request.get('page', default_value='1') # page number

        client = Client()
        # Search for the results.
        results = client.search(q=q, page=page,
                                show_fields='headline,byline,standfirst')

        # Get the nostname that this instance is running on.
        host = self.request.headers.get('host', 'no host')

        # Generate navigation links for the results page.
        nav_urls = generate_nav_urls(host, urllib.quote_plus(q), results)

        # Render and display the results.
        template_values = {
            'total': results.total(),
            'current_page': results.current_page(),
            'pages': results.pages(),
            'numbered_results': results.numbered_results(),
            'url_prev_page': nav_urls['prev'],
            'url_next_page': nav_urls['next'],
        }
        template = jinja_environment.get_template('search.html')
        self.response.write(template.render(template_values))

class Client(object):
    base_url = 'http://content.guardianapis.com/search'

    def __init__(self):
        pass

    def _fetch(self, url):
        """Fetch results from JSON endpoint and return as dict."""
        f = urlfetch.fetch(url)
        if f.status_code != 200:
            raise HTTPError(f.status_code, f.headers)
        return json.loads(f.content)

    def search(self, **kwargs):
        """Search for items, returning results as an instance of
        Results.  Parameters for the URL fields are passed in as
        **kwargs, for example, client.search(q='tomatoes').
        """
        url = '%s?%s' % (self.base_url,
                         urllib.urlencode(self.fix_kwargs(kwargs), doseq=True))
        data = self._fetch(url)
        return Results(data)

    def fix_kwargs(self, kwargs):
        kwargs2 = dict( [ (k.replace('_', '-'), v)
                          for k, v in kwargs.items() ] )
        kwargs2['format'] = 'json'
        # kwargs2['api_key'] = self.api_key
        return kwargs2

class Results(object):
    def __init__(self, data):
        self.data = data

    def total(self):
        """Total number of items found."""
        return int(self.data['response']['total'])

    def start_index(self):
        """Number of first item on this page."""
        return int(self.data['response']['startIndex'])

    def page_size(self):
        """Maximum number of results returned per page."""
        return int(self.data['response']['pageSize'])

    def current_page(self):
        """Page number of current page."""
        return int(self.data['response']['currentPage'])

    def pages(self):
        """Total number of pages found."""
        return int(self.data['response']['pages'])

    def results(self):
        """Items found for this page, returned as a list of results."""
        return self.data['response']['results']

    def numbered_results(self):
        """Items found for this page, returned as a list of tuples,
        where the first element is the number of that item, and the
        second item is the corresponding result.
        """
        r = zip(range(self.start_index(),
                      self.start_index() + len(self.results())),
                self.results())
        return r

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/search', Search)],
                              debug=True)
