"""Construction domain vocabulary for all 8 estimate sections.

Single source of truth for construction-domain keyword patterns.
The generic candidate extractor imports compiled patterns from here
instead of maintaining hardcoded inline lists.

Add new terms here when new sections or materials need to be detected.
Do NOT add project-specific values, filenames, or page numbers.
"""
from __future__ import annotations

import re

# ── Materials by section ───────────────────────────────────────────────────

_EARTHWORKS = [
    r'песок',
    r'геотекстил',      # геотекстиль, геотекстильный
    r'щебен',           # щебень, щебёнка
    r'Плантер',         # PLANTER drainage membrane brand
    r'PLANTERBAND',
]

_CONCRETE_AND_FORMWORK = [
    r'бетон',           # бетон, бетонный, железобетон
    r'арматур',         # арматура, арматурный, армирование
    r'А[0-9]{3}С?',     # rebar classes: А240, А400, А500, А500С, А600
    r'ар-я',            # abbreviation for арматурная (seen in foundation specs)
    r'опалубк',         # опалубка, опалубки, опалубочный
    r'фанер',           # фанера (formwork plywood)
]

_INSULATION_AND_WATERPROOFING = [
    r'ЭППС',            # extruded polystyrene insulation
    r'мембран',         # мембрана, PLANTER мембрана, ПВХ мембр��на
    r'гидроизол',       # гидроизоляция, гидроизоляционный
    r'мастик',          # битумная мастика
    r'праймер',         # битумный праймер
    r'пароизоляц',      # пароизоляция (vapor barrier)
    r'стеклохолст',     # fiberglass underlay (ТЕХНОНИКОЛЬ)
    r'LOGICROOF',       # PVC roofing membrane brand
    r'рубемаст',
    r'утеплит',
    r'пенопол',
]

_THERMAL_INSERTS = [
    r'термовставк',     # термовставка, термовставки
]

_MASONRY = [
    r'газобетон',       # газобетонный блок D400/D500
    r'перемычк',        # перемычка, перемычки (lintels)
    r'кладк',           # кладка, кладочный
    r'пескобетон',      # sand-concrete mortar
]

_ROOFING = [
    r'воронк',          # кровельная воронка, воронки водостока
    r'аэратор',         # кровельный аэратор
    r'разуклонк',       # разуклонка (slope fill)
    r'кровл',           # кровля, кровельный
    r'парапет',         # parapet
]

_VENTILATION = [
    r'Schiedel',
    r'Shiedel',         # common misspelling
    r'вентканал',
    r'вентиляц',        # вентиляция, вентиляционный
]

# ── Combined lists ───────────────────────────────────���─────────────────────

MATERIAL_KEYWORDS: list[str] = (
    _EARTHWORKS
    + _CONCRETE_AND_FORMWORK
    + _INSULATION_AND_WATERPROOFING
    + _THERMAL_INSERTS
    + _MASONRY
    + _ROOFING
    + _VENTILATION
)

# Broader set: materials + geometry terms + structural subjects + utility networks.
# Used to identify any engineering-relevant text worth extracting a quantity from.
SUBJECT_KEYWORDS: list[str] = MATERIAL_KEYWORDS + [
    # Geometry / measurement terms
    r'котлован', r'яма', r'выемк', r'подготовк',
    r'площадь', r'площад',
    r'длин', r'протяжен', r'трасс',
    r'объ[её]м', r'v\s*=',
    r'ширин',
    r'глубин', r'отметк',
    r'итого',
    # Structural elements
    r'фундамент',
    r'перекрыти',       # плита перекрытия
    r'балк',            # балка (beam)
    r'армиров',         # армирование
    r'спецификац',      # спецификация
    # Pipes and fittings (already in _PIPE_KW / _PIPE_FITTING_KW in extractor;
    # duplicated here so _ANY_SUBJECT_KW stays self-contained)
    r'труб', r'ПНД', r'ПВХ', r'гофр', r'трубопровод',
    r'колен', r'муфт', r'тройник',
    r'дождеприём', r'дождеприем',
    r'ревизи',
    # Engineering network labels (generic signals; full pattern in extractor)
    r'К[0-9]', r'В[0-9]', r'ЭО',
]

# ── Compiled patterns ──────────────────────────────────────────────────────

MATERIALS_RE: re.Pattern[str] = re.compile(
    '|'.join(MATERIAL_KEYWORDS),
    re.IGNORECASE | re.UNICODE,
)

SUBJECTS_RE: re.Pattern[str] = re.compile(
    '|'.join(SUBJECT_KEYWORDS),
    re.IGNORECASE | re.UNICODE,
)
