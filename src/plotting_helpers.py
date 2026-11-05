"""Reusable plotting templates for scientific journals, project reports, and slides.

This module is self-contained: it can be installed as a package or copied as a single
file into a project. plotly and matplotlib are optional and only imported when used.

Styles are defined in two backend-neutral layers:
  * designs (nature, sci4clim, ariadne): font family and colours;
  * targets (print, slide): font sizes, line widths, and spacing in pt.
A design and a target are merged into a `Style`, which is then converted into a
backend-specific template (plotly or matplotlib).

Usage:
    from plotting_helpers import get_style_plotly, get_styles_plotly, set_aliases

    set_aliases({"Coal": {"nature": "black", "sci4clim": "grey-dark", "ariadne": "#000000"}})
    template, colours = get_style_plotly("nature", "print", transparent=True)
    for tid, template, colours in get_styles_plotly(["nature", "ariadne"], ["print", "slide"]):
        ...
"""

from dataclasses import dataclass, field, replace
from itertools import product
from pathlib import Path


# %% Units.
# plotly measures sizes in px at 96 px per inch; these helpers convert to px.
def pt(pt: float) -> float:
    return pt * 96 / 72


def mm(mm: float) -> float:
    return mm / 25.4 * 96


# Default resolution of rastered images (PNG). Has no effect on vector formats.
DPI = 300


# %% Colours.
COLOURS = {
    # Springer Nature.
    "nature": {
        "orange-light": "#f36f21",
        "turquoise": "#0e8088",
        "green-dark": "#00813e",
        "blue-dark": "#3647a3",
        "yellow": "#e6af2e",
        "brown": "#8a4c39",
        "purple": "#7c1f8a",
        "blue-light": "#589ace",
        "blue-very-dark": "#253173",
        "green-light": "#6ac100",
        "orange-dark": "#bd4b00",
        "grey-dark": "#444444",
        "grey-medium": "#666666",
        "grey-light": "#cccccc",
        "black": "#000000",
    },
    # SCI4Climate.NRW project.
    "sci4clim": {
        "orange-light": "#f29400",
        "blue-dark": "#00629b",
        "blue-light": "#009ee0",
        "turquoise": "#019b96",
        "yellow": "#f2c200",
        "green-dark": "#009b08",
        "green-light": "#00e01e",
        "red-light": "#e00004",
        "red-dark": "#9b0003",
        "brown": "#8b5300",
        "purple": "#a100f2",
        "grey-light": "#cbcbcb",
        "grey-dark": "#787878",
    },
    # Ariadne project.
    "ariadne": {
        "red-dark": "#903547",
        "blue-light": "#008cb2",
        "blue-dark": "#044177",
        "yellow": "#ecc15d",
        "green-dark": "#3c7d2c",
        "purple": "#5f4491",
    },
}

# Generic aliases shipped with the package. Project-specific aliases are added via
# `set_aliases`.
DEFAULT_ALIASES = {
    "primary": {"nature": "orange-light", "sci4clim": "orange-light", "ariadne": "red-dark"},
}

_aliases: dict = {}


def set_aliases(aliases: dict, replace_existing: bool = True):
    """Register colour aliases used by all subsequent calls of `get_style_*`.

    Each value is either the name of a palette colour (e.g. "black"), a literal colour
    (e.g. "#123456" or "rgb(...)"), or a dict mapping design names to one of these,
    for aliases that need to point to different colours per design.
    """
    global _aliases
    _aliases = dict(aliases) if replace_existing else _aliases | aliases


def _resolve_colour(value, design: str, palette: dict, alias: str) -> str:
    if isinstance(value, dict):
        if design not in value:
            raise KeyError(f"Colour alias '{alias}' has no entry for design '{design}'.")
        value = value[design]
    if value in palette:
        return palette[value]
    if value.startswith(("#", "rgb", "hsl")):
        return value
    raise KeyError(
        f"Colour alias '{alias}' refers to '{value}', which is not in the "
        f"'{design}' palette: {list(palette)}."
    )


def get_colours(design: str) -> dict:
    palette = COLOURS[design]
    aliases = DEFAULT_ALIASES | _aliases
    return palette | {
        alias: _resolve_colour(value, design, palette, alias)
        for alias, value in aliases.items()
    }


def colour_with_alpha(colour: str, alpha: float) -> str:
    """Convert hex colour to rgba string. Non-hex colours are returned unchanged."""
    if not (colour.startswith("#") and len(colour) == 7):
        return colour
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alpha})"


# %% Styles.
@dataclass(frozen=True)
class Style:
    # Font.
    font_family: str
    # Font sizes in pt.
    font_size: float
    title_font_size: float
    axis_title_font_size: float
    tick_font_size: float
    legend_font_size: float
    legend_title_font_size: float
    legend_group_title_font_size: float
    annotation_font_size: float
    # Line widths in pt.
    line_width: float
    axis_line_width: float
    tick_width: float
    legend_border_width: float
    # Spacing in pt.
    axis_title_standoff: float
    margin: float
    # Colours.
    colours: dict = field(default_factory=dict)
    colorway: list = field(default_factory=list)
    transparent: bool = False


DESIGNS = {
    "nature": dict(font_family="Inter"),
    "sci4clim": dict(font_family="Carlito"),
    "ariadne": dict(font_family="Gudea"),
}

TARGETS = {
    "print": dict(
        font_size=5,
        title_font_size=7,
        axis_title_font_size=6,
        tick_font_size=5,
        legend_font_size=5,
        legend_title_font_size=7,
        legend_group_title_font_size=6,
        annotation_font_size=5,
        line_width=0.5,
        axis_line_width=0.5,
        tick_width=0.5,
        legend_border_width=0.5,
        axis_title_standoff=5,
        margin=10,
    ),
    "slide": dict(
        font_size=6,
        title_font_size=8,
        axis_title_font_size=7,
        tick_font_size=6,
        legend_font_size=6,
        legend_title_font_size=8,
        legend_group_title_font_size=7,
        annotation_font_size=6,
        line_width=1,
        axis_line_width=1,
        tick_width=1,
        legend_border_width=1,
        axis_title_standoff=6,
        margin=10,
    ),
}


def get_style(design: str, target: str, transparent: bool = False, **overrides) -> Style:
    """Merge design and target into a backend-neutral `Style`.

    Keyword arguments override individual fields, e.g. `font_size=8`.
    """
    if design not in DESIGNS:
        raise KeyError(f"Unknown design '{design}'. Choose from {list(DESIGNS)}.")
    if target not in TARGETS:
        raise KeyError(f"Unknown target '{target}'. Choose from {list(TARGETS)}.")
    style = Style(
        **DESIGNS[design],
        **TARGETS[target],
        colours=get_colours(design),
        colorway=list(COLOURS[design].values()),
        transparent=transparent,
    )
    return replace(style, **overrides)


# %% Backends.
def to_plotly(style: Style):
    import plotly.graph_objects as go
    import plotly.io as pio

    transparent = "rgba(255, 255, 255, 0)"
    axis = dict(
        showline=True,
        showgrid=False,
        zeroline=False,
        mirror=True,
        fixedrange=True,
        ticks="outside",
        linewidth=pt(style.axis_line_width),
        tickwidth=pt(style.tick_width),
        title_font_size=pt(style.axis_title_font_size),
        tickfont_size=pt(style.tick_font_size),
        title_standoff=pt(style.axis_title_standoff),
    )
    layout = dict(
        font_family=style.font_family,
        font_size=pt(style.font_size),
        title_font_size=pt(style.title_font_size),
        colorway=style.colorway,
        margin=dict(l=pt(style.margin), r=pt(style.margin), b=pt(style.margin), t=pt(style.margin)),
        legend=dict(
            bgcolor=transparent,
            borderwidth=pt(style.legend_border_width),
            font_size=pt(style.legend_font_size),
            title_font_size=pt(style.legend_title_font_size),
            grouptitlefont_size=pt(style.legend_group_title_font_size),
        ),
        annotationdefaults=dict(font_size=pt(style.annotation_font_size)),
        xaxis=axis,
        yaxis=axis,
    )
    if style.transparent:
        layout |= dict(plot_bgcolor=transparent, paper_bgcolor=transparent)
    line = dict(line=dict(width=pt(style.line_width)))
    data = dict(
        bar=[dict(marker=dict(line=dict(width=0)))],
        scatter=[line],
        scattergl=[line],
    )

    return go.layout.Template(pio.templates["simple_white"]).update(layout=layout, data=data)


def to_matplotlib(style: Style) -> dict:
    """Return rcParams, usable via `plt.rcParams.update(...)` or `plt.rc_context(...)`.

    matplotlib measures sizes in pt natively, so no unit conversion is needed.
    """
    from cycler import cycler

    return {
        "font.family": style.font_family,
        "font.size": style.font_size,
        "axes.titlesize": style.title_font_size,
        "axes.labelsize": style.axis_title_font_size,
        "axes.labelpad": style.axis_title_standoff,
        "axes.linewidth": style.axis_line_width,
        "axes.grid": False,
        "axes.prop_cycle": cycler(color=style.colorway),
        "xtick.labelsize": style.tick_font_size,
        "ytick.labelsize": style.tick_font_size,
        "xtick.major.width": style.tick_width,
        "ytick.major.width": style.tick_width,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "legend.fontsize": style.legend_font_size,
        "legend.title_fontsize": style.legend_title_font_size,
        "legend.frameon": False,
        "lines.linewidth": style.line_width,
        "savefig.transparent": style.transparent,
    }


# %% Public interface.
def style_id(design: str, target: str, transparent: bool = False) -> str:
    return f"{design}_{target}" + ("_transparent" if transparent else "")


def get_style_plotly(design: str, target: str, transparent: bool = False, **overrides):
    """Return `(template, colours)` for plotly.

    The template is also registered in `plotly.io.templates` under its ID
    (e.g. "nature_print"), so it can be referenced by name.
    """
    import plotly.io as pio

    style = get_style(design, target, transparent, **overrides)
    template = to_plotly(style)
    pio.templates[style_id(design, target, transparent)] = template
    return template, style.colours


def get_style_matplotlib(design: str, target: str, transparent: bool = False, **overrides):
    """Return `(rcparams, colours)` for matplotlib."""
    style = get_style(design, target, transparent, **overrides)
    return to_matplotlib(style), style.colours


def _iterate(get, designs, targets, transparent, **overrides):
    as_list = lambda x: list(x) if isinstance(x, (list, tuple)) else [x]
    for design, target, transp in product(as_list(designs), as_list(targets), as_list(transparent)):
        template, colours = get(design, target, transp, **overrides)
        yield style_id(design, target, transp), template, colours


def get_styles_plotly(designs, targets, transparent=False, **overrides):
    """Yield `(id, template, colours)` for all combinations of designs, targets, and
    transparency settings. Each argument accepts a single value or a list.
    """
    return _iterate(get_style_plotly, designs, targets, transparent, **overrides)


def get_styles_matplotlib(designs, targets, transparent=False, **overrides):
    """Yield `(id, rcparams, colours)` for all combinations of designs, targets, and
    transparency settings. Each argument accepts a single value or a list.
    """
    return _iterate(get_style_matplotlib, designs, targets, transparent, **overrides)


# %% Export.
def write_images(fig, name: str, path: Path | str = ".",
                 width: float | None = None, height: float | None = None,
                 formats: list = ("png", "svg", "pdf"), dpi: float = DPI):
    """Export a plotly figure to several formats. Width and height are in px; use
    `mm()` to convert, e.g. `width=mm(180)`.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    for f in formats:
        if f not in ("png", "svg", "pdf", "ps", "eps"):
            raise ValueError(f"Unsupported format '{f}'.")
        kwargs = {}
        if width:
            kwargs["width"] = width
        if height:
            kwargs["height"] = height
        if f == "png":
            kwargs["scale"] = dpi / 96
        fig.write_image(path / f"{name}.{f}", **kwargs)
