# plotting-helpers

Reusable plotting templates for plotly (and, in basic form, matplotlib) for three designs (`nature`: Springer Nature; `sci4clim`: SCI4Climate.NRW; `ariadne`: Ariadne) and two targets (`print`, `slide`).

## Installation

Either install as a dependency:

```bash
# plotly (add "export" for figure export via kaleido):
uv add "plotting-helpers[plotly,export] @ git+https://github.com/<user>/plotting-helpers"
# matplotlib only:
uv add "plotting-helpers[matplotlib] @ git+https://github.com/<user>/plotting-helpers"
```

or copy `src/plotting_helpers.py` into the project folder. The file only requires plotly and/or matplotlib, depending on which is used.

## Usage

```python
from plotting_helpers import get_style_plotly, get_styles_plotly, set_aliases, write_images, mm

# Project-specific colour aliases, defined once at the top of the notebook.
# Values are palette names, literal colours, or dicts per design.
set_aliases({
    "Coal": {"nature": "black", "sci4clim": "grey-dark", "ariadne": "#000000"},
    "Gas": "blue-dark",
})

# Single template.
template, colours = get_style_plotly("nature", "print", transparent=True)
fig = go.Figure(go.Scatter(x=x, y=y, line_color=colours["Coal"]), layout=dict(template=template))

# Loop over combinations; `tid` is e.g. "nature_print".
for tid, template, colours in get_styles_plotly(["nature", "ariadne"], ["print", "slide"]):
    fig = make_figure(template, colours)
    write_images(fig, "fig1", path=FIG_PATH / tid, width=mm(180))

# matplotlib: returns rcParams.
from plotting_helpers import get_style_matplotlib, get_styles_matplotlib
rc, colours = get_style_matplotlib("nature", "print")
with plt.rc_context(rc):
    ...
```

Individual style parameters can be overridden, e.g. `get_style_plotly("nature", "slide", font_size=8)`.

## Structure

Styles are defined in backend-neutral layers in pt:

- `DESIGNS`: font family per design; `COLOURS`: named palette per design.
- `TARGETS`: font sizes, line widths, and spacing per target.

`get_style()` merges a design and a target into a `Style` object. `to_plotly()` and `to_matplotlib()` convert it into the respective backend format. A new design or target means adding an entry to `DESIGNS`/`COLOURS` or `TARGETS`; a new backend means adding `to_<backend>()` and `get_style(s)_<backend>()`.
