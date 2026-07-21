"""RSS数据采集模块 - 聚合多源AI资讯"""

import json
import os
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

import feedparser
import requests
from dateutil import parser as date_parser

from config import FEED_SOURCES, HEAT_WEIGHTS, FEEDS_DIR

# AI相关关键词（用于过滤非AI文章）
AI_KEYWORDS_ZH = [
    "ai", "人工智能", "大模型", "llm", "gpt", "claude", "gemini", "智能体",
    "agent", "机器学习", "深度学习", "神经网络", "agi", "aigc", "生成式",
    "智谱", "通义", "文心", "千问", "kimi", "deepseek", "qwen", "llama",
    "开源模型", "多模态", "对话", "chat", "推理", "训练", "微调", "finetune",
    "transformer", "扩散模型", "diffusion", "embedding", "向量", "rag",
    "copilot", "自动驾驶", "语音识别", "图像识别", "自然语言", "nlp",
    "计算机视觉", "cv", "机器人", "robot", "sora", "midjourney", "stable diffusion",
    "芯片", "gpu", "算力", "英伟达", "nvidia", "tpu", "华为升腾",
    "openai", "anthropic", "google deepmind", "百度ai", "阿里ai", "腾讯ai",
    "字节ai", "moonshot", "月之暗面", "minimax", "零一万物", "百川智能",
]

AI_KEYWORDS_EN = [
    "ai", "artificial intelligence", "llm", "gpt", "claude", "gemini", "agent",
    "machine learning", "deep learning", "neural network", "agi", "aigc",
    "generative", "transformer", "model", "training", "inference", "finetune",
    "multimodal", "chatbot", "diffusion", "embedding", "rag", "copilot",
    "autonomous", "nlp", "computer vision", "robot", "sora", "midjourney",
    "openai", "anthropic", "deepmind", "nvidia", "gpu", "tpu",
    "hugging face", "huggingface", "langchain", "pytorch", "tensorflow",
]


def is_ai_related(article, strict=False):
    """检查文章是否与AI相关
    
    Args:
        article: 文章字典
        strict: 严格模式（用于needs_ai_filter标记的源），需要更高匹配度
    
    Returns:
        bool: 是否为AI相关文章
    """
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    text = f"{title} {summary}"
    
    # 计算匹配的关键词数量
    zh_matches = sum(1 for kw in AI_KEYWORDS_ZH if kw in text)
    en_matches = sum(1 for kw in AI_KEYWORDS_EN if kw in text)
    total_matches = zh_matches + en_matches
    
    if strict:
        # 严格模式：需要至少1个匹配（用于通用科技源过滤）
        return total_matches >= 1
    else:
        # 宽松模式：不需要过滤（AI专项源默认通过）
        return True


def ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(FEEDS_DIR, exist_ok=True)


def fetch_feed(source_name, source_config):
    """抓取单个RSS源，返回标准化后的文章列表"""
    url = source_config["url"]
    category = source_config["category"]
    lang = source_config["lang"]

    try:
        # 设置请求头，避免被某些网站拒绝
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        feed = feedparser.parse(resp.content)
        articles = []

        for entry in feed.entries[:30]:  # 每个源最多取30条
            # 解析发布时间
            published = None
            if hasattr(entry, "published"):
                try:
                    published = date_parser.parse(entry.published)
                except (ValueError, TypeError):
                    pass
            elif hasattr(entry, "updated"):
                try:
                    published = date_parser.parse(entry.updated)
                except (ValueError, TypeError):
                    pass

            if published is None:
                published = datetime.now()

            # 清理HTML标签
            summary = ""
            if hasattr(entry, "summary"):
                summary = re.sub(r"<[^>]+>", "", entry.summary)[:300]
            elif hasattr(entry, "description"):
                summary = re.sub(r"<[^>]+>", "", entry.description)[:300]

            article = {
                "title": entry.get("title", "无标题"),
                "link": entry.get("link", ""),
                "summary": summary,
                "published": published.isoformat(),
                "source": source_name,
                "source_category": category,
                "lang": lang,
                "heat_score": HEAT_WEIGHTS.get(category, 1.0),
            }
            articles.append(article)

        return articles

    except Exception as e:
        print(f"[警告] 抓取 {source_name} ({url}) 失败: {e}")
        return []


def fetch_all_feeds():
    """抓取所有配置的RSS源，返回合并后的文章列表"""
    ensure_data_dir()
    all_articles = []
    total_before_filter = 0
    total_after_filter = 0

    for source_name, source_config in FEED_SOURCES.items():
        print(f"[采集] 正在抓取: {source_name}...")
        articles = fetch_feed(source_name, source_config)
        total_before_filter += len(articles)
        
        # 对标记为needs_ai_filter的源进行AI内容过滤
        if source_config.get("needs_ai_filter", False) and articles:
            before_count = len(articles)
            articles = [a for a in articles if is_ai_related(a, strict=True)]
            filtered_count = before_count - len(articles)
            if filtered_count > 0:
                print(f"  -> AI过滤: 移除 {filtered_count} 条非AI文章，保留 {len(articles)} 条")
        
        total_after_filter += len(articles)
        all_articles.extend(articles)
        print(f"  -> 获取 {len(articles)} 条")

    # 按发布时间倒序排列
    all_articles.sort(key=lambda x: x["published"], reverse=True)

    # 去重（基于标题相似度）
    all_articles = deduplicate_articles(all_articles)
    
    print(f"[统计] 过滤前: {total_before_filter} 条, 过滤后: {total_after_filter} 条, 去重后: {len(all_articles)} 条")

    # 保存到本地JSON
    save_articles(all_articles)

    return all_articles


def deduplicate_articles(articles):
    """基于标题相似度去重"""
    seen_titles = []
    unique_articles = []

    for article in articles:
        title_lower = article["title"].lower().strip()
        # 简单去重：检查是否已有非常相似的标题
        is_duplicate = False
        for seen in seen_titles:
            if title_lower == seen or (len(title_lower) > 10 and title_lower in seen) or (len(seen) > 10 and seen in title_lower):
                is_duplicate = True
                break

        if not is_duplicate:
            seen_titles.append(title_lower)
            unique_articles.append(article)

    return unique_articles


def save_articles(articles):
    """保存文章数据到本地JSON文件"""
    ensure_data_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(FEEDS_DIR, f"{today}.json")

    data = {
        "date": today,
        "updated_at": datetime.now().isoformat(),
        "count": len(articles),
        "articles": articles,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[存储] 已保存 {len(articles)} 条文章到 {filepath}")


def load_articles(date_str=None):
    """从本地JSON加载文章数据"""
    ensure_data_dir()

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    filepath = os.path.join(FEEDS_DIR, f"{date_str}.json")

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    return None


def get_available_dates():
    """获取所有可用的日期列表"""
    ensure_data_dir()
    dates = []

    for filename in os.listdir(FEEDS_DIR):
        if filename.endswith(".json"):
            date_str = filename.replace(".json", "")
            dates.append(date_str)

    dates.sort(reverse=True)
    return dates


def categorize_article(article):
    """基于关键词对文章进行自动分类"""
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    text = f"{title} {summary}"

    # 分类关键词映射
    category_keywords = {
        "product": ["发布", "launch", "release", "发布", "新品", "产品", "gpt", "claude", "gemini", "模型发布", "announce"],
        "technology": ["突破", "breakthrough", "技术", "算法", "algorithm", "训练", "training", "架构", "architecture", "性能", "performance"],
        "opinion": ["观点", "观点", "看法", "opinion", "评论", "review", "分析", "analysis", "趋势", "trend"],
        "open_source": ["开源", "open source", "github", "huggingface", "开源项目", "开源模型"],
        "research": ["论文", "paper", "研究", "research", "arxiv", "学术", "实验", "experiment"],
        "industry": ["融资", "funding", "收购", "acquisition", "上市", "ipo", "市场", "market", "估值", "投资"],
    }

    scores = {}
    for cat, keywords in category_keywords.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[cat] = score

    if scores:
        return max(scores, key=scores.get)

    return "industry"  # 默认分类