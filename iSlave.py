#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Description:
# Author: fkolacek@redhat.com
# Version: 0.9

import socket
import sys
import re
from datetime import datetime, date, time

RHOST = "irc.example.com"
RPORT = 6667
RNICK = "fkolacek"
RNAME = "Yet another slave"
RCHANS = [ "example"]
RMASTER_NICK = "FLC"
RMASTER_NAME = "Franta"

class UserState:
    New, Demanding = range(2)

class Brain(object):

    counter = 1
    users = []
    userStates = {}
    usersDates = {}
    userMessages = {}

    stringIntroduce = "Greetings %s, I'm %s's slave. Unfortunatelly my master is not available at this very moment. Do you want to leave him a message? (Use !schedule_meeting if you want to contact him)"
    stringScheduled = "Please stand by, my master is talking to someone else. He will respond to you as soon as possible (ticket number: %d)."

    def activate(self, nick, user, host, channel, message):
        replies = []

        if nick not in self.users:
            self.users.append(nick)
            self.userStates[nick] = UserState.New
            self.usersDates[nick] = datetime.now()
            self.userMessages[nick] = []
            self.userMessages[nick].append(message)

            replies.append((nick, self.stringIntroduce % (nick, RMASTER_NAME)))

        elif self.userStates[nick] == UserState.New:
            if message.find("!schedule_meeting") != -1:
                self.userStates[nick] = UserState.Demanding
                #self.userMessages[nick].append(message)

                replies.append((nick, self.stringScheduled % self.counter))
                self.counter += 1

                replies.append((RMASTER_NICK, "User %s wants to have meeting with you." % nick))
                for message in self.userMessages[nick]:
                    replies.append((RMASTER_NICK, "%s: %s" % (nick, message)))

                self.userMessages[nick] = []
            else:
                self.userMessages[nick].append(message)

        elif self.userStates[nick] == UserState.Demanding:
            replies.append((RMASTER_NICK, "%s: %s" % (nick, message)))

        return replies

def parseLine(rawLine):
    line = rawLine.strip()

    #PING
    if line.find("PING") != -1:
        IRC.send("PONG %s\n" % line.split()[1])
    #PRIVMSG
    elif line.find("PRIVMSG") != -1:
        # nick!~user@host PRIVMSG channel :msg
        parts = re.search("^:([^!]+)!~([^@]+)@([^ ]+) PRIVMSG ([^ ]*) :(.*)$", line)

        if parts:
            nick, user, host, channel, message = parts.groups()

            #Direct message
            if channel == RNICK:
                print "[*] Got message from %s: %s" % (nick, message)
                replies = BRAIN.activate(nick, user, host, channel, message)
                for reply in replies:
                    IRC.send("PRIVMSG %s :%s\n" % reply)
            #Channel
            else:
                pass
        else:
            print "[?] PRIVMSG DEBUG: %s" % line
    #QUIT|NICK|JOIN
    elif line.find("QUIT") != -1 or line.find("NICK") != -1 or line.find("JOIN") != -1:
        parts = re.search("^:([^!]+)!~([^@]+)@([^ ]+) (QUIT|NICK|JOIN) :(.*)$", line)

        if parts:
             nick, user, host, command, msg = parts.groups()

             # TODO

    #WHATEVER
    else:
        print "[?] DEBUG: %s" % line

if __name__ == '__main__':
    IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print "[*] Connecting to: %s:%d" % (RHOST, RPORT)

    IRC.connect((RHOST, RPORT))

    print "[*] Connected"

    IRC.send("USER %s %s %s :%s\n" % (RNICK, RNICK, RNICK, RNAME))
    IRC.send("NICK %s\n" % RNICK)

    print "[*] Joining channels"
    for channel in RCHANS:
        print "[*] Joining %s" % channel
        IRC.send("JOIN %s\n" % channel)

    print "[*] Looking for master"
    IRC.send("WHO %s\n" % RMASTER_NICK)

    buffer = ""
    BRAIN = Brain()

    while True:
        buffer += IRC.recv(1024)

        while buffer.find("\n") != -1:
            pos = buffer.find("\n")

            line = buffer[:pos]

            parseLine(line)

            buffer = buffer[pos+1:]
