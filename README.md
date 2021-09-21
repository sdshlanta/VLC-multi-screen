# VLC Multi-Screen Controller

Loads and controls the same media in multiple VLC player windows in a
synchronized fashion.

## Usage

### CLI

```
usage: VideoControler.py [-h] [-w WINDOWS] [-v] media

Control a VLC media player.

positional arguments:
  media                 The media file to play.

optional arguments:
  -h, --help            show this help message and exit
  -w WINDOWS, --windows WINDOWS
                        The number of windows to create, defaults to 2.
  -v, --verbose         Enable verbose logging.
```

#### CLI Example

The following command will start a video called `example.mp4` in two windows, as
two is the default number of windows:

`python3 ./VideoController.py ./example.mp4`

To override the number of windows use the `-w` or `--windows` flag:

`python3 ./VideoController.py ./example.mp4 -w 5`

### Playback Controls

During playback the following controls are available in the terminal:

```
[q]: Quit: Exit the program.
[p/' ']: Play/Pause: Pause a playing video and play a paused video
[r]: Restart Video: Restart the video, currently skips the first second of media
[f]: Toggle Full Screen: Toggles the fullscreen state of the player
```

Pressing Enter/Return is not required to engage these controls