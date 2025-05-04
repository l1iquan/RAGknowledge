import sys
from pathlib import Path
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from src.utils.helpers import setup_logging
from src.api.routes import app

def main():
    # 设置日志
    setup_logging()

    # 配置静态文件
    static_dir = Path(__file__).parent.parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # 添加根路径重定向到前端页面
    @app.get("/", include_in_schema=False)
    async def redirect_to_frontend():
        return RedirectResponse(url="/static/index.html")

    # 运行服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()