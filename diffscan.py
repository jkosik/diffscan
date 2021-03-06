#!/usr/bin/python3

import sys
sys.path.insert(0, './vault')
from vault import *
import subprocess
import shlex
import os
import shutil
import datetime
import requests
import json

#rename last scan result to xxx.old 
def version_files(target):
    abspath = os.path.abspath("outputs")
    if not os.path.exists(abspath+"/"+target):
        os.makedirs(abspath+"/"+target)
    for filename in os.listdir(abspath+"/"+target):
#        print("filenames in outputs/target: ", filename)
        if filename != target+".out": os.remove(abspath+"/"+target+"/"+filename) #remove everything but target.out
        if filename == target+".out": os.rename(abspath+"/"+target+"/"+filename, abspath+"/"+target+"/"+filename+".old") #version only target.out

def scan(target):
    print("Scanning {0}...".format(target))
    cmd1 = "nmap -Pn -iL configs/{0}.conf --top-ports 10 -oG outputs/{0}/{0}.out --open".format(target)
    cmd2 = "sed -i '/Ports/!d' outputs/{0}/{0}.out".format(target)
    cmd3 = "sed -i 's/Ignored.*$//' outputs/{0}/{0}.out".format(target)
    subprocess.check_call(shlex.split(cmd1))
    shutil.copyfile("outputs/"+target+"/"+target+".out", "history/"+target+".out."+str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+".raw")) #backup also raw scan

    subprocess.check_call(shlex.split(cmd2))
    subprocess.check_call(shlex.split(cmd3))

#subprocess.check_call dost not allow to redirect stdout to file (>). Use Popen instead:
#    out_file_path = "outputs/{0}/{0}.out".format(target)
#    out_file = open(out_file_path, 'w+')
#    subprocess.Popen(shlex.split(cmdX), stdout=out_file, stderr=subprocess.PIPE)

def compare(target):
    print("Comparing with the previous scan...")
    url = SLACK_WEBHOOK
    old = "outputs/"+target+"/"+target+".out.old"
    new = "outputs/"+target+"/"+target+".out"
    if os.path.exists(old):
        print("Comparing {0} and {1}".format(old, new))
        with open (old, "r") as myfile1:
            oldfile=myfile1.readlines()
        with open (new, "r") as myfile2:
            newfile=myfile2.readlines()
        diff = list(set(newfile) - set(oldfile)) #diff new and old
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
            data = {"channel":SLACK_CHANNEL, "username":"DIFFSCAN", "text":text, "icon_emoji":":pentest:"}
            headers = {'Content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(data), headers=headers)
        else:
            print("Target - {0}: No new records found in the last scan.".format(target))
            
            '''print for slack'''
            text_nonew = "*Target - {0}:* No new records found in the last scan.".format(target)
            data = {"channel":SLACK_CHANNEL, "username":"DIFFSCAN", "text":text_nonew, "icon_emoji":":pentest:"}
            headers = {'Content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(data), headers=headers)

    else:
        print("Older scan results not found. Nothing to compare.")
        text = "*Target - {0}*: Nothing to compare yet. Full scan results:\n".format(target)
        with open (new, "r") as myfile2:
            newfile=myfile2.readlines()
        for i in newfile:
            text += (i)
        print(text)
        data = {"channel":SLACK_CHANNEL, "username":"DIFFSCAN", "text":text, "icon_emoji":":pentest:"}
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers)

#cleanup - keep only latest(actual) results in /outputs. Versioned old files are not needed after diff. Moving them to /history...
def archive(target):
    shutil.copyfile("outputs/"+target+"/"+target+".out", "history/"+target+".out."+str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')))


### EXEC

#create list of potential targets
targets = []
for conf in os.listdir("configs"):
    name, extension = os.path.splitext(conf)
    targets.append(name)
print("Configs available: ", targets)

targets_to_use = ['test'] #add configs to be used
for i in targets_to_use:
    print("=== RUNNING DIFFSCAN AGAINST {0} ===".format(i))
    version_files(i)
    scan(i)
    compare(i)
    archive(i)

print("/outputs dir: ",os.listdir("outputs"))



