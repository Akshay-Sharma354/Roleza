from fastapi import APIRouter
from playwright.async_api import async_playwright

router = APIRouter()


@router.get("/test-browser")
async def test_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        page = await browser.new_page()

        await page.goto("https://example.com")

        title = await page.title()

        await browser.close()

        return {
            "success": True,
            "title": title
        }