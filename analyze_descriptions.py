"""
analyze_descriptions.py
-----------------------
Analisa todos os arquivos .md de descrições de vídeos e gera um relatório
(report.md) com problemas encontrados e estatísticas.

Uso:
    python analyze_descriptions.py
"""

import os
import re
from pathlib import Path

import frontmatter

DESCRIPTIONS_DIR = os.getenv("DESCRIPTIONS_DIR", "videos/descriptions")
REPORT_FILE = "report.md"

TAGLINE = "*MundoEdu: O melhor cursinho online agora é 100% gratuito!*"
PLANO_URL = "https://mundoedu.com.br/plano-de-estudos"
BARE_URL = "https://mundoedu.com.br"

# Matérias reconhecidas (titulo → hashtag)
SUBJECT_MAP = {
    "matemática": "#Matemática",
    "física": "#Física",
    "química": "#Química",
    "biologia": "#Biologia",
    "história": "#História",
    "geografia": "#Geografia",
    "filosofia": "#Filosofia",
    "sociologia": "#Sociologia",
    "literatura": "#Literatura",
    "gramática": "#Português",
    "português": "#Português",
    "redação": "#Redação",
    "artes": "#Artes",
    "atualidades": "#Atualidades",
    "linguagem": "#LínguaPortuguesa",
}


def extract_hashtags(body: str) -> list[str]:
    """Extrai todas as hashtags do corpo da descrição."""
    tags = re.findall(r"#\w+", body)
    # Remove hashtags puramente numéricas (#1, #2, etc.)
    return [t for t in tags if not re.match(r"^#\d+$", t)]


def detect_subject_from_title(title: str) -> str | None:
    """Detecta a matéria a partir do título do vídeo."""
    title_lower = title.lower()
    for keyword, tag in SUBJECT_MAP.items():
        if keyword in title_lower:
            return tag
    return None


def extract_topic_from_title(title: str) -> str | None:
    """Extrai o tópico principal do título (texto antes do primeiro - ou :)."""
    # Padrão: "Emoji Topic (N/M): Subtopic - Matéria - ENEM"
    # Queremos extrair "Topic" ou "Topic: Subtopic"
    clean = re.sub(r"^[^\w]*", "", title)  # remove emojis do início
    parts = re.split(r"\s*-\s*", clean)
    if parts:
        topic = parts[0].strip()
        # Remove (N/M) notation
        topic = re.sub(r"\s*\(\d+/\d+\)\s*:?\s*", " ", topic).strip()
        # Remove : suffix content for short tag
        topic = topic.split(":")[0].strip()
        return topic
    return None


def has_summary(body: str) -> bool:
    """Verifica se o corpo tem uma descrição/resumo além do tagline, links e hashtags."""
    lines = body.strip().split("\n")
    content_lines = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        # Ignora tagline
        if line_stripped == TAGLINE:
            continue
        # Ignora linhas que são apenas URLs
        if re.match(r"^https?://", line_stripped):
            continue
        # Ignora linhas que são apenas hashtags
        if re.match(r"^(#\w+\s*)+$", line_stripped):
            continue
        # Ignora linhas de título de seção (PLANO DE ESTUDOS, etc.)
        if "PLANO DE ESTUDOS" in line_stripped.upper():
            continue
        if "Plano de Estudos" in line_stripped:
            continue
        # Ignora linhas de links úteis
        if line_stripped.startswith("✨ Links úteis"):
            continue
        if line_stripped.startswith("✨ Plano"):
            continue
        # Ignora linhas de módulo (✔️ Aula N -)
        if line_stripped.startswith("✔️"):
            continue
        # Ignora emojis + MÓDULO COMPLETO headers
        if "MÓDULO COMPLETO" in line_stripped.upper():
            continue
        if re.match(r"^[^\w]*Módulo completo", line_stripped, re.IGNORECASE):
            continue
        # Ignora "👉 Módulo completo"
        if "módulo completo" in line_stripped.lower():
            continue
        content_lines.append(line_stripped)

    return len(content_lines) > 0


def has_plano_link(body: str) -> bool:
    return PLANO_URL in body


def has_bare_url(body: str) -> bool:
    """Verifica se tem o link base sem ser o plano-de-estudos."""
    # Procura mundoedu.com.br que NÃO é seguido por /plano ou /videoaula
    lines = body.split("\n")
    for line in lines:
        line_stripped = line.strip()
        if line_stripped == BARE_URL or line_stripped == BARE_URL + "/":
            return True
        if re.match(r"^https://mundoedu\.com\.br/?$", line_stripped):
            return True
    return False


def has_tagline(body: str) -> bool:
    return TAGLINE in body


def detect_study_plan_format(body: str) -> str | None:
    """Detecta o formato usado para o link do plano de estudos."""
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if PLANO_URL in line:
            # Pode estar na mesma linha ou na anterior
            if "Plano de Estudos" in line or "PLANO DE ESTUDOS" in line:
                return line.strip()
            # Verifica linha anterior
            if i > 0:
                prev = lines[i - 1].strip()
                if "PLANO DE ESTUDOS" in prev.upper() or "Plano de Estudos" in prev:
                    return f"{prev}\n{line.strip()}"
        elif "PLANO DE ESTUDOS" in line.upper() or "Plano de Estudos" in line:
            # Linha de header sem o link na mesma linha
            if i + 1 < len(lines) and PLANO_URL in lines[i + 1]:
                return f"{line.strip()}\n{lines[i + 1].strip()}"
    return None


def check_filename_id_match(filepath: Path, video_id: str) -> bool:
    """Verifica se o nome do arquivo corresponde ao ID do vídeo."""
    expected = f"{video_id}.md"
    return filepath.name == expected


def analyze_file(filepath: Path) -> dict:
    """Analisa um arquivo de descrição e retorna um dicionário de issues."""
    post = frontmatter.load(str(filepath))
    body = post.content
    metadata = post.metadata

    video_id = metadata.get("id", "")
    title = metadata.get("title", "")

    issues = []
    info = {
        "filepath": str(filepath),
        "filename": filepath.name,
        "id": video_id,
        "title": title,
    }

    # 1. Filename vs ID mismatch
    if not check_filename_id_match(filepath, video_id):
        issues.append("FILENAME_MISMATCH")

    # 2. Missing tagline
    if not has_tagline(body):
        issues.append("MISSING_TAGLINE")

    # 3. Missing plano de estudos link
    if not has_plano_link(body):
        issues.append("MISSING_PLANO_LINK")

    # 4. Redundant bare URL
    if has_bare_url(body) and has_plano_link(body):
        issues.append("REDUNDANT_BARE_URL")

    # 5. Missing hashtags
    hashtags = extract_hashtags(body)
    if not hashtags:
        issues.append("MISSING_HASHTAGS")
    else:
        # Check for #ENEM
        if "#ENEM" not in hashtags:
            issues.append("MISSING_ENEM_TAG")

        # Check for subject tag
        subject = detect_subject_from_title(title)
        if subject and subject not in hashtags:
            # Check case-insensitive
            hashtags_lower = [h.lower() for h in hashtags]
            if subject.lower() not in hashtags_lower:
                issues.append("MISSING_SUBJECT_TAG")

    # 6. Missing summary/description
    if not has_summary(body):
        issues.append("MISSING_SUMMARY")

    # 7. Study plan format (non-standard)
    plan_format = detect_study_plan_format(body)
    if plan_format and "✨ Plano de Estudos:" not in plan_format:
        issues.append("NONSTANDARD_PLANO_FORMAT")

    # 8. Too few hashtags (< 4)
    if hashtags and len(hashtags) < 4:
        issues.append("FEW_HASHTAGS")

    info["issues"] = issues
    info["hashtags"] = hashtags
    info["has_summary"] = has_summary(body)
    info["subject"] = detect_subject_from_title(title)
    info["plan_format"] = plan_format

    return info


def generate_report(results: list[dict]) -> str:
    """Gera o relatório em Markdown."""
    total = len(results)
    files_with_issues = [r for r in results if r["issues"]]
    files_ok = total - len(files_with_issues)

    # Contadores por tipo de issue
    issue_counts = {}
    issue_files = {}
    for r in results:
        for issue in r["issues"]:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
            if issue not in issue_files:
                issue_files[issue] = []
            issue_files[issue].append(r)

    report = []
    report.append("# Relatório de Análise — Descrições MundoEdu\n")
    report.append(f"**Total de arquivos**: {total}")
    report.append(f"**Arquivos OK**: {files_ok}")
    report.append(f"**Arquivos com problemas**: {len(files_with_issues)}\n")

    report.append("## Resumo de Problemas\n")
    report.append("| Problema | Quantidade |")
    report.append("| --- | --- |")

    issue_labels = {
        "FILENAME_MISMATCH": "Nome de arquivo ≠ ID do vídeo",
        "MISSING_TAGLINE": "Tagline MundoEdu ausente",
        "MISSING_PLANO_LINK": "Link do Plano de Estudos ausente",
        "REDUNDANT_BARE_URL": "URL base redundante (mundoedu.com.br)",
        "MISSING_HASHTAGS": "Sem hashtags",
        "MISSING_ENEM_TAG": "Hashtag #ENEM ausente",
        "MISSING_SUBJECT_TAG": "Hashtag da matéria ausente",
        "MISSING_SUMMARY": "Sem resumo/descrição do conteúdo",
        "NONSTANDARD_PLANO_FORMAT": "Formato do link Plano de Estudos fora do padrão",
        "FEW_HASHTAGS": "Menos de 4 hashtags",
    }

    for issue_key in [
        "FILENAME_MISMATCH",
        "MISSING_TAGLINE",
        "MISSING_PLANO_LINK",
        "REDUNDANT_BARE_URL",
        "MISSING_HASHTAGS",
        "MISSING_ENEM_TAG",
        "MISSING_SUBJECT_TAG",
        "MISSING_SUMMARY",
        "NONSTANDARD_PLANO_FORMAT",
        "FEW_HASHTAGS",
    ]:
        count = issue_counts.get(issue_key, 0)
        label = issue_labels.get(issue_key, issue_key)
        report.append(f"| {label} | {count} |")

    report.append("")

    # Detalhes por categoria
    for issue_key, label in issue_labels.items():
        files = issue_files.get(issue_key, [])
        if not files:
            continue

        report.append(f"\n## {label} ({len(files)} arquivos)\n")

        if issue_key == "FILENAME_MISMATCH":
            for f in files:
                report.append(f"- `{f['filename']}` → ID no arquivo: `{f['id']}`")
        elif issue_key in ("MISSING_HASHTAGS", "MISSING_ENEM_TAG", "MISSING_SUBJECT_TAG", "FEW_HASHTAGS"):
            for f in files:
                tags = ", ".join(f["hashtags"]) if f["hashtags"] else "(nenhuma)"
                subject = f["subject"] or "?"
                report.append(f"- `{f['filename']}` — tags: {tags} — matéria: {subject}")
        elif issue_key == "NONSTANDARD_PLANO_FORMAT":
            # Mostrar apenas primeiros 10
            shown = files[:10]
            for f in shown:
                fmt = (f["plan_format"] or "").replace("\n", " → ")
                report.append(f"- `{f['filename']}` — formato: `{fmt}`")
            if len(files) > 10:
                report.append(f"- ... e mais {len(files) - 10} arquivos")
        else:
            for f in files[:30]:
                report.append(f"- `{f['filename']}` — {f['title']}")
            if len(files) > 30:
                report.append(f"- ... e mais {len(files) - 30} arquivos")

    report.append("")
    return "\n".join(report)


def main():
    desc_dir = Path(DESCRIPTIONS_DIR)
    if not desc_dir.exists():
        print(f"ERRO: Diretório '{DESCRIPTIONS_DIR}' não encontrado.")
        return

    md_files = sorted(desc_dir.glob("*.md"))
    print(f"Analisando {len(md_files)} arquivos...")

    results = []
    for filepath in md_files:
        try:
            result = analyze_file(filepath)
            results.append(result)
        except Exception as e:
            print(f"  ERRO ao analisar {filepath.name}: {e}")
            results.append({
                "filepath": str(filepath),
                "filename": filepath.name,
                "id": "",
                "title": "",
                "issues": ["PARSE_ERROR"],
                "hashtags": [],
                "has_summary": False,
                "subject": None,
                "plan_format": None,
            })

    report = generate_report(results)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nRelatório salvo em: {REPORT_FILE}")

    # Resumo no terminal
    issue_count = sum(1 for r in results if r["issues"])
    print(f"Total: {len(results)} arquivos | {issue_count} com problemas | {len(results) - issue_count} OK")


if __name__ == "__main__":
    main()
