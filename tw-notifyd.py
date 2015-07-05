#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: kakakaya, Date: Thu Feb 26 05:23:07 2015

# import os
# import sys
# import codecs
from pprint import pprint as pp
from pymongo import MongoClient, DESCENDING
import json
import twitter as tw
# import sqlite3
import argparse
import datetime


def loadConfig():
    # メモ:
    # 強い監視 := 画像も保存、など
    # 弱い監視 := テキスト本文のみ
    # 無視 := 保存しない
    # {{強, 弱}い監視, 無視}をする対象の{アカウント、発言}を分類できるようにする
    return {}


def reformDate(created_at):
    # Thu Mar 12 15:54:41 +0000 2015
    time = datetime.datetime.strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y")
    return time.strftime("(%y/%m/%d_%H:%M:%S)")


def matchRule(rules, message):
    if "text" not in message.keys():
        return True
    else:
        return False


def deleteNotify(msg, db):
    delId = msg["delete"]["status"]["id"]
    tweets = db.tweets
    tweets.create_index([("id", DESCENDING)])
    delList = list(tweets.find({"id": delId}))
    if len(delList) == 1:
        deletedMsg = delList[0]
        created_at = reformDate(deletedMsg["created_at"])
        print "[DEL]"+created_at+" @"+deletedMsg["user"]["screen_name"]+": ", deletedMsg["text"]
        # notifyTweet("[DEL] @"+deletedMsg["user"]["screen_name"]+": "+deletedMsg["text"])
    else:
        # print "[DEL] Unknown ID:", delId
        pass


def favoriteNotify(msg):
    created_at = reformDate(msg["created_at"])
    print "[FAV]"+created_at+" @"+msg["source"]["screen_name"]+" to @"+msg["target"]["screen_name"]


def notifyTweet(tweet):
    pass


def loop(auth, args):
    client = MongoClient()
    db = client["tw-notifyd_tweet"]
    tweets = db.tweets
    twitter_stream = tw.TwitterStream(
        auth=auth,
        domain="userstream.twitter.com"
    )
    rules = loadConfig()
    # argsに基いてrulesの上書きを行う
    if args.v:
        rules["verbose"] = True
    print "[INFO]Started loop", rules
    for msg in twitter_stream.user():
        # if matchRule(rules, msg):
        #     # notifyTweet(rules, msg)
        #     pprint(msg),
        #     print len(msg)
        #     pass
        if "text" in msg.keys():
            # seems to be a normal tweet
            tweets.insert(msg)
        elif "delete" in msg.keys():
            # deleted tweet
            deleteNotify(msg, db)
            if rules["verbose"]:
                pp(msg)
        elif "event" in msg.keys():
            event_type = msg["event"]
            if event_type == "favorite":
                favoriteNotify(msg)
                if rules["verbose"]:
                    pp(msg)
            elif event_type == "favorited_retweet":
                pass
            elif event_type == "retweetd_retweet":
                pass
            elif event_type == "follow":
                pass
            else:
                print "unknown event",
                pp(msg)
        elif "friends" in msg.keys():
            pass
        elif "hangup":
            # 上に繋げてやりなおす
            pass
        else:
            print "unknown type",
            pp(msg)


def main():
    # sys.stdout = codecs.lookup("utf_8")[-1](sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()

    with open('key.json') as key:
        keys = key.read()
    data = json.loads(keys)
    # pprint(data)
    CONSUMER_KEY = data["consumerKey"]
    CONSUMER_SECRET = data["consumerSecret"]
    ACCESS_TOKEN = data["accessToken"]
    ACCESS_TOKEN_SECRET = data["accessSecret"]

    auth = tw.OAuth(
        ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
        CONSUMER_KEY, CONSUMER_SECRET
    )
    while True:
        loop(auth, args)


if __name__ == "__main__":
    main()
