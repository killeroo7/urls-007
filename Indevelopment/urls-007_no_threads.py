#!/usr/bin/env python3

import subprocess
from termcolor import colored
import os
import threading
import time
import argparse
import shutil
import signal,sys
import socket
import re,configparser

def banner():
	x="""
		_  _ _ _    _    ____ ____   ____ ____ ___ 
		|_/  | |    |    |___ |__/   |  | |  |   /
		| \\_ | |___ |___ |___ |  \\   |__| |__|  /  
      """


 
	y = "		+-----------------------------------------+"     
	z = "							~~Twitter: Killeroo7p\n\n"
	print(colored(x,'blue'))
	print(colored(y,'red'))
	print(colored(z,'green'))


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-u','--url',dest='url',required=True,help="Specify URL")
	parser.add_argument('-o','--output',dest='output',help="Output Location")
	parser.add_argument('-g','--gau-single',dest='gau_single',action='store_true',help="Run gau on the main domain only",default=False)

	args = parser.parse_args()
	return args

def filter_duplicate_domains(x):
  return list(dict.fromkeys(x))

def getallURLs(url,gau_single):
	os.mkdir("ALL_URLS")
	print(colored("[+] Started GetAllURLS(gau) [This may take some time]","green"))
	if gau_single:
		gau_cmd = f"gau {url} > ALL_URLS/gau_results" 
	else:
		gau_cmd = f"cat subdomains.txt | gau > ALL_URLS/gau_results" 

	with open(os.devnull,'w') as devnull:
		subprocess.call(gau_cmd,shell=True,stderr=devnull)	
	print(colored("[+] GetallURLs Scan Completed","yellow"))


def get_url_with_param():

	with open("ALL_URLS/gau_results","r") as subfile:
		with open("ALL_URLS/urls_with_parameters","w") as paramfile:
			for line in subfile:
				if "?" and "=" in line:
					paramfile.write(line)
	print(colored("[+] Filtered URLs with Parameters","yellow"))

def get_urls_with_uniq_params():  

	param_wordlist =[]   		#For Parameter Wordlist 
	unique_params=[]     		#List Used For Filtering Purpose
	urls_with_unique_params =[] #List to Store All Unique URLS

	with open("ALL_URLS/urls_with_parameters","r") as file:
		for url in file:
			url_part = (re.search(r"(.*)(?:\?)",url))
			first_param = (re.search(r"(?:\?)(\w+)(?:=)",url))
			other_params = re.findall(r"(?:\&)(\w*)",url)

			all_items=""

			if first_param and other_params and url_part:   #IF URL Contain More than one parameter

				for item in other_params:             #Extracting other parameters as a list
					all_items +=item

					if item not in param_wordlist:    #Add other parameters to Wordlist File
						param_wordlist.append(item)

					if first_param.group(1) not in param_wordlist:    #Add first parameter to wordlist file
						param_wordlist.append(first_param.group(1))

				total = url_part.group(1)+":"+first_param.group(1)+all_items   #Concatenating as URL:FirstParamOtherPsram
				if total not in unique_params:								   #If the concatenated url not in the unique param
					unique_params.append(total)
					urls_with_unique_params.append(url)


			elif first_param and url_part:							#IF URL Contains Only one parameter
				total = url_part.group(1)+":"+first_param.group(1)

				if first_param.group(1) not in param_wordlist:      #Add first parameter to wordlist file
					param_wordlist.append(first_param.group(1))

				if total not in unique_params:
					unique_params.append(total)
					urls_with_unique_params.append(url)
		

	with open("ALL_URLS/urls_with_unique_params","w") as file:
		for item in urls_with_unique_params:
			file.write(item)

	with open("ALL_URLS/parameter_wordlist","w") as file:
		for item in param_wordlist:
			file.write(item+"\n")

	print(colored("[+] Created Dictionary Unique Parameters","yellow"))
	print(colored("[+] Filtered URLs Containing Unique Parameters","yellow"))


def get_urls_with_http():

	#One liner bash
	# cut -c5- urls_with_parameters |grep "http" | sed -e 's/^/http/' > new_urls_with_http
	urls_with_http=[]
	with open ("ALL_URLS/urls_with_unique_params","r") as file:
		for line in file:
			if "http" in line[6:]:
				urls_with_http.append(line)


	with open ("ALL_URLS/urls_with_http_in_param","w") as file:
		for line in urls_with_http:
			file.write(line)

	print(colored("[+] Filtered URLs Containing HTTP in Parameters","yellow"))

def main():

	args = get_args()
	url = args.urls
	gau_single = args.gau_single

	getallURLs(url,gau_single)
	urls_with_parameters()
	urls_with_unique_params()
	urls_with_http_in_param()

	print(colored("\n[+] url-007 Completed","blue"))