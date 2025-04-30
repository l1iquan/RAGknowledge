import uvicorn
from src.utils.helpers import setup_logging
from src.api.routes import app

def main():
    # 设置日志
    setup_logging()
    
    # 运行服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main() 