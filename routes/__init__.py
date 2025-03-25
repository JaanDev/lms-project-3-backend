from fastapi import APIRouter

from . import auth, buylist, products, product_types, product_categories, analytics, notifications

router = APIRouter()

router.include_router(auth.router)
router.include_router(buylist.router)
router.include_router(products.router)
router.include_router(product_types.router)
router.include_router(product_categories.router)
router.include_router(analytics.router)
router.include_router(notifications.router)
