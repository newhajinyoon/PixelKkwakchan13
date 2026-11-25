import os
import sys
from PIL import Image
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

N = 13
FINAL_W = lambda T: N
FINAL_TRIM_V = {'ㅏ', 'ㅑ', 'ㅘ'}  # 오른쪽 획이 튀어나오는 모음은 받침 끝 1px 비움

OVR = {}
REQ = set()
LATIN_OVR = {}
SYM_OVR = {}

CHO = list('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
JUNG = list('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
JONG = [''] + list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

TENSE = {'ㄲ': 'ㄱ', 'ㄸ': 'ㄷ', 'ㅃ': 'ㅂ', 'ㅆ': 'ㅅ', 'ㅉ': 'ㅈ'}
COMPOUND = {
    'ㄳ': ('ㄱ', 'ㅅ'), 'ㄵ': ('ㄴ', 'ㅈ'), 'ㄶ': ('ㄴ', 'ㅎ'), 'ㄺ': ('ㄹ', 'ㄱ'),
    'ㄻ': ('ㄹ', 'ㅁ'), 'ㄼ': ('ㄹ', 'ㅂ'), 'ㄽ': ('ㄹ', 'ㅅ'), 'ㄾ': ('ㄹ', 'ㅌ'),
    'ㄿ': ('ㄹ', 'ㅍ'), 'ㅀ': ('ㄹ', 'ㅎ'), 'ㅄ': ('ㅂ', 'ㅅ'),
}
VW = {
    'ㅣ': 1, 'ㅏ': 3, 'ㅑ': 3, 'ㅓ': 3, 'ㅕ': 3, 'ㅐ': 4, 'ㅒ': 4, 'ㅔ': 4, 'ㅖ': 4,
    'ㅓ_ㅝ': 3, 'ㅔ_ㅞ': 4,
}
MIX = {
    'ㅘ': ('ㅗ', 'ㅏ'), 'ㅙ': ('ㅗ', 'ㅐ'), 'ㅚ': ('ㅗ', 'ㅣ'),
    'ㅝ': ('ㅜ', 'ㅓ_ㅝ'), 'ㅞ': ('ㅜ', 'ㅔ_ㅞ'), 'ㅟ': ('ㅜ', 'ㅣ'),
    'ㅢ': ('ㅡ', 'ㅣ'),
}
HORIZ = 'ㅗㅛㅜㅠㅡ'


def shift(S, dx, dy):
    return {(x + dx, y + dy) for x, y in S}


# ---------- PNG 자모 조합 ----------
def cons(c, w, h):
    if c in TENSE or c in COMPOUND:
        o = OVR.get(('c', c, w, h))
        if o is not None:
            return set(o)
        a, b = (TENSE[c], TENSE[c]) if c in TENSE else COMPOUND[c]
        wl = (w - 1) // 2
        return cons(a, wl, h) | shift(cons(b, w - 1 - wl, h), wl + 1, 0)
    key = ('c', c, w, h)
    REQ.add(key)
    return set(OVR.get(key, ()))


def vpart(v, h):
    key = ('v', v, VW[v], h)
    REQ.add(key)
    return set(OVR.get(key, ()))


def hpart(v, w, hv):
    key = ('h', v, w, hv)
    REQ.add(key)
    return set(OVR.get(key, ()))


def _l_dims(V_, hasF):
    if V_ in MIX or V_ in HORIZ:
        hp = MIX[V_][0] if V_ in MIX else V_
        wl = N - VW[MIX[V_][1]] - 1 if V_ in MIX else N
        hi = (5 if hp == 'ㅡ' else 4) if hasF else (11 if hp == 'ㅡ' else 9)
    else:
        wl = N - VW[V_] - 1
        hi = 7 if hasF else N
    return wl, hi


def _v_parts(V_, hasF):
    if V_ in MIX or V_ in HORIZ:
        hp = MIX[V_][0] if V_ in MIX else V_
        wl = N - VW[MIX[V_][1]] - 1 if V_ in MIX else N
        if not hasF:
            yv, hv = (12, 1) if hp == 'ㅡ' else (10, 3)
        else:
            yv, hv = (6, 1) if hp == 'ㅡ' else (5, 2)
        res = [shift(hpart(hp, wl, hv), 0, yv)]
        if V_ in MIX:
            vp = MIX[V_][1]
            res.insert(0, shift(vpart(vp, 7 if hasF else N), N - VW[vp], 0))
        return res
    return [shift(vpart(V_, 7 if hasF else N), N - VW[V_], 0)]


def _t_part(T, trim):
    fw = min(FINAL_W(T), N - 2) if trim else FINAL_W(T)
    return shift(cons(T, fw, 5), 0 if trim else (N - fw) // 2, 8)


def parts(L, V_, T):
    hasF = bool(T)
    comps = _v_parts(V_, hasF)
    if L:
        wl, hi = _l_dims(V_, hasF)
        comps.append(cons(L, wl, hi))
    if hasF:
        comps.append(_t_part(T, V_ in FINAL_TRIM_V))
    return comps


def syllable(L, V_, T):
    S = set()
    for c in parts(L, V_, T):
        S |= c
    return S


def standalone_cons(c):
    return cons(c, N, N)


def standalone_vowel(v):
    return syllable('', v, '')


# ---------- 윤곽선 / TTF 빌드 ----------
PX = 100
ADV = (N + 1) * PX        # 전각 폭 1400
ASC, DESC = N * PX, 100   # 잉크 13px + 하단 여백 1px

_ROW_MASK = (1 << N) - 1
_V_SHIFT = (N + 1).bit_length()
_V_MASK = (1 << _V_SHIFT) - 1
_V_SIZE = (N + 1) << _V_SHIFT


def _to_mask(S):
    m = 0
    for x, y in S:
        m |= 1 << (y * N + x)
    return m


def _mask_contours(mask):
    if not mask:
        return []
    nxt1 = [-1] * _V_SIZE
    nxt2 = [-1] * _V_SIZE
    starts = []

    def add_edge(u, v):
        if nxt1[u] < 0:
            nxt1[u] = v
            starts.append(u)
        else:
            nxt2[u] = v

    for y in range(N):
        r = (mask >> (y * N)) & _ROW_MASK
        if not r:
            continue
        Y = N - 1 - y
        up = (mask >> ((y - 1) * N)) & _ROW_MASK if y > 0 else 0
        dn = (mask >> ((y + 1) * N)) & _ROW_MASK if y + 1 < N else 0

        b = r & ~(r << 1)
        while b:
            lsb = b & -b
            x = lsb.bit_length() - 1
            b ^= lsb
            u = (x << _V_SHIFT) | Y
            add_edge(u, u + 1)

        b = r & ~up
        while b:
            lsb = b & -b
            x = lsb.bit_length() - 1
            b ^= lsb
            u = (x << _V_SHIFT) | (Y + 1)
            add_edge(u, u + (1 << _V_SHIFT))

        b = r & ~(r >> 1)
        while b:
            lsb = b & -b
            x = lsb.bit_length() - 1
            b ^= lsb
            u = ((x + 1) << _V_SHIFT) | (Y + 1)
            add_edge(u, u - 1)

        b = r & ~dn
        while b:
            lsb = b & -b
            x = lsb.bit_length() - 1
            b ^= lsb
            u = ((x + 1) << _V_SHIFT) | Y
            add_edge(u, u - (1 << _V_SHIFT))

    loops = []
    for s in starts:
        # degree-1 꼭짓점에서만 시작하면 대각 교차점의 진행 방향이 항상 확정됨
        if nxt1[s] < 0 or nxt2[s] >= 0:
            continue
        a = s
        path = [a]
        prev = -1
        while True:
            if nxt2[a] < 0:
                b = nxt1[a]
                nxt1[a] = -1
            else:
                b0, b1 = nxt1[a], nxt2[a]
                ax, ay = a >> _V_SHIFT, a & _V_MASK
                dx, dy = ax - (prev >> _V_SHIFT), ay - (prev & _V_MASK)
                t0 = -(dx * ((b0 & _V_MASK) - ay) - dy * ((b0 >> _V_SHIFT) - ax))
                t1 = -(dx * ((b1 & _V_MASK) - ay) - dy * ((b1 >> _V_SHIFT) - ax))
                if t0 >= t1:
                    b = b0
                    nxt1[a] = b1
                else:
                    b = b1
                nxt2[a] = -1
            prev, a = a, b
            if a == s:
                break
            path.append(a)
        m = len(path)
        loops.append([
            (path[i] >> _V_SHIFT, path[i] & _V_MASK) for i in range(m)
            if (path[i - 1] >> _V_SHIFT) != (path[(i + 1) % m] >> _V_SHIFT)
            and (path[i - 1] & _V_MASK) != (path[(i + 1) % m] & _V_MASK)
        ])
    return loops


def contours(S):
    return _mask_contours(_to_mask(S)) if S else []


def _glyph_from_loops(loops, ox=0):
    pen = TTGlyphPen(None)
    for lp in loops:
        pen.moveTo((lp[0][0] * PX + ox, lp[0][1] * PX))
        for x, y in lp[1:]:
            pen.lineTo((x * PX + ox, y * PX))
        pen.closePath()
    return pen.glyph()


def make_glyph(S, ox=0):
    return _glyph_from_loops(contours(S), ox)


def _make_glyph_mask(mask, ox=0):
    return _glyph_from_loops(_mask_contours(mask), ox)


# 세로쓰기 치환표 (가로 문장부호 -> 세로 문장부호)
VERT_MAP = {
    0x3001: 0xFE11, 0x3002: 0xFE12, 0x2026: 0xFE19, 0x2025: 0xFE30,
    0x2014: 0xFE31, 0x2015: 0xFE31, 0x2013: 0xFE32, 0x301C: 0xFE34,
    0xFF5E: 0xFE34, 0xFF08: 0xFE35, 0xFF09: 0xFE36, 0xFF5B: 0xFE37,
    0xFF5D: 0xFE38, 0x3010: 0xFE3B, 0x3011: 0xFE3C, 0x300A: 0xFE3D,
    0x300B: 0xFE3E, 0x3008: 0xFE3F, 0x3009: 0xFE40, 0x300C: 0xFE41,
    0x300D: 0xFE42, 0x300E: 0xFE43, 0x300F: 0xFE44, 0xFF3B: 0xFE47,
    0xFF3D: 0xFE48,
}


def _build_opentype_features(l_groups, l_variants, v_trim_names, v_other_names, zero_comb):
    l_orig = [f'uni{0x1100 + i:04X}' for i in range(19)]
    v_orig = [f'uni{0x1161 + i:04X}' for i in range(21)]
    t_orig = [f'uni{0x11A8 + i:04X}' for i in range(27)]

    lines = [
        'languagesystem DFLT dflt;',
        'languagesystem hang dflt;',
        'languagesystem hang KOR;',
        'languagesystem hani dflt;',
        'languagesystem kana dflt;',
        f'@L_orig = [{" ".join(l_orig)}];',
        f'@V_orig = [{" ".join(v_orig)}];',
        f'@T_orig = [{" ".join(t_orig)}];',
        f'@L_ALL = [uni115F {" ".join(l_orig)} {" ".join(l_variants)}];',
        f'@V_TRIM_ALL = [{" ".join(v_trim_names)}];',
        f'@V_OTHER_ALL = [{" ".join(v_other_names)}];',
        f'@ZERO_COMB = [{" ".join(zero_comb)}];',
    ]

    for wl, hi in sorted({dims for _, dims in l_groups}):
        tag = f'w{wl}h{hi}'
        lines.append(f'lookup LJMO_{tag} {{')
        for g in l_orig:
            lines.append(f'  sub {g} by {g}.{tag};')
        lines.append(f'}} LJMO_{tag};')

    for suffix, name in (('v1', 'VJMO_v1'), ('v0', 'VJMO_v0')):
        lines.append(f'lookup {name} {{')
        for g in v_orig:
            lines.append(f'  sub {g} by {g}.{suffix};')
        lines.append(f'}} {name};')

    lines.append('lookup VJMO_filler {\n  sub uni1160 by uni1160.vjmo;\n} VJMO_filler;')

    for suffix, name in (('t1', 'TJMO_t1'), ('t0', 'TJMO_t0')):
        lines.append(f'lookup {name} {{')
        for g in t_orig:
            lines.append(f'  sub {g} by {g}.{suffix};')
        lines.append(f'}} {name};')

    lines.append('feature ljmo {')
    lines.append('  lookup LJMO_T {')
    for (hasF, (wl, hi)), v_names in sorted(l_groups.items()):
        if hasF:
            lines.append(f'    sub @L_orig\' lookup LJMO_w{wl}h{hi} [{" ".join(v_names)}] @T_orig;')
    lines.append('  } LJMO_T;')
    lines.append('  lookup LJMO_NO_T {')
    for (hasF, (wl, hi)), v_names in sorted(l_groups.items()):
        if not hasF:
            lines.append(f'    sub @L_orig\' lookup LJMO_w{wl}h{hi} [{" ".join(v_names)}];')
    lines.append('  } LJMO_NO_T;')
    lines.append('} ljmo;')

    lines.append(
        'feature vjmo {\n'
        '  lookup VJMO_T {\n'
        '    sub @L_ALL @V_orig\' lookup VJMO_v1 @T_orig;\n'
        '    sub @L_ALL uni1160\' lookup VJMO_filler @T_orig;\n'
        '  } VJMO_T;\n'
        '  lookup VJMO_NO_T {\n'
        '    sub @L_ALL @V_orig\' lookup VJMO_v0;\n'
        '    sub @L_ALL uni1160\' lookup VJMO_filler;\n'
        '  } VJMO_NO_T;\n'
        '} vjmo;'
    )

    lines.append(
        'feature tjmo {\n'
        '  lookup TJMO_ALL {\n'
        '    sub @L_ALL @V_TRIM_ALL @T_orig\' lookup TJMO_t1;\n'
        '    sub @L_ALL @V_OTHER_ALL @T_orig\' lookup TJMO_t0;\n'
        '  } TJMO_ALL;\n'
        '} tjmo;'
    )

    lines.append('feature vert {')
    for h_cp, v_cp in VERT_MAP.items():
        lines.append(f'  sub uni{h_cp:04X} by uni{v_cp:04X};')
    lines.append('} vert;')

    # 세로쓰기 시 폭 0 결합 자모가 초성 중심축에 정렬되도록 X 보정
    lines.append(f'feature vert {{\n  pos @ZERO_COMB <{ADV // 2} 0 0 0>;\n}} vert;')
    return '\n'.join(lines)


def build(path, family='PixelKkwakchan13', style='Regular'):
    glyphs = {}
    adv_map = {}
    cmap = {}

    def add_glyph(name, g, adv, cp=None):
        glyphs[name] = g
        adv_map[name] = adv
        if cp is not None:
            cmap[cp] = name

    def reg(cp, S, adv, ox=0):
        add_glyph(f'uni{cp:04X}', make_glyph(S, ox), adv, cp)

    notdef = {(x, y) for x in (1, 11) for y in range(1, 12)} | {(x, y) for y in (1, 11) for x in range(1, 12)}
    add_glyph('.notdef', make_glyph(notdef), ADV)
    add_glyph('space', TTGlyphPen(None).glyph(), ADV // 2, 0x20)
    add_glyph('uni3000', TTGlyphPen(None).glyph(), ADV, 0x3000)

    for cp in list(range(0x21, 0x7F)) + list(HALF_EXTRA_NAME):
        reg(cp, LATIN_OVR.get(cp, set()), ADV // 2)

    # 자모 부품을 비트마스크로 캐시 (완성형 11,172자 + 첫가끝 공유)
    l_masks = {}
    for hasF in (False, True):
        for V_ in JUNG:
            wl, hi = _l_dims(V_, hasF)
            if (wl, hi) not in l_masks:
                l_masks[(wl, hi)] = [_to_mask(cons(L, wl, hi)) for L in CHO]
        dims_f = (N, 7 if hasF else N)
        if dims_f not in l_masks:
            l_masks[dims_f] = [_to_mask(cons(L, *dims_f)) for L in CHO]

    v_masks = {
        (vi, hasF): _to_mask({pt for c in _v_parts(V_, hasF) for pt in c})
        for hasF in (False, True)
        for vi, V_ in enumerate(JUNG)
    }

    t_masks = {
        (ti, trim): _to_mask(_t_part(T, trim))
        for trim in (False, True)
        for ti, T in enumerate(JONG) if ti > 0
    }
    t_masks.update({(0, False): 0, (0, True): 0})

    v_is_trim = [V_ in FINAL_TRIM_V for V_ in JUNG]
    v_ldims = {hasF: [_l_dims(V_, hasF) for V_ in JUNG] for hasF in (False, True)}

    for i in range(11172):
        li = i // 588
        vi = (i % 588) // 28
        ti = i % 28
        hasF = ti > 0
        mask = l_masks[v_ldims[hasF][vi]][li] | v_masks[(vi, hasF)] | t_masks[(ti, v_is_trim[vi])]
        add_glyph(f'uni{0xAC00 + i:04X}', _make_glyph_mask(mask), ADV, 0xAC00 + i)

    for cp in range(0x3131, 0x3164):
        ch = chr(cp)
        if ch in CHO or ch in JONG[1:] or ch in COMPOUND:
            S = standalone_cons(ch)
        elif ch in JUNG:
            S = standalone_vowel(ch)
        else:
            continue
        reg(cp, S, ADV)

    for cp in list(SYM_NAME) + FULLWIDTH_LATIN_CPS + FULLWIDTH_SYM_CPS:
        reg(cp, SYM_OVR.get(cp, set()), ADV)

    # 첫가끝 기본 자모 (U+1100..U+11C2) 및 채움자
    for i, ch in enumerate(CHO):
        reg(0x1100 + i, standalone_cons(ch), ADV)
    add_glyph('uni115F', TTGlyphPen(None).glyph(), ADV, 0x115F)
    add_glyph('uni1160', TTGlyphPen(None).glyph(), ADV, 0x1160)
    for i, ch in enumerate(JUNG):
        reg(0x1161 + i, standalone_vowel(ch), ADV)
    for i, ch in enumerate(JONG[1:]):
        reg(0x11A8 + i, shift(cons(ch, N, 5), 0, 8), ADV)

    # 첫가끝 문맥 변형 글리프 (ljmo / vjmo / tjmo)
    l_groups = {}
    for hasF in (False, True):
        for vi, V_ in enumerate(JUNG):
            l_groups.setdefault((hasF, _l_dims(V_, hasF)), []).append(f'uni{0x1161 + vi:04X}')
        l_groups.setdefault((hasF, (N, 7 if hasF else N)), []).append('uni1160')

    l_variants = []
    for wl, hi in sorted({dims for _, dims in l_groups}):
        tag = f'w{wl}h{hi}'
        for i, m in enumerate(l_masks[(wl, hi)]):
            gname = f'uni{0x1100 + i:04X}.{tag}'
            add_glyph(gname, _make_glyph_mask(m), ADV)
            l_variants.append(gname)

    zero_comb = []
    v_trim_names = []
    v_other_names = ['uni1160', 'uni1160.vjmo']
    add_glyph('uni1160.vjmo', TTGlyphPen(None).glyph(), 0)
    for vi in range(len(JUNG)):
        base = f'uni{0x1161 + vi:04X}'
        names = [base]
        for hasF, suffix in ((False, 'v0'), (True, 'v1')):
            gname = f'{base}.{suffix}'
            add_glyph(gname, _make_glyph_mask(v_masks[(vi, hasF)], ox=-ADV), 0)
            zero_comb.append(gname)
            names.append(gname)
        (v_trim_names if v_is_trim[vi] else v_other_names).extend(names)

    for ti in range(1, len(JONG)):
        base = f'uni{0x11A8 + ti - 1:04X}'
        for trim, suffix in ((False, 't0'), (True, 't1')):
            gname = f'{base}.{suffix}'
            add_glyph(gname, _make_glyph_mask(t_masks[(ti, trim)], ox=-ADV), 0)
            zero_comb.append(gname)

    order = ['.notdef', 'space'] + [n for n in glyphs if n not in ('.notdef', 'space')]
    fb = FontBuilder(ADV, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf({n: glyphs[n] for n in order})

    glyf = fb.font['glyf']
    zero_comb_set = set(zero_comb)
    hm, vm = {}, {}
    for n in order:
        g = glyf[n]
        g.recalcBounds(glyf)
        adv = adv_map[n]
        hm[n] = (adv, g.xMin if g.numberOfContours else 0)
        if g.numberOfContours:
            tsb = (ASC - g.yMax - ADV) if n in zero_comb_set else (ASC - g.yMax)
        else:
            tsb = 0
        vm[n] = (ADV if adv else 0, tsb)

    fb.setupHorizontalMetrics(hm)
    fb.setupVerticalMetrics(vm)
    fb.setupHorizontalHeader(ascent=ASC, descent=-DESC)
    fb.setupVerticalHeader(ascent=ADV // 2, descent=-(ADV // 2), caretSlopeRun=1)
    fb.setupNameTable({
        'familyName': '픽셀꽉찬체13',
        'styleName': style,
        'uniqueFontIdentifier': f'{family}-{style}',
        'fullName': f'픽셀꽉찬체13 {style}',
        'psName': f'{family}-{style}',
        'version': 'Version 1.000',
        'copyright': 'Copyright 2026 Hajin Yoon (SIL OFL 1.1)',
        'licenseDescription': 'SIL Open Font License 1.1',
    }, mac=False)
    fb.setupOS2(
        sTypoAscender=ASC, sTypoDescender=-DESC, sTypoLineGap=0,
        usWinAscent=ASC, usWinDescent=DESC, sxHeight=600, sCapHeight=900,
        fsType=0, achVendID='JMPX', xAvgCharWidth=ADV, fsSelection=0x40, version=4,
    )
    fb.setupPost(isFixedPitch=0, underlinePosition=-100, underlineThickness=PX)

    fea = _build_opentype_features(l_groups, l_variants, v_trim_names, v_other_names, zero_comb)
    addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(path)
    return len(glyphs)


# ---------- PNG 로드 ----------
HERE = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join(HERE, 'jamo_png')
OUT_TTF = os.path.join(HERE, 'PixelKkwakchan13.ttf')
KIND_DIR = {'c': '자음', 'v': '모음_세로', 'h': '모음_가로'}


def png_path(kind, c, w, h):
    d = os.path.join(PNG_DIR, KIND_DIR[kind])
    if kind == 'c':
        d = os.path.join(d, c)
    return os.path.join(d, f'{c}_{w}x{h}.png')


PUNCT_NAME = {
    '!': '느낌표', '"': '큰따옴표', '#': '샵', '$': '달러', '%': '퍼센트', '&': '앤드',
    "'": '작은따옴표', '(': '여는소괄호', ')': '닫는소괄호', '*': '별표', '+': '더하기',
    ',': '쉼표', '-': '하이픈', '.': '마침표', '/': '슬래시', ':': '콜론', ';': '세미콜론',
    '<': '작다', '=': '등호', '>': '크다', '?': '물음표', '@': '골뱅이', '[': '여는대괄호',
    '\\': '역슬래시', ']': '닫는대괄호', '^': '캐럿', '_': '밑줄', '`': '백틱',
    '{': '여는중괄호', '|': '세로선', '}': '닫는중괄호', '~': '물결',
}
SYM_NAME = {
    0x00B7: '가운뎃점', 0x2025: '두점줄임표', 0x2026: '말줄임표',
    0x2018: '왼쪽작은따옴표', 0x2019: '오른쪽작은따옴표',
    0x201C: '왼쪽큰따옴표', 0x201D: '오른쪽큰따옴표',
    0x3001: '모점', 0x3002: '고리점',
    0x3008: '왼쪽홑화살괄호', 0x3009: '오른쪽홑화살괄호',
    0x300A: '왼쪽겹화살괄호', 0x300B: '오른쪽겹화살괄호',
    0x300C: '왼쪽낫표', 0x300D: '오른쪽낫표',
    0x300E: '왼쪽겹낫표', 0x300F: '오른쪽겹낫표',
    0x3010: '왼쪽검정대괄호', 0x3011: '오른쪽검정대괄호', 0x301C: '파도줄표',
    0x2014: '줄표', 0x2015: '수평선',
    0x25CB: '빈동그라미', 0x25CF: '채운동그라미', 0x25CE: '이중동그라미',
    0x25A1: '빈네모', 0x25A0: '채운네모',
    0x25B3: '빈위삼각형', 0x25B2: '채운위삼각형',
    0x25BD: '빈아래삼각형', 0x25BC: '채운아래삼각형',
    0x25C7: '빈마름모', 0x25C6: '채운마름모',
    0x2192: '오른쪽화살표', 0x2190: '왼쪽화살표', 0x2191: '위쪽화살표', 0x2193: '아래쪽화살표',
    0x2194: '좌우화살표', 0x2605: '채운별', 0x2606: '빈별', 0x2661: '빈하트', 0x2665: '채운하트',
    0x00B1: '더하기빼기', 0x00D7: '곱하기', 0x00F7: '나누기', 0x00B0: '도',
    0x203B: '참고표', 0x20A9: '원화', 0x00A5: '엔화', 0xFFE6: '전각원화',
    0x2260: '같지않음', 0x2264: '작거나같음', 0x2265: '크거나같음',
    0xFE11: '세로모점', 0xFE12: '세로고리점', 0xFE19: '세로말줄임표',
    0xFE30: '세로두점줄임표', 0xFE31: '세로줄표', 0xFE32: '세로붙임표', 0xFE34: '세로물결',
    0xFE35: '세로여는소괄호', 0xFE36: '세로닫는소괄호',
    0xFE37: '세로여는중괄호', 0xFE38: '세로닫는중괄호',
    0xFE3B: '세로여는검정대괄호', 0xFE3C: '세로닫는검정대괄호',
    0xFE3D: '세로여는겹화살괄호', 0xFE3E: '세로닫는겹화살괄호',
    0xFE3F: '세로여는홑화살괄호', 0xFE40: '세로닫는홑화살괄호',
    0xFE41: '세로왼쪽낫표', 0xFE42: '세로오른쪽낫표',
    0xFE43: '세로왼쪽겹낫표', 0xFE44: '세로오른쪽겹낫표',
    0xFE47: '세로여는대괄호', 0xFE48: '세로닫는대괄호',
}
HALF_EXTRA_NAME = {0x2013: '붙임표', 0xFF62: '반각왼쪽낫표', 0xFF63: '반각오른쪽낫표'}
FULLWIDTH_LATIN_CPS = list(range(0xFF21, 0xFF3B)) + list(range(0xFF41, 0xFF5B))
FULLWIDTH_SYM_CPS = [cp for cp in range(0xFF01, 0xFF5F) if cp not in FULLWIDTH_LATIN_CPS]
LATIN_W, LATIN_H, SYM_W, SYM_H = 7, 13, 13, 13
EXTRA_CPS = list(range(0x21, 0x7F)) + list(HALF_EXTRA_NAME) + list(SYM_NAME) + FULLWIDTH_LATIN_CPS + FULLWIDTH_SYM_CPS


def extra_path(cp):
    ch = chr(cp)
    if cp >= 0x80:
        if cp in HALF_EXTRA_NAME:
            d, f, w, h = '기호_반각', HALF_EXTRA_NAME[cp], LATIN_W, LATIN_H
        elif 0xFF21 <= cp <= 0xFF3A:
            d, f, w, h = '전각_영문_대문자', f'전각_대문자_{chr(cp - 0xFF21 + 65)}', SYM_W, SYM_H
        elif 0xFF41 <= cp <= 0xFF5A:
            d, f, w, h = '전각_영문_소문자', f'전각_소문자_{chr(cp - 0xFF41 + 97)}', SYM_W, SYM_H
        elif 0xFF10 <= cp <= 0xFF19:
            d, f, w, h = '전각_숫자', f'전각_숫자_{chr(cp - 0xFF10 + 48)}', SYM_W, SYM_H
        elif cp in FULLWIDTH_SYM_CPS:
            d, f, w, h = '기호_전각', f'전각_{PUNCT_NAME[chr(cp - 0xFEE0)]}', SYM_W, SYM_H
        else:
            d, f, w, h = '기호_전각', SYM_NAME[cp], SYM_W, SYM_H
    elif ch.isdigit():
        d, f, w, h = '숫자', f'숫자_{ch}', LATIN_W, LATIN_H
    elif ch.isupper():
        d, f, w, h = '영문_대문자', f'대문자_{ch}', LATIN_W, LATIN_H
    elif ch.islower():
        d, f, w, h = '영문_소문자', f'소문자_{ch}', LATIN_W, LATIN_H
    else:
        d, f, w, h = '기호_반각', PUNCT_NAME[ch], LATIN_W, LATIN_H
    return os.path.join(PNG_DIR, d, f'{f}.png'), w, h


def load_png(path, w, h):
    with Image.open(path) as im:
        if im.size != (w, h):
            print(f'  ! 크기 불일치, 무시: {os.path.basename(path)} ({w}x{h} 이어야 함, 현재 {im.size[0]}x{im.size[1]})')
            return None
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            rgba = im.convert('RGBA')
            bg = Image.new('RGBA', (w, h), (255, 255, 255, 255))
            bg.alpha_composite(rgba)
            gray = bg.convert('L')
        else:
            gray = im.convert('L')
        buf = gray.tobytes()
    return {(i % w, i // w) for i, v in enumerate(buf) if v < 128}


def collect_requests():
    OVR.clear()
    REQ.clear()
    for V_ in JUNG:
        for T in ('', 'ㄱ'):
            for L in CHO:
                parts(L, V_, T)
        for T in JONG[1:]:
            parts('ㄱ', V_, T)
    for c in CHO + JONG[1:]:
        standalone_cons(c)
    for v in JUNG:
        standalone_vowel(v)
    return sorted(REQ)


def load_overrides(reqs=None):
    if reqs is None:
        reqs = collect_requests()
    OVR.clear()
    n = 0
    for kind, c, w, h in reqs:
        p = png_path(kind, c, w, h)
        if os.path.exists(p):
            S = load_png(p, w, h)
            if S is not None:
                OVR[(kind, c, w, h)] = S
                n += 1

    # 쌍자음/겹받침 PNG를 별도로 그려둔 경우 우선 사용
    c_sizes = {(w, h) for kind, _, w, h in reqs if kind == 'c'}
    for c in tuple(TENSE) + tuple(COMPOUND):
        for w, h in c_sizes:
            p = png_path('c', c, w, h)
            if os.path.exists(p):
                S = load_png(p, w, h)
                if S is not None:
                    OVR[('c', c, w, h)] = S
                    n += 1
    print(f'PNG 자모 {n}개 불러옴 (기본 필요 {len(reqs)}개)')

    LATIN_OVR.clear()
    SYM_OVR.clear()
    n = 0
    for cp in EXTRA_CPS:
        p, w, h = extra_path(cp)
        if os.path.exists(p):
            S = load_png(p, w, h)
            if S is not None:
                (SYM_OVR if w == SYM_W else LATIN_OVR)[cp] = S
                n += 1
    print(f'PNG 영문/숫자/기호 {n}개 불러옴')


if __name__ == '__main__':
    if not os.path.isdir(PNG_DIR):
        print(f'오류: PNG 폴더를 찾을 수 없습니다 -> {PNG_DIR}')
        sys.exit(1)
    reqs = collect_requests()
    load_overrides(reqs=reqs)
    n = build(OUT_TTF, family='PixelKkwakchan13')
    print(f'완료: {OUT_TTF} (글리프 {n}개)')