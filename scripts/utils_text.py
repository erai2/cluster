import regex as re

# --- 헤딩 규칙 ---
# 제1장, 제2절 ... / [대주제], [부부관계] 등  → H1/H2/H3
H1_PATTS = [
    r'^\s*제\s*\d+\s*장\b',             # 제1장
    r'^\s*사례\s*\d+\b',                # 사례 12
]
H2_PATTS = [
    r'^\s*제\s*\d+\s*절\b',             # 제1절
    r'^\s*\[[^\]]+\]\s*$',              # [부부관계], [직종관계]
    r'^\s*(원문|구조분석|해석)\s*:\s*$', # 섹션 키워드:
]
H3_PATTS = [
    r'^\s*〈?예〉?\s*$',                # <예> or 〈예〉
    r'^\s*참고\s*$',                    # 참고
]

# 불릿/기호: ●, •, ‣, ※, - 등
BULLETS = r'^[\s]*([●•‣\-–—])\s*'

# ※ 주석 → blockquote 강조
NOTE_PAT = r'^\s*※\s*(.+)$'

# 공백/줄바꿈 정리
MULTISPACE = re.compile(r'[ \t]+')
MULTIBLANK = re.compile(r'\n{3,}')

def to_heading(line: str) -> str:
    s = line.strip()
    for p in H1_PATTS:
        if re.match(p, s):
            return f"# {re.sub(r'^\\s*', '', s)}"
    for p in H2_PATTS:
        if re.match(p, s):
            return f"## {re.sub(r'^\\s*', '', s).strip(': ')}"
    for p in H3_PATTS:
        if re.match(p, s):
            return f"### {re.sub(r'^\\s*', '', s)}"
    return ""

def normalize_bullet(line: str) -> str:
    # ●/•/‣/– → "- " 로
    if re.match(BULLETS, line):
        content = re.sub(BULLETS, '', line).strip()
        return f"- {content}"
    # " -text" 같은 경우
    if re.match(r'^\s*-\s*', line):
        return re.sub(r'^\s*-', '-', line)
    return line

def normalize_note(line: str) -> str:
    m = re.match(NOTE_PAT, line)
    if m:
        body = m.group(1).strip()
        return f"> **참고:** {body}"
    return line

def normalize_inline(s: str) -> str:
    # 연속 스페이스 최소화
    s = MULTISPACE.sub(' ', s)
    # 특수 기호 공백 정리
    s = re.sub(r'\s+([,:;])', r'\1', s)
    return s.strip()

def normalize_block(text: str) -> str:
    # 빈 줄 2줄로 압축
    return MULTIBLANK.sub('\n\n', text.strip())

def transform_lines(lines):
    out = []
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            out.append("")
            continue

        # 헤딩 인식 우선
        h = to_heading(line)
        if h:
            out.append(h)
            continue

        # 불릿/주석/인라인 규칙
        line = normalize_bullet(line)
        line = normalize_note(line)
        line = normalize_inline(line)
        out.append(line)

    text = "\n".join(out)
    text = normalize_block(text)
    return text
