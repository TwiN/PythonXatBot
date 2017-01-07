# -*- coding: utf-8 -*-
import urllib2
import cookielib
import socket
from math import floor
from time import sleep 
import random
import os
import re
import sys
# bs4=required for urbansearch function, uncomment only if bs4 installed
#from bs4 import BeautifulSoup # Beautiful Soup 4

'''--------------------------------------------------
A basic xat bot that does not require the (BOT) power.

@author    Twin
@date      2016/07/15
@website   https://twinnation.org
--------------------------------------------------'''

###########################
######## VARIABLES ########
###########################

############
# Settings #
############
isRegistered = False # FIXME: Xat changed some packets, this is broken for now
# You can still connect using a non-registered bot, however
autoMember = False # TODO: fix calculateRank()

#################
# Do not modify #
#################
chatName = ''
chatData = ''
chatid   = 0
chatport = 0
chatip   = ''

gSocket = None

c_retry = False
chatBackground = ''
userListInfo = {}

##########################
######## BOT INFO ########
##########################

botRegName="bot_username" # I recommend using an unregistered 
botPasswrd="bot_password" # bot because laziness > all

botID = "1517381276"            
botK1 = "280ee724245772b81c00"  
botK2 = "537616878"            

botDisplayName = "TwiNNatioNBoT"
botAvatar      = "http://oi48.tinypic.com/9uqgex.jpg"
botHomepage    = "https://twinnation.org"

owner = "888103269" # Bot owner ID goes here (NOT THE BOT ID)

########
# MISC #
########

greetings = ["Hey", "Hi", "Hello", "Welcome", "Yo"]

colors = ["red", "blue", "green", "yellow","orange",
         "purple", "white", "black", "pink", "gray"]

###########################
######## FUNCTIONS ########
###########################

'''
Function that gets the chat data (id, ip and port)
@param cname    chat name
'''
def getChatData(cname):
    site= "https://twinnation.org/API/xat.php?chat=%s" % cname
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(site, headers=hdr)
    try:
        page = urllib2.urlopen(req, timeout=5)
    except urllib2.HTTPError, e:
        print e.fp.read()
    content=(page.read()).split(':')
    cdata = {
        'chatname': content[0],
        'chatid': content[1],
        'chatip': content[2],
        'chatport': int(content[3])
    }
    return cdata

'''
Function that returns the source from the target url
@param url  
'''
def file_get_contents(url):
    site = str(url).replace(" ", "+")
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(site, headers=hdr)
    try:
        page = urllib2.urlopen(req, timeout=5)
        return page.read()
    except urllib2.HTTPError, e:
        print e.fp.read()
    return 'Oops, I didnt manage to get that :('


'''
Function that returns the substring between two strings
'''
def getBetween(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''
    return ''


'''
Function that checks if a sentence contains an element in a list.
NOTE: This function should be used as the last statement.
@param xList 
@param xStr
'''
def is_string_from_list_in_sentence(list_of_words, sentence_to_check):
    words = sentence_to_check.split(" ")
    for element in list_of_words:
        for word in words:
            if element.lower() == word.lower():
                return True
    return False


'''
Function that removes a key from a dictionary and returns the new
dictionary
@param d    dictionary
@param key  key to remove
'''
def removeFromDictionary(d, key):
    temp = dict(d)
    try:
        del temp[key]
    except KeyError:
        if DEBUG: print "Key '"+str(key)+"' was not found, thus it cannot be deleted."
    return temp


'''
Function that reads a local file
@param fname    path and filename
'''
def readLocalFile(fname):
    content=''
    with open(fname, 'r') as f:
        content += f.read()
    return content.rstrip("\n") #removes last newline


'''
Function that OVERWRITES data in a file
@param fname    file name
@param data     data to write
'''
def writeInFile(fname, data):
    fhandler = open(fname, "w")
    fhandler.write(data)
    fhandler.close()


'''
Function that returns true on lucky occasions
'''
def chance(percentage):
    return random.randint(0, 100) < percentage


##############
# connection #
##############

'''
Function that logs in the user to the xat log in server
'''
def login():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('54.84.152.77', 10001))
    print "Connected to login server successfully."
    s.sendall('<v p="'+botPasswrd+'" u="'+botRegName+'" />\x00')
    print "Account information for "+botRegName+" have been parsed."
    data = s.recv(4096)
    print 'Connection successful!'
    s.close()


'''
Function that connects the bot to xat's server.
'''
def connect():
    global gSocket, userListInfo, c_retry
    gSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gSocket.connect((chatip, chatport))
    gSocket.sendall('<y r="'+str(chatid)+'" m="1" v="0" u="'+str(botID)+'" />\x00')
    data = gSocket.recv(2048)
    pkt_i  = getBetween(data, 'i="', '"')
    pkt_l5 = str(getL5(pkt_i, getBetween(data, 'p="', '"')))
    sleep(1)
    if isRegistered: # if its a registered user
        gSocket.sendall('<j2 cb="89" l5="'+pkt_l5+'" y="'+pkt_i+'" k="'+botK1+'" k3="" p="0" c="'+str(chatid)+'" f="0" u="'+str(botID)+'" d0="1088" d3="5730386" dt="1467237491" N="'+botRegName+'" n="'+botDisplayName+'" a="'+botAvatar+'" h="'+botHomepage+'" v="0" />\x00')
    else: # if not a registered user
        gSocket.sendall('<j2 cb="0" l5="'+pkt_l5+'" y="'+pkt_i+'" k="'+botK1+'" p="0" c="'+str(chatid)+'" f="0" u="'+str(botID)+'" d0="0" n="'+botDisplayName+'" a="'+botAvatar+'" h="'+botHomepage+'" v="10" />\x00')
    count=0
    i_rounds=0
    while True: # keeps the socket alive
        data = gSocket.recv(2048)
        if data=="":
            count+=1
            print "[ERROR] Failed to connect!"
            sleep(.3)
            if count>2 and not c_retry:
                c_retry = True
                gSocket.close()
                print "[STATUS] Attempting to reconnect in 5 seconds..."
                sleep(5)
                connect()
            elif count>2 and c_retry:
                print "[CRITICAL] Exiting..."
                break
        else:
            if c_retry: i_rounds+=1
            if c_retry and not data.find("<logout")>0 and i_rounds>5:
                print "[INFO] Reconnection was successful, setting c_retry back to False."
                c_retry = False
            handlepacket(data) # everything went well, so handle the packets!
    gSocket.close()
    exit()


'''
Function that handles the packets (events)
@param data     packet
'''
def handlepacket(data):
    global userListInfo
    uid = getBetween(data, 'u="', '"').split('_')[0] # user id
    
    # initial packet, contains chat bg and usrlist
    if data.find('<i ')>0 or len(data)>250: 
        packets = data.split('/>') # cant split by space, so use that
        for packet in packets:
            if packet.find('<u ')>0: 
                userInfo(packet)
            if packet.find('<i')>0:
                print '[INFO] Got background.'
                chatInfo(packet)
            if packet.find('<l')>0 and uid != botID:
                userListInfo = removeFromDictionary(userListInfo, uid) 
    # store users in db regardless of events (hence no elif)
    if data.startswith('<u '):
        if autoMember:
            # TODO: fix calculateRank()
            if calculateRank(getBetween(data, 'f="', '"')) == 'guest':
                mkMember(uid, gSocket)
        userInfo(data)
    # User leaving the chat
    elif data.startswith('<l')>0 and uid != botID:
        userListInfo = removeFromDictionary(userListInfo, uid)

    ###############
    # Interaction #
    ###############
    
    # Main chat
    elif data.startswith('<m '):
        handle(data, 1, gSocket)

    # Private chat
    elif (data.startswith('<p ') or data.startswith('<z ')) and data.find('s="2"')>0:
        handle(data, 2, gSocket)
    
    # Private message
    elif data.startswith('<p '):
        handle(data, 3, gSocket)
            
    # Tickle
    elif data.startswith('<z '): 
        print 'Tickled by '+uid
    
    # Chat information
    elif data.startswith('<i')>0:
        print '[INFO] Got background.'
        chatInfo(data)
        
    # Others
    else:
        print "[<<] "+data


'''
Function that generates the L5.
Using a text file with every possible value
is much faster than using the old L5.swf 
@param i    i packet
@param p    p packet
@author     Nitin
'''
def getL5(i, p):
    l5_info     = p.split("_")
    p_w         = int(l5_info[0])
    p_h         = int(l5_info[1])
    p_octaves   = l5_info[2]
    p_seed      = l5_info[3]
    t       = (int(i) % (p_w * p_h))
    p_x     = (t % p_w)
    p_y     = int(floor((t / p_w)))
    file = open("100_100_5_"+p_seed+".txt", "r") 
    data = filter(None, file.read().split("\n"))
    file.close()
    for info in data:
        xy, value = info.split(":")
        if str(p_x)+","+str(p_y) == xy:
            return value
    return 0

########################
######## Handle ########
########################
'''
Function that makes the bot replies where it should
@param uid          uid, if it applies.
@param msg          message to be sent
@param chatType     1:Main chat 2:PC 3:PM
@param s            socket
'''
def reply(uid, msg, chatType, s=gSocket):
    sleep(.1)
    msg = msg.replace('"','')
    msg = msg.replace('\n','')
    try:
        msg = msg.replace("$uname", userListInfo[str(uid)].split(' : ')[1].split('##', 1)[0])
    except KeyError: # if uid not in same chat as bot, just remove $uname from str
        msg = msg.replace("$uname", '')
    
    bTrigger=False
    sMsg=msg
    if len(msg) > 180:
        bTrigger=True
        msg = msg[0:170]
        sleep(.3)
    
    if chatType == 1: # Main chat
        sM(msg, s)
    if chatType == 2: # Private chat
        sPC(uid, msg, s) 
    if chatType == 3: # Private message
        sPM(uid, msg, s)
    
    if bTrigger:
        sleep(4.5)
        reply(uid, sMsg[170:], chatType, s)


'''
Function that sends a message on the main chat
'''        
def sM(msg, s=gSocket):
    sendMessage(msg, s)

def sendMessage(msg, s=gSocket):
    s.sendall('<m t="'+msg+'" u="'+str(botID)+'" />\x00')


'''
Function that sends a private message to a given uid
'''     
def sPM(uid, msg, s=gSocket): 
    sendPrivateMessage(uid, msg, s)

def sendPrivateMessage(uid, msg, s=gSocket):
    # only work if in same room:
    #s.sendall('<p u="'+str(uid)+'" t="'+msg+'" />\x00')
    # works everywhere:
    s.sendall('<z d="'+str(uid)+'" u="'+str(botID)+'" t="'+msg+'" />\x00')


'''
Function that sends a private chat to a given uid
'''   
def sPC(uid, msg, s=gSocket): 
    sendPrivateChat(uid, msg, s)

def sendPrivateChat(uid, msg, s=gSocket):
    # only work if in same room:
    #s.sendall('<p u="'+str(uid)+'" t="'+msg+'" s="2" d="'+str(botID)+'" />\x00')
    # works everywhere:
    s.sendall('<z d="'+str(uid)+'" u="'+str(botID)+'" t="'+msg+'" s="2" />\x00')


'''
Function that members a given uid
'''   
def mkMember(uid, s=gSocket):
    s.sendall('<c u="'+str(uid)+'" t="/e" />\x00')


'''
Function that changes the chat the bot is currently in.
'''   
def changeChat(cname, s=gSocket):
    global chatName, chatid, chatport, chatip, chatData
    chatName = cname
    writeInFile("chatName.txt", cname)
    chatData = getChatData(chatName)
    chatid   = chatData['chatid']
    chatport = chatData['chatport']
    chatip   = chatData['chatip']
    s.sendall('<q qt="Q12" r="'+chatid+'" />\x00')
    s.close()
    connect()


'''
Function that determines the rank of the user. It might be
inaccurate because I am too lazy to test it right now
@param f    packet['u']['f']
'''
def calculateRank(uf):
    try:
        f = int(uf)
        if (f==-1) or (not (1 & f) and not (2 & f)): return 'guest'
        if (16 & f): return 'banned'
        if (1 & f) and (2 & f): return 'member'
        if (4 & f): return 'owner'
        if (32 & f) and (1 & f) and not (2 & f): return 'main'
        if (2 & f) and not (1 & f): return 'mod'
    except ValueError:
        return 'guest'
    return '???'


'''
Function that saves the user info stored in the u packet in a
temporary database (On my version of the bot, it stores the
information in a SQL database, so this is not very useful
besides for copying other users profile in the same room)
@param data     packet['u']
'''
def userInfo(data):
    uid=getBetween(data, 'u="', '"').split('_')[0]
    uname = ''
    try:
        uname=getBetween(data, 'N="', '"')
    except:
        uname='Not registered'
    udisplayname=getBetween(data, 'n="', '"')
    if uname=='' and udisplayname=='':
        print 'Null user, ignoring '+uid
        return
    print (udisplayname if uname=='Not registered' else uname)+'('+uid+') has joined the chat'
    # if there's no id, no point in storing data OR if id is bot id
    if (len(uid)==0 and not uname) or str(uid)==str(botID):
        return
    uavatar=getBetween(data, 'a="', '"')
    uhomepage=getBetween(data, 'h="', '"')
    if len(uhomepage) == 0:
        uhomepage = "none"
    urank = calculateRank(getBetween(data, 'f="', '"'))
    global userListInfo
    userListInfo[str(uid)]=uname+' : '+udisplayname+' : '+uavatar+' : '+uhomepage+' : '+str(urank)


'''
Function that returns the data found on the id passed as parameter
@param uid      user id
'''
def getUserInfo(uid):
    sInfo = ""
    try:
        sInfo = userListInfo[str(uid)].split(' : ')
    except:
        sInfo = "I can't find any information on that ID!"
    return sInfo
        

'''
Function that returns the rank of the uid passed as param
@param uid      user id
'''
def getUserRank(uid):
    return userListInfo[str(uid)].split(' : ')[3]

    
def chatInfo(data):
    global chatBackground
    chatBackground=getBetween(data, 'b="', ';=')


def getChatBackground():
    return chatBackground
    

'''
Function that returns the top 3 video result from a given string
@param query    search query
'''
def youtube(query):
    vids = []
    source = file_get_contents('https://www.youtube.com/results?search_query='+query)
    while len(vids) < 3:
        vid = getBetween(source, 'href="/watch?v=', '"')
        if not vid.find('list')>0:
            vids.append('https://www.youtube.com/watch?v='+vid)
        source = source.replace('href="/watch?v='+vid+'"', '')
    return vids

'''
Function that returns a random fml from fmylife.com
'''
def fml():
    source = file_get_contents('http://www.fmylife.com/random')
    fmlstory = getBetween(source, 'Today, ', '</')
    while len(fmlstory) > 200:
        fmlstory = getBetween(source, 'Today, ', '</')
    return 'Today, '+fmlstory

'''
Function that searches for a term on urbandictionary
@param query    search query
'''
'''
# NOTE: This function requires beautifulSoup4, and since it is not installed
# by default, I will keep this commented
def urbansearch(query):
    if query == '3nvisi0n' or query == 'twin':
        return 'A true cutiepie'
    query = query.replace(' ', '+')
    source = file_get_contents('http://www.urbandictionary.com/define.php?term='+query)
    soup = BeautifulSoup(source, "html.parser")
    sDef = soup.findAll("div", {"class":"meaning"})[0].get_text().replace('\n', '')
    count = 0
    while len(sDef) == 0 and count < len(sDef)-1:
        count += 1
        sDef = soup.findAll("div", {"class":"meaning"})[count].get_text().replace('\n', '')
    if len(sDef) < 10:
        return "Sorry, I didn't manage to search for that."
    return sDef
'''

###############################################
###############################################
#################### CHAT #####################
###############################################
###############################################
'''
Function that handles the chat
@param packet
@param chatType     1:Main chat 2:PC 3:PM
@param s            socket
'''
def handle(packet, chatType, s):
    uid  = getBetween(packet, 'u="', '"').split('_')[0]
    longName = botDisplayName
    try:
        if uid != botID:
            longName = userListInfo[str(uid)].split(' : ')[0]
    except KeyError:
        longName = ''
    uname = (longName[:20] + '..') if len(longName) > 20 else longName
    msg  = getBetween(packet, 't="', '"').lower().replace('&apos;', '')
    args = msg.split(" ")
    c_type = ['','','[PC]','[PM]'][chatType]
    print c_type+'['+uname+'('+str(uid)+')]: '+msg

    
    ############
    # chatting #
    ############
    # Questions directly asked to the bot
    if msg.find("bot")>=0 and not (re.search(r'bot\w', msg) or re.search(r'\wbot', msg)): # message contains 'bot' but not 'both'
        if is_string_from_list_in_sentence(greetings, msg):
            if uid == owner:
                reply(uid, random.choice(greetings)+", Master.", chatType, s)
            else:
                reply(uid, random.choice(greetings)+".", chatType, s)
                
        elif msg.find("user")>=0 and (msg.find("count")>=0 or (msg.find("many")>=0 and msg.find("how")>=0)):
            reply(uid, "There are currently "+str(len(userListInfo)+1)+" users online.", chatType, s)

    # Bot not minding his own business
    if msg.find("favorite")>=0 and msg.find("color")>=0 and is_string_from_list_in_sentence(colors, msg):
        reply(uid, "I'm really glad that you have a favorite color, but everybody knows that the best color is "+random.choice(colors)+".", chatType, s)
            
    ############
    # commands #
    ############
    if msg[:1] == "@":
        args[0] = args[0][1:] # remove the @
        cmd  = args[0] # this is the command
        argu = msg.replace('@'+cmd+' ', '') # this is everything after command
        print "[COMMAND] "+cmd+" | [ARGUMENT] "+argu 

        # change chat
        if cmd == "go" or cmd == "move":
            if uid == owner:
                try:
                    changeChat(args[1], s)
                except IndexError:
                    reply(uid, "Usage is @go chatid", chatType, s)
            else:
                sPM(uid, "You are not allowed to use this command.", s)

        # kill the bot
        elif cmd == "kill" or cmd == "die":
            if uid == owner:
                s.close()
                sys.exit()
            else:
                sPM(uid, "You are not allowed to use this command.", s)
                
        # pm <id> <msg>
        elif cmd == "pm":
            if uid == owner:
                try:
                    sPM(args[1], argu.replace(args[1], ''), s)
                except IndexError:
                    reply(uid, "Usage is @pm id msg", chatType, s)
            else:
                sPM(uid, "You are not allowed to use this command.", s)
                
        # pc <id> <msg>
        elif cmd == "pc":
            if uid == owner:
                try:
                    sPC(args[1], argu.replace(args[1], ''), s)
                except IndexError:
                    reply(uid, "Usage is @pc id msg", chatType, s)
            else:
                sPC(uid, "You are not allowed to use this command.", s)
            
        ###########
        # General #
        ###########
        
        # say <msg>
        elif cmd == "say":
            reply(uid, msg[len(cmd)+1:], chatType, s)

        # userinfo <uid>
        elif cmd == 'userinfo':
            try:
                ti=getUserInfo(args[1]) # target info
                sleep(1.5)
                reply(uid, 'regName= '+str(ti[0])+", displayName= "+str(ti[1]), chatType, s)
                sleep(2)
                reply(uid, 'Avatar= '+str(ti[2])+", Homepage= "+str(ti[3]), chatType, s)
                sleep(1.5)
            except IndexError:
                reply(uid, "Usage is @userinfo ID", chatType, s)
            except TypeError:
                reply(uid, "Sorry, that ID is not in my database.", chatType, s)
        

        # chat background
        elif cmd == "bg" or cmd == "background" or cmd == "getbg":
            reply(uid, chatBackground, chatType, s)

        # youtube <query>
        elif cmd == "yt" or cmd == "youtube":
            vids = youtube(argu)
            try:
                for i in range(0, len(vids)):
                    reply(uid, vids[i], chatType, s)
                    sleep(1.5)
            except:
                reply(uid, "Looks like something went wrong. Sorry about that!", chatType, s)

        # fml
        elif cmd == "fml":
            reply(uid, fml(), chatType, s)

        # usercount
        elif cmd == "usercount":
            reply(uid, "There are currently "+str(len(userListInfo)+1)+" users online.", chatType, s)

        # let me google that for you
        elif cmd == "g" or cmd == "google" or cmd == "lmgtfy":
            reply(uid, "http://lmgtfy.com/?q="+(argu.replace(' ', '+')), chatType, s)









        '''
        # urbansearch <query>
        elif cmd == "urbansearch" or cmd == "urban":
            try:
                reply(uid, urbansearch(argu), chatType, s)
            except IndexError:
                reply(uid, "Usage is @urban TERM", chatType, s)
        '''

########################################
################# Main #################
########################################
def init():
    global chatName, chatData, chatid, chatport, chatip
    chatName = readLocalFile('chatName.txt')
    chatData = getChatData(chatName)
    chatid   = chatData['chatid']
    chatport = chatData['chatport']
    chatip   = chatData['chatip']
    print "----- Chat info -----"
    print "chatName: %s" % chatName
    print "ID:       %s" % chatid
    print "Port:     %s" % chatport
    print "IP:       %s" % chatip
    print "---------------------"
    if isRegistered:
        login()
    connect()

########################################
# this should always be at the bottom! #
########################################

init()

