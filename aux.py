def generate_nav_urls(host, query, results):
    """Generate links to previous and next pages for navigation."""
    cur_page = results.current_page()
    if cur_page > 1:
        url_prev_page = 'http://' + host + '/search?q=' + query \
                        + '&page=' + str(cur_page - 1)
    else:
        url_prev_page = None

    if cur_page < results.pages():
        url_next_page = 'http://' + host + '/search?q=' + query \
                        + '&page=' + str(cur_page + 1)
    else:
        url_next_page = None

    return {'prev': url_prev_page, 'next': url_next_page}
