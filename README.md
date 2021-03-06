# cogmindgraph
`cogmindgraph` is a tool for generating player progression graphs for
[Cogmind](http://www.gridsagegames.com/cogmind/). Generated graphs are
available online on https://ape3000.com/cogmindgraph/.

<img src="https://ape3000.com/cogmindgraph/Ape/completion.svg" alt="completion" width="100%" />
<img src="https://ape3000.com/cogmindgraph/Ape/score.svg" alt="score" width="100%" />

## Requirements
* Python 3
* Numpy
* Matplotlib
* Yattag (optional)
  * Required for `--html` option
* cairosvg (optional)
  * Required for `--format png` option

## Usage
```
python -m cogmindgraph [-h] [--pb-path PB_PATH]
                       [--xaxis {time,turns,actions,runs,date}]
                       [--player PLAYER] [--format {svg,png}] [--size SIZE]
                       [--html] path output

positional arguments:
  path                  Path to Cogmind scores folder
  output                Path to output folder

optional arguments:
  -h, --help            show this help message and exit
  --pb-path PB_PATH     Path to additional protobuf scores (default: None)
  --xaxis {time,turns,actions,runs,date}
                        X axis variable (default: time)
  --player PLAYER       Only plot the specified player
  --format {svg,png}    Output image format (default: svg)
  --size SIZE           Output image width (default: 1280)
  --html                Make HTML index files (default: False)
```

For example:
```
python -m cogmindgraph /path/to/cogmind/scores /path/to/output
```
