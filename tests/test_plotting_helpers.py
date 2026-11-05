import plotly.graph_objects as go
import plotly.io as pio
import pytest

import plotting_helpers as ph
from plotting_helpers import (
    get_style_matplotlib, get_style_plotly, get_styles_matplotlib, get_styles_plotly, pt, set_aliases,
)


@pytest.fixture(autouse=True)
def reset_aliases():
    set_aliases({})
    yield
    set_aliases({})


def test_get_style_plotly():
    template, colours = get_style_plotly("nature", "print", transparent=True)
    assert isinstance(template, go.layout.Template)
    assert template.layout.font.family == "Inter"
    assert template.layout.font.size == pytest.approx(pt(5))
    assert template.layout.paper_bgcolor == "rgba(255, 255, 255, 0)"
    assert colours["primary"] == "#f36f21"
    assert "nature_print_transparent" in pio.templates


def test_all_designs():
    for tid, template, colours in get_styles_plotly(list(ph.DESIGNS), ["print", "slide"]):
        assert colours["primary"] in template.layout.colorway
    _, colours = get_style_plotly("ariadne", "print")
    assert colours["primary"] == "#903547"


def test_slide_larger_than_print():
    t_print, _ = get_style_plotly("sci4clim", "print")
    t_slide, _ = get_style_plotly("sci4clim", "slide")
    assert t_slide.layout.font.size > t_print.layout.font.size
    assert t_slide.layout.xaxis.linewidth > t_print.layout.xaxis.linewidth


def test_aliases_resolve_per_design():
    set_aliases({
        "Coal": {"nature": "black", "sci4clim": "grey-dark"},
        "Gas": "blue-dark",
        "Custom": "#123456",
    })
    _, c_nature = get_style_plotly("nature", "print")
    _, c_sci4clim = get_style_plotly("sci4clim", "print")
    assert c_nature["Coal"] == "#000000"
    assert c_sci4clim["Coal"] == "#787878"
    assert c_nature["Gas"] == "#3647a3"
    assert c_sci4clim["Custom"] == "#123456"


def test_unknown_alias_target_raises():
    set_aliases({"Coal": "black"})
    with pytest.raises(KeyError):
        get_style_plotly("sci4clim", "print")
    set_aliases({"Coal": {"nature": "black"}})
    with pytest.raises(KeyError):
        get_style_plotly("ariadne", "print")


def test_get_styles_plotly_loop():
    ids = [tid for tid, _, _ in get_styles_plotly(["nature", "sci4clim"], ["print", "slide"])]
    assert ids == ["nature_print", "nature_slide", "sci4clim_print", "sci4clim_slide"]


def test_overrides():
    template, _ = get_style_plotly("nature", "print", font_size=9)
    assert template.layout.font.size == pytest.approx(pt(9))


def test_get_style_matplotlib():
    rc, _ = get_style_matplotlib("nature", "slide")
    import matplotlib.pyplot as plt
    with plt.rc_context(rc):
        assert plt.rcParams["font.size"] == 6
        assert plt.rcParams["lines.linewidth"] == 1


def test_get_styles_matplotlib_loop():
    ids = [tid for tid, _, _ in get_styles_matplotlib("nature", "print", [False, True])]
    assert ids == ["nature_print", "nature_print_transparent"]


def test_colour_with_alpha():
    assert ph.colour_with_alpha("#ff0000", 0.5) == "rgba(255, 0, 0, 0.5)"
    assert ph.colour_with_alpha("red", 0.5) == "red"
