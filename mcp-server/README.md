# 稻盛和夫哲学 MCP Server

将稻盛和夫（Kazuo Inamori）的完整哲学体系暴露为 MCP 工具和资源。

## 安装

```bash
# 前置条件：Python 3.10+
pip install mcp
```

## 配置

### Claude Desktop

在 `claude_desktop_config.json` 中添加：

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

### Claude Code

在 `~/.claude/settings.local.json` 中添加：

```json
{
  "mcpServers": {
    "inamori": {
      "command": "python3",
      "args": ["/path/to/mcp-server/server.py"]
    }
  }
}
```

### Cursor / Continue / 其他 MCP 客户端

参照各客户端的 MCP 配置文档，添加此 server 即可。

## 可用工具

| 工具 | 用途 |
|---|---|
| `inamori_consult` | 主入口：向稻盛和夫咨询任何问题 |
| `inamori_classify` | 仅分类问题，返回问题类型和推荐哲学 |
| `inamori_metaphor` | 查询比喻库（竹子、水库、土俵...） |

## 可用资源

| URI | 内容 |
|---|---|
| `inamori://philosophy` | 完整哲学体系 |
| `inamori://problem-types` | 12种问题分类表 |
| `inamori://metaphors` | 10个比喻详解 |

## 设计理念

此 MCP Server **不调用外部 LLM**。它是纯「数据 + 分类」服务器。调用方 AI 负责生成回应。

这意味着：
- 零 API 费用
- 零依赖外部服务
- 零延迟
- 任何支持 MCP 的 AI 客户端都能用
