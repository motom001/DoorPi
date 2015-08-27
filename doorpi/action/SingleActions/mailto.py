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

from action.base import SingleAction
import doorpi
import os
import subprocess as sub

def fire_action_mail(smtp_to, smtp_subject, smtp_text, smtp_snapshot):
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

 	#add a snapshot
        if (smtp_snapshot and len(doorpi.DoorPi().config.get('SIP-Phone', 'capture_device', '')) > 0):
            file = createSnapshot()
	    if (len(file) > 0):
		    part = MIMEBase('application',"octet-stream")
		    part.set_payload(open(file,"rb").read())
		    Encoders.encode_base64(part)
		    part.add_header('Content-Disposition', 'attachment; filename="%s"'
			       % os.path.basename(file))
		    msg.attach(part)

        server.sendmail(smtp_from, smtp_tolist, msg.as_string())
        server.quit()
    except:
        logger.exception("couldn't send email")
        return False
    return True

def createSnapshot():
    snapshot_file = '/tmp/doorpi.jpg'
    size = doorpi.DoorPi().config.get_string('DoorPi', 'snapshot_size', '1280x720')
    command = "fswebcam --no-banner -r " + size + " " + snapshot_file
    try:
        retcode = subprocess.call(command, shell=True)
    	if retcode != 0:
       	    logger.error('error creating snapshot')
	else:
	    logger.info('snapshot created: %s', snapshot_file)
    	    return snapshot_file
	    
    except OSError as e:
        logger.error('error creating snapshot')
    return ''

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
