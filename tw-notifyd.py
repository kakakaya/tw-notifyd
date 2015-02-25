#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: kakakaya, Date: Thu Feb 26 05:23:07 2015

# import os
# import sys
from pprint import pprint
import json
import twitter as tw


def main():
    with open('key.json') as key:
        keys = key.read()
    data = json.loads(keys)
    pprint(data)
    CONSUMER_KEY = data["consumerKey"]
    CONSUMER_SECRET = data["consumerSecret"]
    ACCESS_TOKEN = data["accessToken"]
    ACCESS_TOKEN_SECRET = data["accessSecret"]

    auth = tw.OAuth(
        ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
        CONSUMER_KEY, CONSUMER_SECRET
    )
    twitter_stream = tw.TwitterStream(
        auth=auth,
        domain="userstream.twitter.com"
    )
    for msg in twitter_stream.user():
        print(msg)

    pass

if __name__ == "__main__":
    main()
