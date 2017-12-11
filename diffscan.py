#!/usr/bin/python3

import sys
sys.path.insert(0, './vault')
from vault import *
import subprocess
import shlex
import os
import time
import requests
import json

#rename last scan result to xxx.old 
def version_files():
    abspath = os.path.abspath("outputs")
    for filename in os.listdir(abspath):
        os.rename(abspath+"/"+filename, abspath+"/"+filename+".old")

def scan(target):
    cmd = "masscan -c configs/{0}.conf".format(target)
    args = shlex.split(cmd)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.communicate()[0]
    

def compare(target):
    old = "outputs/"+target+".out.old"
    new = "outputs/"+target+".out"
    if os.path.exists(old):
        print("Comparing {0} and {1}:".format(old, new))
        with open (old, "r") as myfile1:
            oldfile=myfile1.readlines()
        with open (new, "r") as myfile2:
            newfile=myfile2.readlines()
        oldfile_nocomments = [x for x in oldfile if not x.startswith('#')]
        newfile_nocomments = [x for x in newfile if not x.startswith('#')]
        diff = list(set(newfile_nocomments) - set(oldfile_nocomments)) #diff new and old
        stripped_diff = [s.rstrip() for s in diff] #strip new lines
        non_empty_stripped_diff = list(filter(None, stripped_diff)) #filter out elements evaluated to False (e.g. empty elements)
#        print(non_empty_stripped_diff)
        if len(non_empty_stripped_diff): #if diff list is not empty
            print("Target - {0}: Previously unseen records found".format(target))
            for i in non_empty_stripped_diff:
                print("-", i)

            '''print for slack'''
            text = "*Target - {0}: Previously unseen records found!*\n".format(target)
            for i in non_empty_stripped_diff:
                text += ("- " + i + "\n")

            text += "*Target - {0}: Full scan results:*\n".format(target)
            for i in newfile:
                text += (i)
            url = SLACK_WEBHOOK
            data = {"channel":"#secbots", "username":"DIFFSCAN", "text":text, "icon_emoji":":pentest:"}
            headers = {'Content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(data), headers=headers)
        else:
            print("Target - {0}: No new records found in the last scan.".format(target))
            
            '''print for slack'''
            url = SLACK_WEBHOOK
            text_nonew = "*Target - {0}:* No new records found in the last scan.".format(target)
            data = {"channel":"#secbots", "username":"DIFFSCAN", "text":text_nonew, "icon_emoji":":pentest:"}
            headers = {'Content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(data), headers=headers)

    else:
        print("Older scan results not found. Nothing to compare.")

        '''print for slack'''
        text = "*Target - {0}*: Nothing to compare yet. Full scan results:\n".format(target)
        print(text)
        with open (new, "r") as myfile2:
            newfile=myfile2.readlines()
        for i in newfile:
            text += (i)
        url = SLACK_WEBHOOK
        data = {"channel":"#secbots", "username":"DIFFSCAN", "text":text, "icon_emoji":":pentest:"}
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers)

#cleanup - keep only latest(actual) results in /outputs. Versioned old files are not needed after diff. Moving them to /history...
def remove_mess():
    to_archive = [i + ".out.old" for i in targets] #list of files to archive
    for file in os.listdir("outputs"):
        if file in to_archive:
            os.rename("outputs/"+file, "history/"+file+str(time.time()))
    to_keep = [i + ".out" for i in targets] #list of files to keep in /outputs for next round
    for file in os.listdir("outputs"):
        if file not in to_keep:
            os.remove("outputs/"+file)


### EXEC

#create list of targets based on filenames in /config, e.g. ['test', 'as1234']
targets = []
for conf in os.listdir("configs"):
    name, extension = os.path.splitext(conf)
    targets.append(name)
print("Configs available: ", targets)

version_files()
print("Dir /outputs after versioning: ",os.listdir("outputs"))

scan('test')
compare('test')

remove_mess()
print("Dir /outputs after cleanup: ",os.listdir("outputs"))



