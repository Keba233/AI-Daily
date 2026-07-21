"""AI日报 - Flask主应用"""

import sys
import os

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from flask import Flask, render_template, jsonify, request

from config import CATEGORIES
from services.feed_fetcher import fetch_all_feeds, load_articles, get_available_dates, categorize_article
from services.ai_summary import generate_summary, load_summary, is_summary_cache_valid

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # 确保中文JSON正常显示


@app.template_filter("format_article_time")
def format_article_time(iso_str):
    """Jinja2模板过滤器：格式化文章发布时间"""
    from dateutil import parser as date_parser
    from datetime import datetime

    try:
        dt = date_parser.parse(iso_str)
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        hours = diff.total_seconds() / 3600
        minutes = diff.total_seconds() / 60

        if minutes < 1:
            return "刚刚"
        if minutes < 60:
            return f"{int(minutes)}分钟前"
        if hours < 24:
            return f"{int(hours)}小时前"
        if hours < 48:
            return "昨天"
        if hours < 72:
            return "前天"
        return dt.strftime("%m月%d日 %H:%M")
    except (ValueError, TypeError):
        return iso_str


@app.route("/")
def index():
    """首页 - AI每日总结 + 资讯列表"""
    date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))

    # 加载文章数据
    feed_data = load_articles(date_str)

    # 如果没有缓存数据，触发一次采集
    if feed_data is None and date_str == datetime.now().strftime("%Y-%m-%d"):
        print("[首页] 未找到今日缓存数据，开始采集...")
        articles = fetch_all_feeds()
        feed_data = load_articles(date_str)

    # 加载或生成AI摘要
    summary = load_summary(date_str)
    if summary is None or not is_summary_cache_valid(summary):
        if feed_data and feed_data.get("articles"):
            print("[首页] 生成AI每日总结...")
            summary = generate_summary(feed_data["articles"])

    # 准备模板数据
    articles = feed_data.get("articles", []) if feed_data else []
    available_dates = get_available_dates()

    # 为每篇文章添加分类标签
    for article in articles:
        if "category" not in article:
            article["category"] = categorize_article(article)

    return render_template(
        "index.html",
        summary=summary,
        articles=articles,
        categories=CATEGORIES,
        available_dates=available_dates,
        current_date=date_str,
    )


@app.route("/archive")
def archive():
    """历史归档页面"""
    available_dates = get_available_dates()
    return render_template(
        "archive.html",
        available_dates=available_dates,
    )


@app.route("/api/refresh")
def api_refresh():
    """手动刷新数据接口"""
    print("[API] 手动刷新数据...")
    articles = fetch_all_feeds()
    summary = generate_summary(articles)
    return jsonify({
        "success": True,
        "count": len(articles),
        "summary": summary,
    })


@app.route("/api/articles")
def api_articles():
    """获取文章列表API"""
    date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    view = request.args.get("view", "timeline")  # timeline / category / heat
    feed_data = load_articles(date_str)

    if feed_data is None:
        return jsonify({"articles": [], "date": date_str})

    articles = feed_data.get("articles", [])

    # 为每篇文章添加分类
    for article in articles:
        if "category" not in article:
            article["category"] = categorize_article(article)

    # 根据视图排序
    if view == "heat":
        articles.sort(key=lambda x: x.get("heat_score", 1.0), reverse=True)
    elif view == "category":
        articles.sort(key=lambda x: (x.get("category", "other"), x.get("published", "")), reverse=False)

    return jsonify({
        "articles": articles,
        "date": date_str,
        "count": len(articles),
    })


@app.route("/api/summary")
def api_summary():
    """获取AI摘要API"""
    date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    summary = load_summary(date_str)
    if summary:
        # 兼容前端：将 summary_items 映射为 items
        result = dict(summary)
        result["items"] = summary.get("summary_items", [])
        return jsonify(result)
    return jsonify({"summary_items": [], "summary_text": "暂无数据", "items": []})


if __name__ == "__main__":
    print("=" * 50)
    print("  AI日报 - 启动中...")
    print("=" * 50)

    import socket
    hostname = socket.gethostname()
    local_ip = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
    
    print(f"\n  本地访问: http://127.0.0.1:5000")
    print(f"  局域网访问: http://{local_ip}:5000")
    print(f"  (手机/其他设备请连接同一WiFi后访问局域网地址)")
    print()

    # 启动时自动采集一次数据
    print("[启动] 正在采集最新AI资讯...")
    try:
        fetch_all_feeds()
        print("[启动] 数据采集完成！\n")
    except Exception as e:
        print(f"[启动] 数据采集出错: {e}，将在访问时重试\n")

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)