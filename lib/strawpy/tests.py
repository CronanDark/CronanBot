#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import strawpy


def tests():
    date = time.localtime(time.time())
    time_stamp = "%d-%d-%d" % (date[1], date[2], (date[0] % 100))
    start = time.time()
    # Test getting a poll
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
    # Test creating a poll
    new_poll = strawpy.create_poll('[{ts}] Is Python the best?'.format(ts=time_stamp), ['Yes', 'No'])
    print new_poll
    print new_poll.id
    print new_poll.title
    print new_poll.votes
    print new_poll.options
    print new_poll.captcha
    print new_poll.dupcheck
    print new_poll.results
    print new_poll.results_with_percent
    print new_poll.url
    print new_poll.results_url
    poll.refresh()
    new_poll.open(results=False)
    # Output time
    duration = time.time() - start
    print 'Ran tests in: {duration}'.format(duration=time.strftime("%H:%M:%S", time.gmtime(duration)))

if __name__ == '__main__':
    tests()
