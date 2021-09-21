import argparse
import msvcrt
import os
import threading
import time
from typing import List

import vlc

exiting = False

def loop_thread(players, media_time, adjust_time = 2000):
    media_time -= adjust_time
    get_time = players[0].get_time

    while not exiting:
        cur_time = get_time()
        
        if cur_time >= media_time:
            for player in players:
                player.set_time(1000)

@vlc.CallbackDecorators.LogCb
def null_log_callback(data, level, ctx, fmt, args):
    # Do nothing
    pass

def main():
    global exiting

    # Create MediaPlayer objects and filter out any invalid ones (there 
    # shouldn't be any I'm just making Pylance happy).
    players: List[vlc.MediaPlayer] = list(
        filter(None, [vlc.MediaPlayer() for _ in range(args.screens)])
    )

    # Load media
    media = vlc.Media(args.media)
    for player in players:
        player.set_media(media)
        player.play()

    # hide warnings from VLC
    for player in players:
        instance = player.get_instance()
        instance.log_set(null_log_callback, None)

    os.environ["VLC_VERBOSE"] = str("-1")

    # Delay to allow VLC to load media
    time.sleep(0.2)

    # Hack to skip the first second of the video
    for player in players:
        player.set_time(1000)

    # Startup loop controll thread
    media_time = players[0].get_length()
    thread = threading.Thread(target=loop_thread, args=(players, media_time))
    thread.start()


    # handle keyboard input
    try:
        key = ''
        while not exiting:
            if key == 'q':
                exiting = True
            elif key == 'p' or key == ' ':
                for player in players:
                    player.pause()
            elif key == 'r':
                for player in players:
                    player.set_time(1000)
            elif key == 'f':
                for player in players:
                    player.toggle_fullscreen()

            print(
                "[q]: Quit " \
                "[p]: Play/Pause " \
                "[r]: Restart Video " \
                "[f]: Toggle Full Screen",
                end="\r"
            )
            try:
                key = msvcrt.getch().decode('utf-8').lower()
            except UnicodeError:
                pass

    except KeyboardInterrupt:
        exiting = True
    finally:
        # Terminate loop controll thread
        thread.join()
        for player in players:
            player.stop()
            player.release()
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control a VLC media player.')
    parser.add_argument('media' , help='The media file to play.')
    parser.add_argument(
        '-w', '--windows',
        help='The number of windows to create, defaults to 2.',
        type=int, default=2
    )
    args = parser.parse_args()

    main()
