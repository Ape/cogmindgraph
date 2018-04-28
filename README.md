# cogmindgraph
`cogmindgraph` is a tool for generating player progression graphs for
[Cogmind](http://www.gridsagegames.com/cogmind/).

![lore%](https://i.imgur.com/8EIXovC.png)
![game length](https://i.imgur.com/oE3GivD.png)

## Requirements
* Python 3
* Numpy
* Matplotlib

## Usage
```
usage: main.py [-h] [--xaxis {time,turns,runs,date}] [--name NAME]
               [--output OUTPUT] [--dpi DPI]
               path

positional arguments:
  path                  Path to Cogmind scores folder

optional arguments:
  -h, --help            show this help message and exit
  --xaxis {time,turns,runs,date}
                        X axis variable (default: time)
  --name NAME           Player name
  --output OUTPUT       Path to output folder
  --dpi DPI             Resolution for output files (default: 200)
```

For example:
```
./main.py /path/to/cogmind/scores --output /path/to/output
```
