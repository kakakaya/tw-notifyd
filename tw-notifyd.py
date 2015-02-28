#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: kakakaya, Date: Thu Feb 26 05:23:07 2015

# import os
# import sys
from pprint import pprint
import json
import twitter as tw


def loadConfig():
    pass


def matchRule(rules, message):
    if "event" in message.keys():
        return True
    else:
        return False


def notifyTweet(rules, message):
    pass


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
    rules = loadConfig()
    for msg in twitter_stream.user():
        if matchRule(rules, msg):
            notifyTweet(rules, msg)

if __name__ == "__main__":
    main()
