Pydiagrams is a declarative drawing library built on top of [PyCairo](https://pycairo.readthedocs.io).
The API draws heavy inspiration from Haskell's [diagrams](https://diagrams.github.io/) and Scala's [doodle](https://github.com/creativescala/doodle/).

⚠️ The library is still very much work in progress and subject to change.

## Overview

Below we provide a brief introduction of the main functionality of the library.
These examples are available in the `examples/intro.py` file.

We start by importing the [`colour`](https://github.com/vaab/colour) module and the `diagrams` functions:

```python
from colour import Color
from diagrams import *
```

We also define some colors that will be shortly used:

```python
papaya = Color("#ff9700")
blue = Color("#005FDB")
```

We can easily create basic shapes (the functions `circle`, `square`, `triangle`) and style them with various attributes (the methods`fill_color`, `line_color`, `line_width`).
For example:

```python
d = circle(1).fill_color(papaya)
```

![circle](examples/output/intro-01.png)

The diagram can be saved to an image using the `render` method:

```python
d.render("examples/output/intro-01.png", height=64)
```

We can glue together two diagrams using the combinators `atop` (or `+`), `beside` (or `|`), `above` (or `/`).
For example:

```python
circle(2).fill_color(papaya) | square(1).fill_color(blue)
```

which is equivalent to

```python
circle(2).fill_color(papaya).beside(square(1).fill_color(blue))
```

This code produces the following image:

![atop](examples/output/intro-02.png)

We also provide combinators for a list of diagrams:
`hcat` for horizontal composition, `vcat` for vertical composition.
For example:

```python
hcat(circle(0.1 * i) for i in range(1, 6)).fill_color(blue)
```
![hcat](examples/output/intro-03.png)

We can use Python functions to build more intricate diagrams:

```python
def sierpinski(n: int, size: int) -> Diagram:
    if n <= 1:
        return triangle(size)
    else:
        smaller = sierpinski(n - 1, size / 2)
        return smaller.above(smaller.beside(smaller).center_xy())

d = sierpinski(5, 4).fill_color(papaya)
```

![sierpinski](examples/output/intro-04.png)

For more examples, please check the `examples` folder.
These scripts can be run using [Streamlit](https://streamlit.io/):

```bash
streamlit run examples/squares.py
```

![squares](examples/output/squares.png)

```bash
streamlit run examples/escher_square_limit.py
```

![escher](examples/output/escher_square_limit.png)