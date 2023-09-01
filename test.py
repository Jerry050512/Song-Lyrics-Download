from song_lyrics_spider import get_lyrics_from_song
from selenium import webdriver
from log import log_wd

log_wd.logfile = '1.txt'
log_wd.open_window()

driver = webdriver.Edge()
lyrics = get_lyrics_from_song(driver, 
                              'https://www.musixmatch.com/lyrics/%E4%BA%94%E6%9C%88%E5%A4%A9/2012-1')
log_wd.log(lyrics)