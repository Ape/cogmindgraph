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
usage: main.py [-h] [--xaxis {time,turns,runs,date}] [--name NAME] [--dpi DPI]
               path output

positional arguments:
  path                  Path to Cogmind scores folder
  output                Path to output folder

optional arguments:
  -h, --help            show this help message and exit
  --xaxis {time,turns,runs,date}
                        X axis variable (default: time)
  --name NAME           Player name
  --dpi DPI             Resolution for output files (default: 200)
```

For example:
```
./main.py /path/to/cogmind/scores /path/to/output
```
