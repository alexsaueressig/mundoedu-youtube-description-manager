# Guia de Estilo — Descrições de Vídeos MundoEdu

Este guia define o padrão para todas as descrições de vídeos do canal MundoEdu no YouTube.

---

## Estrutura Padrão

Toda descrição segue esta ordem:

```
---
id: VIDEO_ID
title: "Emoji Tópico (N/M): Subtema - Matéria - ENEM"
url: https://www.youtube.com/watch?v=VIDEO_ID
---

*MundoEdu: O melhor cursinho online agora é 100% gratuito!*

Resumo do conteúdo da videoaula (1-3 frases).

[Bloco de módulo — opcional, para séries]

✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
#ENEM #Matéria #Tópico #Subtópico
```

---

## 1. Frontmatter (YAML)

Sempre incluir os 3 campos obrigatórios:

| Campo   | Formato                  | Exemplo                                             |
| ------- | ------------------------ | --------------------------------------------------- |
| `id`    | ID do YouTube            | `dQw4w9WgXcQ`                                       |
| `title` | Título completo do vídeo | `"🧬 Genética (3/8): Dominância - Biologia - ENEM"` |
| `url`   | URL completa             | `https://www.youtube.com/watch?v=dQw4w9WgXcQ`       |

---

## 2. Tagline

**Sempre** incluir como primeira linha do corpo:

```
*MundoEdu: O melhor cursinho online agora é 100% gratuito!*
```

Deve estar em itálico (entre `*`). Não alterar o texto.

---

## 3. Resumo

Toda descrição deve ter 1-3 frases que expliquem o conteúdo do vídeo. O resumo deve:

- Ser claro e direto
- Mencionar o tópico principal
- Usar linguagem acessível (público ENEM)
- Manter a personalidade do canal (tom leve e engajante)

### Exemplos por tipo de vídeo

**Videoaula de série:**

> Aula 3 de 8 sobre Genética: Ausência de dominância e dominância incompleta. Videoaula de Biologia para o ENEM.

**Videoaula avulsa:**

> Nesta videoaula, o professor Camacho vai falar da famooosa tabela periódica: história, estrutura, organização, simbologia e propriedades.

**Pergunte!:**

> Nesta videoaula, respondemos a pergunta: Qual é a diferença entre a Baixa e a Alta Idade Média?

**Proposta de redação:**

> Proposta de redação sobre doação de sangue no Brasil no estilo ENEM.

**Vídeo especial/institucional:**

> Chegooooooooooou nossa placa dos 100K!! VALEU GALERA!!!

---

## 4. Link do Plano de Estudos

**Formato padronizado** (sem variação):

```
✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
```

Regras:

- Usar sempre o emoji ✨
- Usar `Plano de Estudos:` (com dois-pontos, sem CAPS)
- Nunca duplicar com variações (📜, 🧮, 🌌, etc.)
- **Não** incluir `https://mundoedu.com.br` como link separado quando o plano de estudos já está presente

---

## 5. Bloco de Módulo (Séries)

Para videoaulas que fazem parte de uma série (ex: Genética 1-8), incluir o bloco de módulo completo **antes** do link do plano de estudos:

```
🧬 GENÉTICA - MÓDULO COMPLETO
✔️ Aula 1 - 1ª Lei de Mendel: https://mundoedu.com.br/videoaula/527
✔️ Aula 2 - Cruzamento teste: https://mundoedu.com.br/videoaula/528
✔️ Aula 3 - Ausência de dominância: https://mundoedu.com.br/videoaula/529
...
```

Regras:

- Usar o emoji da matéria no cabeçalho
- Listar TODAS as aulas da série
- Usar ✔️ como marcador
- Manter os links `mundoedu.com.br/videoaula/ID` para cada aula

---

## 6. Hashtags

### Regras

1. **4-5 hashtags** por descrição (ideal)
2. **#ENEM sempre primeiro**
3. **Matéria em segundo** (#Matemática, #Física, etc.)
4. **Tópico em terceiro** (#Genética, #Cinemática, etc.)
5. **Subtópico em quarto** (#SistemaCirculatório, #1ªLeiDeMendel, etc.)
6. **Tags de personalidade são permitidas** (#RUUI, #DaniSensacional, #MundoEdu, etc.)
7. Uma única linha, separadas por espaço

### Matérias reconhecidas

| Matéria             | Hashtag             |
| ------------------- | ------------------- |
| Matemática          | `#Matemática`       |
| Física              | `#Física`           |
| Química             | `#Química`          |
| Biologia            | `#Biologia`         |
| História            | `#História`         |
| Geografia           | `#Geografia`        |
| Filosofia           | `#Filosofia`        |
| Sociologia          | `#Sociologia`       |
| Literatura          | `#Literatura`       |
| Português/Gramática | `#Português`        |
| Redação             | `#Redação`          |
| Artes               | `#Artes`            |
| Atualidades         | `#Atualidades`      |
| Língua Portuguesa   | `#LínguaPortuguesa` |

### Tags especiais (quando aplicável)

| Contexto              | Tag                     |
| --------------------- | ----------------------- |
| Exercícios resolvidos | `#ExercíciosResolvidos` |
| Resumo                | `#Resumo`               |
| Revisão               | `#Revisão`              |
| Proposta de redação   | `#PropostaDeRedação`    |
| Questão resolvida     | `#QuestãoResolvida`     |
| Série "Pergunte!"     | `#Pergunte`             |

### Formato PascalCase

Hashtags compostas usam PascalCase sem espaços:

- ✅ `#AnáliseCombinatória`
- ✅ `#SistemaCirculatório`
- ✅ `#HistóriaDoBrasil`
- ❌ `#analise_combinatoria`
- ❌ `#ANALISE COMBINATORIA`

---

## 7. Exemplo Completo

### Videoaula de série

```markdown
---
id: 61thLTV6U9Y
title: "🧬 Genética (3/8): Ausência de dominância - Biologia - ENEM"
url: https://www.youtube.com/watch?v=61thLTV6U9Y
---

_MundoEdu: O melhor cursinho online agora é 100% gratuito!_

Aula 3 de 8 sobre Genética: Ausência de dominância e dominância incompleta. Videoaula de Biologia para o ENEM.

🧬 GENÉTICA - MÓDULO COMPLETO
✔️ Aula 1 - 1ª Lei de Mendel: https://mundoedu.com.br/videoaula/527
✔️ Aula 2 - Cruzamento teste: https://mundoedu.com.br/videoaula/528
✔️ Aula 3 - Ausência de dominância: https://mundoedu.com.br/videoaula/529
✔️ Aula 4 - Polialelia e 2ª Lei de Mendel: https://mundoedu.com.br/videoaula/530
✔️ Aula 5 - Tipos sanguíneos: https://mundoedu.com.br/videoaula/531
✔️ Aula 6 - Herança ligada ao sexo: https://mundoedu.com.br/videoaula/532
✔️ Aula 7 - Clonagem e CRISPR: https://mundoedu.com.br/videoaula/533
✔️ Aula 8 - Evolução: https://mundoedu.com.br/videoaula/535

✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
#ENEM #Biologia #Genética #AusênciaDominância
```

### Videoaula avulsa

```markdown
---
id: AeV29aGRqSU
title: "👨‍🔬 Tabela Periódica e propriedades - Química - ENEM"
url: https://www.youtube.com/watch?v=AeV29aGRqSU
---

_MundoEdu: O melhor cursinho online agora é 100% gratuito!_

Nesta videoaula, o professor Camacho vai falar da famooosa tabela periódica: história, estrutura, organização, simbologia e propriedades (periódicas e aperiódicas).

✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
#ENEM #Química #TabelaPeriódica #TransformaçõesQuímicas
```

### Vídeo "Pergunte!"

```markdown
---
id: SwmTJxTAud0
title: "Pergunte! - Qual é a diferença entre a Baixa e a Alta Idade Média?"
url: https://www.youtube.com/watch?v=SwmTJxTAud0
---

_MundoEdu: O melhor cursinho online agora é 100% gratuito!_

Nesta videoaula, respondemos a pergunta: Qual é a diferença entre a Baixa e a Alta Idade Média?

✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
#ENEM #História #IdadeMédia #Pergunte #RUUI
```

---

## Scripts de Manutenção

| Script                                    | Função                                       |
| ----------------------------------------- | -------------------------------------------- |
| `python analyze_descriptions.py`          | Analisa todos os arquivos e gera `report.md` |
| `python fix_descriptions.py --dry-run`    | Mostra correções sem aplicar                 |
| `python fix_descriptions.py`              | Aplica todas as correções                    |
| `python fetch_descriptions.py`            | Baixa descrições do YouTube                  |
| `python update_descriptions.py --dry-run` | Preview de push para YouTube                 |
| `python update_descriptions.py`           | Push descrições para YouTube                 |

---

## Checklist para Novas Descrições

- [ ] Frontmatter completo (id, title, url)
- [ ] Tagline MundoEdu na primeira linha
- [ ] Resumo de 1-3 frases sobre o conteúdo
- [ ] Bloco de módulo (se faz parte de uma série)
- [ ] Link `✨ Plano de Estudos:` no formato padrão
- [ ] 4-5 hashtags: #ENEM + matéria + tópico + subtópico
- [ ] Sem URL base `mundoedu.com.br` duplicada
- [ ] Sem linhas em branco excessivas
