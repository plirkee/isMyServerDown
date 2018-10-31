import smtplib
from email.mime.text import MIMEText
import optparse, subprocess, os, sys
import re, time, datetime
from optparse import OptionParser
from os import stat
from os.path import abspath
from stat import ST_SIZE
import httplib
import sys

SLEEP_TIME = 60
email_from = ""
email_to = ""
smtp_server=""
ssl=False
smtp_user=None
smtp_password=None
 
def runProcess(exe):
    FNULL = open(os.devnull, 'w')
    p = subprocess.call(exe, stdout=FNULL, stderr=FNULL)
 
    if p == 0:
        return True
    else:
        return False
 
def sendAlert(state, host, debug,what):
    subject = ""
    statetext = ""
 
    if state == 0:
        statetext = "up"
    elif state == 1:
        statetext = "down"
 
    subject = "Host %s is %s" % (host, statetext)
 
    ts = time.time()
    f_ts = str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
 
    text = "Host " + host + " went " + statetext + " at " + f_ts + " based on " + what
 
    msg = MIMEText(text)
    msg[ 'From' ] = email_from
    msg[ 'To' ] = ", " + email_to
    msg[ 'Subject' ] = subject
    try:
        
		#if ssl/tls smtp
        if ssl:
			s = smtplib.SMTP_SSL(smtp_server)
			if debug: print "SSL SERVER:" +  smtp_server
		#if not encrypted
        else:
			s = smtplib.SMTP(smtp_server)
			if debug: print "PLAIN SMTP SERVER:" +  smtp_server
        if debug:
            s.set_debuglevel(True)
        #if authentication required
        if smtp_user!=None and smtp_password!=None:
			if debug: print "user and pass are set"
			s.login(smtp_user,smtp_password)
        s.sendmail(email_from, [email_to], msg.as_string())
        s.quit()
    except Exception as e:
        if debug: print "error sending email:"
        #if debug: print msg
        if debug: print e
 
def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False, help='enable debugging')
    parser.add_option('-e', '--encrypted', action='store_true', dest='ssl', default=False, help='ssl/tls smtp')
    parser.add_option('-p', '--ping', action='store', dest='host', default=None, help='specify host to ping')
    parser.add_option('-s', '--smtp', action='store', dest='smtp', default=None, help='Specify Mail Server (SMTP)')
    parser.add_option('-t', '--to', action='store', dest='mail_to', default=None, help='Specify Mail Receiver addresses')
    
    
    parser.add_option('-f', '--from', action='store', dest='mail_from', default='Http Ping', help='Specify Mail Sender address')
    
    parser.add_option('-u', '--smtp_user', action='store', dest='smtp_user', default=None, help='SMTP user (optional)')
    parser.add_option('-w', '--smtp_password', action='store', dest='smtp_password', default=None, help='SMTP password (optional)')
    parser.add_option('-z', '--sleepTime', action='store', dest='sleep', default=60, help='sleep time(optional)')
    
 
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit( 1 )
    (options, args) = parser.parse_args()
 
    if options.host == None:
        parser.print_help()
        sys.exit( 1 )

    if options.smtp == None:
        parser.print_help()
        sys.exit( 1 )

    if options.mail_to == None:
        parser.print_help()
        sys.exit( 1 )
    global  SLEEP_TIME,email_from,email_to,ssl,smtp_server 
    SLEEP_TIME = int(options.sleep)
    email_from = options.mail_from
    email_to   = options.mail_to
    smtp_server=options.smtp
    ssl=options.ssl
    
    
    try:
        upflag = True
        while(True):
            if options.debug: print "pinging host: " + str(options.host)
            pingresult = runProcess(["ping", options.host])
            http_ping_result = False
            try:
                conn = httplib.HTTPConnection(options.host)
                conn.request('HEAD', '/')
                url = 'http://{0}/{1}'.format(options.host,"")
                if options.debug: print '    Trying: {0}'.format(url)
                response = conn.getresponse()
                if options.debug: print '    Got: ', response.status, response.reason
                conn.close()
    	        if response.status == 200:
    	            if options.debug: print ("Got Response 200 " +" everything is ok")
                    http_ping_result = True	 
            except:
                e = sys.exc_info()[0]
                print ' Problem in connection  ' + str(e)	
                http_ping_result = False
			
            if pingresult == False or http_ping_result==False:
                what="" 
                if pingresult == False: what =what + "ping "			
                if http_ping_result == False: what =what + " http"			
                if options.debug: print "ping failed" + str(pingresult)
                if upflag == True:
                    if options.debug: print "send down email"
                    sendAlert(1,options.host,options.debug,what)
                    os.system('speech.vbs "Alert! Alert! Server down! Server down!"')
                upflag = False
            else:
                if options.debug: print "ping was successful..."
                if upflag == False:
                    if options.debug: print "send up email"
                    sendAlert(0,options.host,options.debug,what)
                upflag = True
			
            if options.debug: print "sleeping for "+str(SLEEP_TIME) +"s"
            time.sleep(SLEEP_TIME)
    except (KeyboardInterrupt, SystemExit):
        #raise
        print "Exiting"
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        exit ( 1 )
    exit( 1 )
 
if __name__ == '__main__':
    main()
