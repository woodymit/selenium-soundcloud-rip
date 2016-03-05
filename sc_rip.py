import argparse
import glob
import os
import shutil
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from settings import *


def newest_mp3(directory):
	mp3_list = glob.iglob(os.path.join(directory, "*.[Mm][Pp]3"))
	return max(mp3_list, key=os.path.getctime) if mp3_list else None


def rip_url(track_url, dest, driver):
	driver.get('http://soundflush.com/')

	track_url_elem_list = driver.find_elements_by_name('track_url')
	assert len(track_url_elem_list) == 1
	track_url_elem = track_url_elem_list[0]
	track_url_elem.send_keys(track_url)
	track_url_elem.send_keys(Keys.RETURN)

	button_save_list = driver.find_elements_by_class_name('button--save')
	assert len(button_save_list) == 1
	button_save_elem = button_save_list[0]
	
	mp3_list = glob.iglob(os.path.join(downloads_folder, "*.[Mm][Pp]3"))
	prev_newest = max(mp3_list, key=os.path.getctime) if mp3_list else None
	
	button_save_elem.click()

	newest = newest_mp3(downloads_folder)
	while newest == prev_newest:
		time.sleep(0.2)
		newest = newest_mp3(downloads_folder)

	shutil.copyfile(newest, dest)


def get_name_url_tuples(playlist_url, driver):

	driver.get(playlist_url)
	track_elements = driver.find_elements_by_class_name('trackItem__trackTitle')

	return [(e.text, e.get_attribute('href')) for e in track_elements]


def rip_playlist(playlist_url, playlist_foldername, driver):

	dest_folder = os.path.join(mp3_folder, playlist_foldername)
	os.mkdir(dest_folder)
	name_url_tuples = get_name_url_tuples(playlist_url, driver)
	
	for name, url in name_url_tuples:
		sanitized_name = name.replace(' ', '_')
		dest_path = os.path.join(dest_folder, sanitized_name)
		
		rip_url(url, dest_path, driver)


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('playlist_url')
	parser.add_argument('new_folder_name')
	args = parser.parse_args()

	os.environ["webdriver.chrome.driver"] = chromedriver
	driver = webdriver.Chrome(chromedriver)

	rip_playlist(args.playlist_url, args.new_folder_name, driver)

	driver.close()

