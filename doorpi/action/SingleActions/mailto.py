#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import smtplib # used by: fire_action_mail
from email.mime.multipart import MIMEMultipart # used by: fire_action_mail
from email.mime.text import MIMEText # used by: fire_action_mail
from email.Utils import COMMASPACE # used by: fire_action_mail

from action.base import SingleAction
import doorpi

def fire_action_mail(smtp_to, smtp_subject, smtp_text):
    try:
        smtp_host = doorpi.DoorPi().config.get('SMTP', 'server')
        smtp_port = doorpi.DoorPi().config.get_int('SMTP', 'port')
        smtp_user = doorpi.DoorPi().config.get('SMTP', 'username')
        smtp_password = doorpi.DoorPi().config.get('SMTP', 'password')
        smtp_from = doorpi.DoorPi().config.get('SMTP', 'from')

        smtp_use_tls = doorpi.DoorPi().config.get_boolean('SMTP', 'use_tls')
        smtp_need_login = doorpi.DoorPi().config.get_boolean('SMTP', 'need_login')

        smtp_tolist = smtp_to.split()

        server = smtplib.SMTP()
        server.connect(smtp_host, smtp_port)
        server.ehlo()

        if smtp_use_tls: server.starttls()
        if smtp_need_login: server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = COMMASPACE.join(smtp_tolist)
        msg['Subject'] = doorpi.DoorPi().parse_string(smtp_subject)
        msg.attach(MIMEText(doorpi.DoorPi().parse_string(smtp_text), 'html'))
        msg.attach(MIMEText('\nsent by:\n'+doorpi.DoorPi().epilog, 'plain'))
        server.sendmail(smtp_from, smtp_tolist, msg.as_string())
        server.quit()
    except:
        logger.exception("couldn't send email")
        return False
    return True

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 3: return None

    smtp_to = parameter_list[0]
    smtp_subject = parameter_list[1]
    smtp_text = parameter_list[2]

    return MailtoAction(fire_action_mail,
                     smtp_to = smtp_to,
                     smtp_subject = smtp_subject,
                     smtp_text = smtp_text)

class MailtoAction(SingleAction):
    pass
