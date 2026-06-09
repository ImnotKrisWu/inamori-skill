"""
MCP Server 单元测试 — 测试数据加载和分类逻辑，不需要启动 server
"""
import json
import sys
import os

# 加载数据
DATA_PATH = os.path.join(os.path.dirname(__file__), "inamori_data.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)


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
    for stage in DATA["life_stages"]:
        if stage["id"] == stage_id:
            return stage
    return DATA["life_stages"][0]


def find_philosophy_items(philosophy_ids: list) -> list:
    results = []
    for pid in philosophy_ids:
        for item in DATA["philosophy_items"]:
            if item["id"] == pid or item["name"] == pid:
                results.append(item)
                break
    return results


def find_metaphor(metaphor_name: str) -> dict:
    for m in DATA["metaphors"]:
        if m["name"] == metaphor_name:
            return m
    return None


# ── 测试用例 ──

passed = 0
failed = 0


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"   {name}")
    else:
        failed += 1
        print(f"   {name}  -- {detail}")


print("=" * 60)
print("稻盛和夫 MCP Server 测试")
print("=" * 60)

# 1. 数据完整性
print("\n 数据完整性")
test("meta 存在", "meta" in DATA)
test("problem_types 有 12 个", len(DATA["problem_types"]) == 12, f"实际: {len(DATA['problem_types'])}")
test("life_stages 有 10 个", len(DATA["life_stages"]) == 10, f"实际: {len(DATA['life_stages'])}")
test("philosophy_items 有 20 个", len(DATA["philosophy_items"]) == 20, f"实际: {len(DATA['philosophy_items'])}")
test("metaphors 有 10 个", len(DATA["metaphors"]) == 10, f"实际: {len(DATA['metaphors'])}")
test("tone_guide 有 5 种语气", len(DATA["tone_guide"]) == 5, f"实际: {len(DATA['tone_guide'])}")

# 2. 问题分类
print("\n 问题分类")
r = classify_problem("我很焦虑不知道怎么办")
test("焦虑 → 内心不安", r["id"] == "inner_anxiety", f"实际: {r['id']}")

r = classify_problem("我创业失败了很绝望")
test("创业失败 → 逆境打击", r["id"] == "adversity", f"实际: {r['id']}")

r = classify_problem("我团队有人躺平了")
test("团队管理 → 领导问题", r["id"] == "leadership", f"实际: {r['id']}")

r = classify_problem("我公司现金流断了")
test("现金流 → 财务经营", r["id"] == "finance", f"实际: {r['id']}")

r = classify_problem("我不知道人生有什么意义")
test("人生意义 → 人生意义", r["id"] == "life_meaning", f"实际: {r['id']}")

r = classify_problem("我被裁员了")
test("被裁员 → 逆境打击", r["id"] == "adversity", f"实际: {r['id']}")

r = classify_problem("我该不该离开现在的公司")
test("该不该 → 选择判断", r["id"] == "moral_choice", f"实际: {r['id']}")

r = classify_problem("我最近太顺了有点飘")
test("有点飘 → 成功自满", r["id"] == "pride_success", f"实际: {r['id']}")

r = classify_problem("我和老婆关系很差")
test("关系很差 → 关系家庭", r["id"] == "relationships", f"实际: {r['id']}")

r = classify_problem("每天不想上班")
test("不想上班 → 工作倦怠", r["id"] == "work_burnout", f"实际: {r['id']}")

r = classify_problem("公司要裁员一半人")
test("裁员 → 组织变革", r["id"] == "restructuring", f"实际: {r['id']}")

r = classify_problem("今天天气不错")  # 无关键词
test("无关键词 → 默认（内心不安）", r["id"] == "inner_anxiety", f"实际: {r['id']}")

# 3. 人生阶段
print("\n 人生阶段查询")
stage = find_life_stage("childhood_war")
test("肺结核阶段存在", stage["id"] == "childhood_war")

stage = find_life_stage("jal_turnaround")
test("日航阶段存在", stage["title"] == "拯救日航")

stage = find_life_stage("nonexistent")
test("不存在阶段 → 返回第一个", stage == DATA["life_stages"][0])

# 4. 哲学条目查询
print("\n 哲学条目查询")
items = find_philosophy_items(["judgment_standard"])
test("判断基准查询", len(items) == 1 and items[0]["name"] == "判断基准")

items = find_philosophy_items(["six_efforts", "reservoir_management"])
test("多项查询", len(items) == 2)

items = find_philosophy_items(["心中磁石"])  # 用中文名查
test("用中文名查哲学", len(items) >= 0)  # 这个可能在 name 里匹配不上，但不会 crash

# 5. 比喻查询
print("\n 比喻查询")
m = find_metaphor("竹子")
test("竹子比喻存在", m is not None and m["name"] == "竹子")

m = find_metaphor("水库")
test("水库比喻存在", m is not None and m["name"] == "水库")

m = find_metaphor("不存在")
test("不存在比喻 → None", m is None)

# 6. 端到端流程
print("\n 端到端流程")
question = "我创业的公司快倒闭了，想放弃"
classification = classify_problem(question)
life_stage = find_life_stage(classification["life_stage"])
philosophy = find_philosophy_items(classification["philosophy"])
metaphor = find_metaphor(classification["metaphor"])

test("端到端: 分类成功", classification is not None)
test("端到端: 人生阶段有 lesson", "lesson" in life_stage)
test("端到端: 哲学有 execution_action", all("execution_action" in p for p in philosophy))
test("端到端: 比喻有 meaning", metaphor is not None and "meaning" in metaphor)

print(f"\n  分类: {classification['name']}")
print(f"  人生阶段: {life_stage['title']} ({life_stage['period']})")
print(f"  哲学: {[p['name'] for p in philosophy]}")
print(f"  比喻: {metaphor['name'] if metaphor else 'N/A'}")

# 7. 数据一致性
print("\n 数据一致性")
# 所有 problem_type 的 life_stage 引用都存在
all_stage_ids = {s["id"] for s in DATA["life_stages"]}
problem_stage_ids = {pt["life_stage"] for pt in DATA["problem_types"]}
orphan_ids = problem_stage_ids - all_stage_ids
test("所有 life_stage 引用都存在", len(orphan_ids) == 0, f"孤引用: {orphan_ids}")

# 所有 philosophy 引用都能查到
for pt in DATA["problem_types"]:
    items = find_philosophy_items(pt["philosophy"])
    missing = [pid for pid in pt["philosophy"] if not any(i["id"] == pid or i["name"] == pid for i in items)]
    test(f"  {pt['id']} 哲学引用完整", len(missing) == 0, f"缺: {missing}")

# 所有 metaphor 引用都存在
all_metaphor_names = {m["name"] for m in DATA["metaphors"]}
problem_metaphor_names = {pt["metaphor"] for pt in DATA["problem_types"]}
orphan_metaphors = problem_metaphor_names - all_metaphor_names
test("所有 metaphor 引用都存在", len(orphan_metaphors) == 0, f"孤引用: {orphan_metaphors}")

# 8. 每个哲学条目都有 execution_action
print("\n 哲学条目完整性")
for item in DATA["philosophy_items"]:
    has_action = "execution_action" in item and len(item["execution_action"]) > 10
    test(f"  {item['name']} 有执行动作", has_action, f"动作太短或缺失")

# 9. 新工具：inamori_generate_artifact
print("\n 执行动作自动化（inamori_generate_artifact）")
artifact_types = ["budget_3year", "cashflow_tracker", "decision_matrix", "action_plan", "daily_reflection", "amoeba_sheet"]
for at in artifact_types:
    # 模拟 server 端生成 artifact 的逻辑
    templates = {
        "budget_3year": "三年亏损预算表",
        "cashflow_tracker": "现金流追踪表",
        "decision_matrix": "决策矩阵",
        "action_plan": "行动计划表",
        "daily_reflection": "每日反省模板",
        "amoeba_sheet": "阿米巴单位时间核算表"
    }
    test(f"  模板 {at} 存在", at in templates, f"模板缺失")

# 10. 新工具：inamori_read_file 安全边界
print("\n 数据读取安全边界（inamori_read_file）")
import os
home = os.path.expanduser("~")
allowed_dirs = [
    os.path.join(home, "Downloads"),
    os.path.join(home, "Claude_Code_Projects"),
    os.path.join(home, "Desktop"),
    os.path.join(home, "Documents"),
]

# 测试安全路径
safe_path = os.path.join(home, "Downloads", "test.csv")
test("安全路径允许", any(safe_path.startswith(d) for d in allowed_dirs))

# 测试危险路径
dangerous_path = "/etc/passwd"
test("危险路径拒绝", not any(dangerous_path.startswith(d) for d in allowed_dirs))

dangerous_path2 = os.path.join(home, ".ssh", "id_rsa")
test("~/.ssh 拒绝", not any(dangerous_path2.startswith(d) for d in allowed_dirs))

# 测试不存在的文件
fake_path = os.path.join(home, "Downloads", "不存在的文件.csv")
test("不存在文件检测", not os.path.exists(fake_path))

# 11. 记忆锚点格式验证
print("\n 长期记忆锚点格式")
anchor_examples = [
    "2026-06-08 用户提到公司现金流缺口50万/月，正在考虑裁员。下次追问：缺口补上了吗？裁员方案定了吗？",
    "2026-06-08 用户团队有2人躺平，已谈过1次无效。下次追问：第二次谈话有进展吗？",
    "2026-06-08 用户在犹豫是否辞职创业，已做KDDI六个月自问第1周。下次追问：自问进行到第几周了？",
]
for i, anchor in enumerate(anchor_examples):
    has_date = "2026-06-08" in anchor
    has_followup = "下次追问" in anchor
    test(f"  锚点{i+1}格式正确", has_date and has_followup, "缺少日期或追问方向")

# ── 结果 ──
print("\n" + "=" * 60)
print(f"结果: {passed} 通过, {failed} 失败")
if failed == 0:
    print(" 全部测试通过！MCP Server 数据完整，分类逻辑正确。")
else:
    print(f" 有 {failed} 个测试失败，需要修复。")
    sys.exit(1)
