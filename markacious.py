#
#  Markacious v0.11
#
#  Author : ogudacity
#
#  This program analyzes a bookmark file
#  (as produced by popular browsers such as
#	Firefox
#	Chrome
#	Safari
#
#	In development : I.E. 8 or I.E. 9)
#
# Functions:
#
# DONE
#	- basic statistics
#	- look for duplicates
#	- gather folders 
#	- minimum compatibility for various browsers
#	- list all domains and all tlds used in urls
#
# TO DO
#
#    A) Features
#
#	- check if urls are current
#	- gather keywords and tags for each url and folder
#	- proposes folders by using these keywords and the link graph between urls
#	- check for related pages on various services
#	- output modified/enhanced/sorted bookmark files for various browsers
#
#
#    B) Methods
#
#	- group/degroup requests by host, reading robots.txt
#	- create my own UserAgent or fake a traditional one instead of Python's
#	- gather the hierarchical structure of the bookmark file
#
#
#    C) Usability / Compatibility
#
#       - make a command line interface for most common parameters
#	- make a test with Opera
#	- gather "related" info on urls
#	- input saved html files as supplementary data
#
#
#    D) Roadmap
#
#	- turn into a series of browser plugins
#	- find a way to exploit history
#	- automatic updates of specific subfolders
#	- many more
#

#
# Links to CS 101
#
# As I was completely new to python before starting the course, when something
# was not covered during the lectures or homeworks, I relied heavily on
# two sources : the online Python documentation for basic usage
# (especially the content of the standard lib)
# and Stack Overflow for specific problems and smart ways to do things.
#
# Inspired from the course :
#	Building a search engine with a crawler :=> crawling from personal browsing information to assist users. 
#	Crawling pages with a seed page :=> using the bookmark file as a user-generated content.
#
# Directly from the course : 
#	Defining and using data structures based on nested dicts and arrays 
#  	Use of the PageRank principle with the graph weights to enhance sorting of bookmarks
#	Multi-character split (put the reference to homework)
#
# Solved through standard python libraries
#
#
# Solved through non standard libraries
#	TLDs decomposition (with further customization) 
#
# Dictionary sorting
# 	http://writeonly.wordpress.com/2008/08/30/sorting-dictionaries-by-value-in-python-improved/


#
# Regular expression library. 
import re
# Time conversion library
import time



# Extracting subdomains has been programmed many times
# I use a library found on StackOverflow
# http://stackoverflow.com/questions/569137/how-to-get-domain-name-from-url/569219#569219
# I have forked it to disable the use of the logging library (which requires installing it formally)
# and the update of the TLD list as explained in the README of the original library
#

import ogtldextract


#x = raw_input('Do you want to test links (y/N) ?')

#if x=='y' or x=='Y' :
#	for u in websites:
#		print u


# Example found on http://stackoverflow.com/questions/107405/how-do-you-send-a-head-http-request-in-python
# This solution uses the object paradigm in python, but I do not need
# to understand it fully to use it
import urllib2
class HeadRequest(urllib2.Request):
     def get_method(self):
         return "HEAD"

def test_a_few_links():
	for u in (bookmarks.keys())[3:5] : 
		try:
			res = urllib2.urlopen(HeadRequest(u))
			print res.geturl()
			print res.info()
			print res
		except urllib2.HTTPError, error:
			errdata = error.read()
			print errdata
	
# TO DO: a utility routine to check that a url is authorized for retrieval
# by robots.txt


# Inspired by a post of a blog : writeonly.wordpress.com
# Added a parameter
from operator import itemgetter

def dictsort(d,reverse=False):
	return sorted(d.iteritems(), key=itemgetter(1), reverse=True)

def dictsortsub(d,n=0,reverse=False):
	return sorted(d.iteritems(), key=itemgetter(1)[n], reverse=True)

#
# Graph rank computation from Unit6.28   "Finishing the page ranking algorithm."
# It was nice to get it right the first time.
#

def compute_ranks(graph):
    d = 0.77 # damping factor chosen by experiment
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            
            for otherpage in graph:
                if page in graph[otherpage]:
                    newrank = newrank+ d*ranks[otherpage]/len(graph[otherpage])
            
            newranks[page] = newrank
        ranks = newranks
    return ranks




 
# small function to catch missing dates 
# and convert to float for later conversion
def safedate(s):
	if s=='':
		return 0
	return float(s)


# Get useful words from an HTML page
def getwords_fromHTML(page):
	return page.split()
	

# First Loop : reading the bookmark file

# Bookmarks is a dict of arrays
# Folders is a collection of folders and subfolders
# The key is the url
# Each entry has [<title of link/page>, <date of entry>, <use or add counter>]

def read_bookmarks( filename, browser):
	#
	# Dictionary of bookmark file patterns
	# Modern browsers are fairly close in the way they store 
	# bookmarks, but each has its own little peculiarities
	# We also need a way to grab urls from generic html files
	#
	patterns = {
		 'chrome' : {
			'urlmatch' : '[ \t]*<DT><A ',
			'urlgrab'  : 'HREF="([^"]*)".*ADD_DATE="([^"]*)".*>(.*)</A>',
			'foldermatch' : '[ \t]*<DT><H3',
			'foldergrab' : '<H3.*ADD_DATE="([0-9]+)".*>(.*)</H3>',
			'folderstart' : '[ \t]*<DL><p>',
			'folderend'   : '[ \t]*</DL><p>',
			# Chrome does not seem to include <DD> lines, but just in case,
			# same pattern as in firefox
			'summarymatch' : '[ \t]*<DD>',
			# <DD> items are not closed by a </DD>
			'summarygrab' : '<DD>([^<]+)'
			},
			
		 'firefox' : {
			'urlmatch' : '[ \t]*<DT><A ',
			'urlgrab'  : 'HREF="([^"]*)".*ADD_DATE="([^"]*)".*>(.*)</A>',
			'foldermatch' : '[ \t]*<DT><H3',
			'foldergrab' : '<H3.*ADD_DATE="([0-9]+)".*>(.*)</H3>',
			'folderstart' : '[ \t]*<DL><p>',
			'folderend'   : '[ \t]*</DL><p>',
			'summarymatch' : '[ \t]*<DD>',
			# <DD> items are not closed by a </DD>
			'summarygrab' : '<DD>([^<]+)'
			},
			
	# Safari
	#	uses tabs before HTML tags
	#	does not store dates for urls or folders
	#	
		 'safari' : {
			'urlmatch' : '[ \t]*<DT><A ',
			'urlgrab'  : 'HREF="([^"]*)"().*>(.*)</A>',
			'foldermatch' : '[ \t]*<DT><H3',
			'foldergrab' : '<H3 FOLDED.*()>(.*)</H3>',
			'folderstart' : '[ \t]*<DL><p>',
			'folderend'   : '[ \t]*</DL><p>',
			# Safari does not seem to include <DD> lines, but just in case,
			# same pattern as in firefox
			'summarymatch' : '[ \t]*<DD>',
			# <DD> items are not closed by a </DD>
			'summarygrab' : '<DD>([^<]+)'
			},
			
	# In the generic case (any html input file), case-insensitive matches and no expected structure
		'generic' : {
			'urlmatch' : '(?i).*<A ',
			'urlgrav' : '(?i)<A .*HREF="([^"]*)".*>(.*)</A>',
			'foldermatch': 'UYJHGKHR_A_B_Z_Y',
			'foldergrab' : '',
			'summarymatch' : 'UVTBQPP_Y_A_Z_B',
			'summarygrab' : ''
			}
	}
	
	bookmarks = {'unknown': ['unknown', ['Default'], [0.0], 0]} 
	
	folders = {'Default': [0, 0.0, [] ]}
	
	foldertree = [ ]
	
	urlsummary = {}
	
	currentfolder = 'Default'
	currenturl = 'unknown'
	
	# Depth recognition is experimental right now
	currentdepth = 0
	maxdepth = 0
	
	# For statistics purposes
	lcount = 0
	
	# the 'rU' mode means : read only, Universal line break (good for portability)
	bkfile = open(filename, 'rU')
	
	for l in bkfile: 
		lcount +=1
	# Pre-check for new url
		if re.match(patterns[browser]['urlmatch'],l) :
			w = (re.findall(patterns[browser]['urlgrab'],l))
			if w:
	# Normally the pattern should match only once and always by line.
				if len(w) > 1:
					print "ACHTUNG"
				v = w[0]
				currenturl = v[0]
				if currenturl in bookmarks:
	# We have already seen this bookmark. Get the old record, update the counter and add a new date.
					ov = bookmarks[currenturl]
	#				Convert the date string to float for later use
					bookmarks[currenturl] = [v[2], ov[1]+[currentfolder], ov[2]+[safedate(v[1])], ov[3]+1] 
				else:
	# This is a new entry
					bookmarks[currenturl] = [v[2],[currentfolder], [safedate(v[1])],1]
				f= folders[currentfolder]
				f[0] = f[0] + 1
				folders[currentfolder] = f
				
				
	
	
	# Pre-check for summary/comment/tag (<DD> pattern)
		elif re.match(patterns[browser]['summarymatch'],l):
			w = (re.findall(patterns[browser]['summarygrab'],l))
			if w:
				print "====== SUMMARY ======"
				print w
				if currenturl in urlsummary:
					urlsummary[currenturl]= urlsummary[currenturl].join(w)
				else:
					urlsummary[currenturl]=w
	#			w.split()
	#			for t in w:
	#				tags_index['t']= currenturl	
	
	# Pre-check for new folder
		elif re.match(patterns[browser]['foldermatch'],l):
	# Grabing the folder's name
			w = (re.findall(patterns[browser]['foldergrab'],l))
			if w:
				v = w[0]
				folders[v[1]] = [0, currentdepth, currentfolder, safedate(v[0]), []]
				currentfolder = v[1]

		elif re.match(patterns[browser]['folderstart'],l):
			currentdepth = currentdepth+1
			maxdepth = max(maxdepth, currentdepth)
			
		elif re.match(patterns[browser]['folderend'],l):
			currentdepth = currentdepth-1
			if currentdepth < 0:
				print "ACHTUNG : negative depth"

	bkfile.close()
	
	return lcount, maxdepth, bookmarks, folders, foldertree, urlsummary

def bookmarksfile_header():
	return()


def write_bookmarksfile(filename, tree, browser):
	return()


# Second application : print duplicate bookmarks

def print_duplicates():
	for u in bookmarks:
		if bookmarks[u][3]>1:
			print bookmarks[u][0], bookmarks[u][1], time.ctime(bookmarks[u][2][0]+0.0), bookmarks[u][3]



def extract_url_components():
	websites = {}
	domains = {}
	tlds ={}

	for u in bookmarks:
		dlist = ogtldextract.extract(u)
	
		t=''
		if dlist[2] != '':
			t = dlist[2]
			if t in tlds :
				tlds[t] = [tlds[t][0]+1]
			else:
				tlds[t] = [1]
		else:
		# Cases I have seen are
		#	- IP address
		#	- javascript
			print "TLD EMPTY !!!:", dlist
	
		if dlist[1] != '':
			d = dlist[1]+'.'+dlist[2]
			if d in domains :
				domains[d] = [domains[d][0]+1]
			else:
				domains[d] = [1]
		else:
			print "DOMAIN EMPTY !!!:", dlist
	
	# Do not add an extraneaous point is the subdomain is empty
		if dlist[0] == '':
			w = dlist[1]+'.'+dlist[2]
		else:
			w = dlist[0]+'.'+dlist[1]+'.'+dlist[2]
		if w in websites :
			websites[w] = [websites[w][0]+1]
		else:
			websites[w] = [1]
	return websites, domains, tlds




def print_dict(dict):
	v = dictsort(dict)
	for e,f in v:
		if f[0]>1:
			print e,":", f 
	return


# First application : bookmark statistics

def print_statistics():
	print "File:", bookmark_filename
	print lcount, "lines read."
	print len(bookmarks.keys()),"collected urls"
	print len(urlsummary.keys()),"collected url summaries"
	print len(folders.keys()),"folders and subfolders"
	print "Max depth: ", maxdepth
	print "====================="
	return

#
# MAIN CODE
# CALLING THE REST
#
#
#

bookmark_filename = './bookmarks_chrome.html'
#bookmark_filename = './bookmarks_firefox.html'
#bookmark_filename = './bookmarks_safari.html'

# Type of browser creating the bookmark file
#browsertype = 'safari'
browsertype = 'firefox'

lcount, maxdepth, bookmarks, folders, foldertree, urlsummary = read_bookmarks(bookmark_filename, browsertype)

print "\n===============\n\n"

print_statistics()

print "\n===============\n\n"


# Second application : print duplicate bookmarks

print_duplicates()

print "\n===============\n\n"


# Third application : list found folders

print_dict(folders)

print "\n===============\n\n"

# Fourth application : extract web sites and domain names and statistics

websites, domains, tlds = extract_url_components()

print_dict(websites)
print "\n===============\n\n"

print_dict(domains)
print "\n===============\n\n"

print_dict(tlds)
print "\n===============\n\n"


exit()
