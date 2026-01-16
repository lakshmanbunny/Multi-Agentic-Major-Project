"""
Google Colab Automation Utilities

Specialized functions for interacting with Google Colab notebooks.
Contains selectors and helper methods for common Colab operations.
"""

from typing import Optional

from playwright.async_api import Page

from core import setup_logger

logger = setup_logger("colab_automation", level="INFO")


class ColabSelectors:
    """CSS selectors for Google Colab elements"""
    
    # Code cells
    CODE_CELL = ".cell"
    CODE_EDITOR = ".CodeMirror"
    CODE_INPUT = ".CodeMirror-code"
    
    # Execution controls
    RUN_BUTTON = "button[aria-label='Run cell']"
    RUN_ALL_BUTTON = "button[aria-label='Run all']"
    STOP_BUTTON = "button[aria-label='Stop execution']"
    
    # Output
    OUTPUT_AREA = ".output-area"
    OUTPUT_TEXT = ".output_text"
    OUTPUT_ERROR = ".output_error"
    
    # Notebook controls
    NEW_CODE_CELL = "button[aria-label='Add code cell']"
    NEW_TEXT_CELL = "button[aria-label='Add text cell']"
    
    # Status indicators
    RUNTIME_STATUS = ".runtime-status"
    EXECUTION_COUNT = ".cell-execution-count"
    
    # Menus
    FILE_MENU = "button:has-text('File')"
    EDIT_MENU = "button:has-text('Edit')"
    RUNTIME_MENU = "button:has-text('Runtime')"


class ColabAutomation:
    """
    High-level automation functions for Google Colab
    
    Provides easier API for common Colab operations.
    """
    
    def __init__(self, page: Page):
        """
        Initialize Colab automation
        
        Args:
            page: Playwright Page object
        """
        self.page = page
        self.selectors = ColabSelectors()
    
    async def wait_for_notebook_ready(self, timeout: int = 30000):
        """
        Wait for Colab notebook to be fully loaded and ready
        
        Args:
            timeout: Maximum wait time in milliseconds
        """
        logger.info("Waiting for notebook to be ready")
        
        try:
            # Wait for key elements to be visible
            await self.page.wait_for_selector(
                self.selectors.CODE_CELL,
                state="visible",
                timeout=timeout
            )
            
            logger.info("Notebook is ready")
        
        except Exception as e:
            logger.error("Notebook not ready", error=str(e))
            raise
    
    async def add_code_cell(self) -> bool:
        """
        Add a new code cell to the notebook
        
        Returns:
            True if successful
        """
        logger.info("Adding new code cell")
        
        try:
            # Click add code cell button
            await self.page.click(self.selectors.NEW_CODE_CELL)
            
            # Wait for new cell to appear
            await self.page.wait_for_timeout(500)
            
            logger.info("Code cell added")
            return True
        
        except Exception as e:
            logger.error("Failed to add code cell", error=str(e))
            return False
    
    async def insert_code(self, code: str, cell_index: int = -1) -> bool:
        """
        Insert code into a cell
        
        Args:
            code: Python code to insert
            cell_index: Index of cell (-1 for last cell)
        
        Returns:
            True if successful
        """
        logger.info("Inserting code", cell_index=cell_index, code_length=len(code))
        
        try:
            # Get all code cells
            cells = await self.page.query_selector_all(self.selectors.CODE_CELL)
            
            if not cells:
                logger.warning("No code cells found")
                return False
            
            # Select target cell
            target_cell = cells[cell_index]
            
            # Click on cell to focus
            await target_cell.click()
            
            # Find CodeMirror editor within cell
            editor = await target_cell.query_selector(self.selectors.CODE_EDITOR)
            
            if not editor:
                logger.error("Code editor not found in cell")
                return False
            
            # Click editor and insert code
            await editor.click()
            
            # Clear existing code (Ctrl+A, Delete)
            await self.page.keyboard.press("Control+A")
            await self.page.keyboard.press("Backspace")
            
            # Type new code
            await self.page.keyboard.type(code, delay=10)
            
            logger.info("Code inserted successfully")
            return True
        
        except Exception as e:
            logger.error("Failed to insert code", error=str(e), exc_info=True)
            return False
    
    async def run_cell(self, cell_index: int = -1) -> bool:
        """
        Run a specific cell
        
        Args:
            cell_index: Index of cell (-1 for last cell)
        
        Returns:
            True if execution started successfully
        """
        logger.info("Running cell", cell_index=cell_index)
        
        try:
            # Get all code cells
            cells = await self.page.query_selector_all(self.selectors.CODE_CELL)
            
            if not cells:
                logger.warning("No code cells found")
                return False
            
            # Select target cell
            target_cell = cells[cell_index]
            
            # Click on cell to focus
            await target_cell.click()
            
            # Press Shift+Enter to run
            await self.page.keyboard.press("Shift+Enter")
            
            logger.info("Cell execution started")
            return True
        
        except Exception as e:
            logger.error("Failed to run cell", error=str(e))
            return False
    
    async def wait_for_cell_execution(self, timeout: int = 60000) -> bool:
        """
        Wait for cell execution to complete
        
        Args:
            timeout: Maximum wait time in milliseconds
        
        Returns:
            True if execution completed
        """
        logger.info("Waiting for cell execution to complete")
        
        try:
            # TODO: Implement proper waiting logic
            # Check for:
            # - Execution count appears
            # - Spinner disappears
            # - Output appears
            
            # Placeholder: wait fixed time
            await self.page.wait_for_timeout(3000)
            
            logger.info("Cell execution completed")
            return True
        
        except Exception as e:
            logger.error("Error waiting for execution", error=str(e))
            return False
    
    async def get_cell_output(self, cell_index: int = -1) -> Optional[str]:
        """
        Get output text from a cell
        
        Args:
            cell_index: Index of cell (-1 for last cell)
        
        Returns:
            Output text or None if no output
        """
        logger.info("Getting cell output", cell_index=cell_index)
        
        try:
            # Get all code cells
            cells = await self.page.query_selector_all(self.selectors.CODE_CELL)
            
            if not cells:
                logger.warning("No code cells found")
                return None
            
            # Select target cell
            target_cell = cells[cell_index]
            
            # Find output area
            output = await target_cell.query_selector(self.selectors.OUTPUT_TEXT)
            
            if output:
                text = await output.inner_text()
                logger.info("Cell output retrieved", length=len(text))
                return text
            
            logger.info("No output found")
            return None
        
        except Exception as e:
            logger.error("Failed to get cell output", error=str(e))
            return None
    
    async def check_for_errors(self, cell_index: int = -1) -> Optional[str]:
        """
        Check if a cell has execution errors
        
        Args:
            cell_index: Index of cell (-1 for last cell)
        
        Returns:
            Error message if present, None otherwise
        """
        logger.info("Checking for errors", cell_index=cell_index)
        
        try:
            cells = await self.page.query_selector_all(self.selectors.CODE_CELL)
            
            if not cells:
                return None
            
            target_cell = cells[cell_index]
            
            # Find error output
            error = await target_cell.query_selector(self.selectors.OUTPUT_ERROR)
            
            if error:
                error_text = await error.inner_text()
                logger.warning("Error found in cell", error=error_text[:200])
                return error_text
            
            return None
        
        except Exception as e:
            logger.error("Failed to check for errors", error=str(e))
            return None
    
    async def clear_all_outputs(self) -> bool:
        """
        Clear all cell outputs in the notebook
        
        Returns:
            True if successful
        """
        logger.info("Clearing all outputs")
        
        try:
            # Click Edit menu
            await self.page.click(self.selectors.EDIT_MENU)
            await self.page.wait_for_timeout(500)
            
            # Click "Clear all outputs" option
            await self.page.click("text=Clear all outputs")
            
            logger.info("All outputs cleared")
            return True
        
        except Exception as e:
            logger.error("Failed to clear outputs", error=str(e))
            return False
