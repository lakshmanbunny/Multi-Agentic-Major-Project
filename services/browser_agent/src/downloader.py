"""
Dataset Downloader

Handles downloading datasets from various sources (HTTP, Kaggle, etc.)
"""

import os
from pathlib import Path
from typing import Optional

import httpx

from core import setup_logger

logger = setup_logger("downloader", level="INFO")


class DatasetDownloader:
    """
    Download datasets from various sources
    
    Supports:
    - Direct HTTP/HTTPS URLs
    - Kaggle datasets (requires API key)
    - Google Drive links
    """
    
    def __init__(self, download_dir: str = "./data"):
        """
        Initialize downloader
        
        Args:
            download_dir: Directory to save downloaded datasets
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("DatasetDownloader initialized", download_dir=str(self.download_dir))
    
    async def download(self, url: str, destination: Optional[str] = None) -> str:
        """
        Download dataset from URL
        
        Args:
            url: Dataset URL
            destination: Optional custom destination path
        
        Returns:
            Path to downloaded file
        """
        logger.info("Starting download", url=url)
        
        # Determine file name from URL or destination
        if destination:
            file_path = Path(destination)
        else:
            file_name = url.split("/")[-1].split("?")[0] or "dataset.csv"
            file_path = self.download_dir / file_name
        
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use httpx for async HTTP requests
            async with httpx.AsyncClient(follow_redirects=True) as client:
                logger.info("Fetching dataset", url=url)
                
                response = await client.get(url, timeout=60.0)
                response.raise_for_status()
                
                # Write to file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                
                logger.info(
                    "Download complete",
                    file_path=str(file_path),
                    size_bytes=file_size
                )
                
                return str(file_path.absolute())
        
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error during download", status_code=e.response.status_code, url=url)
            raise Exception(f"Failed to download: HTTP {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error("Request error during download", error=str(e), url=url)
            raise Exception(f"Failed to download: {str(e)}")
        
        except Exception as e:
            logger.error("Unexpected error during download", error=str(e), exc_info=True)
            raise
    
    async def download_from_kaggle(self, dataset_id: str, file_name: Optional[str] = None) -> str:
        """
        Download dataset from Kaggle
        
        Args:
            dataset_id: Kaggle dataset identifier (e.g., "username/dataset-name")
            file_name: Optional specific file to download
        
        Returns:
            Path to downloaded file
        
        Note:
            Requires KAGGLE_USERNAME and KAGGLE_KEY environment variables
        """
        logger.info("Downloading from Kaggle", dataset_id=dataset_id)
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            api = KaggleApi()
            api.authenticate()
            
            # Download dataset
            download_path = str(self.download_dir)
            
            if file_name:
                api.dataset_download_file(dataset_id, file_name, path=download_path)
                file_path = self.download_dir / file_name
            else:
                api.dataset_download_files(dataset_id, path=download_path, unzip=True)
                # Return path to directory
                file_path = self.download_dir / dataset_id.split('/')[-1]
            
            logger.info("Kaggle download complete", file_path=str(file_path))
            
            return str(file_path.absolute())
        
        except ImportError:
            logger.error("Kaggle library not installed")
            raise Exception("Kaggle library not installed. Install with: pip install kaggle")
        
        except Exception as e:
            logger.error("Kaggle download failed", error=str(e), exc_info=True)
            raise
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is accessible
        
        Args:
            url: URL to validate
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            import httpx
            
            with httpx.Client() as client:
                response = client.head(url, follow_redirects=True, timeout=10.0)
                return response.status_code == 200
        
        except Exception as e:
            logger.warning("URL validation failed", url=url, error=str(e))
            return False
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get size of downloaded file
        
        Args:
            file_path: Path to file
        
        Returns:
            File size in bytes
        """
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error("Failed to get file size", file_path=file_path, error=str(e))
            return 0
