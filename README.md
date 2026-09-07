# mail-service

用 Python + IMAP 收取 QQ 邮箱邮件的工具：支持列文件夹、按标题过滤、按「未读/已读/全部」读取第 N 封邮件正文，并可用 YAML 配置批量执行任务。

## 1. 快速开始

```bash
copy .env.example .env      # 填入邮箱地址和授权码
python imap_qq_test.py --list-folders      # 先看文件夹列表
python run_tasks.py         # 按 tasks.yml 批量执行
```

依赖：仅标准库 + `pyyaml`（`pip install pyyaml`），Python 3.10+。

## 2. 配置

`.env`（已被 `.gitignore` 忽略，不会提交）：

| 变量 | 说明 | 默认 |
|---|---|---|
| `QQ_MAIL_HOST` | IMAP 服务器 | `imap.qq.com` |
| `QQ_MAIL_PORT` | SSL 端口 | `993` |
| `QQ_MAIL_TIMEOUT` | 超时秒数 | `30` |
| `QQ_MAIL_USER` | 完整邮箱地址 | 必填 |
| `QQ_MAIL_AUTH` | 授权码（非 QQ 密码） | 必填 |

授权码在 QQ 邮箱网页版「设置 → 账户 → IMAP/SMTP 服务」生成。真实环境变量优先级高于 `.env`。

## 3. 文件结构与调用关系

```
imap_qq_test.py      CLI 入口（argparse，单条命令）
run_tasks.py         任务入口（读取 tasks.yml，按数组顺序执行）
tasks.yml            任务配置：动作数组
        │
        ├── config.py           load_settings() → Settings（读 .env）
        │
        ├── mail_client.py      QQMailClient（IMAP 会话）
        │        ├── imap_utf7.py     文件夹名 中文 ⇄ &UXZO1mWHTvZZOQ-
        │        └── email_parser.py  原始字节 → MailMessage
        │
        └── email_parser.py     MailMessage / 正文提取 / HTML→纯文本
```

调用链（以「读第 N 封正文」为例）：

```
read_message(folder, title_contains, nth, read_status, order)
   └─ search()                       # 只取头部，用于匹配
        ├─ resolve_folder()          # 文件夹名 → Folder(raw)，走 imap_utf7_encode
        ├─ _select()                 # IMAP SELECT（readonly=True，不会标记已读）
        ├─ _search_uids()            # UID SEARCH UNSEEN / SEEN / ALL
        └─ _fetch_headers()          # 分块 50 封拉 SUBJECT/FROM/DATE，本地过滤标题
             └─ email_parser.parse_headers()
   └─ fetch(uid)                     # UID FETCH (RFC822) 取整封
        └─ email_parser.parse_message() → MailMessage(.subject/.sender/.date/.body)
```

## 4. 模块 API

### `config.py`

- `load_settings() -> Settings`：`Settings(host, port, timeout, username, auth_code)`
- `load_env_file(path)`：内置零依赖 `.env` 解析（装了 python-dotenv 会自动优先用它）

### `mail_client.py` — `QQMailClient`

支持 `with` 语法，退出时自动关闭连接：

```python
from config import load_settings
from mail_client import QQMailClient

with QQMailClient(load_settings()) as client:
    ...
```

| 方法 | 说明 |
|---|---|
| `list_folders(refresh=False) -> list[Folder]` | 列文件夹，结果缓存；`Folder.raw` 是服务器原名，`Folder.name` 是可读名 |
| `resolve_folder(name) -> Folder` | 支持 `INBOX`、完整路径 `其他文件夹/楽天証券`、末级名 `楽天証券`、中文别名 `收件箱` |
| `search(folder, read_status, title_contains, order, limit) -> list[MailSummary]` | 只拉头部，返回摘要列表 |
| `fetch(folder, uid) -> MailMessage` | 按 UID 取整封并解析 |
| `read_message(folder, title_contains, nth, read_status, order) -> MailMessage \| None` | **核心**：第 N 封邮件的正文 |
| `message_count(folder) -> (总数, 未读数)` | 用于目录列表 |

参数取值：

- `read_status`：`unread` 未读（默认）、`read` 已读、`all` 全部
- `order`：`newest` 最新在前（默认，`nth=1` 即最新一封）、`oldest` 最早在前
- `title_contains`：标题子串，忽略大小写；`None` 不过滤

### `email_parser.py`

- `parse_message(raw_bytes, uid) -> MailMessage`
- `MailMessage` 字段：`uid / subject / sender / to / date / body_text / body_html`
- `MailMessage.body`：优先纯文本，没有正文时把 HTML 转成纯文本
- `html_to_text(html)`、`decode_mime_header(value)`（解 `=?utf-8?B?...?=`）

### `imap_utf7.py`

- `imap_utf7_decode(name)`：`&UXZO1mWHTvZZOQ-` → `已发送`
- `imap_utf7_encode(text)`：`已发送` → `&UXZO1mWHTvZZOQ-`（按中文名选文件夹时要用）

## 5. 命令行用法

```bash
python imap_qq_test.py --list-folders                      # 列出文件夹
python imap_qq_test.py INBOX                               # 最新 1 封未读正文
python imap_qq_test.py "楽天証券" -t "約定" -n 1           # 标题含「約定」的最新未读
python imap_qq_test.py INBOX --status read  -n 1           # 已读邮件里最新 1 封
python imap_qq_test.py INBOX --status all   -n 2 --order oldest   # 全部邮件第 2 封(从旧到新)
python imap_qq_test.py INBOX -t "验证码" --list-matches    # 只列摘要，不下载正文
```

参数：`folder`、`-t/--title`、`-n/--nth`、`--status {unread,read,all}`、`--all`（等价 `--status all`）、`--order {newest,oldest}`、`--list-folders`、`--list-matches`、`--limit`。

找不到邮件时打印提示并返回退出码 `1`。

## 6. 任务模式（YAML）

`tasks.yml` 是一个数组，按顺序执行；`run_tasks.py` 读取它：

```bash
python run_tasks.py                    # 默认 tasks.yml
python run_tasks.py my_tasks.yml       # 指定配置
python run_tasks.py --stop-on-error    # 失败即停
```

三种动作：

```yaml
- action: read            # 读取某一封正文
  name: 读取收件箱最新 1 封未读
  folder: INBOX
  read_status: unread     # unread / read / all
  nth: 1
  order: newest
  # title_contains: 約定   # 可选
  # max_body_chars: 600    # 可选，正文截断

- action: list_matches    # 列出命中摘要
  name: 列出楽天証券最近 5 封
  folder: 其他文件夹/楽天証券
  read_status: all
  order: newest
  limit: 5

- action: list_folders    # 列出所有文件夹
  name: 列出所有文件夹
```

`read` 与 `list_matches` 必填 `folder`；其他字段都有默认值。单个任务出错会打印 `[失败]` 并继续下一个，最后汇总失败数。

任意任务加 `ignore: true` 即可跳过（临时停用，不必删除该条）：

```yaml
- action: list_matches
  name: 列出amazon 3封
  ignore: true          # 跳过本条
  folder: 其他文件夹/amazon
  limit: 3
```

跳过的任务会打印 `[跳过]`，结束时汇总「执行 N 个，跳过 N 个，失败 N 个」。

### 6.1 actions：把任务输出交给脚本处理

任意任务都可以挂 `actions`，任务执行完后，它的**输出文本会通过 stdin 传给脚本**，脚本打印到 stdout 的结果会接在后面：

```yaml
- action: read
  name: 読取楽天証券 投信基準価額メール
  folder: 其他文件夹/楽天証券
  title_contains: 投信基準価額メール
  read_status: all
  nth: 1
  actions:
    - actions/rakuten-sec-action.py
```

约定：

- 脚本从 `stdin` 读文本，结果打印到 `stdout`；退出码非 0 记为失败。
- **多个脚本串联**：上一个脚本的输出作为下一个脚本的输入（统计 → 朗读）。
- 路径相对**配置文件所在目录**（写绝对路径也行）。
- 挂了 `actions` 的任务**默认不打印邮件正文**（只作为中间数据传给脚本），控制台只显示
  `（任务输出 N 字已传给 action，未在控制台打印）` 和脚本结果。
  想看原文加 `quiet: false`；想让没挂 actions 的任务也不打印，加 `quiet: true`。
- 脚本可用任意语言，只要能被 `python <脚本>` 执行；Python 脚本也可以单独用：

```bash
python imap_qq_test.py "楽天証券" -t "投信基準価額" --all -n 1 | python actions/rakuten-sec-action.py
python actions/rakuten-sec-action.py mail.txt
```

### 内置 action：`actions/rakuten-sec-action.py`

解析楽天証券「投信基準価額メール」，统计今日盈亏。**默认不需要任何配置**：直接把各基金的「前営業日比額」求和，得出今日盈亏：

```
基准日 09月04日｜今日盈亏（各基金1万口换算合计）：-823円（-0.29%）⇒ 亏损
```

只输出这一行结论（含基准日、盈亏金额、涨跌幅、盈利/亏损/持平），不打印明细表格。

若想按实际持有份额计算，在脚本顶部 `HOLDINGS` 填持有口数（基准价是每 **1 万口**的价格，所以 `10.5` = 105,000 口；基金名支持部分匹配），会额外多输出一行按持仓的盈亏：

```python
HOLDINGS = {
    "eMAXIS Slim 米国株式（S&P500）": 10,
    "eMAXIS Slim 国内株式（TOPIX）": 5,
}
```

此时输出两行：

```
基准日 09月04日｜今日盈亏（各基金1万口换算合计）：-823円（-0.29%）⇒ 亏损
按持仓合计：市值 607,300円，盈亏 -3,825円（-0.63%）
```

未填口数的基金不计入持仓合计，会单独列在第三行提示。

### 内置 action：`actions/xiaoai-voice-action.py`（通用）

**通用播报器**：把 stdin 里的文本交给 Home Assistant 让小爱音箱朗读。它**不做任何业务相关的文本改写**，只做通用清洗（去多余空白、按长度截断）后发送。

需要针对某类邮件做口语化时，在它前面串一个预处理脚本：

```yaml
  actions:
    - actions/rakuten-sec-action.py   # 输出「今日盈亏」原始结论
    - actions/rakuten-sec-speech.py   # 转成口语化文本（乐天专用，可换）
    - actions/xiaoai-voice-action.py  # 通用朗读：文本 -> HA
```

`.env` 配置：

| 变量 | 说明 |
|---|---|
| `HA_URL` | HA 地址，如 `http://192.168.1.117:8123` |
| `HA_TOKEN` | 长期访问令牌（HA 个人资料页最下方创建） |
| `HA_XIAOAI_ENTITY_ID` | 小爱音箱实体，如 `text.xiaomi_l05b_13c7_play_text`（小米官方集成的「播放文本」，走 `text/set_value`）；填 `media_player.xxx` 则改用 `tts/speak` |
| `HA_TTS_ENTITY` | 用 `media_player` 方式时的 tts 实体 |
| `HA_MAX_CHARS` | 朗读文本最大长度，默认 255 |
| `HA_DRY_RUN=1` | 调试用：只打印将要发送的内容，不真正调用 |

单独使用：

```bash
echo "今天天气不错" | python actions/xiaoai-voice-action.py
HA_DRY_RUN=1 python actions/xiaoai-voice-action.py message.txt
```

仅用标准库 `urllib`，无需 `requests`。

### 内置 action：`actions/rakuten-sec-speech.py`（乐天专用预处理）

只做文本转换（stdin → stdout），把盈亏结论改成适合朗读的中文，不涉及 HA：

```
输入：基准日 09月04日｜今日盈亏（各基金1万口换算合计）：-823円（-0.29%）⇒ 亏损
输出：基准日 09月04日，今日盈亏，各基金1万口换算合计，负823日元，负0.29%，亏损
```

规则：`-/+` → `负/正`、`円` → `日元`、`｜（）：⇒` → 逗号停顿、合并重复逗号、超 255 字截断。

想播报别的内容（如 amazon 到货通知），照这个样子写一个自己的 `xxx-speech.py` 插在通用朗读前面即可，朗读脚本不用改。

## 7. 已知注意点

- **不按 UID 判断新旧**：移动过文件夹的邮件 UID 保留原值，与时间不一致。排序统一按邮件 `Date` 头。
- **标题过滤在本地做**：QQ 的 IMAP SEARCH 对非 ASCII 关键字支持不佳，所以先取 UID 再分块拉头部过滤。
- **只读打开**：所有 `SELECT` 都是 `readonly=True`，读取不会把邮件标记为已读。
- **文件夹命名**：`INBOX` / `Sent Messages` / `Drafts` / `Deleted Messages` / `Junk` 是系统文件夹（收件箱/已发送/草稿箱/已删除/垃圾箱），自建文件夹都在 `其他文件夹/` 下。
