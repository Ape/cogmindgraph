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
usage: main.py [-h] [--turns] [--name NAME] [--output OUTPUT] [--dpi DPI] path

positional arguments:
  path             Path to Cogmind folder

optional arguments:
  -h, --help       show this help message and exit
  --turns          Use turns as the X axis instead of playing time
  --name NAME      Player name
  --output OUTPUT  Path to output folder
  --dpi DPI        Resolution for output files
```

For example:
```
./main.py /path/to/cogmind --output /path/to/output
```
