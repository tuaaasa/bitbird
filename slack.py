# coding: utf-8
import slackweb
import config

WEBHOOK_URL = config.SLACK["WEBHOOK_URL"]

slack = slackweb.Slack(WEBHOOK_URL)

def simple_notify(text, backtest):
    if not backtest:
        slack.notify(text=text)
    else: 
        return

def info(title, text, backtest):
    if not backtest:
        __rich_notify(title, text, 'good')
    else:
        return


def warn(title, text, backtest):
    if not backtest:
        __rich_notify(title, text, 'warning')
    else:
        return


def error(title, text, backtest):
    if not backtest:
        __rich_notify(title, text, 'danger')
    else:
        return


def __rich_notify(title, text, color):
    attachments = []
    attachments.append({
        'title': title,
        'text': text,
        'color': color
    })
    slack.notify(attachments=attachments)
