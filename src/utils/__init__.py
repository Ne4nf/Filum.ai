"""
Utility functions for Pain Point to Solution Agent
Helper functions for text processing, validation, etc.
"""

import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


def normalize_text(text: str) -> str:
    """
    Normalize text for consistent processing

    Args:
        text: Raw text input

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Lowercase and remove extra whitespace
    text = text.lower().strip()

    # Remove special characters except Vietnamese accents
    text = re.sub(
        r"[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]",
        " ",
        text,
    )

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text

    Args:
        text: Input text
        min_length: Minimum length of keyword

    Returns:
        List of unique keywords
    """
    # English stop words
    stop_words = {
        # English
        "and",
        "or",
        "the",
        "a",
        "an",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "among",
        "this",
        "that",
        "these",
        "those",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "could",
        "can",
        "may",
        "might",
        "must",
    }

    # Normalize text
    normalized = normalize_text(text)

    # Extract words
    words = re.findall(r"\b\w+\b", normalized)

    # Filter keywords
    keywords = [
        word for word in words if len(word) >= min_length and word not in stop_words
    ]

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)

    return unique_keywords


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between 2 texts based on keyword overlap

    Args:
        text1, text2: Texts to compare

    Returns:
        Similarity score from 0.0 to 1.0
    """
    if not text1 or not text2:
        return 0.0

    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))

    if not keywords1 or not keywords2:
        return 0.0

    # Jaccard similarity
    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)

    return len(intersection) / len(union) if union else 0.0


def validate_pain_point_input(data: Dict[str, Any]) -> List[str]:
    """
    Validate pain point input data

    Args:
        data: Input data dict

    Returns:
        List of validation errors
    """
    errors = []

    # Check required fields
    if "pain_point" not in data:
        errors.append("Missing 'pain_point' field")
        return errors

    pain_point = data["pain_point"]

    if not isinstance(pain_point, dict):
        errors.append("'pain_point' must be a dictionary")
        return errors

    # Check description
    if "description" not in pain_point:
        errors.append("Missing 'pain_point.description' field")
    elif not isinstance(pain_point["description"], str):
        errors.append("'pain_point.description' must be a string")
    elif len(pain_point["description"].strip()) < 10:
        errors.append("'pain_point.description' must be at least 10 characters")

    # Check optional context fields
    if "context" in pain_point:
        context = pain_point["context"]
        if not isinstance(context, dict):
            errors.append("'pain_point.context' must be a dictionary")
        else:
            # Check company_size if provided
            if "company_size" in context:
                valid_sizes = ["startup", "small", "medium", "large", "enterprise"]
                if context["company_size"] not in valid_sizes:
                    errors.append(f"'company_size' must be one of: {valid_sizes}")

            # Check urgency_level if provided
            if "urgency_level" in context:
                valid_urgency = ["low", "medium", "high"]
                if context["urgency_level"] not in valid_urgency:
                    errors.append(f"'urgency_level' must be one of: {valid_urgency}")

    # Check affected_areas
    if "affected_areas" in pain_point:
        if not isinstance(pain_point["affected_areas"], list):
            errors.append("'affected_areas' must be a list")

    return errors


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file with error handling

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in file {file_path}: {e}", e.doc, e.pos
        )


def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """
    Save data to JSON file

    Args:
        data: Data to save
        file_path: Output file path
        indent: JSON indentation
    """
    file_path = Path(file_path)

    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def format_currency(amount: float, currency: str = "VND") -> str:
    """
    Format currency with thousands separator

    Args:
        amount: Money amount
        currency: Currency type

    Returns:
        Formatted currency string
    """
    if currency.upper() == "VND":
        return f"{amount:,.0f} đ"
    elif currency.upper() == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between 2 values

    Args:
        old_value: Old value
        new_value: New value

    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0.0 if new_value == 0 else float("inf")

    return ((new_value - old_value) / old_value) * 100


def generate_hash_id(text: str, length: int = 8) -> str:
    """
    Generate hash ID from text

    Args:
        text: Input text
        length: Length of hash ID

    Returns:
        Hash ID string
    """
    import hashlib

    # Create hash
    hash_object = hashlib.md5(text.encode("utf-8"))
    hash_hex = hash_object.hexdigest()

    return hash_hex[:length]


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text with suffix

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def is_email_valid(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email string

    Returns:
        True if valid email format
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def clean_phone_number(phone: str) -> str:
    """
    Clean and format phone number

    Args:
        phone: Raw phone number

    Returns:
        Cleaned phone number
    """
    # Remove all non-digits
    digits_only = re.sub(r"\D", "", phone)

    # Add country code if missing (Vietnam)
    if len(digits_only) == 10 and digits_only.startswith("0"):
        digits_only = "84" + digits_only[1:]
    elif len(digits_only) == 9:
        digits_only = "84" + digits_only

    return digits_only


def get_industry_keywords(industry: str) -> List[str]:
    """
    Get characteristic keywords for each industry

    Args:
        industry: Industry name

    Returns:
        List of keywords
    """
    industry_keywords = {
        "e-commerce": [
            "online",
            "website",
            "cart",
            "checkout",
            "product",
            "order",
            "shipping",
        ],
        "banking": [
            "account",
            "transaction",
            "loan",
            "credit",
            "payment",
            "financial",
            "deposit",
        ],
        "healthcare": [
            "patient",
            "doctor",
            "medical",
            "treatment",
            "appointment",
            "hospital",
            "clinic",
        ],
        "retail": [
            "store",
            "customer",
            "purchase",
            "sales",
            "inventory",
            "cashier",
            "pos",
        ],
        "technology": [
            "software",
            "system",
            "platform",
            "user",
            "feature",
            "bug",
            "update",
        ],
        "telecom": [
            "network",
            "call",
            "data",
            "mobile",
            "internet",
            "signal",
            "subscriber",
        ],
        "insurance": [
            "policy",
            "claim",
            "coverage",
            "premium",
            "risk",
            "underwriting",
            "agent",
        ],
    }

    return industry_keywords.get(industry.lower(), [])


def estimate_implementation_time(complexity: str, company_size: str) -> str:
    """
    Estimate implementation time dựa trên complexity và company size

    Args:
        complexity: low, medium, high
        company_size: startup, small, medium, large, enterprise

    Returns:
        Estimated time string
    """
    base_times = {
        "low": {
            "startup": "1-2 weeks",
            "small": "2-3 weeks",
            "medium": "3-4 weeks",
            "large": "4-6 weeks",
            "enterprise": "6-8 weeks",
        },
        "medium": {
            "startup": "3-4 weeks",
            "small": "4-6 weeks",
            "medium": "6-8 weeks",
            "large": "8-12 weeks",
            "enterprise": "12-16 weeks",
        },
        "high": {
            "startup": "6-8 weeks",
            "small": "8-12 weeks",
            "medium": "12-16 weeks",
            "large": "16-24 weeks",
            "enterprise": "24-32 weeks",
        },
    }

    return base_times.get(complexity, {}).get(company_size, "4-8 weeks")


class TextAnalyzer:
    """Class for text analysis with advanced methods"""

    def __init__(self):
        self.sentiment_keywords = {
            "positive": [
                "good",
                "excellent",
                "amazing",
                "great",
                "love",
                "perfect",
                "wonderful",
                "fantastic",
            ],
            "negative": [
                "bad",
                "terrible",
                "awful",
                "hate",
                "worst",
                "horrible",
                "disappointing",
                "frustrating",
            ],
            "neutral": ["okay", "fine", "normal", "average", "acceptable"],
        }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Basic sentiment analysis of text

        Args:
            text: Input text

        Returns:
            Dict với sentiment score và label
        """
        text_lower = text.lower()

        scores = {"positive": 0, "negative": 0, "neutral": 0}

        for sentiment, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                scores[sentiment] += text_lower.count(keyword)

        total_score = sum(scores.values())
        if total_score == 0:
            return {"label": "neutral", "confidence": 0.5, "scores": scores}

        # Normalize scores
        normalized_scores = {k: v / total_score for k, v in scores.items()}

        # Determine primary sentiment
        primary_sentiment = max(
            normalized_scores.keys(), key=lambda k: normalized_scores[k]
        )
        confidence = normalized_scores[primary_sentiment]

        return {
            "label": primary_sentiment,
            "confidence": confidence,
            "scores": normalized_scores,
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract basic entities from text

        Args:
            text: Input text

        Returns:
            Dict with classified entities
        """
        entities = {"tools": [], "metrics": [], "timeframes": [], "departments": []}

        # Tool patterns
        tool_patterns = [
            r"\b(CRM|ERP|API|platform|system|software|tool|application)\b",
            r"\b\w+\.com\b",  # URLs
            r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # Capitalized tool names
        ]

        # Metric patterns
        metric_patterns = [
            r"\b\d+%\b",  # Percentages
            r"\b\d+\s*(hours?|minutes?|seconds?|days?|weeks?|months?)\b",  # Time metrics
            r"\b\d+\s*(customers?|users?|tickets?|calls?)\b",  # Count metrics
        ]

        # Department patterns
        dept_patterns = [
            r"\b(customer service|marketing|sales|support|IT|technical|operations)\b"
        ]

        text_lower = text.lower()

        # Extract tools
        for pattern in tool_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["tools"].extend(matches)

        # Extract metrics
        for pattern in metric_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            entities["metrics"].extend(matches)

        # Extract departments
        for pattern in dept_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            entities["departments"].extend(matches)

        # Clean duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities
