#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import smtplib # used by: fire_action_mail
from email.mime.multipart import MIMEMultipart # used by: fire_action_mail
from email.mime.text import MIMEText # used by: fire_action_mail
from email.MIMEBase import MIMEBase # used by: fire_action_mail
from email import Encoders # used by: fire_action_mail
from email.Utils import COMMASPACE # used by: fire_action_mail

from doorpi.action.base import SingleAction
import doorpi
import os
from take_snapshot import get_last_snapshot
import subprocess as sub

def fire_action_mail(smtp_to, smtp_subject, smtp_text, smtp_snapshot):
    try:
        smtp_host = doorpi.DoorPi().config.get('SMTP', 'server', 'smtp.gmail.com')
        smtp_port = doorpi.DoorPi().config.get_int('SMTP', 'port', 465)
        smtp_user = doorpi.DoorPi().config.get('SMTP', 'username')
        smtp_password = doorpi.DoorPi().config.get('SMTP', 'password')
        smtp_from = doorpi.DoorPi().config.get('SMTP', 'from')

        smtp_use_tls = doorpi.DoorPi().config.get_boolean('SMTP', 'use_tls', False)
        smtp_use_ssl = doorpi.DoorPi().config.get_boolean('SMTP', 'use_ssl', True)
        smtp_need_login = doorpi.DoorPi().config.get_boolean('SMTP', 'need_login', True)

        smtp_tolist = smtp_to.split()

        email_signature = doorpi.DoorPi().config.get_string_parsed('SMTP', 'signature', '!EPILOG!')

        if smtp_use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)

        server.ehlo()
        if smtp_use_tls and not smtp_use_ssl:
            server.starttls()
        if smtp_need_login:
            server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_from
        msg['To'] = COMMASPACE.join(smtp_tolist)
        msg['Subject'] = doorpi.DoorPi().parse_string(smtp_subject)
        msg.attach(MIMEText(doorpi.DoorPi().parse_string(smtp_text), 'html'))
        if email_signature and len(email_signature) > 0:
            msg.attach(MIMEText('\nsent by:\n'+doorpi.DoorPi().epilog, 'plain'))

        if smtp_snapshot:
            smtp_snapshot = doorpi.DoorPi().parse_string(smtp_snapshot)
            if not os.path.exists(smtp_snapshot):
                smtp_snapshot = get_last_snapshot()

        try:
            with open(smtp_snapshot, "rb") as snapshot_file:
                part = MIMEBase('application',"octet-stream")
                part.set_payload(snapshot_file.read())
                Encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    'attachment; filename="%s"' % os.path.basename(smtp_snapshot))
                msg.attach(part)
        except Exception as exp:
            logger.exception("send not attachment for this mail: %s" % exp)

        server.sendmail(smtp_from, smtp_tolist, msg.as_string())
        server.quit()
    except:
        logger.exception("couldn't send email")
        return False
    return True


def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) < 3 or len(parameter_list) > 4: return None

    smtp_to = parameter_list[0]
    smtp_subject = parameter_list[1]
    smtp_text = parameter_list[2]
    if (len(parameter_list) == 4):
        smtp_snapshot = parameter_list[3]
    else:
        smtp_snapshot = False
    
    return MailtoAction(fire_action_mail,
                     smtp_to = smtp_to,
                     smtp_subject = smtp_subject,
                     smtp_text = smtp_text,
                     smtp_snapshot = smtp_snapshot)


class MailtoAction(SingleAction):
    pass
