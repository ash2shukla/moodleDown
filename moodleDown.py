import urllib
import requests
from bs4 import BeautifulSoup
import os
from shutil import rmtree
from sys import argv
import tarfile

class moodleDown:
	def __init__(self,USERNAME,PASSWORD,URL="http://117.55.242.132/moodle/login/index.php"):
		self.data = {
					"username":USERNAME,
					"password":PASSWORD}
		self.URL = URL

	def _get_session(self):
		s = requests.Session()
		s.post(url=self.URL,data=self.data)
		return s

	def _create_soup(self):
		s = requests.Session()
		soup = BeautifulSoup(s.post(url=self.URL,data=self.data).text)
		return soup

	def _get_name(self,soup):
		# base directory will be created as per the name of student
		uname = '_'.join(soup.find('h1').contents[0].split(' '))
		return uname

	def get_subjects(self):
		soup = self._create_soup()
		subjects = soup.findAll('p',{'class':'tree_item branch'})

		# subject dict contains keys as subject name and corresponding course URL as value

		subject_dict={}

		for i in subjects:
			if i.a is not None:
				subject_dict[i.a['title']]=i.a['href']
		return subject_dict


	def load_folder(self,dir_path,URL):
		s = self._get_session()
		try:
			os.mkdir(dir_path)
		except:
			print "Directory Already Exists, Merging downloads in existing directory"
		soup = BeautifulSoup(s.get(URL).text)
		files = soup.findAll('span',{'class':'fp-filename-icon'})
		for i in files :
			for j in i.findAll('a'):
				File_URL = j['href']
				content = s.get(File_URL).content
				open(dir_path+"/"+j.span.contents[0]['alt'],"w").write(content)

	def load_resource(self,dir_path,rsrc_type,URL):
		s = self._get_session()
		if 'pdf' in rsrc_type:
			file_at = dir_path+'.pdf'
		elif 'powerpoint' in rsrc_type:
			file_at = dir_path+'.ppt'
		elif 'document' in rsrc_type:
			file_at = dir_path+'.docx'
		open(file_at,"w").write(s.get(URL).content)

	def to_tar(self,uname):
		with tarfile.open(uname+"_moodle.tar", "w") as tar:
			tar.add(uname,arcname=os.path.basename(uname))


	def loadAll(self):
		base_soup = self._create_soup()
		# create directory with username
		uname = self._get_name(base_soup)
		try:
			os.mkdir(uname)
		except:
			print "Directory already exists . Type 'del' to remove the directory , or Press Enter to Exit. "
			val =  raw_input()
			if val == "":
				exit()
			elif val.lower() == "del":
				rmtree(uname)
				os.mkdir(uname)
		subject_dict = self.get_subjects()
		base_dir = uname+"/"
		# iterate in all subjects

		for k,v in subject_dict.iteritems():
			self.loadSubject(k,base_dir)
		# convert the folder to tar
		self.to_tar(uname)

		# Remove folder
		rmtree(uname)

	def loadSubject(self,subject,base_dir=""):
		dic =  self.get_subjects()
		subject_list = dic.keys()
		if subject in subject_list:
			os.mkdir(base_dir+subject)
			s = self._get_session()
			units = BeautifulSoup(s.get(dic[subject]).text).findAll('li',{'class':'section main clearfix'})
			for i in units:
				# create folders for units inside subjects
				unit_dir = base_dir+subject+"/"+i.span.string
				os.mkdir(unit_dir)
				print "Downloading ... " ,i.span.string

				# Sessions are timedout after certain number of requests so create a new session for each UNIT

				for j in i.findAll('a'):
				# Find all Files
					url = j['href']
					if '/forum/' in url:
						pass
					elif '/folder/' in url:
						file_name = j.span.contents[0]
 						self.load_folder(unit_dir+"/"+file_name,url)
					elif '/resource/' in url:
						file_name = j.span.contents[0]
						self.load_resource(unit_dir+"/"+file_name,j.img['src'],url)
		else:
			raise Exception("Subject not found. Did you try calling get_subjects first ?")

if __name__ == "__main__":
	instance = moodleDown("ashishshukla","!23XyzAbc")
	instance.loadSubject('Web Technology(CSB & CSC)')
