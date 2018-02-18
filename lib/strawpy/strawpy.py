#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import webbrowser

api_url = 'http://strawpoll.me/api/v2/polls'


def get_poll(poll_id):
    """ Get a strawpoll.

    Example:

        poll = strawpy.get_poll('11682852')

    :param poll_id:
    :return: strawpy.Strawpoll object
    """
    return StrawPoll(requests.get('{api_url}/{poll_id}'.format(api_url=api_url, poll_id=poll_id)))


def create_poll(title, options, multi=True, permissive=True, captcha=False, dupcheck='normal'):
    """ Create a strawpoll.

    Example:

        new_poll = strawpy.create_poll('Is Python the best?', ['Yes', 'No'])

    :param title:
    :param options:
    :param multi:
    :param permissive:
    :param captcha:
    :param dupcheck:
    :return: strawpy.Strawpoll object
    """
    query = {
        'title': title,
        'options': options,
        'multi': multi,
        'permissive': permissive,
        'captcha': captcha,
        'dupcheck': dupcheck
    }
    return StrawPoll(requests.post('http://strawpoll.me/api/v2/polls', data=json.dumps(query)))


class StrawPollException(Exception):

    def __init__(self, error, response):
        self.error = error
        self.response = response
        self.headers = response.headers

    def __str__(self):
        return self.error

    def __eq__(self, other):
        if isinstance(other, "".__class__):
            return self.error == other
        elif isinstance(other, self.__class__):
            return self.error == other.error and self.headers == other.headers
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return super(StrawPollException).__hash__()


def raise_status(response):
    """Raise an exception if the request did not return a status code of 200.

    :param response: Request response body
    """
    if response.status_code != 200:
        if response.status_code == 401:
            raise StrawPollException('Unauthorized', response)
        elif response.status_code == 403:
            raise StrawPollException('Forbidden', response)
        elif response.status_code == 404:
            raise StrawPollException('Not Found', response)
        else:
            response.raise_for_status()


class StrawPoll(object):

    def __init__(self, strawpoll_response):
        """ StrawPoll instance.

        Example:

            poll = strawpy.get_poll('11682852')

            print poll
            print poll.id
            print poll.title
            print poll.votes
            print poll.options
            print poll.captcha
            print poll.dupcheck
            print poll.results
            print poll.results_with_percent
            print poll.url
            print poll.results_url
            poll.refresh()
            poll.open(results=False)

        :param strawpoll_response:
        """
        raise_status(strawpoll_response)
        self.status_code = strawpoll_response.status_code
        self.response_json = strawpoll_response.json()
        self.id = self.response_json['id']
        self.title = self.response_json['title']
        self.options = self.response_json['options']
        self.votes = self.response_json['votes']
        self.captcha = self.response_json['captcha']
        self.dupcheck = self.response_json['dupcheck']
        self.url = 'https://www.strawpoll.me/{id}'.format(id=self.id)
        self.results_url = 'https://www.strawpoll.me/{id}/r'.format(id=self.id)

    def __str__(self):
        return 'strawpy.StrawPoll object for {title} [{id}]'.format(title=self.title, id=self.id)

    def __repr__(self):
        return 'strawpy.StrawPoll(resonse for {title})'.format(title=self.title)

    @property
    def results(self):
        """ Zip options and votes together.

        :return: List of tuples (option, votes)
        """
        return zip(self.options, self.votes)

    @property
    def results_with_percent(self):
        """ Zip options, votes and percents (as integers) together.

        :return: List of tuples (option, votes, percent)
        """
        percents = [int(float(v) / sum(self.votes) * 100) if sum(self.votes) > 0 else 0 for v in self.votes]
        return zip(self.options, self.votes, percents)

    def open(self, results=False):
        """ Open the strawpoll in a browser. Can specify to open the main or results page.

        :param results: True/False
        """
        webbrowser.open(self.results_url if results else self.url)

    def refresh(self):
        """ Refresh all class attributes.

        """
        strawpoll_response = requests.get('{api_url}/{poll_id}'.format(api_url=api_url, poll_id=self.id))
        raise_status(strawpoll_response)
        self.status_code = strawpoll_response.status_code
        self.response_json = strawpoll_response.json()
        self.id = self.response_json['id']
        self.title = self.response_json['title']
        self.options = self.response_json['options']
        self.votes = self.response_json['votes']
        self.captcha = self.response_json['captcha']
        self.dupcheck = self.response_json['dupcheck']
        self.url = 'https://www.strawpoll.me/{id}'.format(id=self.id)
        self.results_url = 'https://www.strawpoll.me/{id}/r'.format(id=self.id)
