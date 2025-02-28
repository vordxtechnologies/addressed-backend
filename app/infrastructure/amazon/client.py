from typing import Any, Dict, List, Optional
import boto3
from botocore.exceptions import ClientError
from app.core.config.settings import get_settings
from app.core.logging.logging_config import logger
from app.shared.exceptions.base import AppException

settings = get_settings()

class AmazonClient:
    """Client for interacting with Amazon's Product Advertising API"""
    
    def __init__(self):
        self.client = boto3.client(
            'paapi5',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.marketplace = settings.AMAZON_MARKETPLACE
        self.partner_tag = settings.AMAZON_PARTNER_TAG
        self.logger = logger

    async def search_items(
        self,
        keywords: str,
        category: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for items on Amazon"""
        try:
            params = {
                'Keywords': keywords,
                'Marketplace': self.marketplace,
                'PartnerTag': self.partner_tag,
                'PartnerType': 'Associates',
                'Resources': [
                    'ItemInfo.Title',
                    'Offers.Listings.Price',
                    'Images.Primary.Large'
                ]
            }
            
            if category:
                params['SearchIndex'] = category

            response = await self.client.search_items(**params)
            
            if 'ItemsResult' not in response:
                return []
                
            items = response['ItemsResult']['Items'][:max_results]
            
            return [self._format_item(item) for item in items]

        except ClientError as e:
            self.logger.error(f"Amazon API error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to search items: {str(e)}")

    async def get_item_details(self, asin: str) -> Dict[str, Any]:
        """Get detailed information about a specific item"""
        try:
            response = await self.client.get_items(
                ItemIds=[asin],
                Marketplace=self.marketplace,
                PartnerTag=self.partner_tag,
                PartnerType='Associates',
                Resources=[
                    'ItemInfo.Title',
                    'ItemInfo.Features',
                    'ItemInfo.ProductInfo',
                    'Offers.Listings.Price',
                    'Images.Primary.Large',
                    'Images.Variants.Large'
                ]
            )
            
            if 'ItemsResult' not in response:
                raise AppException(f"Item {asin} not found")
                
            item = response['ItemsResult']['Items'][0]
            return self._format_item(item, detailed=True)

        except ClientError as e:
            self.logger.error(f"Amazon API error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to get item details: {str(e)}")

    def _format_item(self, item: Dict[str, Any], detailed: bool = False) -> Dict[str, Any]:
        """Format item data for response"""
        formatted = {
            'asin': item['ASIN'],
            'title': item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', ''),
            'url': item.get('DetailPageURL', ''),
            'image_url': item.get('Images', {}).get('Primary', {}).get('Large', {}).get('URL', '')
        }
        
        if 'Offers' in item and item['Offers']['Listings']:
            price_info = item['Offers']['Listings'][0]['Price']
            formatted['price'] = {
                'amount': price_info.get('Amount', 0),
                'currency': price_info.get('Currency', 'USD')
            }
            
        if detailed:
            formatted.update({
                'features': item.get('ItemInfo', {}).get('Features', {}).get('DisplayValues', []),
                'product_info': item.get('ItemInfo', {}).get('ProductInfo', {}),
                'variant_images': [
                    img['Large']['URL']
                    for img in item.get('Images', {}).get('Variants', [])
                    if 'Large' in img
                ]
            })
            
        return formatted 