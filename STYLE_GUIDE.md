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

Toda descrição deve ter 1-2 frases que expliquem o conteúdo do vídeo. O resumo deve:

- Ser casual e direto — sem robotizar
- Mencionar o professor pelo apelido (ver tabela de professores)
- Usar linguagem acessível (público ENEM)
- Ser lowkey engraçado quando possível, sem forçar
- **Nunca** usar o padrão antigo "Aula X de Y sobre Z. Videoaula de W para o ENEM."

### Professores

| Professor       | Matéria(s)                                | Referência no texto    |
| --------------- | ----------------------------------------- | ---------------------- |
| Bussunda        | História                                  | o prof. Bussunda       |
| Camacho         | Química                                   | o prof. Camacho        |
| Gui Valenzuela  | Matemática                                | o prof. Gui Valenzuela |
| Dani Bressan    | Redação, Português, Literatura, Gramática | a profª Dani           |
| Vasco           | Física                                    | o prof. Vasco          |
| Giba            | Geografia                                 | o prof. Giba           |
| JowJow          | Artes                                     | o prof. JowJow         |

### Exemplos por tipo de vídeo

**Videoaula de série:**

> Nesta aula, o prof. Vasco explica transformadores — parte do módulo de magnetismo.

**Videoaula avulsa:**

> Nesta videoaula, o prof. Camacho explica tabela periódica e propriedades.

**Pergunte!:**

> Prof. Bussunda responde: qual é a diferença entre a Baixa e a Alta Idade Média?

**Exercícios:**

> Nesta aula, o prof. Gui Valenzuela resolve exercícios de geometria plana.

**Vídeo especial/institucional:**

> Chegooooooooooou nossa placa dos 100K!! VALEU GALERA!!!

---

## 4. Perguntas SEO

Após o resumo, incluir 2-3 perguntas que os estudantes buscam no Google:

```
👉 O que são transformadores?
👉 Como estudar magnetismo para o ENEM?
```

Regras:

- Usar 👉 como prefixo
- Formular como perguntas reais de busca
- Para "Pergunte!", usar a pergunta do título como SEO
- Para exercícios: "Como resolver exercícios de X?"
- Para "X e Y": "Qual a diferença entre X e Y?"

---

## 5. CTA e Link do Plano de Estudos

**Formato padronizado** (sempre antes do link):

```
Bora estudar de graça? 🚀
✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
```

Regras:

- CTA "Bora estudar de graça? 🚀" **sempre** antes do link
- Usar sempre o emoji ✨ no link
- Usar `Plano de Estudos:` (com dois-pontos, sem CAPS)
- Nunca duplicar com variações (📜, 🧮, 🌌, etc.)
- **Não** incluir `https://mundoedu.com.br` como link separado quando o plano de estudos já está presente

---

## 6. Bloco de Módulo (Séries)

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

## 7. Hashtags

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

## 8. Exemplo Completo

### Videoaula de série

```markdown
---
id: 4gCZ0L2Cnzg
title: "🧲 Magnetismo (2/2): Transformadores - Física - ENEM"
url: https://www.youtube.com/watch?v=4gCZ0L2Cnzg
---

*MundoEdu: O melhor cursinho online agora é 100% gratuito!*

Nesta aula, o prof. Vasco explica transformadores — parte do módulo de magnetismo.

👉 O que são transformadores?
👉 Como estudar magnetismo para o ENEM?

Bora estudar de graça? 🚀
✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
#ENEM #Física #Magnetismo #Transformadores
```

### Videoaula avulsa

```markdown
---
id: BggYghR0eXY
title: "👨‍🔬 Misturas Gasosas - Química - ENEM"
url: https://www.youtube.com/watch?v=BggYghR0eXY
---

*MundoEdu: O melhor cursinho online agora é 100% gratuito!*

Ó o gááás! 🔥
Nesta videoaula, o professor Camacho vai falar sobre bolhas de sabão, mergulhos, jogos da seleção, viagens de balão... e sobre como tudo isso se relaciona com as transformações químicas!

Bora estudar de graça? 🚀
✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
#ENEM #Química #TransformaçõesQuímicas #MisturasGasosas
```

### Vídeo "Pergunte!"

```markdown
---
id: 6SYipWcf7PY
title: "Pergunte! - Qual é a diferença entre pretérito imperfeito e futuro do pretérito?"
url: https://www.youtube.com/watch?v=6SYipWcf7PY
---

*MundoEdu: O melhor cursinho online agora é 100% gratuito!*

Profª Dani responde: qual é a diferença entre pretérito imperfeito e futuro do pretérito?

👉 Qual é a diferença entre pretérito imperfeito e futuro do pretérito?

Bora estudar de graça? 🚀
✨ Plano de Estudos: https://mundoedu.com.br/plano-de-estudos
#ENEM #Sensacional #Pergunte #DaniMaravilha
```

---

## Scripts de Manutenção

| Script                                    | Função                                       |
| ----------------------------------------- | -------------------------------------------- |
| `python analyze_descriptions.py`          | Analisa todos os arquivos e gera `report.md` |
| `python fix_descriptions.py --dry-run`    | Mostra correções estruturais sem aplicar     |
| `python fix_descriptions.py`              | Aplica correções estruturais                 |
| `python improve_descriptions.py --dry-run`| Mostra melhorias de conteúdo sem aplicar     |
| `python improve_descriptions.py`          | Aplica melhorias de conteúdo (SEO + tom)     |
| `python fetch_descriptions.py`            | Baixa descrições do YouTube                  |
| `python update_descriptions.py --dry-run` | Preview de push para YouTube                 |
| `python update_descriptions.py`           | Push descrições para YouTube                 |

---

## Checklist para Novas Descrições

- [ ] Frontmatter completo (id, title, url)
- [ ] Tagline MundoEdu na primeira linha
- [ ] Resumo casual de 1-2 frases com nome do professor
- [ ] 2-3 perguntas SEO com 👉
- [ ] Bloco de módulo (se faz parte de uma série)
- [ ] CTA "Bora estudar de graça? 🚀"
- [ ] Link `✨ Plano de Estudos:` no formato padrão
- [ ] 4-5 hashtags: #ENEM + matéria + tópico + subtópico
- [ ] Sem URL base `mundoedu.com.br` duplicada
- [ ] Sem linhas em branco excessivas
- [ ] Tom casual e direto — não robótico
