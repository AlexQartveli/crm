"""Интеграция с налоговой службой Грузии (RS.ge eAPI).

API: https://eapi.rs.ge
Документация: https://github.com/Kuduxaaa/rsge-python
"""

import os
from datetime import datetime

import httpx

EAPI_BASE = os.getenv("RSGE_EAPI_URL", "https://eapi.rs.ge")
MOCK_MODE = os.getenv("RSGE_MOCK", "true").lower() == "true"

_token: str | None = None


class RsgeError(Exception):
    pass


async def authenticate(username: str, password: str, pin: str | None = None, pin_token: str | None = None) -> dict:
    if MOCK_MODE:
        if pin_token and not pin:
            return {"needs_pin": True, "pin_token": "mock-pin-token"}
        return {"success": True, "access_token": "mock-token", "needs_pin": False}

    async with httpx.AsyncClient(timeout=30) as client:
        if pin_token and pin:
            resp = await client.post(f"{EAPI_BASE}/oauth/token", json={
                "grant_type": "pin",
                "pin_token": pin_token,
                "pin": pin,
            })
        else:
            resp = await client.post(f"{EAPI_BASE}/oauth/token", json={
                "grant_type": "password",
                "username": username,
                "password": password,
            })

        if resp.status_code != 200:
            raise RsgeError(f"Ошибка авторизации RS.ge: {resp.text}")

        data = resp.json()
        global _token
        if data.get("needs_pin") or data.get("pin_token"):
            return {"needs_pin": True, "pin_token": data.get("pin_token")}
        _token = data.get("access_token")
        return {"success": True, "access_token": _token, "needs_pin": False}


async def check_vat_payer(tin: str, vat_date: str | None = None) -> dict:
    if MOCK_MODE:
        return {
            "tin": tin,
            "is_vat_payer": len(tin) >= 9,
            "org_name": f"სატესტო კომპანია {tin[:4]}",
        }

    if not _token:
        raise RsgeError("Не авторизован в RS.ge")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{EAPI_BASE}/api/vat/payer",
            params={"tin": tin, "date": vat_date or datetime.now().strftime("%d-%m-%Y")},
            headers={"Authorization": f"Bearer {_token}"},
        )
        if resp.status_code != 200:
            raise RsgeError(f"Ошибка проверки НДС: {resp.text}")
        data = resp.json()
        return {"tin": tin, "is_vat_payer": data.get("is_vat_payer", False), "org_name": data.get("name")}


async def save_invoice_to_rsge(invoice_data: dict) -> dict:
    if MOCK_MODE:
        import random
        return {
            "transaction_id": f"TXN-{random.randint(10000, 99999)}",
            "invoice_id": random.randint(1000, 9999),
            "status": "pending",
        }

    if not _token:
        raise RsgeError("Не авторизован в RS.ge")

    payload = {
        "inv_category": 1,
        "inv_type": 1,
        "operation_date": invoice_data.get("operation_date", datetime.now().strftime("%d-%m-%Y %H:%M:%S")),
        "tin_seller": invoice_data["tin_seller"],
        "tin_buyer": invoice_data["tin_buyer"],
        "goods": invoice_data.get("goods", []),
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{EAPI_BASE}/api/invoice/save",
            json=payload,
            headers={"Authorization": f"Bearer {_token}"},
        )
        if resp.status_code != 200:
            raise RsgeError(f"Ошибка сохранения счёта: {resp.text}")
        return resp.json()


async def activate_invoice_rsge(invoice_id: int) -> bool:
    if MOCK_MODE:
        return True

    if not _token:
        raise RsgeError("Не авторизован в RS.ge")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{EAPI_BASE}/api/invoice/activate",
            json={"invoice_id": invoice_id},
            headers={"Authorization": f"Bearer {_token}"},
        )
        return resp.status_code == 200


def calc_vat(amount: float, rate: float = 18.0) -> tuple[float, float]:
    vat = round(amount * rate / 100, 2)
    total = round(amount + vat, 2)
    return vat, total
