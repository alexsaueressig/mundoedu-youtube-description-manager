"""
fix_descriptions.py
-------------------
Corrige e padroniza os arquivos .md de descrições de vídeos do MundoEdu.

Correções aplicadas:
  1. Renomeia arquivos cujo nome não corresponde ao ID do vídeo
  2. Adiciona tagline MundoEdu se ausente
  3. Padroniza link do Plano de Estudos para formato ✨
  4. Remove URL base redundante (quando plano-de-estudos já existe)
  5. Corrige hashtags: adiciona #ENEM, matéria e tópico; mantém tags de personalidade
  6. Gera resumo automático para vídeos sem descrição

Uso:
    python fix_descriptions.py [--dry-run]

Opções:
    --dry-run    Mostra as mudanças sem aplicar
"""

import argparse
import os
import re
import shutil
import unicodedata
from pathlib import Path

import frontmatter

DESCRIPTIONS_DIR = os.getenv("DESCRIPTIONS_DIR", "videos/descriptions")

TAGLINE = "*MundoEdu: O melhor cursinho online agora é 100% gratuito!*"
PLANO_URL = "https://mundoedu.com.br/plano-de-estudos"
STANDARD_PLANO_LINE = f"✨ Plano de Estudos: {PLANO_URL}"
BARE_URL_PATTERN = re.compile(r"^https://mundoedu\.com\.br/?$", re.MULTILINE)

# ---------------------------------------------------------------------------
# Mapeamento de matérias
# ---------------------------------------------------------------------------
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
    "gramática": "Português",
    "português": "Português",
    "redação": "Redação",
    "artes": "Artes",
    "atualidades": "Atualidades",
    "linguagem": "LínguaPortuguesa",
}

# Hashtags de personalidade conhecidas ("#RUUI", "#DaniSensacional", etc.)
PERSONALITY_TAGS = {
    "#RUUI", "#DaniSensacional", "#DaniMaravilha", "#DaniRainha",
    "#ExpoMendes", "#MundoEdu",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def strip_accents(s: str) -> str:
    """Remove acentos para comparação case-insensitive."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def detect_subject(title: str) -> str | None:
    """Detecta a matéria a partir do título."""
    title_lower = title.lower()
    for keyword, subject in SUBJECT_MAP.items():
        if keyword in title_lower:
            return subject
    return None


def extract_topic_tag(title: str) -> str | None:
    """Extrai um tópico do título para usar como hashtag.

    Para títulos como "🧬 Genética (3/8): Ausência de dominância - Biologia - ENEM"
    retorna "Genética".
    """
    # Remove emojis do início
    clean = re.sub(r"^[^\w]*", "", title)
    # Pega a primeira parte antes de " - "
    parts = re.split(r"\s+-\s+", clean)
    if not parts:
        return None
    first = parts[0].strip()
    # Remove (N/M) e tudo depois de ":"
    first = re.sub(r"\s*\(\d+/\d+\)\s*:?\s*.*", "", first).strip()
    # Remove "(Resumo)", "(ISIS)", etc
    first = re.sub(r"\s*\(.*?\)\s*", "", first).strip()
    # Remove trailing numbers ("Questão Resolvida 1" → "Questão Resolvida")
    first = re.sub(r"\s+\d+$", "", first).strip()
    # Remove "#N" patterns ("Questão Resolvida #1" → "Questão Resolvida")
    first = re.sub(r"\s*#\d+", "", first).strip()
    # Se sobrou algo razoável (1-3 palavras, <= 25 chars), use como tag
    if first and len(first.split()) <= 3 and len(first) <= 25:
        # Converte para PascalCase sem espaços
        tag = re.sub(r"\s+", "", first.title())
        # Remove caracteres não alfanuméricos exceto acentos
        tag = re.sub(r"[^\w]", "", tag)
        # Remove conectores curtos do meio (E, De, Do, Da, Dos, Das, X)
        tag = re.sub(r"(?<=[a-záéíóúãõâêô])(?:E|De|Do|Da|Dos|Das|X)(?=[A-ZÁÉÍÓÚÃÕÂÊÔ])", "", tag)
        return tag
    return None


def extract_hashtags(body: str) -> list[str]:
    """Extrai todas as hashtags existentes no corpo."""
    tags = re.findall(r"#[\w]+", body)
    # Remove hashtags puramente numéricas (#1, #2, etc.)
    return [t for t in tags if not re.match(r"^#\d+$", t)]


def remove_hashtag_lines(body: str) -> str:
    """Remove linhas que contêm apenas hashtags."""
    lines = body.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and re.match(r"^(#[\w]+\s*)+$", stripped):
            continue
        result.append(line)
    return "\n".join(result)


def has_summary(body: str) -> bool:
    """Verifica se tem resumo além de tagline, links, hashtags e módulos."""
    lines = body.strip().split("\n")
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s == TAGLINE:
            continue
        if re.match(r"^https?://", s):
            continue
        if re.match(r"^(#[\w]+\s*)+$", s):
            continue
        if "PLANO DE ESTUDOS" in s.upper():
            continue
        if "Plano de Estudos" in s:
            continue
        if s.startswith("✨ Links úteis"):
            continue
        if s.startswith("✨ Plano"):
            continue
        if s.startswith("✔️"):
            continue
        if "MÓDULO COMPLETO" in s.upper():
            continue
        if "módulo completo" in s.lower():
            continue
        return True
    return False


def generate_summary(title: str) -> str:
    """Gera um resumo de 1-2 frases a partir do título do vídeo."""
    # Remove emojis do início
    clean = re.sub(r"^[^\w]*", "", title).strip()

    # Detecta padrões comuns
    # Padrão "Pergunte! - Pergunta"
    m = re.match(r"Pergunte!\s*-\s*(.+)", clean)
    if m:
        question = m.group(1).strip().rstrip("?")
        return f"Nesta videoaula, respondemos a pergunta: {question}?"

    # Padrão "Tema (N/M): Subtema - Matéria - ENEM"
    m = re.match(r"(.+?)\s*\((\d+)/(\d+)\)\s*:\s*(.+?)\s*-\s*(\w[\w\s]*?)\s*-\s*ENEM", clean)
    if m:
        topic = m.group(1).strip()
        part = m.group(2)
        total = m.group(3)
        subtitle = m.group(4).strip()
        subject = m.group(5).strip()
        return f"Aula {part} de {total} sobre {topic}: {subtitle}. Videoaula de {subject} para o ENEM."

    # Padrão "Tema (N/M): Subtema - Matéria"
    m = re.match(r"(.+?)\s*\((\d+)/(\d+)\)\s*:\s*(.+?)\s*-\s*(\w[\w\s]*?)$", clean)
    if m:
        topic = m.group(1).strip()
        part = m.group(2)
        total = m.group(3)
        subtitle = m.group(4).strip()
        subject = m.group(5).strip()
        return f"Aula {part} de {total} sobre {topic}: {subtitle}. Videoaula de {subject}."

    # Padrão "Tema: Subtema - Matéria - ENEM"
    m = re.match(r"(.+?)\s*:\s*(.+?)\s*-\s*(\w[\w\s]*?)\s*-\s*ENEM", clean)
    if m:
        topic = m.group(1).strip()
        subtitle = m.group(2).strip()
        subject = m.group(3).strip()
        return f"Videoaula sobre {topic}: {subtitle}. Conteúdo de {subject} para o ENEM."

    # Padrão "Tema - Matéria - ENEM"
    m = re.match(r"(.+?)\s*-\s*(\w[\w\s]*?)\s*-\s*ENEM", clean)
    if m:
        topic = m.group(1).strip()
        subject = m.group(2).strip()
        return f"Videoaula sobre {topic}. Conteúdo de {subject} para o ENEM."

    # Padrão "Tema (Resumo) - Matéria - ENEM"
    m = re.match(r"(.+?)\s*\(Resumo\)\s*-\s*(\w[\w\s]*?)\s*-\s*ENEM", clean, re.IGNORECASE)
    if m:
        topic = m.group(1).strip()
        subject = m.group(2).strip()
        return f"Resumo sobre {topic}. Conteúdo de {subject} para o ENEM."

    # Padrão "ENEM - Algo"
    m = re.match(r"ENEM\s*[-:]\s*(.+)", clean)
    if m:
        desc = m.group(1).strip()
        return f"{desc}."

    # Padrão "Tema - Mundo Atualidades - ENEM"
    m = re.match(r"(.+?)\s*-\s*Mundo\s+(\w+)\s*-\s*ENEM", clean)
    if m:
        topic = m.group(1).strip()
        area = m.group(2).strip()
        return f"Videoaula sobre {topic}. Conteúdo de {area} para o ENEM."

    # Padrão com "Proposta de redação"
    m = re.match(r"Proposta de redação\s*(?:ENEM)?\s*-?\s*(.+)", clean, re.IGNORECASE)
    if m:
        topic = m.group(1).strip()
        return f"Proposta de redação sobre {topic} no estilo ENEM."

    # Padrão genérico com " - "
    parts = re.split(r"\s+-\s+", clean)
    if len(parts) >= 2:
        topic = parts[0].strip()
        return f"Videoaula sobre {topic}."

    # Fallback
    return f"{clean}."


def remove_plano_block(body: str) -> str:
    """Remove todas as variações do bloco de Plano de Estudos."""
    lines = body.split("\n")
    result = []
    skip_next_url = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip URL that follows a plano header
        if skip_next_url:
            skip_next_url = False
            if PLANO_URL in stripped:
                continue

        # Inline format: "✨ Plano de Estudos: URL" or "✨ Plano de Estudos COMPLETO: URL"
        if PLANO_URL in stripped and ("Plano de Estudos" in stripped or "PLANO DE ESTUDOS" in stripped):
            continue

        # Header line followed by URL on next line
        if ("PLANO DE ESTUDOS" in stripped.upper() or "Plano de Estudos" in stripped) and \
                i + 1 < len(lines) and PLANO_URL in lines[i + 1]:
            skip_next_url = True
            continue

        # Standalone plano URL (preceded by a header we already caught, or orphaned)
        if stripped == PLANO_URL:
            # Check if previous non-empty line was a header
            prev_content = ""
            for j in range(i - 1, -1, -1):
                if lines[j].strip():
                    prev_content = lines[j].strip()
                    break
            if "PLANO DE ESTUDOS" in prev_content.upper() or "Plano de Estudos" in prev_content:
                continue
            # Orphaned URL — still remove it (we'll add the standard one back)
            continue

        # "✨ Links úteis" line (often precedes the bare URL)
        if stripped == "✨ Links úteis":
            continue

        result.append(line)

    return "\n".join(result)


def remove_bare_url(body: str) -> str:
    """Remove a URL base mundoedu.com.br quando não faz parte de outro link."""
    lines = body.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^https://mundoedu\.com\.br/?$", stripped):
            continue
        result.append(line)
    return "\n".join(result)


def normalize_hashtag(tag: str) -> str:
    """Normaliza uma hashtag para PascalCase consistente."""
    corrections = {
        "#genetica": "#Genética",
        "#genética": "#Genética",
        "#historia": "#História",
        "#história": "#História",
        "#historiadobrasil": "#HistóriaDoBrasil",
        "#físca": "#Física",
        "#fisica": "#Física",
        "#quimica": "#Química",
        "#matematica": "#Matemática",
        "#linguaportuguesa": "#LínguaPortuguesa",
        "#línguaportuguesa": "#LínguaPortuguesa",
        "#portugues": "#Português",
        "#redaçãoenem": "#RedaçãoENEM",
        "#sociologia": "#Sociologia",
    }
    return corrections.get(tag.lower(), tag)


def build_hashtags(existing_tags: list[str], title: str) -> list[str]:
    """Constrói a lista final de 4-5 hashtags."""
    # Normalizar tags existentes
    existing = [normalize_hashtag(t) for t in existing_tags]

    # Separar personality tags e content tags
    personality = [t for t in existing if t in PERSONALITY_TAGS]
    content = [t for t in existing if t not in PERSONALITY_TAGS]

    # Garantir #ENEM
    if "#ENEM" not in content:
        content.insert(0, "#ENEM")

    # Garantir tag de matéria
    subject = detect_subject(title)
    if subject:
        subject_tag = f"#{subject}"
        subject_tag = normalize_hashtag(subject_tag)
        # Verificar se já existe (case-insensitive)
        existing_lower = [t.lower() for t in content]
        if subject_tag.lower() not in existing_lower:
            # Inserir após #ENEM
            idx = 1 if content and content[0] == "#ENEM" else 0
            content.insert(idx, subject_tag)

    # Garantir tag de tópico (evitar duplicata com matéria)
    topic = extract_topic_tag(title)
    if topic:
        topic_tag = f"#{topic}"
        topic_tag = normalize_hashtag(topic_tag)
        existing_lower = [t.lower() for t in content]
        # Não adicionar se já existe ou se é igual à matéria
        if topic_tag.lower() not in existing_lower and \
                (not subject or topic_tag.lower() != f"#{subject}".lower()):
            content.append(topic_tag)

    # Detectar tags específicas adicionais do título
    title_lower = title.lower()
    extra_tags = []
    if "exercício" in title_lower or "exercícios" in title_lower:
        extra_tags.append("#ExercíciosResolvidos")
    if "resumo" in title_lower:
        extra_tags.append("#Resumo")
    if "revisão" in title_lower:
        extra_tags.append("#Revisão")
    if "proposta de redação" in title_lower:
        extra_tags.append("#PropostaDeRedação")
    if "questão resolvida" in title_lower:
        extra_tags.append("#QuestãoResolvida")
    if "pergunte" in title_lower:
        extra_tags.append("#Pergunte")

    # Extrair subtópico de títulos com formato "(N/M): Subtítulo"
    m = re.search(r"\(\d+/\d+\)\s*:\s*(.+?)\s+-\s+\w", title)
    if m:
        subtitle = m.group(1).strip()
        # Transformar em tag PascalCase (se <= 25 chars e <= 4 palavras)
        if subtitle and len(subtitle.split()) <= 4 and len(subtitle) <= 30:
            # Tratar hifens como espaços para PascalCase
            sub_clean = subtitle.replace("-", " ")
            sub_tag = re.sub(r"\s+", "", sub_clean.title())
            sub_tag = re.sub(r"[^\w]", "", sub_tag)
            if sub_tag:
                extra_tags.append(f"#{sub_tag}")

    # Extrair subtópico de "Tema: Subtema - Matéria"
    if not m:
        m2 = re.search(r":\s*(.+?)\s+-\s+\w", title)
        if m2:
            subtitle2 = m2.group(1).strip()
            if subtitle2 and len(subtitle2.split()) <= 4 and len(subtitle2) <= 30:
                sub_clean2 = subtitle2.replace("-", " ")
                sub_tag2 = re.sub(r"\s+", "", sub_clean2.title())
                sub_tag2 = re.sub(r"[^\w]", "", sub_tag2)
                if sub_tag2:
                    extra_tags.append(f"#{sub_tag2}")

    for et in extra_tags:
        # Aplicar normalização de conectores nas tags extras
        cleaned = re.sub(r"(?<=[a-záéíóúãõâêô])(?:E|De|Do|Da|Dos|Das|X)(?=[A-ZÁÉÍÓÚÃÕÂÊÔ])", "", et)
        if cleaned.lower() not in [t.lower() for t in content]:
            content.append(cleaned)

    # Mover #ENEM para o início
    if "#ENEM" in content:
        content.remove("#ENEM")
        content.insert(0, "#ENEM")

    # Remover duplicatas preservando ordem
    seen = set()
    deduped = []
    for t in content:
        key = t.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(t)
    content = deduped

    # Limitar a 4-5 content tags + personality tags
    final = content[:5]

    # Adicionar personality tags se houver espaço
    for pt in personality:
        if pt not in final:
            final.append(pt)

    return final


def clean_body_whitespace(body: str) -> str:
    """Remove linhas em branco excessivas (máximo 1 linha em branco consecutiva)."""
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
    
    # Remove linhas em branco no início e final
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()

    return "\n".join(result)


def fix_file(filepath: Path, dry_run: bool = False) -> dict:
    """Aplica todas as correções em um arquivo. Retorna um resumo das mudanças."""
    post = frontmatter.load(str(filepath))
    body = post.content
    metadata = post.metadata

    video_id = metadata.get("id", "")
    title = metadata.get("title", "")
    original_body = body

    changes = []

    # 1. Fix filename mismatch
    expected_filename = f"{video_id}.md"
    if filepath.name != expected_filename:
        new_path = filepath.parent / expected_filename
        changes.append(f"RENAME: {filepath.name} → {expected_filename}")
        if not dry_run:
            shutil.move(str(filepath), str(new_path))
            filepath = new_path

    # 2. Extract existing hashtags before stripping
    existing_hashtags = extract_hashtags(body)

    # 3. Remove hashtag lines (will reconstruct at end)
    body = remove_hashtag_lines(body)

    # 4. Remove old plano de estudos block (will reconstruct)
    body = remove_plano_block(body)

    # 5. Remove bare URL if plano link will be added
    body = remove_bare_url(body)

    # 6. Ensure tagline is first
    if TAGLINE not in body:
        changes.append("ADD: tagline MundoEdu")
        body = TAGLINE + "\n\n" + body.lstrip("\n")
    else:
        # Make sure tagline is at the top
        body = body.replace(TAGLINE, "").strip()
        body = TAGLINE + "\n\n" + body.lstrip("\n")

    # 7. Check if summary exists; if not, generate one
    # We need to check the body AFTER tagline but BEFORE plano link insertion
    test_body = body
    if not has_summary(test_body):
        summary = generate_summary(title)
        changes.append(f"ADD: resumo gerado — \"{summary}\"")
        # Insert after tagline
        body = body.replace(TAGLINE, TAGLINE + "\n\n" + summary, 1)

    # 8. Clean up whitespace
    body = clean_body_whitespace(body)

    # 9. Append standard plano link
    changes.append("STANDARDIZE: link Plano de Estudos")
    body = body.rstrip() + "\n\n" + STANDARD_PLANO_LINE

    # 10. Build and append hashtags
    final_tags = build_hashtags(existing_hashtags, title)
    if set(final_tags) != set(existing_hashtags):
        changes.append(f"FIX: hashtags {existing_hashtags} → {final_tags}")
    hashtag_line = " ".join(final_tags)
    body = body.rstrip() + "\n" + hashtag_line

    # Final cleanup
    body = clean_body_whitespace(body)

    # Write if changed
    if body != original_body and not dry_run:
        post.content = body
        with open(str(filepath), "wb") as f:
            frontmatter.dump(post, f)

    return {
        "filepath": str(filepath),
        "filename": filepath.name,
        "id": video_id,
        "title": title,
        "changes": changes,
        "modified": body != original_body,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Corrige e padroniza descrições de vídeos do MundoEdu."
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
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Processando {len(md_files)} arquivos...\n")

    modified = 0
    unchanged = 0
    all_changes = []

    for filepath in md_files:
        try:
            result = fix_file(filepath, dry_run=args.dry_run)
            if result["modified"]:
                modified += 1
                all_changes.append(result)
                if args.dry_run:
                    print(f"  📝 {result['filename']}")
                    for c in result["changes"]:
                        print(f"     └─ {c}")
            else:
                unchanged += 1
        except Exception as e:
            print(f"  ❌ ERRO em {filepath.name}: {e}")

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Resultado:")
    print(f"  Modificados: {modified}")
    print(f"  Sem mudanças: {unchanged}")
    print(f"  Total: {len(md_files)}")

    if args.dry_run and modified > 0:
        print(f"\nExecute sem --dry-run para aplicar as {modified} mudanças.")


if __name__ == "__main__":
    main()
