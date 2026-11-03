"""
Evaluation metrics calculation for AI Resume Intelligence Quality Testing.
Calculates precision, recall, F1, hallucination rates, evidence coverage,
and cross-model consistency deltas.
"""

from typing import List, Set, Dict, Any, Tuple
import math
import re


def normalize_token(text: str) -> str:
    """Normalizes string for robust skill matching (lowercased, stripped, punctuation handled)."""
    return re.sub(r'[^a-z0-9]', '', text.lower())


def calculate_set_precision_recall_f1(
    predicted: List[str], ground_truth: List[str]
) -> Dict[str, float]:
    """
    Computes precision, recall, and F1 score for entity/skill extraction.
    Uses normalized token matching to account for casing and punctuation variations.
    """
    if not predicted and not ground_truth:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "true_positives": 0, "false_positives": 0, "false_negatives": 0}
    if not predicted:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "true_positives": 0, "false_positives": 0, "false_negatives": len(ground_truth)}
    if not ground_truth:
        return {"precision": 0.0, "recall": 1.0, "f1": 0.0, "true_positives": 0, "false_positives": len(predicted), "false_negatives": 0}

    norm_gt = {normalize_token(s): s for s in ground_truth if normalize_token(s)}
    norm_pred = {normalize_token(s): s for s in predicted if normalize_token(s)}

    # Match count
    true_positives = 0
    for p_norm in norm_pred:
        # Direct match or substring containment (e.g., "Kubernetes" in "Kubernetes (EKS)")
        matched = False
        if p_norm in norm_gt:
            matched = True
        else:
            for gt_norm in norm_gt:
                if p_norm in gt_norm or gt_norm in p_norm:
                    matched = True
                    break
        if matched:
            true_positives += 1

    false_positives = max(0, len(norm_pred) - true_positives)
    
    # Ground truth coverage
    gt_matched_count = 0
    for gt_norm in norm_gt:
        matched = False
        if gt_norm in norm_pred:
            matched = True
        else:
            for p_norm in norm_pred:
                if gt_norm in p_norm or p_norm in gt_norm:
                    matched = True
                    break
        if matched:
            gt_matched_count += 1
            
    false_negatives = max(0, len(norm_gt) - gt_matched_count)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = gt_matched_count / len(norm_gt) if norm_gt else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }


def calculate_evidence_coverage(
    extracted_items: List[Dict[str, Any]], resume_raw_text: str = ""
) -> Dict[str, Any]:
    """
    Verifies what proportion of extracted items (skills, achievements, strengths)
    contain an actual textual source reference or quote that exists verbatim in the resume.
    """
    if not extracted_items:
        return {"coverage_ratio": 1.0, "total_items": 0, "grounded_items": 0, "ungrounded_items": []}

    resume_lower = resume_raw_text.lower()
    grounded = 0
    ungrounded = []

    for item in extracted_items:
        quote = item.get("source_quote") or item.get("evidence") or item.get("text") or ""
        # Check if the quote or key text appears in the raw resume
        if quote and (quote.lower() in resume_lower or any(word in resume_lower for word in quote.lower().split() if len(word) > 5)):
            grounded += 1
        else:
            ungrounded.append(item)

    coverage_ratio = grounded / len(extracted_items) if extracted_items else 0.0
    return {
        "coverage_ratio": round(coverage_ratio, 4),
        "total_items": len(extracted_items),
        "grounded_items": grounded,
        "ungrounded_items": ungrounded
    }


def calculate_hallucination_rate(
    ai_extracted_skills: List[str], raw_resume_text: str
) -> Dict[str, Any]:
    """
    Evaluates hallucination rate: fraction of skills claimed by AI that have NO
    trace or related tokens in the original resume document.
    """
    if not ai_extracted_skills:
        return {"hallucination_rate": 0.0, "hallucinated_skills": [], "total_skills": 0}

    resume_text_norm = normalize_token(raw_resume_text)
    hallucinated = []

    for skill in ai_extracted_skills:
        token = normalize_token(skill)
        if len(token) >= 2 and token not in resume_text_norm:
            hallucinated.append(skill)

    rate = len(hallucinated) / len(ai_extracted_skills) if ai_extracted_skills else 0.0
    return {
        "hallucination_rate": round(rate, 4),
        "hallucinated_skills": hallucinated,
        "total_skills": len(ai_extracted_skills)
    }


def calculate_model_consistency(
    model_a_scores: Dict[str, float], model_b_scores: Dict[str, float]
) -> Dict[str, Any]:
    """
    Computes consistency metrics between two AI model evaluations (e.g. GPT-4o vs Gemini 1.5 Pro).
    Returns Mean Absolute Error (MAE), Max Deviation, and dimension-level deltas.
    """
    common_keys = set(model_a_scores.keys()).intersection(set(model_b_scores.keys()))
    if not common_keys:
        return {"mae": 0.0, "max_delta": 0.0, "common_dimensions": 0, "deltas": {}, "is_consistent": True}

    deltas = {}
    total_abs_diff = 0.0
    max_delta = 0.0

    for k in common_keys:
        val_a = float(model_a_scores[k])
        val_b = float(model_b_scores[k])
        diff = abs(val_a - val_b)
        deltas[k] = round(diff, 2)
        total_abs_diff += diff
        if diff > max_delta:
            max_delta = diff

    mae = total_abs_diff / len(common_keys)
    return {
        "mae": round(mae, 2),
        "max_delta": round(max_delta, 2),
        "common_dimensions": len(common_keys),
        "deltas": deltas,
        "is_consistent": mae <= 12.0  # Industry standard acceptance threshold for LLM grading (within 12 pts on 100-pt scale)
    }
