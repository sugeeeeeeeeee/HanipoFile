# -*- coding: utf-8 -*-
import slackweb
import re
import pandas as pd
import datetime
import os
import time
import configparser
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

webhook=os.environ.get("webhook")
c=os.environ.get("c")
bot=os.environ.get("bot")
emoji=os.environ.get("emoji")
log=os.environ.get("log")
now=str(datetime.datetime.now().strftime("%Y-%m-%d"))

config = configparser.ConfigParser()
config.read("config.ini")
sleep=config["global"]["sleep"]
columns=config["dataFrame"]["columns"].split(",")
siptitle=config["sip"]["title"]
ahtitle=config["agent"]["headtitle"]
attitle=config["agent"]["tailtitle"]

def main():
  # ファイルを読み込み、ログをParseする
  data=[]
  with open(log) as f:
    pat = re.compile(r'.*{0}.*'.format(now))
    for line in f:
      match = re.search(pat, line)
      if match is None:
        print('Not match')
        return 1
      else:
        data.append(parseLog(line))

  # Parseされたログをpandasでデータフレームに格納
  df=pd.DataFrame(data)
  df.columns=columns

  # サマリ作成 集計
  ## Source IP Summary TOP5
  message = df["sip"].value_counts().head()
  slackSend(siptitle + now, message)

  ## User Agent Count Top5
  message = df["agent"].value_counts().head()
  slackSend(ahtitle + now, message)
  message = df["agent"].value_counts().tail()
  slackSend(attitle + now, message)
  return 0

def parseLog(line):
  # 日付とagent部分のスペースをアンダースコア"_"に変換
  line = re.match(r'(\[.*\])(.+)', line)
  line = line.group(1).replace(" ","_") + line.group(2)
  line = re.match(r'(.+) (\".*\") (.+)', line)
  message = " ".join([line.group(1), line.group(2).replace(" ","_"), line.group(3)])
  return message.split(" ")

def slackSend(title,message):
  message = decolateMessage(title,message)
  s=slackweb.Slack(url=webhook)
  s.notify(text=message, channel=c, username=bot, icon_emoji=emoji, mrkdwn=True)
  time.sleep(int(sleep))
  return 0

def decolateMessage(title,message):
  return title + "\n```" + str(message) + "```\n"

if __name__ == "__main__":
  main()
