# 第一次的人生 · The First Time

[English](README.en.md) · 中文

把每个人都会遇到、却没人教过的「第一次」写成**可检索的说明书**：出行、金钱、办事、医疗、工作、安全。
每条固定三段——**怎么办 / 容易踩什么坑 / 依据哪份官方文件**——并标注证据等级。

> 线上站点：<https://thefirst.easymoreai.com/>
> 离线单文件版：<https://thefirst.easymoreai.com/offline.html>（整本书一个文件，断网、转发都能用）

- **438 条**内容，覆盖 18 个篇章（出行 / 飞机 / 酒店 / 独立生活 / 金钱 / 消费 / 学校 / 求职 / 医疗 / 证件法律 / 驾驶 / 社交 / 恋爱婚姻 / 家庭 / 旅行出国 / 数码 / 餐饮娱乐 / 安全）
- **264 个出处链接**，全部实测可访问；证据分 A（法规与官方文件）/ B（官方科普或权威媒体）/ C（经验性、多家一致）
- **457 个独立 URL**：每条内容一个页面，纯静态预渲染，搜索引擎可直接抓取
- 零外部依赖：系统字体栈、无图片、无 CDN、无第三方脚本

## 目录结构

```
content/            438 条正文（18 个 JSON，唯一的数据源，改内容只动这里）
web/                站点源码：app.css（设计系统）+ app.js（交互）
build.py            生成器：content/ + web/ → docs/
verify.py           质检：结构、覆盖率、跨篇重复、id 唯一、字段完整、出处批量探活
docs/               生成物（GitHub Pages 从这里发布，不要手改）
outline/raw.json    最初的 1028 条标题大纲（内容溯源用）
STYLE.md            内容制作规范（合并规则 / 写作规范 / 取源纪律）
```

## 本地预览

```bash
python3 build.py                 # 生成 docs/
python3 -m http.server -d docs   # 打开 http://localhost:8000
```

直接双击 `docs/index.html` 也能看，只是站内链接需要 http 服务才正常。

## 改内容

所有内容都在 `content/NN-篇名.json` 里，一个条目长这样：

```json
{
  "id": "trip-01",
  "title": "第一次买火车票、改签与退票",
  "merged_from": ["第一次买火车票", "第一次使用 12306", "第一次候补购票"],
  "tags": ["交通", "火车"],
  "cost": { "money": "票价", "time": "10–30 分钟", "willpower": "低" },
  "evidence": "A",
  "body": {
    "plain": "车票实行实名制，在 12306 官网或 APP 买最稳……",
    "steps": ["12306 注册并完成实名核验", "查车次 → 选席别 → 提交订单后按期支付"],
    "pitfalls": ["别把账号密码交给第三方抢票软件"]
  },
  "sources": [
    { "name": "《铁路旅客运输规程》", "url": "https://www.gov.cn/…", "note": "第五章：改签与退票" }
  ]
}
```

改完两个命令收尾：

```bash
python3 verify.py --fields --cross --urls   # 质检：结构 / id 唯一 / 覆盖率 / 重复 / 出处是否都能打开
python3 build.py --cname 你的域名            # 重新生成 docs/
```

字段含义、合并规则、写作纪律见 **[STYLE.md](STYLE.md)**；想加条目请先读 **[CONTRIBUTING.md](CONTRIBUTING.md)**。

## 部署

### 部署在自己的域名（根路径）

GitHub Pages 设置：**Settings → Pages → Source: Deploy from a branch → main / docs**，
然后在 DNS 加一条 CNAME 指向 `<你的用户名>.github.io`，并在 `build.py` 里把 `--url` 和 `--cname` 换成你的域名：

```bash
python3 build.py --cname thefirst.example.com --url https://thefirst.example.com
```

### 部署成项目站（子路径 `https://user.github.io/repo/`）

子路径部署必须带上 `--base`，否则站内链接会指到别人的域名根目录：

```bash
python3 build.py --base /repo/ --url https://user.github.io/repo
```

### 任意静态托管

`docs/` 是纯静态目录，丢给 Vercel、Cloudflare Pages、Netlify、对象存储、nginx 都能跑。

## 内容纪律（重要）

1. **每条必须有出处**，且出处是**真的打开过**的官方页面（gov.cn、部委、法院、省级政府、国家标准优先）。
2. 官方页面抓不到（JS 渲染 / 反爬）时，改用同级官方转载页，并在 `note` 里写明转载方与核对到的关键词。
3. **不编数字、不编链接**。拿不准的手续费、时限一律写「以官方页面为准」并给出官方页。
4. 只写「流程怎么办、依据是什么」，**不写医疗诊断、投资建议与法律意见**。

## 许可

- **代码**（`build.py`、`verify.py`、`web/`、`.github/`）：[MIT](LICENSE)
- **内容**（`content/`、`outline/`、`docs/` 中的正文）：[CC BY 4.0](LICENSE-CONTENT)，署名即可自由使用与改编

站点形式参考开源项目 [高性价比人生指南 HowToLiveBetter](https://github.com/eternity4719/HowToLiveBetter)（CC BY 4.0），页脚已保留署名。

## 免责声明

内容仅供办事参考，具体以官方最新规定为准。本站不构成医疗、法律或投资建议。
