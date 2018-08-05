#!/usr/bin/python
# -*- coding: UTF-8 -*-

from email.mime.text import MIMEText
import ConfigParser


def do_telnet(host, port):
    import telnetlib
    import socket

    try:
        tn = telnetlib.Telnet(host, port=port, timeout=5)
        tn.close()
        print "Telnet " + host + " successfully"
        return True
    except socket.timeout:
        print "Telnet " + host + " failed"
        return False


def send_alarm_mail(message_text):
    import smtplib
    from email.header import Header

    config = ConfigParser.ConfigParser()
    with open("smtp.cfg", "r") as cfgfile:
        config.readfp(cfgfile)
        sender = config.get('smtp', "sender")
        password = config.get('smtp', "password")
        receiver = config.get('smtp', "receiver")
        smtp_server = config.get('smtp', "smtp_server")
        smtp_port = int(config.get('smtp', "smtp_port"))

    message = message_text
    message['From'] = sender
    message['To'] =  receiver

    subject = 'System Alarm'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        #server.set_debuglevel(True)
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
        server.quit()
        print "mail sent successfully."
    except smtplib.SMTPException:
        print "mail send failed"


def check_servers():
    config = ConfigParser.ConfigParser()
    with open("alarm.cfg", "rw") as cfgfile:
        config.readfp(cfgfile)

        for section in config.sections():
            ip = config.get(section, "ip")
            port = int(config.get(section, "port"))
            fail = int(config.get(section, "fail"))
            alive = config.get(section, "alive")
            if alive == "True":
                if not do_telnet(ip, port):
                    fail = fail + 1
                    config.set(section, "fail", fail)
                    if fail >= 3:
                        config.set(section, "alive", False)
                        message_text = MIMEText(section + ' server ' + ip + ' telnet failed.', 'plain', 'utf-8')
                        send_alarm_mail(message_text)
                    else:
                        message_text = MIMEText(section + ' server ' + ip + ' lost connection ' + str(fail) + ' time.', 'plain', 'utf-8')
                        send_alarm_mail(message_text)
            else:
                if do_telnet(ip, port):
                    fail = 0
                    config.set(section, "fail", fail)
                    config.set(section, "alive", True)
                    message_text = MIMEText(section + ' server ' + ip + ' connection recovered.', 'plain', 'utf-8')
                    send_alarm_mail(message_text)
    config.write(open("alarm.cfg", "w"))

check_servers()
