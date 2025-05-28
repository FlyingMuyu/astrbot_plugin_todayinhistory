from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import aiohttp
import json

@register(
    "astrbot_plugin_todayinhistory",
    "FlyingMuyu",
    "历史事件查询插件",
    "1.0",
    "https://github.com/FlyingMuyu/astrbot_plugin_todayinhistory"
)
class HistoryTodayPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @filter.command("历史上的今天")
    async def history_today(self, event: AstrMessageEvent):
        """纯API数据查询插件"""
        api_url = "https://zj.v.api.aa1.cn/api/bk/?num=5&type=json"
        
        try:
            # 使用标准HTTP客户端获取数据
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=10) as response:
                    if response.status != 200:
                        yield event.plain_result("服务暂时不可用，错误码：%d" % response.status)
                        return
                    
                    # 直接解析JSON数据
                    raw_data = await response.text()
                    data = json.loads(raw_data)
                    
                    # 数据有效性验证
                    if not isinstance(data, dict) or data.get("code") != 200:
                        yield event.plain_result("数据源异常，请稍后重试")
                        return
                    
                    # 纯字符串处理
                    output = [
                        "📆 %s 历史事件：" % data.get('day', ''),
                        *["• %s" % item for item in data.get('content', [])]
                    ]
                    
                    yield event.plain_result("\n".join(output))

        except aiohttp.ClientError as e:
            logger.error("网络请求失败：%s" % str(e))
            yield event.plain_result("网络连接异常")
        except json.JSONDecodeError:
            logger.error("无效的JSON响应")
            yield event.plain_result("数据解析失败")
        except Exception as e:
            logger.error("系统错误：%s" % str(e))
            yield event.plain_result("服务暂时不可用")

    async def terminate(self):
        """资源清理"""
        pass