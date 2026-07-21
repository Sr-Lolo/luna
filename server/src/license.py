import asyncio
import sys
from typing import Optional, Callable

_STORE_AVAILABLE = False
try:
    import winrt.windows.services.store as wss
    _STORE_AVAILABLE = True
except ImportError:
    pass

_license_cache: Optional[bool] = None


def _get_context():
    if not _STORE_AVAILABLE:
        return None
    try:
        return wss.StoreContext.get_default()
    except Exception:
        return None


def _query_store_license(addon_id: str):
    context = _get_context()
    if context is None:
        return None
    try:
        app_license = context.get_app_license_async().get_results()
        if app_license.is_active:
            if addon_id and app_license.add_on_licenses:
                for lic in app_license.add_on_licenses.values():
                    if lic.sku_store_id == addon_id and lic.is_active:
                        return True
            return True
        return False
    except Exception:
        return None


def is_store_app() -> bool:
    return _get_context() is not None


def refresh_license(config_load: Callable, config_save: Callable) -> bool:
    global _license_cache

    cfg = config_load()
    addon_id = cfg.get("store_addon_id", "")

    store_result = _query_store_license(addon_id)
    if store_result is not None:
        if cfg.get("pro_license") != store_result:
            cfg["pro_license"] = store_result
            config_save(cfg)
        _license_cache = store_result
        return store_result

    _license_cache = cfg.get("pro_license", False)
    return _license_cache


def check_license(config_load: Callable, config_save: Callable, force=False) -> bool:
    global _license_cache
    if force or _license_cache is None:
        return refresh_license(config_load, config_save)
    return _license_cache


def invalidate_cache():
    global _license_cache
    _license_cache = None


async def purchase_license(addon_id: str):
    context = _get_context()
    if context is None:
        return {"success": False, "redirect_url": f"ms-windows-store://pdp/?productid={addon_id}"}
    try:
        result = await context.request_purchase_async(addon_id)
        ok = result.status == wss.StorePurchaseStatus.succeeded
        return {"success": ok}
    except Exception as e:
        return {"success": False, "error": str(e)}
