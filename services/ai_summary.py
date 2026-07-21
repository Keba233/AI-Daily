"""AI每日总结模块 - 调用Ollama本地模型生成中文摘要"""

import json
import os
import re
from datetime import datetime

import requests

from config import (
    SUMMARY_MAX_ITEMS,
    SUMMARY_CACHE_HOURS,
    FEEDS_DIR,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_MAX_ARTICLES,
    CATEGORIES,
)
from services.feed_fetcher import categorize_article

# 中文类别名到英文key的反向映射
CATEGORY_CN_TO_KEY = {v: k for k, v in CATEGORIES.items()}


def _build_prompt(articles):
    """构建发送给Ollama的提示词"""
    articles = articles[:OLLAMA_MAX_ARTICLES]

    article_list = []
    for i, a in enumerate(articles, 1):
        title = a.get("title", "无标题")
        source = a.get("source", "未知来源")
        link = a.get("link", "")
        summary = a.get("summary", "")
        lang = a.get("lang", "en")
        lang_tag = "[中文]" if lang == "zh" else "[英文]"
        article_list.append(f"{i}. {lang_tag}【{source}】{title}\n   链接：{link}\n   摘要：{summary[:200]}")

    articles_text = "\n".join(article_list)

    # 列出类别key和名称的对应关系
    cat_list = ", ".join([f'"{k}"({v})' for k, v in CATEGORIES.items()])

    prompt = f"""以下是今天采集的AI相关新闻：

{articles_text}

请从中筛选出最重要的{SUMMARY_MAX_ITEMS}条新闻，用中文为每条写3-5句话的深度概括（包含关键事实、核心数据、发布方、影响分析），并写一段200-300字的总体概览（涵盖今日AI领域的主要趋势和重要事件，分析各事件之间的关联）。
category_key可选值：{cat_list}，务必使用英文key。

严格按以下JSON格式返回，不要添加任何其他文字：
{{
  "overview": "总体概览文字，200-300字，涵盖今日AI领域主要趋势、重要事件及其关联分析",
  "items": [
    {{
      "index": 1,
      "title": "原始标题",
      "link": "原始链接",
      "source": "来源名称",
      "category_key": "英文类别key",
      "summary": "你用中文写的3-5句话深度概括，包含关键事实、核心数据、发布方、影响分析"
    }}
  ]
}}"""

    return prompt


def _call_ollama(prompt):
    """调用Ollama本地模型生成摘要"""
    url = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是一位专业的AI行业分析师，擅长用简洁精炼的中文概括AI领域动态。你总是返回严格的JSON格式数据，不添加任何多余文字。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 8192,
        },
    }

    try:
        print(f"[Ollama] 正在调用模型 {OLLAMA_MODEL} 生成摘要...")
        resp = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
        resp.raise_for_status()

        data = resp.json()
        msg = data.get("message", {})
        content = msg.get("content", "")
        thinking = msg.get("thinking", "")

        print(f"[Ollama] 返回字段: content长度={len(content)}, thinking长度={len(thinking)}")

        # 如果content为空但thinking有内容，尝试从thinking中提取JSON
        if not content and thinking:
            print("[Ollama] content为空，尝试从thinking中提取JSON...")
            # 思考型模型的最终输出通常在thinking末尾
            # 策略：从末尾向前搜索最后一个完整的JSON对象
            # 先找最后一个包含"overview"的JSON块
            last_overview = thinking.rfind('"overview"')
            if last_overview > 0:
                # 从这个位置向前找最近的 {
                start = thinking.rfind('{', 0, last_overview)
                if start >= 0:
                    # 从start位置向后找匹配的 }
                    brace_count = 0
                    end = start
                    for i in range(start, len(thinking)):
                        if thinking[i] == '{':
                            brace_count += 1
                        elif thinking[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end = i + 1
                                break
                    if end > start:
                        content = thinking[start:end]
                        print(f"[Ollama] 从thinking末尾提取到JSON，长度: {len(content)}")
            
            # 如果上面没找到，回退到正则
            if not content:
                json_match = re.search(r'\{[\s\S]*\}', thinking)
                if json_match:
                    content = json_match.group()
                    print(f"[Ollama] 从thinking正则提取到JSON，长度: {len(content)}")

        if not content:
            print("[Ollama] 模型返回content为空")
            return None

        print(f"[Ollama] 模型返回成功，内容长度: {len(content)}")
        return content

    except requests.exceptions.Timeout:
        print(f"[Ollama] 请求超时（{OLLAMA_TIMEOUT}秒）")
        return None
    except requests.exceptions.ConnectionError:
        print("[Ollama] 无法连接到Ollama服务，请确认Ollama正在运行")
        return None
    except Exception as e:
        print(f"[Ollama] 调用出错: {e}")
        return None


def _normalize_category_key(category_key):
    """将类别key标准化为英文key，支持中文值映射"""
    if not category_key:
        return "industry"
    # 如果已经是合法的英文key
    if category_key in CATEGORIES:
        return category_key
    # 尝试从中文映射到英文
    if category_key in CATEGORY_CN_TO_KEY:
        return CATEGORY_CN_TO_KEY[category_key]
    # 尝试模糊匹配
    for cn_name, en_key in CATEGORY_CN_TO_KEY.items():
        if category_key in cn_name or cn_name in category_key:
            return en_key
    return "industry"


def _fix_json_string(json_str):
    """修复常见的JSON格式问题"""
    # 替换所有控制字符为空格（模型可能在文本中插入未转义的换行/制表符）
    # JSON结构不需要格式化空白，json.loads能正确解析
    json_str = re.sub(r'[\x00-\x1f]', ' ', json_str)
    # 移除尾随逗号（逗号后直接跟}或]）
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    return json_str


def _parse_ollama_response(content, articles):
    """解析Ollama返回的JSON，合并原文链接等信息"""
    # 清理思考标签（<think>...</think>格式）
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

    # 提取JSON块
    json_str = content
    start_idx = content.find("{")
    end_idx = content.rfind("}") + 1
    if start_idx >= 0 and end_idx > start_idx:
        json_str = content[start_idx:end_idx]

    # 修复常见JSON问题
    json_str = _fix_json_string(json_str)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[Ollama] JSON解析失败: {e}")
        print(f"[Ollama] 尝试修复后重试...")
        try:
            # 更激进的修复：尝试找到第一个完整的items数组
            overview_match = re.search(r'"overview"\s*:\s*"([^"]*)"', json_str)
            items_matches = re.findall(
                r'\{\s*"index"\s*:\s*\d+\s*,\s*"title"\s*:\s*"([^"]*)"\s*,\s*"link"\s*:\s*"([^"]*)"\s*,\s*"source"\s*:\s*"([^"]*)"\s*,\s*"category_key"\s*:\s*"([^"]*)"\s*,\s*"summary"\s*:\s*"([^"]*)"\s*\}',
                json_str
            )
            if items_matches:
                data = {
                    "overview": overview_match.group(1) if overview_match else "暂无概览",
                    "items": [
                        {
                            "index": i + 1,
                            "title": m[0],
                            "link": m[1],
                            "source": m[2],
                            "category_key": m[3],
                            "summary": m[4],
                        }
                        for i, m in enumerate(items_matches)
                    ],
                }
                print(f"[Ollama] 正则提取成功，共 {len(items_matches)} 条")
            else:
                print(f"[Ollama] 正则提取也失败，原始内容前300字: {content[:300]}")
                return None
        except Exception as e2:
            print(f"[Ollama] 所有解析尝试均失败: {e2}")
            return None

    overview = data.get("overview", "暂无概览")
    items_raw = data.get("items", [])

    # 构建文章索引映射（用于查找原始链接）
    article_by_index = {i: a for i, a in enumerate(articles, 1)}
    article_by_title = {}
    for a in articles:
        title = a.get("title", "")
        if title:
            article_by_title[title] = a

    # 合并结果
    items = []
    for item in items_raw[:SUMMARY_MAX_ITEMS]:
        original_title = item.get("title", "")
        item_index = item.get("index")
        model_link = item.get("link", "")

        # 优先使用模型返回的link（模型从prompt中获取了原始链接）
        # 仅当模型link无效时才回退到匹配
        if model_link and model_link.startswith("http"):
            original_article = {"link": model_link}
        else:
            original_article = {}

        # 回退1：通过index匹配原文
        if not original_article.get("link") and item_index:
            matched = article_by_index.get(item_index, {})
            if matched.get("link"):
                original_article = matched

        # 回退2：通过标题精确匹配
        if not original_article.get("link"):
            matched = article_by_title.get(original_title, {})
            if matched.get("link"):
                original_article = matched

        # 回退3：模糊标题匹配
        if not original_article.get("link"):
            for t, a in article_by_title.items():
                if original_title and (original_title in t or t in original_title):
                    original_article = a
                    break

        category_key = _normalize_category_key(item.get("category_key", "industry"))

        items.append({
            "title": original_title,
            "link": original_article.get("link", item.get("link", "#")),
            "source": item.get("source", original_article.get("source", "未知来源")),
            "category": category_key,
            "summary": item.get("summary", original_title),
        })

    return {
        "overview": overview,
        "items": items,
    }


def generate_summary(articles):
    """
    调用Ollama本地模型生成AI每日中文总结
    如果Ollama不可用，降级为规则摘要
    """
    if not articles:
        return _empty_summary()

    # 构建提示词
    prompt = _build_prompt(articles)

    # 调用Ollama
    content = _call_ollama(prompt)

    if content:
        # 解析返回结果
        parsed = _parse_ollama_response(content, articles)
        if parsed and parsed.get("items"):
            overview = parsed["overview"]
            # 如果overview为空或无效，从条目自动生成
            if not overview or overview in ("暂无概览", "暂无今日AI资讯", ""):
                overview = _generate_overview(parsed["items"])
            result = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "generated_at": datetime.now().isoformat(),
                "summary_text": overview,
                "summary_items": parsed["items"],
                "model": OLLAMA_MODEL,
            }
            _save_summary(result)
            print(f"[Ollama] AI摘要生成成功，共 {len(parsed['items'])} 条")
            return result

    # 降级：使用规则摘要
    print("[Ollama] 降级为规则摘要模式...")
    return _fallback_summary(articles)


def _fallback_summary(articles):
    """降级方案：基于规则的摘要（不使用AI模型）"""
    categorized = {}
    for article in articles:
        cat = categorize_article(article)
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(article)

    summary_items = []
    category_order = ["product", "technology", "research", "open_source", "industry", "opinion"]

    for cat in category_order:
        if cat in categorized and categorized[cat]:
            cat_articles = sorted(
                categorized[cat],
                key=lambda x: x.get("heat_score", 1.0),
                reverse=True,
            )
            for article in cat_articles[:2]:
                if len(summary_items) >= SUMMARY_MAX_ITEMS:
                    break
                summary_items.append({
                    "title": article["title"],
                    "link": article["link"],
                    "source": article["source"],
                    "category": cat,
                    "summary": _generate_item_summary(article),
                })

    if len(summary_items) < SUMMARY_MAX_ITEMS:
        remaining = [a for a in articles if a["title"] not in {s["title"] for s in summary_items}]
        for article in remaining:
            if len(summary_items) >= SUMMARY_MAX_ITEMS:
                break
            summary_items.append({
                "title": article["title"],
                "link": article["link"],
                "source": article["source"],
                "category": categorize_article(article),
                "summary": _generate_item_summary(article),
            })

    overview = _generate_overview(summary_items)

    result = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().isoformat(),
        "summary_text": overview,
        "summary_items": summary_items,
        "model": "rule-based",
    }
    _save_summary(result)
    return result


def _generate_item_summary(article):
    """为单条文章生成一句话摘要（降级用）"""
    title = article.get("title", "")
    summary = article.get("summary", "")
    if not summary or len(summary) < 20:
        return title
    clean_summary = summary.strip()[:100]
    if len(summary) > 100:
        clean_summary += "..."
    return clean_summary


def _generate_overview(items):
    """生成总览文本（降级用）"""
    if not items:
        return "暂无今日AI资讯"
    categories_count = {}
    for item in items:
        cat = item.get("category", "other")
        categories_count[cat] = categories_count.get(cat, 0) + 1
    cat_names = {
        "product": "产品发布", "technology": "技术突破", "opinion": "行业观点",
        "open_source": "开源项目", "research": "学术研究", "industry": "产业动态",
    }
    parts = []
    for cat, count in categories_count.items():
        name = cat_names.get(cat, cat)
        parts.append(f"{name}{count}条")
    return f"今日AI圈共精选{len(items)}条重要动态：" + "、".join(parts) + "。"


def _empty_summary():
    """返回空摘要"""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().isoformat(),
        "summary_text": "暂无今日AI资讯",
        "summary_items": [],
        "model": None,
    }


def _save_summary(summary_data):
    """保存摘要到本地"""
    os.makedirs(FEEDS_DIR, exist_ok=True)
    date_str = summary_data["date"]
    filepath = os.path.join(FEEDS_DIR, f"summary_{date_str}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    print(f"[存储] 摘要已保存到 {filepath}")


def load_summary(date_str=None):
    """加载已缓存的摘要"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(FEEDS_DIR, f"summary_{date_str}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def is_summary_cache_valid(summary_data):
    """检查摘要缓存是否仍然有效"""
    if not summary_data:
        return False
    generated_at = summary_data.get("generated_at")
    if not generated_at:
        return False
    try:
        gen_time = datetime.fromisoformat(generated_at)
        elapsed = (datetime.now() - gen_time).total_seconds() / 3600
        return elapsed < SUMMARY_CACHE_HOURS
    except (ValueError, TypeError):
        return False