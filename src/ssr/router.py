from fastapi import APIRouter

from src.ssr.auth import page as auth_page
from src.ssr.landing import page as landing_page
from src.ssr.notification import page as notification_page
from src.ssr.users import page as users_page


router = APIRouter(tags=["ssr"])
router.include_router(landing_page)
router.include_router(auth_page)
router.include_router(users_page)
router.include_router(notification_page)
