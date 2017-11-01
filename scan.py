#!/usr/bin/python3

import subprocess
import shlex
import os
import time

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
        diff = list(set(newfile_nocomments) - set(oldfile_nocomments)) #diff new old
        stripped_diff = [s.rstrip() for s in diff] #strip new lines
        non_empty_stripped_diff = list(filter(None, stripped_diff)) #filter elements evaluated to False (e.g. empty elements)
#        print(non_empty_stripped_diff)
        if len(non_empty_stripped_diff): #if list empty
            print("Previously unseen records found: ")
            for i in non_empty_stripped_diff:
                print("-", i)
        else:
            print("No new records found in the last scan.")
    else:
        print("Older scan results not found. Nothing to compare.")

###^ ked pribudne v .out, najde rozdiel. ak odpbudne v .out, rozdiel nenajde. hlada len to, co pribudlo v new (.out)


#cleanup - keep only latest(actual) results in /outputs, e.g. ['test.out', 'as1234'.out]. Versioned old files are not needed after diff. Removing them...
def remove_mess():
    to_archive = [i + ".out.old" for i in targets] #list of files to archive
    for file in os.listdir("outputs"):
        if file in to_archive:
            os.rename("outputs/"+file, "history/"+file+str(time.time()))
    to_keep = [i + ".out" for i in targets] #lsit of files to keep in /outputs for next round
    for file in os.listdir("outputs"):
        if file not in to_keep:
            os.remove("outputs/"+file)


### EXEC

#create list of targets based on filenames in /config, e.g. ['test', 'as1234']
targets = []
for conf in os.listdir("configs"):
    name, extension = os.path.splitext(conf)
    targets.append(name)
print("Configs defined: ", targets)

version_files()
print("Dir /outpus after versioning: ",os.listdir("outputs"))

scan('jk')
print("Dir /outputs after scan: ",os.listdir("outputs"))

compare('jk')

remove_mess()
print("Dir /outputs after cleanup: ",os.listdir("outputs"))



