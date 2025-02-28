from typing import Any, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.infrastructure.ai.anthropic.client import ClaudeClient
from app.infrastructure.database.chromadb.client import ChromaDBClient
from app.infrastructure.amazon.client import AmazonClient
from app.core.logging.logging_config import logger
from app.shared.exceptions.base import AppException
from app.core.config.settings import get_settings

settings = get_settings()

class AIService:
    """Service for AI-powered features combining Claude, ChromaDB, and product recommendations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.claude = ClaudeClient()
            self.chromadb = ChromaDBClient()
            self.amazon = AmazonClient()
            self.logger = logger
            self._initialized = True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_text_with_context(
        self,
        text: str,
        context_collection: str,
        instruction: str,
        n_context: int = 3
    ) -> Dict[str, Any]:
        """Analyze text with relevant context from ChromaDB"""
        try:
            # Query relevant context
            context_results = await self.chromadb.query(
                collection_name=context_collection,
                query_texts=[text],
                n_results=n_context
            )
            
            if not context_results['documents'][0]:
                self.logger.warning(f"No context found in collection {context_collection}")
                return {
                    'analysis': await self.claude.analyze_document(
                        document=text,
                        instruction=instruction
                    ),
                    'context_used': [],
                    'context_metadata': []
                }
            
            # Combine context documents
            context = "\n\n".join(context_results['documents'][0])
            
            # Analyze with Claude
            analysis = await self.claude.analyze_document(
                document=text,
                instruction=f"Context:\n{context}\n\n{instruction}"
            )
            
            return {
                'analysis': analysis,
                'context_used': context_results['documents'][0],
                'context_metadata': context_results['metadatas'][0]
            }
            
        except Exception as e:
            self.logger.error(f"Analysis error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to analyze text: {str(e)}")

    async def generate_product_recommendations(
        self,
        user_input: str,
        max_products: int = 5
    ) -> Dict[str, Any]:
        """Generate personalized product recommendations"""
        try:
            # Generate search keywords with Claude
            prompt = f"""
            Based on the following user input, generate 3-5 relevant product search keywords.
            Format the response as a comma-separated list.
            
            User Input: {user_input}
            """
            
            keywords_response = await self.claude.generate_response(prompt)
            keywords = [k.strip() for k in keywords_response.split(',')]
            
            # Search products for each keyword
            all_products = []
            for keyword in keywords:
                products = await self.amazon.search_items(
                    keywords=keyword,
                    max_results=3
                )
                all_products.extend(products)
            
            # Generate personalized descriptions with Claude
            recommendations = []
            for product in all_products[:max_products]:
                prompt = f"""
                Generate a personalized product recommendation based on the user's input and product details.
                Keep it concise (2-3 sentences) and highlight why it's relevant.
                
                User Input: {user_input}
                Product: {product['title']}
                Features: {', '.join(product.get('features', []))}
                """
                
                description = await self.claude.generate_response(
                    prompt,
                    max_tokens=200
                )
                
                recommendations.append({
                    **product,
                    'personalized_description': description
                })
            
            return {
                'recommendations': recommendations,
                'keywords_used': keywords
            }
            
        except Exception as e:
            self.logger.error(f"Recommendation error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to generate recommendations: {str(e)}")

    async def store_and_analyze_document(
        self,
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: str = "documents"
    ) -> Dict[str, Any]:
        """Store document in ChromaDB and analyze it"""
        try:
            # Store in ChromaDB
            await self.chromadb.add_documents(
                collection_name=collection_name,
                documents=[document],
                metadatas=[metadata] if metadata else None
            )
            
            # Generate analysis with Claude
            analysis = await self.claude.analyze_document(
                document=document,
                instruction="Provide a comprehensive analysis of this document, including:\n"
                          "1. Main topics and themes\n"
                          "2. Key insights\n"
                          "3. Potential applications or recommendations"
            )
            
            return {
                'analysis': analysis,
                'stored_in_collection': collection_name,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Document processing error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to process document: {str(e)}")

    async def semantic_search(
        self,
        query: str,
        collection_name: str,
        n_results: int = 5,
        rerank: bool = True
    ) -> Dict[str, Any]:
        """Perform semantic search with optional Claude-based reranking"""
        try:
            # Initial ChromaDB search
            results = await self.chromadb.query(
                collection_name=collection_name,
                query_texts=[query],
                n_results=n_results * 2 if rerank else n_results
            )
            
            if not rerank:
                return {
                    'results': [
                        {
                            'document': doc,
                            'metadata': meta,
                            'score': 1 - dist  # Convert distance to similarity score
                        }
                        for doc, meta, dist in zip(
                            results['documents'][0],
                            results['metadatas'][0],
                            results['distances'][0]
                        )
                    ][:n_results]
                }
            
            # Rerank with Claude
            documents = results['documents'][0]
            prompt = f"""
            Rate each document's relevance to the query on a scale of 0-100.
            Provide the score and a brief explanation for each.
            Format: score|explanation
            
            Query: {query}
            
            Documents to rate:
            {chr(10).join(f"{i+1}. {doc}" for i, doc in enumerate(documents))}
            """
            
            rankings = await self.claude.generate_response(prompt)
            
            # Parse rankings and sort results
            ranked_results = []
            for i, (score_exp, doc, meta) in enumerate(zip(
                rankings.split('\n'),
                documents,
                results['metadatas'][0]
            )):
                try:
                    score, explanation = score_exp.split('|')
                    score = float(score.strip())
                    ranked_results.append({
                        'document': doc,
                        'metadata': meta,
                        'score': score / 100,
                        'explanation': explanation.strip()
                    })
                except Exception:
                    self.logger.warning(f"Failed to parse ranking for document {i}")
                    continue
            
            ranked_results.sort(key=lambda x: x['score'], reverse=True)
            
            return {'results': ranked_results[:n_results]}
            
        except Exception as e:
            self.logger.error(f"Search error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to perform search: {str(e)}")