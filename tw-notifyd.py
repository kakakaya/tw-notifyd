#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author: kakakaya, Date: Thu Feb 26 05:23:07 2015

import os
# import sys
# import codecs
from pprint import pprint as pp
from pymongo import MongoClient, DESCENDING
import json
import twitter as tw
# import sqlite3
import argparse
from datetime import datetime, timedelta


def loadConfig(args):
    # メモ:
    # 強い監視 := 画像も保存、など
    # 弱い監視 := テキスト本文のみ
    # 無視 := 保存しない
    # {{強, 弱}い監視, 無視}をする対象の{アカウント、発言}を分類できるようにする
    config_path = os.path.dirname(__file__)+"/config.json"  # 仮、そのうち指定できるようにする
    with open(config_path) as key:
        keys = key.read()
        conf = json.loads(keys)

    # argsの内容に応じて上書きをする
    if args.v:
        conf["verbose"] = True

    return conf


def reformDate(created_at):
    u"""Thu Mar 12 15:54:41 +0000 2015
    みたいな形式から
    2015/03/13_00:54:41
    みたいな形式に変える
    """
    time = datetime.strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y") + timedelta(hours=9)
    return time.strftime("%y/%m/%d_%H:%M:%S")


def matchRule(rules, message):
    if "text" not in message.keys():
        return True
    else:
        return False


def hangupNotify():
    time = datetime.now().strftime("%y/%m/%d_%H:%M:%S")
    print("[HANGUP]", time)


def deleteNotify(msg, db):
    delId = msg["delete"]["status"]["id"]
    tweets = db.tweets
    delList = list(tweets.find({"id": delId}))
    if len(delList) == 1:
        deletedMsg = delList[0]
        created_at = reformDate(deletedMsg["created_at"])
        print("[DEL]", created_at, "@"+deletedMsg["user"]["screen_name"]+": ", deletedMsg["text"])
        # notifyTweet("[DEL] @"+deletedMsg["user"]["screen_name"]+": "+deletedMsg["text"])
    else:
        # print("[DEL] Unknown ID:", delId)
        pass


def favoriteNotify(msg):
    created_at = reformDate(msg["created_at"])
    print("[FAV]"+created_at+" @"+msg["source"]["screen_name"]+" to @"+msg["target"]["screen_name"])


def notifyTweet(tweet):
    pass


def loop(auth, conf):
    client = MongoClient()
    db = client["tw-notifyd_tweet"]
    tweets = db.tweets
    tweets.create_index([("id", DESCENDING)])
    twitter_stream = tw.TwitterStream(
        auth=auth,
        domain="userstream.twitter.com"
    )
    print("[INFO]Started loop", conf)

    try:
        for msg in twitter_stream.user():
            # if matchRule(conf, msg):
            #     # notifyTweet(conf, msg)
            #     pprint(msg),
            #     print(len(msg))
            #     pass
            if "text" in msg.keys():
                # seems to be a normal tweet
                tweets.insert(msg)
            elif "delete" in msg.keys():
                # deleted tweet
                deleteNotify(msg, db)
                if conf["verbose"]:
                    pp(msg)
            elif "event" in msg.keys():
                event_type = msg["event"]
                if event_type == "favorite":
                    favoriteNotify(msg)
                    if conf["verbose"]:
                        pp(msg)
                elif event_type == "favorited_retweet":
                    pass
                elif event_type == "retweeted_retweet":
                    pass
                elif event_type == "follow":
                    pass
                else:
                    pp(msg)
            elif "friends" in msg.keys():
                pass
            elif "hangup":
                # 上に繋げてやりなおす
                hangupNotify()
            else:
                pp(msg)

    except ValueError:
        # JSONの読み取り失敗
        pass


def main():
    # sys.stdout = codecs.lookup("utf_8")[-1](sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true')
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()
    conf = loadConfig(args)     # 引数で設定を適当に上書く

    # pprint(data)
    CONSUMER_KEY = conf["consumerKey"]
    CONSUMER_SECRET = conf["consumerSecret"]
    ACCESS_TOKEN = conf["accessToken"]
    ACCESS_TOKEN_SECRET = conf["accessSecret"]

    while True:
        auth = tw.OAuth(
            ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
            CONSUMER_KEY, CONSUMER_SECRET
        )
        loop(auth, conf)


if __name__ == "__main__":
    main()
