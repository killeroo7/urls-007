#!/usr/bin/env python3

import subprocess
from termcolor import colored
import os
import threading
import time
import argparse
import shutil,time
import signal,sys
import socket,math
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
	t = time.localtime()
	current_time = time.strftime("%H:%M:%S", t)
	print(colored(f"TIME: {current_time}","blue"))

def num_of_lines(wordlist):
    num_lines=0
    with open(wordlist,"r") as fp:
        for line in fp:
            num_lines +=1           
        return num_lines


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-w','--wordlist',dest='wordlist',help="File Containing list of subdomains",default=False)
	parser.add_argument('-u','--url',dest='url',help="Run gau on the main domain only",default=False)
	parser.add_argument('-v','--verbose',dest='verbose',help="Verbose Mode",action="store_true",default=False)
	parser.add_argument('-t','--thread',dest='threads',help="Number Of threads",default=2,type=int)
	parser.add_argument('-o','--output',dest='output',help="Output Location")

	args = parser.parse_args()
	if not args.wordlist and not args.url:
		parser.error(colored("Please specify either URL or File","red"))
	return args

def filter_duplicate_domains(x):
  return list(dict.fromkeys(x))

def getallURLs(url,wordlist,verbose):
	os.mkdir("ALL_URLS")
	print(colored("[+] Started GetAllURLS(gau) [This may take some time]","green"))
	if url:
		if verbose:
			gau_cmd = f"gau {url} | tee ALL_URLS/gau_results_temp"
		else:
			gau_cmd = f"gau {url} > ALL_URLS/gau_results_temp" 
	else:
		if verbose:
			gau_cmd = f"cat {wordlist} | gau | tee ALL_URLS/gau_results_temp" 
		else:
			gau_cmd = f"cat {wordlist} | gau > ALL_URLS/gau_results_temp" 

	with open(os.devnull,'w') as devnull:
		subprocess.call(gau_cmd,shell=True)	

	subprocess.call("sort -u ALL_URLS/gau_results_temp > ALL_URLS/gau_results",shell=True)
	os.remove("ALL_URLS/gau_results_temp")
	
	print(colored("[+] GetallURLs Scan Completed","yellow"))

def get_url_with_param(starto,endo,wordlist):
	start_line = starto                 
	end_line = endo
	with open(wordlist,"r") as subfile:
		for line in range(start_line):
			subfile.readline()

		with open("ALL_URLS/urls_with_parameters","w") as paramfile:
			for line in subfile:
				if "?" and "=" in line:
					paramfile.write(line)

				start_line +=1
				if(start_line==end_line):
					return

param_wordlist =[]   		#For Parameter Wordlist 
unique_params=[]     		#List Used For Filtering Purpose
urls_with_unique_params =[] #List to Store All Unique URLS


def get_urls_with_uniq_params(starto,endo,wordlist):
	start_line = starto                 
	end_line = endo
    
	with open(wordlist,"r") as file:
		for line in range(start_line):
			file.readline()

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

			start_line +=1
			if(start_line==end_line):
				with open("ALL_URLS/urls_with_unique_params.txt","a+") as file:
					for item in urls_with_unique_params:
						file.write(item)

				with open("ALL_URLS/parameter_wordlist_temp","a+") as file:
					for item in param_wordlist:
						file.write(item+"\n")

				return


def get_juicy_files_n_params():
	juicy_files_n_params_cmd = "grep -iE 'xmlrpc|resetpass' ALL_URLS/gau_results > ALL_URLS/juicy_files_n_params.txt"
	subprocess.call(juicy_files_n_params_cmd,shell=True)

	juicy_extension_cmd = "grep -iE '\.config|\.php|\.asp|\.jsp' ALL_URLS/gau_results > ALL_URLS/juicy_extensions.txt"
	subprocess.call(juicy_extension_cmd,shell=True)

	urls_with_http_in_params_cmd = '''cut -b 1-4 --complement ALL_URLS/urls_with_unique_params.txt | grep "http" | awk -F="" '{print "http"$0}' > ALL_URLS/http_in_params.txt'''
	subprocess.call(urls_with_http_in_params_cmd,shell=True)


def thread_it(function_name,threads,wordlist,*Msg):
	print(colored(f"{Msg[0]}","green"))
	no_of_threads= threads
	total_words = num_of_lines(wordlist)
	each_thread_words = math.ceil(int(total_words/no_of_threads))
	begin=0
	end=each_thread_words
	
	for i in range(no_of_threads):                      
		t1 = threading.Thread(target=function_name, args=(begin,end,wordlist)) 
		t1.start()
		begin += each_thread_words
		end += each_thread_words

	t1.join()
	endtime=time.time()
	print(colored(f"{Msg[1]}","yellow"))

def main():
	banner()
	args = get_args()

	url = args.url
	wordlist = args.wordlist
	threads = args.threads
	verbose = args.verbose

	getallURLs(url,wordlist,verbose)

	Msg=["[+] Filtering URLs with Parameters","[+] Filtered URLs with Parameters"]
	thread_it(get_url_with_param,threads,"ALL_URLS/gau_results",*Msg)

	Msg=["[+] Filtering URLs Having Unique Parameters","[+] Created Parameter Wordlist\n[+] Filtered URLs Containing Unique Parameters"]
	thread_it(get_urls_with_uniq_params,threads,"ALL_URLS/urls_with_parameters",*Msg)

	try:
		subprocess.call("sort -u ALL_URLS/parameter_wordlist_temp > ALL_URLS/parameter_wordlist",shell=True)
		os.remove("ALL_URLS/parameter_wordlist_temp")
	except:
		pass

	get_juicy_files_n_params()

main()