# cogmindgraph
`cogmindgraph` is a tool for generating player progression graphs for
[Cogmind](http://www.gridsagegames.com/cogmind/).

![lore%](https://i.imgur.com/8EIXovC.png)
![game length](https://i.imgur.com/oE3GivD.png)

## Requirements
* Python 3
* Numpy
* Matplotlib
* Yattag (optional)
  * Required for `--html` option

## Usage
```
usage: main.py [-h] [--xaxis {time,turns,runs,date}] [--dpi DPI] [--html]
               path output

positional arguments:
  path                  Path to Cogmind scores folder
  output                Path to output folder

optional arguments:
  -h, --help            show this help message and exit
  --xaxis {time,turns,runs,date}
                        X axis variable (default: time)
  --dpi DPI             Resolution for output files (default: 200)
  --html                Make HTML index files (default: False)
```

For example:
```
./main.py /path/to/cogmind/scores /path/to/output
```
