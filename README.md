# Bard
A simple music bot for discord.

# Prerequisites

You need a couple of stuff to make this plug&n play:

```python
pip install discord
```
```python
pip install asyncio
```
```python
python3 -m pip install --force-reinstall https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz
```

It's very important that you install that specific version of yt_dlp because otherwise you'll get that annyoing "no user id found" error.

If you want it to be easily replaced in your code just do:
```python
import yt_dlp as youtube_dl
```

You'll also need FFmpeg for either windows/linux/mac. For windows you simply add it as an environmental variable for the .exe. For Linux and Mac you'll have to look it up. 

# Commands

?play <youtube link>	- plays the song 
?stop									- stops the song and kicks the bot from the channel.
?skip									- skips the song 
?add 									- adds to queue

Simple and easy.

For more features, stay tooned.
