# coding: utf-8
import slackweb
import config

WEBHOOK_URL = config.SLACK["WEBHOOK_URL"]

slack = slackweb.Slack(WEBHOOK_URL)


def simple_notify(text):
    slack.notify(text=text)


def rich_notify(title, text, color):
    attachments = []
    attachments.append({
        'title': title,
        'text': text,
        'color': color
    })
    slack.notify(attachments=attachments)


def info(title, text):
    rich_notify(title, text, 'good')


def warn(title, text):
    rich_notify(title, text, 'warning')


def error(title, text):
    rich_notify(title, text, 'danger')
