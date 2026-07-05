"""Tests for text_normalization.py.

All examples are synthetic – no project-specific values, filenames,
page numbers or real PDF data are used as test fixtures."""
import pytest
from text_normalization import normalize_text, parse_quantities


# ── normalize_text: merged number+unit ────────────────────────────────────

@pytest.mark.parametrize('raw, expected_fragment', [
    ('56,784м3',    '56,784 м3'),
    ('189,28м2',   '189,28 м2'),
    ('12,4п.м',    '12,4 п.м'),
    ('500мм',      '500 мм'),
    ('0,5м',       '0,5 м'),
    ('Ø110мм',     'Ø110 мм'),
    ('15шт',       '15 шт'),
    ('100м2',      '100 м2'),
    ('25,0м3',     '25,0 м3'),
])
def test_normalize_merged_number_unit(raw: str, expected_fragment: str) -> None:
    result = normalize_text(raw)
    assert expected_fragment in result, f'normalize_text({raw!r}) = {result!r}'


# ── normalize_text: merged building words ─────────────────────────────────

@pytest.mark.parametrize('raw, expected_fragment', [
    ('Площадькотлована',        'Площадь котлована'),
    ('Глубинакотлована',        'Глубина котлована'),
    ('ПНДтруба',                'ПНД труба'),
    ('Гофротруба',              'Гофро труба'),
    ('Труба1м',                 'Труба 1'),
    ('ЭППС100мм',               'ЭППС 100'),
    ('ПНД110мм',                'ПНД 110'),
    ('Фундаментнаяплита',       'Фундаментная плита'),
    ('Песчаноеоснование',       'Песчаное основание'),
    ('Ливневаяканализация',     'Ливневая канализация'),
    ('Дренажнаясистема',        'Дренажная система'),
])
def test_normalize_merged_words(raw: str, expected_fragment: str) -> None:
    result = normalize_text(raw)
    assert expected_fragment in result, f'normalize_text({raw!r}) = {result!r}'


# ── normalize_text: diameter symbols ──────────────────────────────────────

@pytest.mark.parametrize('raw, expected_fragment', [
    ('Ф110',       'Ø110'),
    ('d=110',      'Ø110'),
    ('Ø 110 мм',   'Ø110'),
])
def test_normalize_diameter_symbols(raw: str, expected_fragment: str) -> None:
    result = normalize_text(raw)
    assert expected_fragment in result, f'normalize_text({raw!r}) = {result!r}'


# ── normalize_text: route labels ──────────────────────────────────────────

@pytest.mark.parametrize('raw, expected', [
    ('К-1',  'К1'),
    ('К 1',  'К1'),
    ('К/1',  'К1'),
    ('В-1',  'В1'),
    ('В 1',  'В1'),
    ('К-2',  'К2'),
])
def test_normalize_route_labels(raw: str, expected: str) -> None:
    result = normalize_text(raw)
    assert expected in result, f'normalize_text({raw!r}) = {result!r}'


# ── normalize_text: multiplication separator ──────────────────────────────

@pytest.mark.parametrize('raw, expected_fragment', [
    ('300х300х300',   '300 × 300 × 300'),
    ('25х25мм',       '25 × 25'),
    ('600х400х250',   '600 × 400 × 250'),
])
def test_normalize_multiplication(raw: str, expected_fragment: str) -> None:
    result = normalize_text(raw)
    assert expected_fragment in result, f'normalize_text({raw!r}) = {result!r}'


# ── normalize_text: raw_text is never modified (immutability) ─────────────

def test_normalize_text_does_not_modify_input() -> None:
    raw = 'Площадькотлована-189,28м2'
    original = raw
    result = normalize_text(raw)
    assert raw == original, 'normalize_text must not modify the input string'
    assert result != raw, 'normalized text should differ from raw for this input'


def test_preposition_v_before_digit_not_altered() -> None:
    """Lowercase 'в' (preposition) before a digit must not become a route label."""
    result = normalize_text('Глубина в 0,9 м')
    assert 'В0' not in result, f'Preposition "в" incorrectly normalized: {result!r}'
    assert 'в' in result.lower(), f'Preposition "в" was removed: {result!r}'


def test_preposition_k_before_digit_not_altered() -> None:
    """Lowercase 'к' (preposition) before a digit must not become a route label."""
    result = normalize_text('Ширина к 1,5 м')
    assert 'К1' not in result, f'Preposition "к" incorrectly normalized: {result!r}'


# ── parse_quantities: area units → normalized_unit = "m2" ─────────────────

@pytest.mark.parametrize('text', [
    '100 м2',
    '100 м²',
    '100 м^2',
    '100 м кв',
    '100 м.кв.',
    '100 кв.м',
    '100 кв. м',
])
def test_parse_quantities_area(text: str) -> None:
    quantities = parse_quantities(text)
    areas = [q for q in quantities if q.get('normalized_unit') == 'm2']
    assert areas, f'Expected m2 in parse_quantities({text!r}), got {quantities}'


# ── parse_quantities: volume units → normalized_unit = "m3" ──────────────

@pytest.mark.parametrize('text', [
    '50 м3',
    '50 м³',
    '50 м^3',
    '50 м куб',
    '50 м.куб.',
    '50 куб.м',
    '50 куб. м',
])
def test_parse_quantities_volume(text: str) -> None:
    quantities = parse_quantities(text)
    vols = [q for q in quantities if q.get('normalized_unit') == 'm3']
    assert vols, f'Expected m3 in parse_quantities({text!r}), got {quantities}'


# ── parse_quantities: linear metre units → normalized_unit = "linear_m" ──

@pytest.mark.parametrize('text', [
    '12,4 п.м',
    '12,4 п. м.',
    '12,4 пог.м',
    '12,4 м.п.',
    '12,4 м/п',
])
def test_parse_quantities_linear_m(text: str) -> None:
    quantities = parse_quantities(text)
    lins = [q for q in quantities if q.get('normalized_unit') == 'linear_m']
    assert lins, f'Expected linear_m in parse_quantities({text!r}), got {quantities}'


# ── parse_quantities: canonical length conversion ─────────────────────────

@pytest.mark.parametrize('text, expected_canon', [
    ('500 мм',  0.5),
    ('50 см',   0.5),
    ('0,5 м',   0.5),
    ('0.5 м',   0.5),
])
def test_parse_quantities_canonical_length(text: str, expected_canon: float) -> None:
    quantities = parse_quantities(text)
    lengths = [q for q in quantities if q.get('kind') == 'length']
    assert lengths, f'No length in parse_quantities({text!r}): {quantities}'
    assert any(
        abs((q.get('canonical_value') or 0) - expected_canon) < 1e-6
        for q in lengths
    ), f'Expected canonical_value={expected_canon} in {lengths}'


# ── parse_quantities: diameter ─────────────────────────────────────────────

@pytest.mark.parametrize('text', [
    'Ø110 мм',
    'Ø110',
])
def test_parse_quantities_diameter(text: str) -> None:
    quantities = parse_quantities(normalize_text(text))
    diams = [q for q in quantities if q.get('kind') == 'diameter']
    assert diams, f'Expected diameter in parse_quantities({text!r}), got {quantities}'
    assert any(
        abs((q.get('canonical_value') or 0) - 0.11) < 1e-6
        for q in diams
    ), f'Expected canonical_value=0.11 for Ø110, got {diams}'


# ── parse_quantities: negative elevation ──────────────────────────────────

def test_parse_quantities_negative_elevation() -> None:
    quantities = parse_quantities('-0,800')
    elevs = [q for q in quantities if q.get('kind') == 'elevation']
    assert elevs, f'Expected elevation, got {quantities}'
    assert any(q.get('sign') == 'negative' for q in elevs)
    assert any(q.get('value_decimal', 0) < 0 for q in elevs)


# ── parse_quantities: positive elevation ──────────────────────────────────

def test_parse_quantities_positive_elevation() -> None:
    quantities = parse_quantities('+3,750')
    elevs = [q for q in quantities if q.get('kind') == 'elevation']
    assert elevs, f'Expected elevation, got {quantities}'
    assert any(q.get('sign') == 'positive' for q in elevs)


# ── parse_quantities: pieces ───────────────────────────────────────────────

@pytest.mark.parametrize('text', [
    '5 шт',
    '5 шт.',
    '5 ед.',
    '5 компл.',
])
def test_parse_quantities_pieces(text: str) -> None:
    quantities = parse_quantities(text)
    pcs = [q for q in quantities if q.get('normalized_unit') == 'pcs']
    assert pcs, f'Expected pcs in parse_quantities({text!r}), got {quantities}'


# ── parse_quantities: dimensions ──────────────────────────────────────────

def test_parse_quantities_dimensions() -> None:
    # normalize_text first produces × separator from х
    normalized = normalize_text('300х300х300')
    quantities = parse_quantities(normalized)
    dims = [q for q in quantities if q.get('kind') == 'dimensions']
    assert dims, f'Expected dimensions, got {quantities}'


# ── A0.1: diameter normalization fixes ────────────────────────────────────

def test_f150_not_diameter() -> None:
    """F150 (frost resistance grade) must NOT be normalized to Ø150."""
    norm = normalize_text('Бетон В22,5 W6 F150 П4 42,56 м3')
    assert 'Ø150' not in norm, f'F150 wrongly normalized to Ø150 in: {norm!r}'
    # Volume must still be parseable
    qtys = parse_quantities(norm)
    vols = [q for q in qtys if q.get('normalized_unit') == 'm3']
    assert vols, f'Volume m3 not found after normalize_text: {norm!r}'
    assert any(abs(q['value_decimal'] - 42.56) < 0.001 for q in vols)


def test_d400_not_diameter() -> None:
    """D400 (gas-concrete density grade) must NOT be normalized to Ø400."""
    norm = normalize_text('Газобетонный блок D400 600х400х250 54,11 м3')
    assert 'Ø400' not in norm, f'D400 wrongly normalized to Ø400 in: {norm!r}'
    assert 'D400' in norm, f'D400 text lost in: {norm!r}'
    qtys = parse_quantities(norm)
    vols = [q for q in qtys if q.get('normalized_unit') == 'm3']
    assert vols, f'Volume m3 not found after normalize_text: {norm!r}'
    assert any(abs(q['value_decimal'] - 54.11) < 0.001 for q in vols)


def test_d500_not_diameter() -> None:
    """D500 (gas-concrete density grade) must NOT be normalized to Ø500."""
    norm = normalize_text('Газобетонный блок D500 600х250х250 30,4 м3')
    assert 'Ø500' not in norm, f'D500 wrongly normalized to Ø500 in: {norm!r}'
    assert 'D500' in norm, f'D500 text lost in: {norm!r}'


def test_d_equals_diameter_still_works() -> None:
    """D=110 notation (pipe diameter with equals sign) must still normalize to Ø110."""
    norm = normalize_text('Труба D=110 длина 12,4 п.м')
    assert 'Ø110' in norm, f'D=110 not normalized to Ø110 in: {norm!r}'
    qtys = parse_quantities(norm)
    linear = [q for q in qtys if q.get('normalized_unit') == 'linear_m']
    assert linear, f'Linear length not found: {norm!r}'
    assert any(abs(q['value_decimal'] - 12.4) < 0.001 for q in linear)


def test_cyrillic_f_diameter_still_works() -> None:
    """Ф110 (Cyrillic Ф) must still normalize to Ø110."""
    norm = normalize_text('Труба ф110 12,4 п.м')
    assert 'Ø110' in norm, f'ф110 not normalized to Ø110 in: {norm!r}'


def test_rebar_cyrillic_f_diameter() -> None:
    """Арматура Ф12 А500С — Cyrillic Ф used as rebar diameter, must parse diameter."""
    norm = normalize_text('Арматура Ф12 А500С 94,28 кг')
    assert 'Ø12' in norm, f'Ф12 not normalized to Ø12 in: {norm!r}'
    qtys = parse_quantities(norm)
    kg = [q for q in qtys if q.get('normalized_unit') == 'kg']
    assert kg, f'kg not found: {norm!r}'
    assert any(abs(q['value_decimal'] - 94.28) < 0.001 for q in kg)


def test_ohm_diameter_still_works() -> None:
    """Ø110 (already normalized symbol) must pass through correctly."""
    norm = normalize_text('Труба Ø110 12,4 п.м')
    assert 'Ø110' in norm, f'Ø110 lost in: {norm!r}'
