"""AI日报配置文件 - RSS源和分类定义"""

# RSS 订阅源配置
FEED_SOURCES = {
    # 中文AI垂直媒体（高精准度）
    "量子位": {
        "url": "https://www.qbitai.com/feed",
        "category": "中文媒体",
        "lang": "zh",
    },
    "阮一峰网络日志": {
        "url": "http://www.ruanyifeng.com/blog/atom.xml",
        "category": "中文媒体",
        "lang": "zh",
        "needs_ai_filter": True,
    },
    "雷峰网": {
        "url": "https://www.leiphone.com/feed",
        "category": "中文媒体",
        "lang": "zh",
    },
    "宝玉的博客": {
        "url": "https://baoyu.io/feed.xml",
        "category": "中文媒体",
        "lang": "zh",
    },
    # 中文综合科技媒体（需AI过滤）
    "36氪": {
        "url": "https://36kr.com/feed",
        "category": "中文媒体",
        "lang": "zh",
        "needs_ai_filter": True,
    },
    "IT之家": {
        "url": "https://www.ithome.com/rss/",
        "category": "中文媒体",
        "lang": "zh",
        "needs_ai_filter": True,
    },
    "爱范儿": {
        "url": "https://www.ifanr.com/feed",
        "category": "中文媒体",
        "lang": "zh",
        "needs_ai_filter": True,
    },
    # 英文AI媒体
    "TechCrunch AI": {
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "英文媒体",
        "lang": "en",
    },
    "The Verge AI": {
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "category": "英文媒体",
        "lang": "en",
    },
    "VentureBeat AI": {
        "url": "https://venturebeat.com/category/ai/feed/",
        "category": "英文媒体",
        "lang": "en",
    },
    "Import AI": {
        "url": "https://importai.substack.com/feed",
        "category": "英文媒体",
        "lang": "en",
    },
    "Ahead of AI": {
        "url": "https://magazine.sebastianraschka.com/feed",
        "category": "英文媒体",
        "lang": "en",
    },
    # 技术社区
    "Hacker News": {
        "url": "https://news.ycombinator.com/rss",
        "category": "技术社区",
        "lang": "en",
        "needs_ai_filter": True,
    },
    # 官方博客
    "OpenAI Blog": {
        "url": "https://openai.com/blog/rss.xml",
        "category": "官方博客",
        "lang": "en",
    },
    "Google AI Blog": {
        "url": "https://blog.google/technology/ai/rss/",
        "category": "官方博客",
        "lang": "en",
    },
    "Google DeepMind": {
        "url": "https://deepmind.google/blog/rss.xml",
        "category": "官方博客",
        "lang": "en",
    },
}

# 资讯分类定义
CATEGORIES = {
    "product": "产品发布",
    "technology": "技术突破",
    "opinion": "行业观点",
    "open_source": "开源项目",
    "research": "学术研究",
    "industry": "产业动态",
}

# 热度权重配置
HEAT_WEIGHTS = {
    "官方博客": 3.0,
    "英文媒体": 2.0,
    "中文媒体": 2.0,
    "技术社区": 1.5,
}

# 数据存储路径
DATA_DIR = "data"
FEEDS_DIR = "data/feeds"

# AI摘要配置
SUMMARY_MAX_ITEMS = 25  # 每日摘要最大条目数（从15增加到25，覆盖更多重要新闻）
SUMMARY_CACHE_HOURS = 6  # 摘要缓存时长（小时）

# DeepSeek API 配置（可选，用于云端部署时的AI摘要）
# 设置环境变量 DEEPSEEK_API_KEY 即可使用
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"  # 也可用 "deepseek-reasoner"
DEEPSEEK_TIMEOUT = 180  # 生成超时时间（秒）
DEEPSEEK_MAX_ARTICLES = 80  # 发送给模型的最大文章数

# Ollama 本地模型配置（备用）
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3.5:9b"
OLLAMA_TIMEOUT = 180  # 生成超时时间（秒，增加以适应更多条目）
OLLAMA_MAX_ARTICLES = 80  # 发送给模型的最大文章数