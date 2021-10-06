# VLC Multi-Screen Controller

Loads and controls the same media in multiple VLC player windows in a
synchronized fashion.

## Usage

### CLI

```
usage: VideoControler.py [-h] [-w WINDOWS] [-v] [-s]
                         media_files [media_files ...]

Control a VLC media player.

positional arguments:
  media_files           The media file to play.

optional arguments:
  -h, --help            show this help message and exit
  -w WINDOWS, --windows WINDOWS
                        The number of windows to create, defaults to 2.
  -v, --verbose         Enable verbose logging.
  -s, --shuffle         Shuffle the playlist at initial load.
```

#### CLI Example

The following command will start a video called `example.mp4` in two windows, as
two is the default number of windows:

`python3 .\VideoController.py .\example.mp4`

To override the number of windows use the `-w` or `--windows` flag:

`python3 .\VideoController.py .\example.mp4 -w 5`

To create a playlist, simply provide additional videos as positional arguments:

`python3 .\VideoController.py .\example.mp4 .\example2.mp4`

By default the playlist will play in order the file names were provided, to
shuffle them provide the `-s` flag.

### Playback Controls

During playback the following controls are available in the terminal:

```
[q]: Quit
[' '/p]: Play/Pause
[r]: Restart Video
[f]: Toggle Full Screen
[<]: Previous Video
[>]: Next Video
[l]: Toggle Loop Mode
[v]: Volume Up/Down
[m]: Toggle Minimize
```

Pressing Enter/Return is not required to engage these controls