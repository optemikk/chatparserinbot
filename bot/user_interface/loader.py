from aiogram import Router

from bot.user_interface.info.handlers import router as info_router
from bot.user_interface.keywords.handlers import router as keywords_router
from bot.user_interface.send_sources.handlers import router as send_sources_router
from bot.user_interface.start_msg.handlers import router as start_msg_router
from bot.user_interface.start_parsing.handlers import router as start_parsing_router
from bot.user_interface.support.handlers import router as support_router
from bot.user_interface.set_timer.handlers import router as set_interval_router
from bot.user_interface.subscription.handlers import router as subscription_router



router = Router()

router.include_router(info_router)
router.include_router(keywords_router)
router.include_router(send_sources_router)
router.include_router(start_msg_router)
router.include_router(start_parsing_router)
router.include_router(support_router)
router.include_router(set_interval_router)
router.include_router(subscription_router)
