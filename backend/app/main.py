from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import add_error_handlers
from app.core.logging import configure_logging
from app.modules.ai.router import router as ai_router
from app.modules.chat.router import router as chat_router
from app.modules.financials.router import router as financials_router
from app.modules.health.router import router as health_router
from app.modules.holdings.router import router as holdings_router
from app.modules.market_data.router import router as market_data_router
from app.modules.news.router import router as news_router
from app.modules.watchlist.router import router as watchlist_router

configure_logging()
app = FastAPI(title=settings.app_name)
add_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(holdings_router)
app.include_router(watchlist_router)
app.include_router(market_data_router)
app.include_router(news_router)
app.include_router(financials_router)
app.include_router(ai_router)
app.include_router(chat_router)
