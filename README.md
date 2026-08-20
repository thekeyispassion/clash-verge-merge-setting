# Clash Verge 规则编写与使用教程

> 配套文件：`ClashVerge-国内直连规则-Merge片段.yaml`（可直接粘贴使用的规则片段）
> 本文教你自己写规则：怎么强制直连、强制代理、屏蔽广告，以及怎么导入 Clash Verge 生效。

---

## ⚡ 维护速查（平时只需记这 5 件事）

**1. 加一个网站（强制直连）**
打开规则文件 → 复制任意一行 → 把域名换成新的，粘贴到对应分类下：

```yaml
  - DOMAIN-SUFFIX,新网站.com,DIRECT
```

**2. 想让某站走代理**
把该行结尾的 `DIRECT` 改成 `PROXY`；想完全恢复订阅默认行为，直接删掉那一行。

**3. 判断要不要写（省事口诀）**
`.cn` 域名不用写（兜底自动直连）；非 `.cn` 但国内能直连 → 才加一行。
拿不准就按下面的判断图走：

```
新网站
  ├─ 被墙的站？（Google/YouTube/X/Telegram/OpenAI/Discord/Wikipedia…）
  │     └─ 是 → 不用写（订阅已让它走代理，直连反而打不开）
  │
  ├─ 域名以 .cn 结尾？（含 .com.cn / .edu.cn / .net.cn）
  │     └─ 是 → 不用写（末尾兜底自动直连）
  │
  ├─ 是国内服务/公司？（秀米 xiumi.us、剪映 jianying.com、B站图床 hdslb.com…）
  │     └─ 是 → 写一行 DOMAIN-SUFFIX,域名,DIRECT
  │
  ├─ 是国外服务，但国内直连能访问且不算慢？（GitHub/Kaggle/Codeforces…）
  │     └─ 是 → 写一行 DOMAIN-SUFFIX,域名,DIRECT
  │
  └─ 其他 / 不确定
        └─ 不用写，保持订阅默认
           （若某个站直连太慢、想让订阅里没写到的站强制代理，
            再补一行 DOMAIN-SUFFIX,域名,PROXY）
```

**4. 改完必须「重新订阅」才生效**（不用重启软件）

**5. 想全部撤销**
清空 Merge 编辑器内容 → 重新订阅即可，订阅本身不受影响。

> 语法最常见的两个错误：缩进必须是**两个空格**、逗号后面**不能有空格**。

---

## 一、核心概念：为什么用 Merge 扩展

你的机场订阅自带一套规则（订阅里已写好哪个站走代理、哪个站直连），**这套规则不能直接改**。

Clash Verge 的 **Merge（合并）扩展** 可以把自己的规则**插进订阅规则的前面或后面**：

- `prepend-rules:` —— 插到**最前面**，优先级最高（你写的规则最先被匹配）
- `append-rules:` —— 插到**最后面**，优先级最低（订阅规则都匹配不上才轮到它）

判断规则时**从上往下逐条匹配，命中一条就立即生效，不再继续往后查**。
所以「强制」= 把规则放进 `prepend-rules`，让它在订阅规则之前被命中。

---

## 二、规则语法速查

每行规则格式统一：

```
- 规则类型,匹配内容,动作
```

### 规则类型（匹配方式）

| 类型 | 写法示例 | 含义 |
|---|---|---|
| `DOMAIN-SUFFIX` | `- DOMAIN-SUFFIX,bilibili.com,DIRECT` | 匹配该域名**及其所有子域名**（最常用） |
| `DOMAIN` | `- DOMAIN,exact.com,DIRECT` | **只匹配这一个域名**，不含子域名 |
| `DOMAIN-KEYWORD` | `- DOMAIN-KEYWORD,google,DIRECT` | 域名**包含**关键词即匹配 |
| `IP-CIDR` | `- IP-CIDR,1.2.3.0/24,DIRECT,no-resolve` | 按 IP 网段匹配 |
| `GEOIP` | `- GEOIP,CN,DIRECT,no-resolve` | 按 IP 归属地匹配（需要 geoip 数据库） |
| `GEOSITE` | `- GEOSITE,cn,DIRECT` | 按「域名分类库」匹配（需要 geosite 数据库，见第七节） |
| `PROCESS-NAME` | `- PROCESS-NAME,WeChat.exe,DIRECT` | 按**进程名**匹配（Windows 生效，整机级强制） |
| `MATCH` | `- MATCH,DIRECT` | 兜底：匹配一切没被上面命中的流量 |

> `no-resolve` 表示不主动触发 DNS 解析，查 IP 时直接看已有解析结果，性能更好。

### 动作（规则命中后怎么处理）

| 动作 | 含义 |
|---|---|
| `DIRECT` | 直连（不走代理） |
| `PROXY` | 走代理（默认代理组，一般就是机场的「节点选择」） |
| `REJECT` | 拒绝连接（用于屏蔽广告、跟踪域名） |
| `你自己的代理组名` | 指定走某个分组，如 `- DOMAIN-SUFFIX,xxx.com,🚀 节点选择` |

> 注意：`PROXY` 是通用写法，实际你的订阅里代理组可能叫别的名字（如「自动选择」「香港节点」）。
> 想精确指定时，把 `PROXY` 换成订阅配置里的 group 名称即可；一般用 `PROXY` 就够了。

---

## 三、怎么写「强制直连」

**场景**：某个国内网站被订阅规则错误地送进了代理，或者你想让某个国外站不走代理。

**写法**：在 `prepend-rules:` 里加一行：

```yaml
prepend-rules:
  - DOMAIN-SUFFIX,example.com,DIRECT    # 该域名及所有子域名强制直连
```

**原则**：
1. 国内站（.cn / .com.cn / 国内公司的 .com）→ 直连几乎总是更快
2. 国外站（GitHub、Microsoft、Apple、Kaggle 等）没有被墙但走代理慢 → 也可以直连
3. **被墙的站（Google、YouTube、Telegram、X、OpenAI 等）绝不能强制直连**，否则直接打不开

**省事技巧**：想加新网站时，复制现成的一行，改掉域名就行：

```yaml
  - DOMAIN-SUFFIX,xxx.com,DIRECT
```

---

## 四、怎么写「强制代理」

**场景**：某个域名被订阅规则直连了，但直连很慢/打不开，你想强制它走代理。

**写法**（同样放 `prepend-rules`，规则会优先于订阅命中）：

```yaml
prepend-rules:
  - DOMAIN-SUFFIX,example.com,PROXY     # 强制走代理
  - PROCESS-NAME,SomeApp.exe,PROXY      # 某个程序整机强制走代理
```

**进阶：一行代理一整类网站**（推荐！）

订阅依赖的 geosite 数据库自带大量分类，一个分类往往包含几十上百个域名，一行顶几十行：

```yaml
  - GEOSITE,google,PROXY      # Google 全家桶（搜索/邮箱/相册等）
  - GEOSITE,openai,PROXY      # OpenAI 全家桶（ChatGPT、API 全走代理）
  - GEOSITE,telegram,PROXY    # Telegram
  - GEOSITE,twitter,PROXY     # X / Twitter
  - GEOSITE,youtube,PROXY     # YouTube
  - GEOSITE,netflix,PROXY     # Netflix
  - GEOSITE,anthropic,PROXY   # Claude / Anthropic（若你要用 API）
```

> GEOSITE 分类名取决于 geosite 数据库版本（Clash Verge 默认自带），常用分类见第七节。
> 注意：GEOSITE 匹配的是域名分类，GEOIP 匹配的是 IP 归属，两者互补。

---

## 五、怎么写「屏蔽广告 / 恶意域名」

```yaml
prepend-rules:
  - DOMAIN-SUFFIX,ads.example.com,REJECT     # 屏蔽广告域名
  - DOMAIN-KEYWORD,adservice,REJECT          # 域名含 adservice 的屏蔽
```

REJECT 会直接断开连接，适合广告、统计、挖矿等域名。注意别误伤正常服务。

---

## 六、优先级与执行顺序（重要！）

```
流量 → prepend-rules（你的规则，自上而下）
     → 订阅自带规则（自上而下）
     → 订阅自带兜底（一般是 MATCH,PROXY 或 MATCH,DIRECT）
```

**三条铁律**：

1. **别把 `MATCH` 写进 prepend-rules** —— 它会匹配一切流量，后面的订阅规则全部作废，等于整机被劫持。
2. **兜底规则放在最前是安全的**：本文件里的 `GEOIP,CN,DIRECT` 只匹配中国 IP 的流量，`GEOSITE,cn` 只匹配国内域名分类，不会截胡 Google/YouTube 这类海外流量，所以它们放在最前面也没问题。
3. **规则顺序有讲究**：具体域名规则（DOMAIN-SUFFIX）应该排在泛规则（GEOIP/GEOSITE）**前面**，因为 DOMAIN-SUFFIX 更精确，先命中先结算，逻辑更清晰。

### 兜底三件套：一行顶千行的原理与边界

本文件末尾三行是自动兜底：

```yaml
- DOMAIN-SUFFIX,cn,DIRECT        # 所有 .cn 结尾的域名
- GEOSITE,cn,DIRECT              # geosite 数据库里的「国内站点」分类（几千个域名）
- GEOIP,CN,DIRECT,no-resolve     # 解析出的 IP 属于中国
```

- **GEOSITE** = 按域名查分类库：`cn` 分类收录了几千个国内常用域名，一行顶手写几百行
- **GEOIP** = 按 IP 查归属库：目标 IP 是中国 IP 就直连，**不管域名是什么**，连新站/小众站都能兜住
- **no-resolve** = 只有已解析出 IP 的请求才参与判断，不主动发起 DNS 查询（性能优化，也避免误解析）

**那为什么还要手动维护列表？** 因为兜底有覆盖不到的盲区：

| 情况 | 例子 | 兜底能处理吗 |
|---|---|---|
| .cn / .com.cn 域名 | 学校、政务、银行、洛谷 | ✅ DOMAIN-SUFFIX,cn 和 GEOSITE 都行 |
| 国内公司用海外域名 | 秀米 xiumi.us、小宇宙 xiaoyuzhoufm.com、B站图床 hdslb.com | ❌ 不在 cn 分类，必须手动加 |
| 未被墙的国际服务 | GitHub、Kaggle、HuggingFace、Codeforces | ❌ 分类库不含，手动加才直连 |
| 新上线/小众的国内站 | 刚火的 AI 站 | ⚠️ 分类库更新有滞后，手动加最稳 |

所以正确姿势是「**漏斗**」：精确的 DOMAIN-SUFFIX 在前（覆盖特殊域名 + 国际可直连服务），GEOSITE / GEOIP 兜底在后（自动吃掉没写到的国内流量）。

**省事技巧**：新网站先想一句「域名是 .cn 吗」——是 → 不用写，兜底自动直连；不是 → 判断能直连再手动加一行。

---

## 七、GEOSITE 常用分类参考

（以下分类在主流 geosite 数据库中都存在；写前可在 Clash Verge 的 geosite 文件里确认）

| 分类 | 覆盖内容 | 典型用途 |
|---|---|---|
| `cn` | 国内常用网站（几千条） | 一行直连所有国内站 |
| `google` | Google 全部服务 | 强制代理 |
| `openai` | ChatGPT、OpenAI API | 强制代理 |
| `anthropic` | Claude / Anthropic | 强制代理 |
| `telegram` | Telegram 全部 | 强制代理 |
| `twitter` | X / Twitter | 强制代理 |
| `youtube` | YouTube | 强制代理 |
| `facebook` / `instagram` | Meta 系 | 强制代理 |
| `netflix` / `disney` / `primevideo` | 流媒体 | 强制代理 |
| `github` | GitHub 全家桶 | 直连或代理均可 |
| `microsoft` / `apple` | 微软 / 苹果全家桶 | 直连 |
| `steam` / `epicgames` | 游戏平台 | 直连（商店部分） |
| `paypal` / `amazon` | 支付 / 电商 | 按需 |

---

## 八、Clash Verge 导入与使用教程

### 第 1 步：安装

- 下载 Clash Verge Rev（社区维护版）：GitHub 搜 `clash-verge-rev`，Windows 装 `.exe` 安装包
- 安装后打开，Windows 需要管理员权限才能使用 TUN 模式（可选）

### 第 2 步：导入机场订阅

1. 主界面 → **订阅** → 右上角「新建」
2. 粘贴机场给你的订阅链接 → 输入名称 → 保存
3. 点击「重新订阅」拉取最新配置

### 第 3 步：打开 Merge 扩展（关键）

任选一种方式：

- **方式 A（推荐）**：订阅列表 → 点击你的订阅右侧下拉 → **编辑文件 → Merge**
- **方式 B**：主界面右上「设置」→ 找到「全局扩展」→ 打开 **Merge**

### 第 4 步：粘贴规则

把 `ClashVerge-国内直连规则-Merge片段.yaml` 里从 `prepend-rules:` 开始的内容全部粘贴进去，`Ctrl+S` 保存。

### 第 5 步：重新订阅使规则生效

回到订阅列表 → 点击「重新订阅」（或设置里「应用」）。
**以后每次改规则，重新订阅一次即可生效，无需重启软件。**

### 第 6 步：验证是否生效

1. 打开一个国内网站（如 bilibili.com）
2. 查看主界面「连接」面板（或日志），找到该请求
3. 看它的路由是 `DIRECT`（直连）还是代理 —— 国内站应显示 DIRECT
4. 打开 YouTube 验证代理是否正常 —— 应显示走了代理

---

## 九、常见问题 FAQ

**Q1：规则粘贴后没生效？**
- 检查 YAML 语法：每行必须是 `  - 类型,内容,动作`，缩进为**两个空格**，逗号后不能有空格（`DIRECT` 等动作前后无空格）
- 检查是否点了「重新订阅」
- 检查粘贴的是否在 `prepend-rules:` 下面、并且缩进正确

**Q2：某个网站直连很慢，想改走代理？**
- 在 Merge 里删掉该行 → 重新订阅即可（恢复订阅默认行为）
- 或者把该行动作改成 `PROXY`

**Q3：想强制一个被直连的站走代理？**
- 加一行 `- DOMAIN-SUFFIX,xxx.com,PROXY` 到 prepend-rules 最前

**Q4：GEOIP / GEOSITE 报错？**
- 说明 geoip/geosite 数据库缺失或损坏：Clash Verge → 设置 → 找「Geodata 更新」或「订阅默认 Geodata」，重新下载即可

**Q5：加规则后所有网站都走代理了？**
- 大概率是你在 prepend 里写了 `MATCH,PROXY`，立即删掉

**Q6：Merge 会对多条订阅生效吗？**
- 会。Merge 是全局的，`prepend-rules` 会插到**所有订阅**前面。换订阅也不影响你的规则。

**Q7：怎么恢复默认？**
- 清空 Merge 编辑器内容 → 重新订阅即可，不会影响订阅本身。

**Q8：机场节点全挂，会不会断网？**
- 不会。你的直连规则仍生效，国内流量正常；海外流量因节点全挂才无法访问，这是正常的。

---

## 十、本文件维护建议

1. **新增网站**：在对应分类下复制一行，改域名，重新订阅
2. **删除网站**：删掉对应行，重新订阅（恢复订阅对该域的默认行为）
3. **定期整理**：文件里的注释帮你分类，保持分类整齐即可
4. **检查重复**：同一个域名写两行不会报错，但没必要，保持整洁

---

## 附：本套规则的文件结构

```
prepend-rules:
  ├── 一、国内常用网站/域名（强制 DIRECT）
  │     ├── 通用静态资源 / CDN
  │     ├── 搜索 / 门户
  │     ├── 即时通讯 / 社交
  │     ├── 电商 / 购物 / 生活服务
  │     ├── 视频 / 直播 / 音乐 / 影音
  │     ├── 新闻 / 资讯
  │     ├── 银行 / 支付
  │     ├── 出行 / 物流 / 交通（含新能源车）
  │     ├── 办公 / 云服务 / 开发社区
  │     ├── AI / 大模型（2023-2026 热门）
  │     ├── 教育 / 阅读 / 其他常用
  │     └── 运营商 / 智能硬件
  ├── 二、无需代理即可直连的国际服务
  │     ├── AI 服务（Claude Code / Anthropic）
  │     ├── Microsoft / Apple / GitHub
  │     ├── 学习 / 工具
  │     └── 硬件驱动 / 游戏平台
  └── 三、兜底：.cn 域名 / geosite 国内站点 / 国内 IP 全部直连
```
