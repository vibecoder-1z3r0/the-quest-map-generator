"""Character filtering and the markdown subset, including hostile input."""

from __future__ import annotations

import pytest

CLEAN = "(t, o) => QMG.cleanText(t, o)"


def clean(page, text, **opts):
    return page.evaluate(CLEAN, [text, opts])


@pytest.fixture
def cleaner(page):
    def run(text, **opts):
        return page.evaluate("([t, o]) => QMG.cleanText(t, o)", [text, opts])

    return run


def test_allowed_characters_pass_through_unchanged(cleaner):
    text = "Aa 09 . , ! ? ' \" : ; ( ) [ ] - * # | & \\ / + _ ü日"
    assert cleaner(text)["text"] == text
    assert cleaner(text)["removed"] is False


def test_disallowed_characters_are_removed(cleaner):
    out = cleaner("a<b>c`d%e=f~g@h$i^j")
    assert out["text"] == "abcdefghij"
    assert out["removed"] is True


def test_invisible_and_bidi_characters_are_removed(cleaner):
    out = cleaner("a​b‮c⁦d\u0007e")
    assert out["text"] == "abcde"


def test_typographic_characters_are_normalized(cleaner):
    out = cleaner("‘hi’ “there” – — wait… ok\tyes")
    assert out["text"] == "'hi' \"there\" - - wait... ok yes"
    assert out["removed"] is False


def test_single_line_fields_flatten_newlines_and_multiline_keep_them(cleaner):
    assert cleaner("a\nb")["text"] == "a b"
    assert cleaner("a\r\nb\rc", multiline=True)["text"] == "a\nb\nc"


def test_length_limit_counts_code_points(cleaner):
    out = cleaner("日" * 10, limit=4)
    assert out["text"] == "日" * 4 and out["truncated"] is True


def render(page, kind, text):
    return page.evaluate(
        """([kind, text]) => {
          const el = document.createElement('div');
          (kind === 'notes' ? QMG.renderNotes : QMG.renderIntro)(el, text);
          return el.innerHTML;
        }""",
        [kind, text],
    )


def test_inline_markdown(page):
    html = render(page, "notes", "a **bold** and *italic* and \\*literal\\*")
    assert html == "<p>a <strong>bold</strong> and <em>italic</em> and *literal*</p>"


def test_unmatched_markers_stay_literal(page):
    assert render(page, "notes", "2 * 3 and **open") == "<p>2 * 3 and **open</p>"


def test_headings_lists_rules_and_tables(page):
    html = render(
        page,
        "notes",
        "# One\n## Two\n### Three\n- a\n- b\n\n1. x\n2. y\n\n---\n| H1 | H2 |\n|---|---|\n| c1 | **c2** |",
    )
    assert '<h3 class="md-heading">One</h3>' in html
    assert '<h4 class="md-heading">Two</h4>' in html
    assert '<h5 class="md-heading">Three</h5>' in html
    assert "<ul><li>a</li><li>b</li></ul>" in html
    assert "<ol><li>x</li><li>y</li></ol>" in html
    assert "<hr>" in html
    assert "<th>H1</th>" in html and "<td><strong>c2</strong></td>" in html


def test_single_newline_is_a_line_break_and_extra_blank_lines_add_space(page):
    html = render(page, "notes", "line1\nline2\n\npara2\n\n\n\npara3")
    assert "<p>line1<br>line2</p>" in html
    assert html.count('class="md-spacer"') == 2  # 3 blank lines -> 2 extra
    assert "<p>para2</p>" in html and "<p>para3</p>" in html


def test_intro_only_supports_bold_and_italics(page):
    html = render(page, "intro", "# not a heading\n- not a list\n**yes** *yes*")
    assert "<h3" not in html and "<ul" not in html
    assert "<strong>yes</strong>" in html and "<em>yes</em>" in html
    assert "# not a heading" in html and "- not a list" in html


HOSTILE = [
    "<script>window.pwned=1</script>",
    '<img src=x onerror="window.pwned=1">',
    "[click](javascript:window.pwned=1)",
    "![x](http://evil.example/a.png)",
    "<iframe src=//evil.example></iframe>",
    "**<b onmouseover=window.pwned=1>x</b>**",
    "| <script> | b |\n|---|---|\n| <img onerror=window.pwned=1> | d |",
]


@pytest.mark.parametrize("payload", HOSTILE)
@pytest.mark.parametrize("kind", ["notes", "intro"])
def test_hostile_text_never_becomes_markup(page, kind, payload):
    result = page.evaluate(
        """([kind, text]) => {
          const el = document.createElement('div');
          document.body.append(el);
          (kind === 'notes' ? QMG.renderNotes : QMG.renderIntro)(el, text);
          return {
            bad: el.querySelectorAll('script, img, iframe, a, object, embed, svg, [onerror], [onmouseover]').length,
            text: el.textContent, pwned: window.pwned === undefined,
          };
        }""",
        [kind, payload],
    )
    assert result["bad"] == 0
    assert result["pwned"] is True
    assert result["text"] != ""


def test_hostile_text_through_a_link_is_stripped_and_inert(page, site):
    import reference as ref
    from conftest import open_link

    st = ref.blank()
    st["notes"] = "<script>window.pwned=1</script> **ok**"
    st["title"] = "<img src=x onerror=window.pwned=1>"
    open_link(page, site, ref.encode(st))
    assert page.evaluate("window.pwned === undefined")
    assert page.locator("#sheet-notes script, #sheet-notes img").count() == 0
    assert page.evaluate("QMG.app.state.notes") == "scriptwindow.pwned1/script **ok**"
    assert "Some unsupported characters" in page.locator("#banner").inner_text()
