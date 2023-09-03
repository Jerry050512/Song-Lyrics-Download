# Song-Lyrics-Download

A simple python web spider to fetch lyrics from musixmatch.com

## Environment

Test Operating System: Windows 11 23H2

Before start, you should install the following python modules:
1. selenium: An brower automate test module
2. window_terminal: To create a new console showing clear output.

After opening terminal in the project folder, you just need to run the following code to install them:
```python
pip install -r requirements.txt
```

## Usage

1. Modify the constant `TARGET_URL` in the `song_lyrics_spider.py` file.
 The `TARGET_URL` is an album page of one singer.
2. Run the python code and you'll get the result in the `lyrics.txt` file.

Note. Accessing too many web pages might cause the rechaptcha page. The program will wait you until you pass the rechaptcha test and press the enter key in the main terminal.