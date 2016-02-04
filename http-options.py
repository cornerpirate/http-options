#!/usr/bin/python
# script used to check HTTP options against a provided list
# of directories on a server
#
# calling: ./http-options.py <file_of_directories> <url>
# for example: ./http-options.py dirs.txt http://192.168.100.108
# 
# Copyright 2016 cornerpirate.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# == Developers
# cornerpirate - https://twitter.com/cornerpirate
import sys
import httplib
import re
from urlparse import urlparse
from colorama import init, Fore

init() # initialise colour support

#uncomment if you want to see requests in detail
#httplib.HTTPConnection.debuglevel=1
finalanswer = []

# check the answer, if it has DAV in the response headers
# or PUT|DELETE in the allow header, then display it in RED
# with the text "ENABLED" to allow grepping
def checkAnswer(folder, url, response):

	dav = str(response.getheader("DAV"))
	if dav == "None":
		dav = "Dav DISABLED"
	else:
		dav = "Dave ENABLED (" + dav + ")"
	allows = str(response.getheader("allow"))

	if re.search('PUT|DELETE', allows, re.IGNORECASE):
		# Dav is likely enabled, we have PUT or DELETE too
		print(Fore.RED + folder + ":" + dav + ":" + allows + Fore.RESET)
		finalanswer.append("davtest -url " + url + folder + " -move -sendbd auto")
	else:
		# Dav is likey disabled but look at the pretty options
		print(Fore.GREEN + folder + ":" + dav + ":" + allows + Fore.RESET)

# make an OPTIONS request to the URL with the directory appended
def tryOptions(dir, url):
	o = urlparse(url)
	host = o.netloc	
	protocol = o.scheme
	# Work out the protocol and then establish connection appropriately
	conn = None
	if protocol == "http":
		conn = httplib.HTTPConnection(host)
	else:
		conn = httplib.HTTPSConnection(host)

	# Optional headers, add any more like cookies etc which is unlikely for OPTIONS
	headers = '''
Host: ^^host^^
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.6.0
'''
	headers = headers.replace("^^host^^", host)
	headers = dict([[field.strip() for field in pair.split(":", 1)] for pair in headers.strip().split('\n')])
	conn.request("OPTIONS", dir, "" , headers)
	response = conn.getresponse()

	allows = response.getheader("allow")
	checkAnswer(folder, url, response)
	#data = response.read()

# Check that the user has input a string
if len(sys.argv) != 3:
	print "Usage : " + sys.argv[0] + " <directory_file> <url> "
	print "Example: " + sys.argv[0] + " folders.txt http://192.168.5.108 "
	sys.exit(-1)

in_file = sys.argv[1]
url = sys.argv[2]

print "=== Using: " + in_file

dir_file = open(in_file, "r") # open the file for reading

for folder in dir_file:
	folder = folder.strip() # remove \n
	tryOptions(folder, url) # execute check

print "=== Recommended next action(s) ==="
for answer in finalanswer:
	print answer

dir_file.close() # close the file

