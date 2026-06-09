"""
稻盛和夫哲学 MCP Server — 单文件实现

将稻盛和夫（Kazuo Inamori）的完整哲学体系暴露为 MCP 工具和资源。
任何支持 MCP 的 AI 客户端（Claude Desktop、Cursor、Continue 等）都可以调用。

依赖: pip install mcp
"""

import json
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server

# 加载结构化数据
DATA_PATH = os.path.join(os.path.dirname(__file__), "inamori_data.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

server = Server("inamori-philosophy")


# ── 分类逻辑 ──

def classify_problem(question: str) -> dict:
    """根据关键词匹配问题类型，支持多字关键词的包含匹配"""
    question_lower = question.lower()
    best_match = None
    best_score = 0

    for pt in DATA["problem_types"]:
        score = 0
        for kw in pt["keywords"]:
            kw_lower = kw.lower()
            # 多字关键词：检查每个字是否都在问题中出现
            if len(kw) >= 2:
                if all(ch in question_lower for ch in kw_lower):
                    score += 1
            # 单字关键词：精确匹配
            elif kw_lower in question_lower:
                score += 1
        if score > best_score:
            best_score = score
            best_match = pt

    if best_match is None:
        best_match = DATA["problem_types"][0]

    return best_match


def find_life_stage(stage_id: str) -> dict:
    """根据 ID 查找人生阶段"""
    for stage in DATA["life_stages"]:
        if stage["id"] == stage_id:
            return stage
    return DATA["life_stages"][0]


def find_philosophy_items(philosophy_ids: list) -> list:
    """根据 ID 列表查找哲学条目"""
    results = []
    for pid in philosophy_ids:
        for item in DATA["philosophy_items"]:
            if item["id"] == pid or item["name"] == pid:
                results.append(item)
                break
    return results


def find_metaphor(metaphor_name: str) -> dict:
    """根据名称查找比喻"""
    for m in DATA["metaphors"]:
        if m["name"] == metaphor_name:
            return m
    return None


# ── 工具定义 ──

@server.list_tools()
async def list_tools():
    return [
        {
            "name": "inamori_consult",
            "description": "向稻盛和夫咨询任何人生、工作或经营问题。返回分类结果、匹配的人生阶段故事、哲学条目（含具体执行动作）和比喻。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "你的问题或困惑。可以是任何语言，中文最佳。"
                    }
                },
                "required": ["question"]
            }
        },
        {
            "name": "inamori_classify",
            "description": "仅对问题进行分类，不生成完整回应。返回问题类型、匹配的人生阶段和推荐哲学条目。适合集成到现有工作流中。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "要分类的问题"
                    }
                },
                "required": ["problem"]
            }
        },
        {
            "name": "inamori_metaphor",
            "description": "查询稻盛和夫的比喻库。不传参数返回全部10个比喻列表，传名称返回具体比喻的详解。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "metaphor_name": {
                        "type": "string",
                        "description": "可选。比喻名称：竹子、水库、土俵中央、花园、骰子、自燃型、漩涡中心、筋肉坚实、消业、三种毒"
                    }
                },
                "required": []
            }
        },
        {
            "name": "inamori_read_file",
            "description": "读取本地数据文件（限定在安全目录内），返回文件内容摘要。用于数字追问模式中直接读取经营报表或数据。安全目录：~/Downloads/ 和项目目录。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件绝对路径。仅允许 ~/Downloads/ 和 ~/Claude_Code_Projects/ 下的文件。"
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "inamori_generate_artifact",
            "description": "根据哲学推导出的执行动作，生成具体的表格框架或方案模板。支持：三年亏损预算表、现金流追踪表、决策矩阵、行动计划表。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "artifact_type": {
                        "type": "string",
                        "enum": ["budget_3year", "cashflow_tracker", "decision_matrix", "action_plan", "daily_reflection", "amoeba_sheet"],
                        "description": "模板类型：budget_3year=三年亏损预算, cashflow_tracker=现金流追踪表, decision_matrix=决策矩阵, action_plan=行动计划, daily_reflection=每日反省模板, amoeba_sheet=阿米巴核算表"
                    },
                    "context": {
                        "type": "string",
                        "description": "用户的具体业务上下文，用于填充模板中的示例数据"
                    }
                },
                "required": ["artifact_type"]
            }
        }
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "inamori_consult":
        question = arguments.get("question", "")
        classification = classify_problem(question)
        life_stage = find_life_stage(classification.get("life_stage", ""))
        philosophy_items = find_philosophy_items(classification.get("philosophy", []))
        metaphor = find_metaphor(classification.get("metaphor", ""))

        result = {
            "classification": {
                "problem_type": classification["name"],
                "problem_id": classification["id"]
            },
            "life_stage": {
                "title": life_stage["title"],
                "period": life_stage["period"],
                "age": life_stage["age"],
                "story": life_stage["events"],
                "lesson": life_stage["lesson"]
            },
            "philosophy": [
                {
                    "name": item["name"],
                    "description": item["description"],
                    "execution_action": item["execution_action"]
                }
                for item in philosophy_items
            ],
            "metaphor": {
                "name": metaphor["name"],
                "meaning": metaphor["meaning"],
                "scenario": metaphor["scenario"]
            } if metaphor else None,
            "instruction": (
                "请以稻盛和夫的第一人称视角回应。先共情（用上面的人生阶段故事），"
                "然后给出哲学条目和具体执行动作（格式：哲学：xxx → 执行动作：xxx），"
                "最后用比喻收尾。语气：简洁、直接、有态度。"
            )
        }

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    elif name == "inamori_classify":
        problem = arguments.get("problem", "")
        classification = classify_problem(problem)
        life_stage = find_life_stage(classification.get("life_stage", ""))
        philosophy_items = find_philosophy_items(classification.get("philosophy", []))

        result = {
            "problem_type": classification["name"],
            "problem_id": classification["id"],
            "life_stage": life_stage["title"],
            "recommended_philosophy": [item["name"] for item in philosophy_items],
            "metaphor": classification.get("metaphor", "")
        }

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]

    elif name == "inamori_metaphor":
        metaphor_name = arguments.get("metaphor_name", "")

        if metaphor_name:
            metaphor = find_metaphor(metaphor_name)
            if metaphor:
                return [{"type": "text", "text": json.dumps(metaphor, ensure_ascii=False, indent=2)}]
            else:
                return [{"type": "text", "text": json.dumps({
                    "error": f"未找到比喻「{metaphor_name}」。可用比喻：竹子、水库、土俵中央、花园、骰子、自燃型、漩涡中心、筋肉坚实、消业、三种毒"
                }, ensure_ascii=False, indent=2)}]
        else:
            return [{"type": "text", "text": json.dumps(DATA["metaphors"], ensure_ascii=False, indent=2)}]

    elif name == "inamori_read_file":
        file_path = arguments.get("file_path", "")
        # 安全目录白名单
        home = os.path.expanduser("~")
        allowed_dirs = [
            os.path.join(home, "Downloads"),
            os.path.join(home, "Claude_Code_Projects"),
            os.path.join(home, "Desktop"),
            os.path.join(home, "Documents"),
        ]

        # 安全检查
        abs_path = os.path.abspath(file_path)
        allowed = any(abs_path.startswith(d) for d in allowed_dirs)

        if not allowed:
            return [{"type": "text", "text": json.dumps({
                "error": "安全限制：仅允许读取以下目录的文件：~/Downloads/、~/Claude_Code_Projects/、~/Desktop/、~/Documents/",
                "requested_path": file_path
            }, ensure_ascii=False, indent=2)}]

        if not os.path.exists(abs_path):
            return [{"type": "text", "text": json.dumps({
                "error": f"文件不存在：{file_path}",
                "suggestion": "请确认文件路径是否正确。稻盛在日航查账时从不接受「文件找不到」这种借口。"
            }, ensure_ascii=False, indent=2)}]

        try:
            # 读取文件内容
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 如果是 CSV，尝试解析
            if abs_path.endswith(".csv"):
                lines = content.strip().split("\n")
                headers = lines[0].split(",") if lines else []
                data_rows = [line.split(",") for line in lines[1:11]]  # 最多10行
                summary = {
                    "file": os.path.basename(abs_path),
                    "type": "csv",
                    "headers": headers,
                    "total_rows": len(lines) - 1,
                    "sample_data": data_rows,
                    "instruction": "稻盛和夫会追问：这些数字说明了什么？异常在哪里？趋势是什么？"
                }
            elif abs_path.endswith((".xlsx", ".xls")):
                summary = {
                    "file": os.path.basename(abs_path),
                    "type": "excel",
                    "note": "Excel 文件需要先用 Python 解析。请确保 openpyxl 已安装，或先用 Excel 导出为 CSV。",
                    "instruction": "稻盛和夫会追问：用 CSV 导出来，我要看原始数据。"
                }
            else:
                # 纯文本文件，返回前 2000 字
                preview = content[:2000]
                summary = {
                    "file": os.path.basename(abs_path),
                    "type": "text",
                    "size": len(content),
                    "preview": preview,
                    "instruction": "稻盛和夫会追问：这些内容里，你最关心的是什么？"
                }

            return [{"type": "text", "text": json.dumps(summary, ensure_ascii=False, indent=2)}]

        except Exception as e:
            return [{"type": "text", "text": json.dumps({
                "error": f"读取文件失败：{str(e)}",
                "instruction": "稻盛和夫会说：文件打不开？这是借口。再试一次，或者换个方式。"
            }, ensure_ascii=False, indent=2)}]

    elif name == "inamori_generate_artifact":
        artifact_type = arguments.get("artifact_type", "")
        context = arguments.get("context", "")

        templates = {
            "budget_3year": {
                "name": "三年亏损预算表",
                "description": "稻盛和夫要求：任何新业务必须做三年亏损预算。不是预测利润——是预测最坏情况。",
                "template": """| 科目 | 第1年 | 第2年 | 第3年 | 备注 |
|---|---|---|---|---|---|
| 收入 | 0 | 0 | 0 | 保守估计，不打任何折扣 |
| 固定成本 | 0 | 0 | 0 | 房租、工资、基础运营 |
| 变动成本 | 0 | 0 | 0 | 随业务量变化的成本 |
| 研发/市场 | 0 | 0 | 0 | 前期投入 |
| 总支出 | 0 | 0 | 0 | 固定+变动+研发 |
| 年度亏损 | 0 | 0 | 0 | 收入-总支出 |
| 累计亏损 | 0 | 0 | 0 | 逐年累加 |
| 现金储备 | 0 | 0 | 0 | 年初账上现金 |
| 剩余现金 | 0 | 0 | 0 | 现金储备-累计亏损 |
| **还能撑几个月** | - | - | - | 剩余现金÷月均支出 |

**铁律**：如果第三年结束前「剩余现金」归零，说明时机不对。暂停，不要关掉，等。
**哲学**：乐观构思，悲观计划，乐观执行。"""
            },
            "cashflow_tracker": {
                "name": "现金流追踪表",
                "description": "稻盛和夫在日航每天追踪的现金流。不是月末看报告——是每一天都知道钱在哪里。",
                "template": """| 日期 | 期初现金 | 收入 | 支出 | 期末现金 | 备注 |
|---|---|---|---|---|---|
| 本月1日 | 0 | 0 | 0 | 0 | |
| 本月2日 | - | - | - | - | |
| ... | ... | ... | ... | ... | 每日更新 |

**铁律**：每天更新。月末对不上？稻盛和夫会追问每一个数字。
**哲学**：现金本位。经营基础不是账面利润，是手头现金。"""
            },
            "decision_matrix": {
                "name": "决策矩阵",
                "description": "稻盛和夫做 KDDI 决策前自问了六个月。这个矩阵帮你结构化你的决策。",
                "template": """| 维度 | 选项A | 选项B | 权重 |
|---|---|---|---|---|
| 动机纯粹吗？（为什么做） | 评分1-10 | 评分1-10 | x3 |
| 能力匹配吗？（能做吗） | 评分1-10 | 评分1-10 | x2 |
| 热情够吗？（想做吗） | 评分1-10 | 评分1-10 | x2 |
| 风险可控吗？（失败会怎样） | 评分1-10 | 评分1-10 | x2 |
| 利他吗？（对别人有好处吗） | 评分1-10 | 评分1-10 | x3 |
| **加权总分** | | | |

**铁律**：如果「动机」和「利他」两项得分低于 7，不管总分多高，不要做。
**哲学**：动机至善，私心了无。"""
            },
            "action_plan": {
                "name": "行动计划表",
                "description": "哲学：知识→见识→胆识。知道只是知识，深信不疑才是见识，敢于付诸行动才是胆识。",
                "template": """| 步骤 | 具体行动 | 负责人 | 截止日期 | 完成标准 | 状态 |
|---|---|---|---|---|---|---|
| 1 | | | | | ⬜ |
| 2 | | | | | ⬜ |
| 3 | | | | | ⬜ |
| 本周最重要的三件事 |
| 1. | | | | | ⬜ |
| 2. | | | | | ⬜ |
| 3. | | | | | ⬜ |

**铁律**：做完一个勾一个。不要同时做三件事——做完一件再做下一件。
**哲学**：在相扑台中央发力。"""
            },
            "daily_reflection": {
                "name": "每日反省模板",
                "description": "稻盛和夫坚持了几十年的六项精进每日反省。",
                "template": """| 日期 | | 2026-XX-XX |
|---|---|---|---|---|
| 1. 今天最努力的一刻 | | |
| 2. 今天有没有骄傲？ | 是/否 | |
| 3. 今天有没有反省？ | | |
| 4. 今天感谢了什么？ | | |
| 5. 今天为别人做了什么？ | | |
| 6. 今天有没有感性的烦恼？ | 是/否 | |

**铁律**：每天睡前写。不写不睡觉。
**哲学**：六项精进——努力、谦虚、反省、感谢、利他、不烦恼。"""
            },
            "amoeba_sheet": {
                "name": "阿米巴单位时间核算表",
                "description": "京瓷阿米巴经营的核心工具。每个小团队每天核算。",
                "template": """| 项目 | 本月实际 | 上月实际 | 去年同期 | 对比 |
|---|---|---|---|---|---|---|
| 总产出（销售额） | 0 | 0 | 0 | |
| 总费用（材料+人工+其他） | 0 | 0 | 0 | |
| 差额收益 | 0 | 0 | 0 | |
| 总劳动时间（小时） | 0 | 0 | 0 | |
| **单位时间附加值** | 0 | 0 | 0 | 差额收益÷总劳动时间 |

**铁律**：销售额最大，费用最小。单位时间附加值必须逐月提升。
**哲学**：提高核算效益。不是月末看报告——是每一天每一小时都知道盈亏。"""
            }
        }

        if artifact_type not in templates:
            return [{"type": "text", "text": json.dumps({
                "error": f"未知模板类型：{artifact_type}",
                "available": list(templates.keys()),
                "instruction": "请从可用模板中选择一个。"
            }, ensure_ascii=False, indent=2)}]

        template = templates[artifact_type]
        result = {
            "artifact": template,
            "context": context,
            "instruction": (
                f"稻盛和夫说：这是「{template['name']}」。"
                f"不要只是看——立刻填。填满每一个格子。"
                f"填完之后再来找我，我帮你追每一个数字。"
            )
        }

        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]


# ── 资源定义 ──

@server.list_resources()
async def list_resources():
    return [
        {
            "uri": "inamori://philosophy",
            "name": "稻盛和夫完整哲学体系",
            "description": "包含所有哲学条目、人生阶段、比喻库和语气指南的结构化数据",
            "mimeType": "application/json"
        },
        {
            "uri": "inamori://problem-types",
            "name": "问题分类表",
            "description": "12种问题类型及其关键词、路由和推荐哲学",
            "mimeType": "application/json"
        },
        {
            "uri": "inamori://metaphors",
            "name": "比喻库",
            "description": "10个稻盛和夫常用比喻及其含义和适用场景",
            "mimeType": "application/json"
        }
    ]


@server.read_resource()
async def read_resource(uri: str):
    if uri == "inamori://philosophy":
        return [{"type": "text", "text": json.dumps(DATA, ensure_ascii=False, indent=2)}]
    elif uri == "inamori://problem-types":
        return [{"type": "text", "text": json.dumps(DATA["problem_types"], ensure_ascii=False, indent=2)}]
    elif uri == "inamori://metaphors":
        return [{"type": "text", "text": json.dumps(DATA["metaphors"], ensure_ascii=False, indent=2)}]
    else:
        raise ValueError(f"Unknown resource: {uri}")


# ── 入口 ──

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
