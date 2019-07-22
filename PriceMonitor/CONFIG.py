# All time in seconds
#配置文件。
ITEM_CRAWL_TIME = 60 * 1  # Monitor loop time, if not using proxy
UPDATE_TIME = 60 * 1  # Crawl item which updated before this time value
Email_TIME = 10  # Send email sleep time
PROXY_CRAWL = 0  # 0: Use local ip 1: Use proxy pool 2: Use zhi ma ip
PROXY_POOL_IP = "127.0.0.1"  # Redis server ip
