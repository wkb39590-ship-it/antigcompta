import { chromium } from 'playwright';

(async () => {
    try {
        const browser = await chromium.launch();
        const page = await browser.newPage();
        await page.goto('http://localhost:3333/login', { waitUntil: 'networkidle' });
        await page.screenshot({ path: 'C:/Users/asus/.gemini/antigravity/brain/a2ccee39-eac7-4562-8e94-17f5aec30bb3/current_login_state.png', fullPage: true });
        await browser.close();
        console.log('Screenshot saved');
    } catch (e) {
        console.error(e);
    }
})();
