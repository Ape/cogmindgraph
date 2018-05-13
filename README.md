# cogmindgraph
`cogmindgraph` is a tool for generating player progression graphs for
[Cogmind](http://www.gridsagegames.com/cogmind/). Generated graphs are
available online on https://ape3000.com/cogmindgraph/.

![completion](https://ape3000.com/cogmindgraph/Ape/completion.png)
![score](https://ape3000.com/cogmindgraph/Ape/score.png)

## Requirements
* Python 3
* Numpy
* Matplotlib
* Yattag (optional)
  * Required for `--html` option

## Usage
```
usage: main.py [-h] [--xaxis {time,turns,actions,runs,date}] [--player PLAYER]
               [--dpi DPI] [--html]
               path output

positional arguments:
  path                  Path to Cogmind scores folder
  output                Path to output folder

optional arguments:
  -h, --help            show this help message and exit
  --xaxis {time,turns,actions,runs,date}
                        X axis variable (default: time)
  --player PLAYER       Only plot the specified player
  --dpi DPI             Resolution for output files (default: 200)
  --html                Make HTML index files (default: False)
```

For example:
```
./main.py /path/to/cogmind/scores /path/to/output
```
