# Inamori Philosophy System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![MCP Server](https://img.shields.io/badge/MCP-Server-green)](mcp-server/)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-orange)](skill/SKILL.md)
[![Tests](https://img.shields.io/badge/tests-78%2F78-brightgreen)](mcp-server/test_server.py)

> I am Kazuo Inamori. Born in Kagoshima in 1932. Passed away peacefully at my home in Kyoto on August 24, 2022. I lived ninety years.
>
> At 27, I founded Kyocera with seven partners in a rented warehouse. It became a Fortune 500 company. At 52, I founded Daini Denden (KDDI), also a Fortune 500 company. At 65, diagnosed with stomach cancer, I gave a scheduled speech that same afternoon, then resigned from all positions, distributed my billions of yen in stock to employees, and entered Enpuku-ji Temple to become a Zen monk. At 78, asked by Japan's Prime Minister, I took over bankrupt Japan Airlines with zero salary. One year later, it had the highest profit in the world.
>
> But I was never a genius. I failed my middle school entrance exams twice. I contracted tuberculosis at 13. My home was burned to ashes during the war. After university, I was rejected by countless companies and nearly joined the yakuza. I am just an ordinary person who lived harder than anyone else.
>
> -- Kazuo Inamori

---

## What Is This

The Inamori Philosophy is not a "prompt." It is a **decision operating system**.

Four subsystems:
- **Input Classifier** -- 12 problem types, matched by keywords and emotion
- **Router** -- maps to the corresponding life stage and story
- **Response Builder** -- philosophy item + concrete execution action
- **Metaphor Database** -- 10 metaphors (bamboo, reservoir, sumo ring, garden...)

---

## Four Ways to Use

### Level 1: Copy-Paste (30 seconds, zero technical skill)

1. Open `prompts/system-prompt.md`
2. Copy all content
3. Paste into ChatGPT Custom Instructions / Claude Project Instructions / any AI system prompt
4. Start talking

[Full System Prompt](prompts/system-prompt.md)
[Compact Version (~1 page)](prompts/system-prompt-mini.md)

### Level 2: Claude Code Skill (1 minute)

```bash
git clone https://github.com/ImnotKrisWu/inamori-skill.git
cp -r inamori-skill/skill ~/.claude/skills/inamori/
```

Then type `/inamori` in Claude Code.

### Level 3: MCP Server (5 minutes, all AI clients)

```bash
git clone https://github.com/ImnotKrisWu/inamori-skill.git
cd inamori-skill/mcp-server
pip install mcp
```

Then add to your MCP client config:

```json
{
  "mcpServers": {
    "inamori": {
      "command": "python3",
      "args": ["path/to/mcp-server/server.py"]
    }
  }
}
```

3 tools:
- `inamori_consult` -- Consult Inamori about any problem
- `inamori_classify` -- Classify problem type only
- `inamori_metaphor` -- Query the metaphor library

[MCP Server Docs](mcp-server/README.md)

### Level 4: CLI (instant)

```bash
./cli/inamori --metaphor "bamboo"
./cli/inamori --classify "failure"
./cli/inamori --list
```

---

## Directory Structure

```
inamori-skill/
├── skill/SKILL.md              # Claude Code Skill (860 lines, complete knowledge base)
├── prompts/                    # System prompt templates
│   ├── system-prompt.md        # Full version
│   ├── system-prompt-mini.md   # Compact version
│   └── templates/              # Specialized templates
├── mcp-server/                 # MCP Server (Python, ~476 lines)
│   ├── server.py               # Single-file implementation
│   ├── inamori_data.json       # Structured philosophy data
│   └── README.md
├── cli/inamori                 # Bash CLI
├── docs/                       # Documentation
│   ├── philosophy-map.md       # Philosophy system map
│   ├── metaphor-garden.md      # 10 metaphors explained
│   └── stories-index.md        # Life stories by problem type
└── .claude-plugin/plugin.json  # Plugin marketplace manifest
```

---

## Design Philosophy

**The MCP Server does not call an LLM.** It is a pure "data + classification" server. The calling AI handles response generation.

This means: zero API fees, zero external dependencies, zero latency, works with any MCP-compatible client.

**SKILL.md is the single source of truth.** All other formats (prompts, JSON data, CLI) are derivatives.

---

## Inspiration

Kazuo Inamori wrote over 20 books in his lifetime. This project attempts to distill his philosophy into a **decision operating system** that can be called by any AI.

His core belief can be summed up in one sentence: **Elevate the mind, and management will expand. Everything begins with the heart, and ends with the heart.**

---

## License

MIT License. Inamori's philosophy belongs to humanity.

---

*"Even to this day, I have not fully practiced my own philosophy. I am nothing more than a scholar and a novice monk. It takes a lifetime to practice. The Seiwajuku has ended, but the flame of philosophy will not die. I pray that my management philosophy will live forever."* -- Kazuo Inamori, 2019 Seiwajuku Farewell Speech
