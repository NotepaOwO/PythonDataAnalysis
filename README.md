# osu! 数据采集与分析系统技术文档

## 1. 项目背景与目标

本项目基于 **osu! 官方 API v2**，构建一个完整的数据采集、存储与分析框架，目标是：

* 从 osu! 官方接口 **合法、自动化地抓取用户成绩数据**；
* 将原始 JSON 数据 **结构化存入 SQLite 数据库**；
* 支持 **批量抓取（万级用户）与并发加速**；
* 为后续 **数据分析 / 机器学习建模** 提供干净、可复现的数据来源。

本项目非常适合作为：

* Python 数据工程 / 数据分析课程实验
* API 数据采集 + SQL + ML 的综合实践项目

---

## 2. 总体架构

```text
PythonDataAnalysis/
├─ config/
│  └─ api.yaml                    # API 密钥配置（不入库）
├─ data/
│  └─ osu.db                      # SQLite 数据库（运行后生成）
├─ src/
│  ├─ collect/
│  │  ├─ osu_client.py            # osu API 客户端（OAuth2 + 请求）
│  │  └─ fetch_parallel.py        # 并发抓取入口
│  ├─ utils/
│  │  ├─ config_loader.py         # 读取 api.yaml
│  │  ├─ db.py                    # 数据库连接与建表
│  │  ├─ db_writer.py             # 单线程写入数据库   
│  │  └─ logger.py                # 打印日志
│  └─ analysis/
│     ├─ evaluate_model.py        # 评估模型
│     ├─ fearture_engineering.py  # 根据数据构建矩阵
│     ├─ load_dataset.py          # 加载数据库
│     ├─ pred.py                  # 预测pp，给出数据和图表（可视化）
│     ├─ train_model.py           # 训练模型
│     └─ visualize.py             # 数据可视化
├─ requirements.txt
└─ README.md
```

---

## 3. 环境与依赖

### 3.1 requirements.txt

```txt
pyyaml
requests
numpy
pandas
scikit-learn
matplotlib
joblib
```

安装命令：

```bash
pip install -r requirements.txt
```

---

## 4. 配置文件说明（api.yaml）

```yaml
osu:
  client_id: 你的client_id
  client_secret: 你的client_secret
  token_url: https://osu.ppy.sh/oauth/token
  api_base: https://osu.ppy.sh/api/v2
```

说明：

* 使用 **OAuth2 client_credentials 模式**；
* 仅访问 `public` 范围数据；
* `api.yaml` 必须加入 `.gitignore`。

---

## 5. 核心模块说明

---

### 5.1 osu_client.py —— osu API 客户端

**作用**：

* 负责 OAuth2 token 获取与缓存；
* 对外提供统一的 API 调用接口。

#### 接口 1：get_user_scores

```python
get_user_scores(user_id, score_type="best", mode="osu", limit=100)
```

功能：

* 获取指定用户在指定模式下的成绩列表。

参数说明：

| 参数         | 含义                           |
| ---------- | ---------------------------- |
| user_id    | osu 用户 ID                    |
| score_type | best / recent / firsts       |
| mode       | osu / taiko / fruits / mania |
| limit      | 返回成绩数量                       |

返回值：

* `list[dict]`，每个元素是一条成绩（原始 JSON）。

---

### 5.2 user_sampler.py —— 用户采样模块

**作用**：

* 从给定范围中随机抽取用户 ID；
* 用于构造大规模抓取候选集。

```python
sample_user_ids(n, low=1, high=30_000_000)
```

---

### 5.3 db.py —— 数据库模块

**作用**：

* 创建 SQLite 数据库；
* 提供统一的数据库连接。

#### 数据表：user_scores

字段说明（核心字段）：

| 字段         | 含义                 |
| ---------- | ------------------ |
| user_id    | 用户 ID              |
| score_id   | 成绩唯一 ID            |
| pp         | Performance Points |
| accuracy   | 准确率                |
| beatmap_id | 谱面 ID              |
| raw_json   | 原始 JSON（完整）        |

---

### 5.4 save_scores.py —— 数据持久化

**作用**：

* 将 API 返回的 JSON 成绩写入数据库；
* 使用 `INSERT OR IGNORE` 防止重复。

```python
save_user_scores(user_id, scores)
```

---

### 5.5 fetch_parallel.py —— 并发抓取入口

**作用**：

* 使用 ThreadPoolExecutor 并发抓取；
* 自动跳过无成绩 / 请求失败用户；
* 直到收集到指定数量的有效用户。

核心参数：

```python
TARGET_MODE = "osu"
TARGET_USERS = 10_000
MAX_WORKERS = 8
```

---

## 6. 数据验证方式

### 6.1 检查数据库是否生成

```bash
ls data/osu.db
```

### 6.2 使用 SQLite 查看

```bash
sqlite3 data/osu.db
```

```sql
.tables
SELECT COUNT(*) FROM user_scores;
SELECT user_id, pp FROM user_scores ORDER BY pp DESC LIMIT 10;
```

---

## 7. 数据分析与机器学习接口

### 7.1 dataset.py —— 构造 ML 数据集

功能：

* 从 SQLite 读取数据；
* 构造特征矩阵 X 与标签 y。

示例特征：

* accuracy
* max_combo
* beatmap difficulty

示例标签：

* pp
* 是否高 PP（分类）

---

### 7.2 baseline.py —— ML 示例

功能：

* 使用 scikit-learn 做简单回归 / 分类；
* 输出评估指标（MSE / R² / accuracy）。

---

## 8. 四种游戏模式说明

| mode   | 名称             | 说明     |
| ------ | -------------- | ------ |
| osu    | Standard       | 圆圈点击模式 |
| taiko  | 太鼓             | 节奏敲击   |
| fruits | Catch the Beat | 接水果    |
| mania  | 键盘下落           | 类音游    |

---

## 9. 扩展方向（机器学习）

你当前的数据 **非常适合 ML**，可以做：

* PP 预测（回归）
* 玩家水平分类（新手 / 中阶 / 高手）
* 模式差异建模
* Beatmap 难度与成绩关系分析

---

## 10. 总结

本项目完整覆盖：

* API 调用（OAuth2）
* 并发爬取
* 数据库存储
* 数据验证
* 分析与机器学习入口

这是一个 **从工程到数据科学的完整闭环项目**。

---

如果你愿意，下一步我可以：

* 帮你写 **analysis/ 目录下完整 ML 代码**
* 或整理成 **课程实验报告 / 技术论文格式**
