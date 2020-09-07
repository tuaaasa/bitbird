# coding: utf-8
import slackweb
import config

WEBHOOK_URL = config.SLACK["WEBHOOK_URL"]

slack = slackweb.Slack(WEBHOOK_URL)


def notify(text):
    slack.notify(text=text)
