import sys
import os
import json
import logging
import math
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.engine.pipeline import RecommendationPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def dcg_at_k(relevance_scores, k):
    relevance_scores = relevance_scores[:k]
    return sum(rel / math.log2(idx + 2) for idx, rel in enumerate(relevance_scores))

def ndcg_at_k(relevance_scores, k):
    dcg = dcg_at_k(relevance_scores, k)
    ideal_relevance_scores = sorted(relevance_scores, reverse=True)
    idcg = dcg_at_k(ideal_relevance_scores, k)
    if idcg == 0:
        return 0.0
    return dcg / idcg

def evaluate():
    dataset_path = Path(__file__).resolve().parents[1] / "evaluation" / "retrieval_ground_truth.json"
    if not dataset_path.exists():
        logger.error(f"Evaluation dataset not found at {dataset_path}")
        return
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    db = SessionLocal()
    pipeline = RecommendationPipeline(db)
    
    total_p5 = 0.0
    total_r10 = 0.0
    total_mrr = 0.0
    total_ndcg = 0.0
    n_queries = len(dataset)
    
    logger.info(f"Evaluating {n_queries} queries...")
    
    try:
        for data in dataset:
            query = data["query"]
            expected = [e.lower() for e in data["expected"]]
            
            # Retrieve top 10
            context = {}  # No personalization for baseline eval
            results = pipeline.run(query, context, limit=10)
            
            # Collect results' names
            retrieved_names = [r.name.lower() for r in results]
            
            # Calculate metrics
            relevance = [1 if name in expected else 0 for name in retrieved_names]
            
            # Precision@5
            p5 = sum(relevance[:5]) / 5.0
            total_p5 += p5
            
            # Recall@10
            # Assuming all expected are relevant and nothing else is. True total relevant is len(expected)
            r10 = sum(relevance[:10]) / len(expected) if expected else 0.0
            total_r10 += r10
            
            # MRR
            mrr = 0.0
            for idx, rel in enumerate(relevance):
                if rel == 1:
                    mrr = 1.0 / (idx + 1)
                    break
            total_mrr += mrr
            
            # NDCG@10
            ndcg = ndcg_at_k(relevance, 10)
            total_ndcg += ndcg
            
            logger.info(f"Query: '{query}' -> P@5: {p5:.2f}, R@10: {r10:.2f}, MRR: {mrr:.2f}, NDCG: {ndcg:.2f}")

        # Averages
        avg_p5 = total_p5 / n_queries if n_queries > 0 else 0
        avg_r10 = total_r10 / n_queries if n_queries > 0 else 0
        avg_mrr = total_mrr / n_queries if n_queries > 0 else 0
        avg_ndcg = total_ndcg / n_queries if n_queries > 0 else 0
        
        logger.info("\n=== EVALUATION RESULTS ===")
        logger.info(f"Precision@5: {avg_p5:.4f}")
        logger.info(f"Recall@10:   {avg_r10:.4f}")
        logger.info(f"MRR:         {avg_mrr:.4f}")
        logger.info(f"NDCG:        {avg_ndcg:.4f}")
        
    finally:
        db.close()

if __name__ == "__main__":
    evaluate()
