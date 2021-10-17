#!/usr/bin/env python3

import argparse
import msvcrt
import os
import threading
import time
import random
from typing import Iterator, List

import vlc
import win32api
import win32gui
import win32con

exiting = False


# Provide loopable loop settings
def toggle_loop_settings():
    values = list(vlc.PlaybackMode._enum_names_.keys())

    while not exiting:
        for item in values:
            yield item
                
def volume_values():
    while not exiting:
        for i in range(0, 101, 5):
            yield i

def action_control_thread(players: List[vlc.MediaListPlayer], media_time, adjust_time = 2000):
    media_time -= adjust_time
    get_time = players[0].get_media_player().get_time
    get_media_name = players[0].get_media_player().get_media().get_mrl
    current_media = get_media_name()
    # print(f"Current media: {current_media}")

    while not exiting:
        if current_media != get_media_name():
            media_time = players[0].get_media_player().get_length()
            current_media = get_media_name()
            # print(f"Current media: {current_media}")
        cur_time = get_time()
        

@vlc.CallbackDecorators.LogCb
def null_log_callback(data, level, ctx, fmt, args):
    # Do nothing
    pass

def main():
    global exiting

    # Detect OS
    if os.name != "nt":
        print("Only Windows is supported at this time.")
        return

    
    if args.shuffle:
        random.shuffle(args.media_files)

    media_list = vlc.MediaList()
    if media_list is None:
        print("Failed to create media list")
        return
    for media_file in args.media_files:
        # Check that the media file exists/is accessible, if not, exit. We use a try
        # block here because if the file doesn't exist, we get a PermissionError and 
        # os.access() is not always effective.
        try:
            with open(media_file, 'r') as f:
                pass
        except FileNotFoundError:
            print(
                f"Media file {media_file} does not exist!"
            )

        except PermissionError:
            print(
                f"Media file {media_file} is not accessible!"
            )

        media_list.add_media(vlc.Media(media_file))

    # Create MediaPlayer objects and filter out any invalid ones (there 
    # shouldn't be any I'm just making Pylance happy).
    players: List[vlc.MediaListPlayer] = list(
        filter(None, [vlc.MediaListPlayer() for _ in range(args.windows)])
    )

    # Load media and position windows
    window_handles = []
    for i, player in enumerate(players, start=num_monitors-args.windows):
        player.set_media_list(media_list)
        player.play()

        # Sleep required to ensure that window gets put on the correct screen. 
        # Otherwise, the window will be on the primary screen. (so weird)
        time.sleep(0.5)

        hwnd = 0
        while hwnd is 0:
            hwnd = win32gui.FindWindow(None, 'VLC (Direct3D11 output)')

        window_handles.append(hwnd)

        monitor = win32api.EnumDisplayMonitors()[i]
        monitor_info = win32api.GetMonitorInfo(monitor[0])
        monotor_position = monitor_info['Monitor']
        win32gui.MoveWindow(hwnd, monotor_position[0], monotor_position[1], monotor_position[2], monotor_position[3], True)

    # Sync up footage after play starts
    for player in players:
        player.get_media_player().set_time(1000)

    # hide warnings from VLC
    if args.verbose:
        os.environ["VLC_VERBOSE"] = str("3")
    else:
        for player in players:
            instance = player.get_instance()
            instance.log_set(null_log_callback, None)
        os.environ["VLC_VERBOSE"] = str("-1")

    # Set players to loop and enable full screen
    for player in players:
        player.set_playback_mode(vlc.PlaybackMode.loop)
        player.get_media_player().toggle_fullscreen()

    # Startup loop controll thread
    media_time = players[0].get_media_player().get_length()
    thread = threading.Thread(target=action_control_thread, args=(players, media_time))
    thread.start()

    # Hacky forever looping iterator to loop through playlist loop control
    # states and volume values.
    loop_control_state: Iterator = toggle_loop_settings()
    volume_value: Iterator = volume_values()

    minimized = False
    # handle keyboard input
    try:
        key = ''
        while not exiting:
            if key == 'q':
                exiting = True
            elif key == ' ' or key == 'p':
                for player in players:
                    player.pause()
            elif key == 'r':
                for player in players:
                    player.get_media_player().set_time(1000)
            elif key == 'f':
                for player in players:
                    player.get_media_player().toggle_fullscreen()
            elif key == '.' or key == '>':
                for player in players:
                    player.next()
            elif key == ',' or key == '<':
                for player in players:
                    player.previous()
            elif key == 'l':
                loop_state = next(loop_control_state)
                for player in players:
                    player.set_playback_mode(loop_state)
            elif key == 'v':
                volume = next(volume_value)
                for player in players:
                    player.get_media_player().audio_set_volume(volume)
            elif key == 'm':
                for window in window_handles:
                    if minimized:
                        win32gui.ShowWindow(window, win32con.SW_SHOW)
                    else:
                        win32gui.ShowWindow(window, win32con.SW_HIDE)
                minimized = not minimized

            print(' '.join(
                    [
                        "[q]: Quit",
                        "[' '/p]: Play/Pause",
                        "[r]: Restart Video",
                        "[f]: Toggle Full Screen",
                        "[<]: Previous Video",
                        "[>]: Next Video",
                        "[l]: Toggle Loop Mode",
                        "[v]: Volume Up/Down",
                        "[m]: Toggle Minimize",
                    ]
                ),
                end="\r"
            )
            try:
                key = msvcrt.getch().decode('utf-8').lower()
            except UnicodeError:
                pass

    except KeyboardInterrupt:
        exiting = True
    finally:
        thread.join()
        # Terminate loop controll thread
        for player in players:
            player.stop()
            player.release()
    # Print a newline to give the prompt a clean line to print
    print('')
            
if __name__ == '__main__':
    num_monitors = len(win32api.EnumDisplayMonitors())
    if num_monitors - 1 > 0:
        available_monitors = num_monitors - 1
    
    parser = argparse.ArgumentParser(description='Control a VLC media player.')
    parser.add_argument('media_files', nargs="+", help='The media file to play.')
    parser.add_argument(
        '-w', '--windows',
        help=f'The number of windows to create, defaults to '  \
             f'{available_monitors}. (Will place them on the non-primary ' \
             f'monitor by default unless there is only one monitor)',
        type=int, default=available_monitors
    )
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose logging.',
        action='store_true'
    )
    parser.add_argument(
        '-s', '--shuffle',
        help='Shuffle the playlist at initial load.',
        action='store_true'
    )
    args = parser.parse_args()
    print(args.windows)
    main()
