from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from time import sleep
from os import system
from urllib.parse import unquote
import atexit
import json

from log import log_wd

# The album page of a singer in the musixmatch.com
TARGET_URL = 'https://www.musixmatch.com/artist/%E4%BA%94%E6%9C%88%E5%A4%A9/albums'
MAX_ATTEMPT_TIME = 50
JSON_INDENT = 4
SLEEP_TIME = 1.5

get_resource_name = lambda url: unquote(url.split('/')[-1])
pause = lambda: system('pause')

def recaptcha_detect(driver: webdriver.Edge):
    '''Detect if the page was redirected to the recaptcha. When the site was accessed 
    too many times, it will be redirected to the recaptcha page.
    
    Return: 1 if redirected else 0'''
    current_url = driver.current_url
    if 'verify-user' in current_url: 
        log_wd.log('Wait for the recaptcha...')
        log_wd.window.input('输入回车以继续...')
        log_wd.log('Recaptcha passed...')
        return 1
    return 0

def load_page(driver: webdriver.Edge):
    '''Try to click the load more button many times so that the webpage can
    be fully loaded.
    
    Return: None'''
    driver.refresh()
    i, max_time = 1, 6
    while i < max_time:
        log_wd.log(f'Try {i}th time to load more...')
        i += 1
        try:
            button = driver.find_element(By.CSS_SELECTOR, "a.button.page-load-more")
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
        except:
            # Anything wrong? Just wait, wait, and wait...
            log_wd.log(f'Unable to click the load button, wait {i+2} secs...', 'error')
            driver.refresh()
            max_time += 1
            if max_time > MAX_ATTEMPT_TIME:
                log_wd.log('\n'.join(('Unable to load page...', 
                               f'Trial time: {i}')), 'error')
                driver.refresh()
                return
            sleep(i)
        sleep(2)
    if recaptcha_detect(driver):
        driver.get(TARGET_URL)
        load_page(driver)
    log_wd.log('Root page loaded...')

def get_albums_url(driver: webdriver.Edge):
    '''Get albums url from current page.
    
    Return: list of albums url'''
    try:
        albums = driver.find_elements(By.CSS_SELECTOR, "div > h2.media-card-title > a")
        albums = [album.get_attribute('href') for album in albums]
    except:
        log_wd.log('Unable to get album list...', 'error')
        albums = []
    log_wd.log('Get album url list: ')
    log_wd.log('\n'.join((unquote(album) for album in albums)))
    return albums

def write_title(url: str, type: str):
    '''Just a function to quick write the title or album name of the song...
    
    Return: title(str) of the resource'''
    title = get_resource_name(url)
    line_break = '\n' * 3 if title == 'Album' else '\n' * 2
    with open('lyrics.txt', 'a+', encoding='utf-8') as f:
        f.write(f'{type}-{title}{line_break}')
    return title

def get_songs_from_album(driver: webdriver.Edge, url: str):
    '''Get the songs\' url in the given album url.
    
    Return: list of songs\' url'''
    driver.get(url)
    while recaptcha_detect(driver):
        driver.get(url)
    title = get_resource_name(url)
    sleep(SLEEP_TIME)
    try:
        songs = [song.get_attribute("href") for song in driver.find_elements(By.CSS_SELECTOR, "ul.mui-collection.mui-collection--list.mui-collection--medium > li > a")]
    except:
        log_wd.log(f'Unable to get song list in {title}', 'error')
        songs = []
    return songs

def get_lyrics_from_song(driver: webdriver.Edge, url: str, accessed_songs=None):
    '''Get the lyrics from the song page. Skip songs in accessed_songs(list).
    
    Return: lyrics(str)'''
    driver.get(url)
    while recaptcha_detect(driver):
        driver.get(url)
    
    # Check if accessed
    if accessed_songs is None:
        accessed_songs = []
    song_name = get_resource_name(url)
    if song_name in accessed_songs:
        log_wd.log(f'Accessed song: {song_name}')
        return ""
    accessed_songs.append(song_name)
    sleep(SLEEP_TIME)
    
    try:
        # If the page do not have lyrics due to some reasons, it renders this.
        empty_title = driver.find_element(By.CSS_SELECTOR, 'h2.mxm-empty__title').text
        log_wd.log(f'{song_name}: {empty_title}', 'error')
    except:
        pass
    try:
        empty_message = driver.find_element(By.CSS_SELECTOR, 'div.empty-message').text
        log_wd.log(f'{song_name}: {empty_message}', 'error')
    except:
        pass

    try:
        # When the lyrics have some error to modify, it renders this.
        lyrics = [lyric.text for lyric in driver.find_elements(By.CSS_SELECTOR, "span.lyrics__content__error")]
        if lyrics:
            lyrics = "\n\n".join(lyrics) + '\n\n\n'
            log_wd.log(f'Get lyrics of {song_name}')
            return lyrics
    except:
        pass

    try:
        # Normally the lyrics render like this.
        lyrics = [lyric.text for lyric in driver.find_elements(By.CSS_SELECTOR, "span.lyrics__content__ok")]
        if lyrics:
            lyrics = "\n\n".join(lyrics) + '\n\n\n'
            log_wd.log(f'Get lyrics of {song_name}')
        else:
            log_wd.log(f'Unable to get lyrics of {song_name}', 'error')
            lyrics = ""
    except:
        # I don't know how to cause this exception, but it truly happened.
        log_wd.log(f'Unable to get lyrics of {song_name}', 'error')
        lyrics = ""
    return lyrics

def exit_handler(accessed_songs: list):
    '''Save file before exit.

    Note. Changes will not be saved if you click the close button. But this can 
    handle the Ctrl+C keyborad interruption.
    
    Return: None'''
    log_wd.log('Exit program. Saving data...')
    print('Exit program. Saving data...')
    with open('saved_songs.json', 'w', encoding='utf-8') as f:
        json.dump(accessed_songs, f, indent=JSON_INDENT)


def main():
    # Open the log window.
    log_wd.open_window()

    options = Options()
    driver = webdriver.Edge()
    driver.get(TARGET_URL)

    # Read the accessed_song list.
    accessed_songs = []
    try:
        with open('saved_songs.json', 'r', encoding='utf-8') as f:
            accessed_songs = json.load(f)
    except:
        log_wd.log('saved_song.json did not exist or invalid expression in the file...', 'error')

    # Register the exit_handler.
    atexit.register(exit_handler, accessed_songs)

    # Load the root album page.
    while recaptcha_detect(driver):
        driver.get(TARGET_URL)
    load_page(driver)

    albums = get_albums_url(driver)
    driver.quit()
    # Switch the option to save loading time.
    options.page_load_strategy = 'none'
    driver = webdriver.Edge(options=options)


    # Iterate the albums list
    for album in albums:
        songs = get_songs_from_album(driver, album)
        album_name = get_resource_name(album)
        log_wd.log(f'Iterate in album {album_name}')
        # Use the flag to confirm if the album has something to save.
        flag = False
        for song in songs:
            lyrics = get_lyrics_from_song(driver, song, accessed_songs)
            if lyrics:
                if not flag:
                    write_title(album, 'Album')
                    flag = True
                with open("lyrics.txt", "a+", encoding="utf-8") as f:
                    f.write(lyrics)

    pause()
    driver.quit()

if __name__ == '__main__':
    main()