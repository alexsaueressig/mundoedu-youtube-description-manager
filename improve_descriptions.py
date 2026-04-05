"""
improve_descriptions.py
-----------------------
Reescreve descrições robóticas com conteúdo casual e SEO-friendly.
Adiciona CTA "Bora estudar de graça? 🚀" em todos os arquivos.

Melhorias:
  1. Detecta e reescreve resumos auto-gerados (robóticos)
  2. Adiciona 2-3 perguntas SEO (👉) baseadas no título
  3. Adiciona CTA antes do Plano de Estudos em todos os arquivos
  4. Preserva conteúdo humano, módulos e timestamps

Uso:
    python improve_descriptions.py [--dry-run]
"""

import argparse
import os
import re
from pathlib import Path

import frontmatter

DESCRIPTIONS_DIR = os.getenv("DESCRIPTIONS_DIR", "videos/descriptions")

TAGLINE = "*MundoEdu: O melhor cursinho online agora é 100% gratuito!*"
PLANO_URL = "https://mundoedu.com.br/plano-de-estudos"
STANDARD_PLANO_LINE = f"✨ Plano de Estudos: {PLANO_URL}"
CTA_LINE = "Bora estudar de graça? 🚀"

# ---------------------------------------------------------------------------
# Professor map: subject → (display_name, gender)
# ---------------------------------------------------------------------------
PROFESSOR_MAP = {
    "História": ("Bussunda", "m"),
    "Química": ("Camacho", "m"),
    "Matemática": ("Gui Valenzuela", "m"),
    "Redação": ("Dani", "f"),
    "Português": ("Dani", "f"),
    "Literatura": ("Dani", "f"),
    "Gramática": ("Dani", "f"),
    "Física": ("Vasco", "m"),
    "Geografia": ("Giba", "m"),
    "Artes": ("JowJow", "m"),
}

# Subject detection from title keywords
SUBJECT_MAP = {
    "matemática": "Matemática",
    "física": "Física",
    "química": "Química",
    "biologia": "Biologia",
    "história": "História",
    "geografia": "Geografia",
    "filosofia": "Filosofia",
    "sociologia": "Sociologia",
    "literatura": "Literatura",
    "gramática": "Gramática",
    "português": "Português",
    "redação": "Redação",
    "artes": "Artes",
    "atualidades": "Atualidades",
}

# Robotic content patterns
ROBOTIC_PATTERNS = [
    re.compile(r"^Aula \d+ de \d+ sobre .+\.\s*Videoaula de .+\.$", re.MULTILINE),
    re.compile(r"^Videoaula sobre .+\.\s*Conteúdo de .+ para o ENEM\.$", re.MULTILINE),
    re.compile(r"^Videoaula sobre .+\.\s*Videoaula de .+\.$", re.MULTILINE),
    re.compile(r"^Resumo sobre .+\.\s*Conteúdo de .+ para o ENEM\.$", re.MULTILINE),
    re.compile(r"^Proposta de redação sobre .+ no estilo ENEM\.$", re.MULTILINE),
    re.compile(r"^Nesta videoaula, respondemos a pergunta:", re.MULTILINE),
    re.compile(r"^Videoaula sobre .+\.$", re.MULTILINE),
]

ROBOTIC_PERGUNTE = re.compile(r"^[OA] professor[a]?\s+.+\s+responde!", re.MULTILINE)
FILLER_LINE = re.compile(r"^Estude para o ENEM com videoaulas divertidas:?$")


PROPER_NOUNS = {
    "brasil", "china", "eua", "europa", "áfrica", "ásia", "américa",
    "portugal", "espanha", "frança", "roma", "grécia", "índia", "japão",
    "kant", "mendel", "newton", "darwin", "einstein", "marx", "weber",
    "freud", "nietzsche", "platão", "aristóteles", "sócrates", "maquiavel",
    "mauá", "getúlio", "vargas", "hitler", "stalin", "mussolini",
    "jekyll", "hamlet", "machado", "drummond", "clarice",
}


def smart_lower(text: str) -> str:
    """Lowercase but preserve acronyms and proper nouns."""
    if not text:
        return text
    words = text.split()
    result = []
    for word in words:
        clean = word.strip(",.;:!?()[]")
        if clean.isupper() and 1 < len(clean) <= 6:
            result.append(word)  # CRISPR, DNA, MCU, POP
        elif clean.lower() in PROPER_NOUNS:
            result.append(word)  # Brasil, Kant, etc.
        else:
            result.append(word.lower())
    return " ".join(result)


def verb_ser(term: str) -> str:
    """Return 'é' or 'são' based on rough Portuguese plurality."""
    t = term.strip().lower()
    if t.endswith(("s", "ões", "ais", "éis", "óis")):
        return "são"
    return "é"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def detect_subject(title: str) -> str | None:
    title_lower = title.lower()
    for keyword, subject in SUBJECT_MAP.items():
        if keyword in title_lower:
            return subject
    return None


def get_professor_ref(subject: str | None, with_article: bool = True) -> str | None:
    """Get professor reference like 'o prof. Bussunda' or 'prof. Bussunda'."""
    if not subject or subject not in PROFESSOR_MAP:
        return None
    name, gender = PROFESSOR_MAP[subject]
    title = "profª" if gender == "f" else "prof."
    if with_article:
        article = "a" if gender == "f" else "o"
        return f"{article} {title} {name}"
    return f"{title} {name}"


def extract_professor_from_body(body: str) -> str | None:
    """Extract professor display name from Pergunte! body for fallback."""
    m = re.search(r"[OA] professor[a]?\s+(.+?)\s+responde!", body)
    if not m:
        return None
    raw_name = m.group(1).strip()
    known = {
        "Bussunda": ("Bussunda", "m"),
        "Camacho": ("Camacho", "m"),
        "Gui Valenzuela": ("Gui Valenzuela", "m"),
        "Dani Bressan": ("Dani", "f"),
        "Vasco": ("Vasco", "m"),
        "Giba": ("Giba", "m"),
        "JowJow": ("JowJow", "m"),
    }
    for full_name, (display, gender) in known.items():
        if full_name.lower() in raw_name.lower():
            prefix = "profª" if gender == "f" else "prof."
            return f"{prefix} {display}"
    return f"prof. {raw_name}"


def extract_content_lines(body: str) -> list[str]:
    """Extract content lines, excluding structural elements."""
    lines = body.strip().split("\n")
    content = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s == TAGLINE:
            continue
        if s.startswith("✨ Plano de Estudos"):
            continue
        if s == CTA_LINE:
            continue
        if re.match(r"^(#[\w]+\s*)+$", s):
            continue
        if s.startswith("✔️"):
            continue
        if "MÓDULO COMPLETO" in s.upper():
            continue
        content.append(s)
    return content


def is_robotic(body: str) -> bool:
    """Check if content is auto-generated/robotic."""
    content = extract_content_lines(body)
    if not content:
        return True

    text = "\n".join(content)

    for pattern in ROBOTIC_PATTERNS:
        if pattern.search(text):
            return True

    # Pergunte! one-liner: "O professor X responde!" + optional filler
    if ROBOTIC_PERGUNTE.search(text):
        non_filler = [
            l for l in content
            if not ROBOTIC_PERGUNTE.search(l) and not FILLER_LINE.match(l)
        ]
        if len(non_filler) == 0:
            return True

    return False


# ---------------------------------------------------------------------------
# Title parsing
# ---------------------------------------------------------------------------
def parse_title(title: str) -> dict:
    """Parse video title into structured components."""
    clean = re.sub(r"^[^\w]*", "", title).strip()

    # Pergunte!
    m = re.match(r"Pergunte!\s*-\s*(.+)", clean)
    if m:
        return {
            "type": "pergunte",
            "question": m.group(1).strip(),
            "topic": None,
            "subtopic": None,
        }

    # Split on " - " to separate topic, subject, ENEM
    parts = re.split(r"\s+-\s+", clean)

    # Remove trailing "ENEM"
    if parts and parts[-1].strip().upper() == "ENEM":
        parts = parts[:-1]

    result = {
        "type": "standard",
        "topic": None,
        "subtopic": None,
        "part": None,
        "total": None,
        "subject_text": None,
    }

    if len(parts) >= 2:
        result["subject_text"] = parts[-1].strip()
        topic_part = " - ".join(parts[:-1])
    elif parts:
        result["subject_text"] = None
        topic_part = parts[0]
    else:
        result["subject_text"] = None
        topic_part = clean

    # Series with subtopic: "Topic (N/M): Subtitle"
    m = re.match(r"(.+?)\s*\((\d+)/(\d+)\)\s*:\s*(.+)$", topic_part)
    if m:
        result["type"] = "series"
        result["topic"] = m.group(1).strip()
        result["part"] = m.group(2)
        result["total"] = m.group(3)
        result["subtopic"] = m.group(4).strip()
        return result

    # Series without subtopic: "Topic (N/M)"
    m = re.match(r"(.+?)\s*\((\d+)/(\d+)\)\s*$", topic_part)
    if m:
        result["type"] = "series"
        result["topic"] = m.group(1).strip()
        result["part"] = m.group(2)
        result["total"] = m.group(3)
        return result

    # Topic with subtopic: "Topic: Subtitle"
    if ":" in topic_part:
        colon_parts = topic_part.split(":", 1)
        result["topic"] = colon_parts[0].strip()
        result["subtopic"] = colon_parts[1].strip()
    else:
        result["topic"] = topic_part.strip()

    # Special type detection
    topic = result.get("topic") or ""
    if re.search(r"\(resumo\)", topic, re.IGNORECASE):
        result["type"] = "resumo"
        result["topic"] = re.sub(r"\s*\([Rr]esumo\)\s*", "", topic).strip()
    elif "exercício" in topic.lower() or "exercícios" in topic.lower():
        result["type"] = "exercicios"
    elif "revisão" in topic.lower():
        result["type"] = "revisao"

    return result


# ---------------------------------------------------------------------------
# Content generation
# ---------------------------------------------------------------------------
def generate_summary(parsed: dict, professor: str | None) -> str:
    """Generate a casual 1-2 line summary from parsed title."""
    t = parsed

    if t["type"] == "pergunte":
        q = t["question"].rstrip("?").strip()
        # Lowercase first letter (unless starts with article O/A/Os/As)
        if q and q[0].isupper() and not q.startswith(("O ", "A ", "Os ", "As ")):
            q = q[0].lower() + q[1:]
        if professor:
            prof_display = professor[0].upper() + professor[1:]
            return f"{prof_display} responde: {q}?"
        return f"Respondemos: {q}?"

    topic = t.get("topic") or ""
    subtopic = t.get("subtopic") or ""
    topic_sl = smart_lower(topic)
    subtopic_sl = smart_lower(subtopic)

    if t["type"] == "series" and subtopic:
        # Special case: subtopic is exercises
        if "exercício" in subtopic.lower() or "exercícios" in subtopic.lower():
            if professor:
                return f"Nesta aula, {professor} resolve exercícios de {topic_sl}."
            return f"Exercícios resolvidos de {topic_sl} para o ENEM."
        if professor:
            return f"Nesta aula, {professor} explica {subtopic_sl} — parte do módulo de {topic_sl}."
        return f"Nesta aula, explicamos {subtopic_sl} — parte do módulo de {topic_sl}."

    if t["type"] == "series":
        if professor:
            return f"Nesta aula, {professor} explica {topic_sl}."
        return f"Nesta aula, explicamos {topic_sl}."

    if t["type"] == "resumo":
        if professor:
            return f"Nesta videoaula, {professor} faz um resumão de {topic_sl} pra você revisar pro ENEM."
        return f"Um resumão de {topic_sl} pra você revisar pro ENEM."

    if t["type"] == "exercicios":
        if professor:
            return f"Nesta videoaula, {professor} resolve exercícios de {topic_sl}."
        return f"Exercícios resolvidos de {topic_sl} para o ENEM."

    if t["type"] == "revisao":
        if professor:
            return f"Nesta videoaula, {professor} faz uma revisão de {topic_sl}."
        return f"Revisão de {topic_sl} para o ENEM."

    # Standard / standalone
    if subtopic:
        full = f"{topic_sl}: {subtopic_sl}"
    else:
        full = topic_sl
    if professor:
        return f"Nesta videoaula, {professor} explica {full}."
    return f"Nesta videoaula, explicamos {full}."


def generate_seo_questions(parsed: dict) -> list[str]:
    """Generate 2-3 SEO search questions from the title."""
    t = parsed
    questions = []

    if t["type"] == "pergunte":
        q = t["question"].strip()
        if not q.endswith("?"):
            q += "?"
        questions.append(f"👉 {q}")
        return questions

    topic = t.get("topic") or ""
    subtopic = t.get("subtopic") or ""
    main = subtopic or topic

    if not main:
        return questions

    main_sl = smart_lower(main)
    topic_sl = smart_lower(topic)
    is_exercise_sub = "exercício" in main.lower() or "exercícios" in main.lower()

    if t["type"] == "exercicios" or is_exercise_sub:
        questions.append(f"👉 Como resolver exercícios de {topic_sl}?")
        questions.append(f"👉 Quais exercícios de {topic_sl} caem no ENEM?")
    elif t["type"] in ("resumo", "revisao"):
        questions.append(f"👉 O que estudar sobre {topic_sl} pro ENEM?")
        questions.append(f"👉 Quais os principais conceitos de {topic_sl}?")
    else:
        # Check for "X e Y" comparison pattern (but not comma-separated lists)
        and_match = re.search(r"(.+?)\s+(?:e|x|vs\.?)\s+(.+)", main, re.IGNORECASE)
        if and_match and "," not in main:
            a = smart_lower(and_match.group(1).strip())
            b = smart_lower(and_match.group(2).strip())
            questions.append(f"👉 Qual a diferença entre {a} e {b}?")
        else:
            v = verb_ser(main_sl)
            questions.append(f"👉 O que {v} {main_sl}?")

        # Second question
        if subtopic and topic:
            questions.append(f"👉 Como estudar {topic_sl} para o ENEM?")
        else:
            questions.append(f"👉 Como {main_sl} cai no ENEM?")

    return questions[:3]


# ---------------------------------------------------------------------------
# Body parsing and reassembly
# ---------------------------------------------------------------------------
def parse_body(body: str) -> dict:
    """Parse body into structured sections."""
    lines = body.strip().split("\n")

    tagline = None
    content = []
    module_block = []
    plano_line = None
    hashtag_line = None
    has_cta = False
    in_module = False

    for line in lines:
        s = line.strip()

        if s == TAGLINE:
            tagline = s
            continue

        if s == CTA_LINE:
            has_cta = True
            continue

        if s.startswith("✨ Plano de Estudos:"):
            plano_line = s
            continue

        # Hashtag-only line (must be non-empty)
        if s and re.match(r"^(#[\w]+\s*)+$", s):
            hashtag_line = s
            continue

        # Module block: header line
        if not in_module and s and "MÓDULO COMPLETO" in s.upper():
            in_module = True
            module_block.append(line)
            continue

        # Module block: lesson links or empty lines within
        if in_module:
            if s.startswith("✔️") or not s:
                module_block.append(line)
                continue
            else:
                in_module = False

        content.append(line)

    return {
        "tagline": tagline or TAGLINE,
        "content": "\n".join(content).strip(),
        "module_block": "\n".join(module_block).strip(),
        "plano_line": plano_line or STANDARD_PLANO_LINE,
        "hashtag_line": hashtag_line or "",
        "has_cta": has_cta,
    }


def reassemble_body(sections: dict) -> str:
    """Reassemble body from sections."""
    parts = [sections["tagline"]]

    if sections["content"]:
        parts.append("")
        parts.append(sections["content"])

    if sections["module_block"]:
        parts.append("")
        parts.append(sections["module_block"])

    parts.append("")
    parts.append(CTA_LINE)
    parts.append(sections["plano_line"])

    if sections["hashtag_line"]:
        parts.append(sections["hashtag_line"])

    return "\n".join(parts)


def clean_whitespace(body: str) -> str:
    """Collapse multiple blank lines, trim edges."""
    lines = body.split("\n")
    result = []
    prev_empty = False
    for line in lines:
        if not line.strip():
            if prev_empty:
                continue
            prev_empty = True
        else:
            prev_empty = False
        result.append(line)
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------
def improve_file(filepath: Path, dry_run: bool = False) -> dict:
    """Process a single file. Returns summary of changes."""
    post = frontmatter.load(str(filepath))
    body = post.content
    title = post.metadata.get("title", "")
    original_body = body

    changes = []
    sections = parse_body(body)

    # Detect subject and professor
    subject = detect_subject(title)
    professor_with_article = get_professor_ref(subject, with_article=True)
    professor_no_article = get_professor_ref(subject, with_article=False)

    # Parse title
    parsed = parse_title(title)

    # For Pergunte! without a detected subject, extract professor from body
    if parsed["type"] == "pergunte" and not professor_no_article:
        prof_from_body = extract_professor_from_body(body)
        if prof_from_body:
            professor_no_article = prof_from_body

    # Check if content is robotic → rewrite
    robotic = is_robotic(body)
    if robotic:
        prof = professor_no_article if parsed["type"] == "pergunte" else professor_with_article
        summary = generate_summary(parsed, prof)
        seo_qs = generate_seo_questions(parsed)

        new_content_parts = [summary]
        if seo_qs:
            new_content_parts.append("")
            new_content_parts.extend(seo_qs)

        sections["content"] = "\n".join(new_content_parts)
        changes.append("REWRITE: robotic → casual summary")
        changes.append(f"  Summary: {summary}")
        for q in seo_qs:
            changes.append(f"  SEO: {q}")

    # Add CTA if missing
    cta_added = not sections["has_cta"]
    if cta_added:
        changes.append("ADD: CTA 'Bora estudar de graça? 🚀'")

    # Only write if something changed
    if not robotic and not cta_added:
        return {
            "filepath": str(filepath),
            "filename": filepath.name,
            "title": title,
            "changes": [],
            "modified": False,
            "was_robotic": False,
        }

    # Reassemble body
    new_body = reassemble_body(sections)
    new_body = clean_whitespace(new_body)

    if not dry_run:
        post.content = new_body
        with open(str(filepath), "wb") as f:
            frontmatter.dump(post, f)

    return {
        "filepath": str(filepath),
        "filename": filepath.name,
        "title": title,
        "changes": changes,
        "modified": True,
        "was_robotic": robotic,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Melhora descrições de vídeos do MundoEdu."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra mudanças sem aplicar.",
    )
    args = parser.parse_args()

    desc_dir = Path(DESCRIPTIONS_DIR)
    if not desc_dir.exists():
        print(f"ERRO: Diretório '{DESCRIPTIONS_DIR}' não encontrado.")
        return

    md_files = sorted(desc_dir.glob("*.md"))
    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"{prefix}Processando {len(md_files)} arquivos...\n")

    modified = 0
    rewritten = 0
    cta_added = 0
    errors = 0

    for filepath in md_files:
        try:
            result = improve_file(filepath, dry_run=args.dry_run)
            if result["modified"]:
                modified += 1
                if result["was_robotic"]:
                    rewritten += 1
                if any("CTA" in c for c in result["changes"]):
                    cta_added += 1
                if args.dry_run:
                    print(f"  📝 {result['filename']}")
                    for c in result["changes"]:
                        print(f"     └─ {c}")
        except Exception as e:
            errors += 1
            print(f"  ❌ ERRO em {filepath.name}: {e}")

    print(f"\n{prefix}Resultado:")
    print(f"  Modificados: {modified}")
    print(f"  Descrições reescritas: {rewritten}")
    print(f"  CTA adicionado: {cta_added}")
    print(f"  Erros: {errors}")
    print(f"  Total: {len(md_files)}")

    if args.dry_run and modified > 0:
        print(f"\nExecute sem --dry-run para aplicar as {modified} mudanças.")


if __name__ == "__main__":
    main()
