"""
Google Colab Automation Bot

Uses Playwright to automate code execution in Google Colab notebooks.
"""

import os
import sys
import asyncio
from typing import Dict

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from playwright.async_api import async_playwright, BrowserContext, Page
from libs.core.logger import setup_logger

logger = setup_logger("colab_bot", level="INFO")

class ColabBot:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.context: BrowserContext = None
        self.playwright = None
        # Persistent data dir
        self.user_data_dir = os.path.join(os.getcwd(), "chrome_data")
        logger.info(f"ColabBot initialized (headless={headless})")

    async def execute_code(self, code: str) -> Dict:
        logger.info("🚀 Starting Colab automation...")
        
        # We start a fresh Playwright instance every time to avoid stale handles
        async with async_playwright() as p:
            logger.info("Launching Chrome with persistent context...")
            
            # Launch with specific args to avoid bot detection
            self.context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                channel="chrome", 
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                viewport=None,
                no_viewport=True
            )
            
            page = self.context.pages[0]
            logger.info("✅ Browser context created")

            try:
                # 1. DIRECT SHORTCUT: Create new notebook immediately
                logger.info("📂 Navigating to NEW notebook directly...")
                await page.goto("https://colab.research.google.com/#create=true", timeout=60000)
                
                # 2. WAIT FOR EDITOR
                # Colab uses 'Monaco' editor (like VS Code). We wait for the view-lines.
                logger.info("⏳ Waiting for editor to load...")
                
                # We try a few selectors to be safe
                editor = await page.wait_for_selector(
                    ".monaco-editor, .cmd-input-area", 
                    state="visible", 
                    timeout=45000
                )
                
                if not editor:
                    raise Exception("Could not find code editor")

                # Small pause to let animations settle
                await asyncio.sleep(2)

                # 3. CLICK TO FOCUS
                logger.info("✅ Editor found. Clicking to focus...")
                # We click the center of the screen often helps focus the active cell
                await editor.click()
                await page.keyboard.press("Escape") # Close any popups
                await editor.click()

                # 4. PASTE CODE (Faster than typing)
                logger.info(f"⌨️ Pasting code ({len(code)} chars)...")
                
                # Copy to clipboard via JS
                # Note: We use a JS workaround because simple clipboard write can be blocked
                escaped_code = code.replace("`", "\\`").replace("\\", "\\\\")
                await page.evaluate(f"""
                    navigator.clipboard.writeText(`{escaped_code}`);
                """)
                
                # Paste
                await page.keyboard.press("Control+v")
                await asyncio.sleep(1)

                # 5. EXECUTE (Ctrl+Enter)
                logger.info("▶️ Executing code...")
                await page.keyboard.press("Control+Enter")

                # 1. WAIT for charts to render (give it 10-15 seconds)
                logger.info("⏳ Waiting 15s for charts to render...")
                await asyncio.sleep(15)
                
                # 2. CAPTURE OUTPUT from the executed cell
                logger.info("📋 Capturing cell output...")
                captured_logs = ""
                
                try:
                    # Colab outputs are in various places, try multiple selectors
                    # Look for output in the current focused/executing cell
                    output_selectors = [
                        ".output-area .output-text",  # Common output text
                        ".output .stream",            # Stream output
                        "pre",                         # Pre-formatted text
                        ".output-content",            # Output content div
                    ]
                    
                    for selector in output_selectors:
                        try:
                            outputs = await page.locator(selector).all_text_contents()
                            if outputs:
                                captured_logs += "\n".join(outputs)
                                logger.info(f"✅ Captured {len(captured_logs)} chars from {selector}")
                                break
                        except:
                            continue
                    
                    # If still empty, try getting all visible text from output area
                    if not captured_logs:
                        try:
                            # Get the last output div
                            output_area = page.locator(".output-area").last
                            captured_logs = await output_area.inner_text()
                        except:
                            logger.warning("Could not capture cell output")
                            captured_logs = "Output capture failed"
                    
                    logger.info(f"📝 Captured logs preview: {captured_logs[:200]}...")
                    
                except Exception as e:
                    logger.warning(f"Failed to capture output: {e}")
                    captured_logs = f"Output capture error: {str(e)}"

                # 7. SCREENSHOT
                logger.info("📸 Taking screenshot...")
                screenshot_path = "eda_result.png"
                await page.screenshot(path=screenshot_path)

                # === NEW DYNAMIC WAIT BLOCK ===
                logger.info("🍿 Browser is OPEN. The bot is waiting for you to close the window...")
                
                try:
                    # This line pauses code execution strictly until the page is closed
                    await page.wait_for_event("close", timeout=0) 
                except Exception as e:
                    # Ignore errors if the browser crashes or force closes
                    logger.info("Browser window closed.")
                # ==============================
                
                
                
                logger.info("✅ Execution complete!")
                return {
                    "status": "success", 
                    "message": "Code executed successfully", 
                    "screenshot": screenshot_path,
                    "logs": captured_logs  # NEW: Return captured output
                }

            except Exception as e:
                logger.error(f"❌ Colab automation failed: {str(e)}")
                await page.screenshot(path="error_screenshot.png")
                raise e
            finally:
                await self.context.close()