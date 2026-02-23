"""
NLP Processor for Sentinel-Net
Provides sentiment analysis, intent classification, risk scoring, and entity extraction
from development-related text (commits, issues, PRs)
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    # Download required NLTK data
    try:
        nltk.data.find('sentiment/vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False


@dataclass
class NLPAnalysis:
    """Result of NLP analysis on a text"""
    text: str
    sentiment_score: float  # -1 to 1
    sentiment_label: str  # negative, neutral, positive
    intent_category: str  # bug_fix, feature, refactor, docs, chore, test, unknown
    intent_confidence: float  # 0 to 1
    risk_level: str  # low, medium, high, critical
    risk_score: float  # 0 to 1
    keywords: List[str]  # Important terms extracted
    has_urgency: bool  # Contains urgent language
    is_bug_related: bool  # Likely bug-related
    factors: List[str]  # Contributing factors to analysis


class SentimentLabel(Enum):
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class IntentCategory(Enum):
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    DOCS = "docs"
    CHORE = "chore"
    TEST = "test"
    UNKNOWN = "unknown"
    SECURITY = "security"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NLPProcessor:
    """NLP analysis engine for development signals"""
    
    def __init__(self):
        """Initialize NLP processor with sentiment analyzer"""
        self.sentiment_analyzer = None
        if VADER_AVAILABLE:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Keyword patterns for classification
        self.intent_keywords = {
            IntentCategory.BUG_FIX: [
                r'fix', r'bug', r'issue', r'broken', r'crash', r'error',
                r'patch', r'resolve', r'correction', r'regression', r'hotfix'
            ],
            IntentCategory.FEATURE: [
                r'add', r'new', r'feature', r'implement', r'support',
                r'enable', r'introduce', r'launch', r'beta'
            ],
            IntentCategory.REFACTOR: [
                r'refactor', r'refactoring', r'cleanup', r'clean up',
                r'simplify', r'improve', r'optimize', r'enhance',
                r'restructure', r'reorganize'
            ],
            IntentCategory.DOCS: [
                r'doc', r'documentation', r'readme', r'comment',
                r'update docs', r'update documentation'
            ],
            IntentCategory.TEST: [
                r'test', r'tests', r'testing', r'coverage', r'assert',
                r'unittest', r'pytest', r'tdd'
            ],
            IntentCategory.SECURITY: [
                r'security', r'vulnerab', r'cve', r'xss', r'sql', r'csrf',
                r'exploit', r'breach', r'auth', r'encrypt'
            ],
            IntentCategory.CHORE: [
                r'chore', r'bump', r'update', r'upgrade', r'version',
                r'dependency', r'merge', r'sync'
            ]
        }
        
        # Risk indicators
        self.high_risk_patterns = [
            r'critical', r'severe', r'emergency', r'urgent', r'asap',
            r'crash', r'data loss', r'memory leak', r'infinite loop',
            r'security', r'vulnerab', r'exploit', r'breach'
        ]
        
        self.urgency_patterns = [
            r'urgent', r'asap', r'emergency', r'critical', r'immediately',
            r'now', r'hotfix', r'down', r'outage'
        ]
        
        self.bug_keywords = [
            r'bug', r'fix', r'crash', r'error', r'broken', r'issue',
            r'regression', r'fail', r'exception', r'undefined', r'null'
        ]
    
    def analyze(self, text: str) -> NLPAnalysis:
        """
        Perform comprehensive NLP analysis on text
        
        Args:
            text: Input text to analyze (commit message, issue title, etc.)
        
        Returns:
            NLPAnalysis object with all metrics
        """
        text_lower = text.lower().strip()
        
        # Sentiment analysis
        sentiment_score, sentiment_label = self._analyze_sentiment(text_lower)
        
        # Intent classification
        intent_category, intent_confidence = self._classify_intent(text_lower)
        
        # Risk scoring
        risk_level, risk_score = self._assess_risk(text_lower, sentiment_score)
        
        # Keyword extraction
        keywords = self._extract_keywords(text_lower)
        
        # Urgency detection
        has_urgency = self._check_urgency(text_lower)
        
        # Bug detection
        is_bug = self._check_bug_related(text_lower)
        
        # Contributing factors
        factors = self._extract_factors(text_lower, sentiment_score, intent_category, risk_level)
        
        return NLPAnalysis(
            text=text,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            intent_category=intent_category.value,
            intent_confidence=intent_confidence,
            risk_level=risk_level.value,
            risk_score=risk_score,
            keywords=keywords,
            has_urgency=has_urgency,
            is_bug_related=is_bug,
            factors=factors
        )
    
    def _analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of text using VADER
        
        Returns:
            (sentiment_score: -1 to 1, sentiment_label: 'negative'/'neutral'/'positive')
        """
        if not VADER_AVAILABLE or not self.sentiment_analyzer:
            return 0.0, SentimentLabel.NEUTRAL.value
        
        try:
            scores = self.sentiment_analyzer.polarity_scores(text)
            compound = scores['compound']  # -1 to 1
            
            if compound < -0.1:
                label = SentimentLabel.NEGATIVE.value
            elif compound > 0.1:
                label = SentimentLabel.POSITIVE.value
            else:
                label = SentimentLabel.NEUTRAL.value
            
            return float(compound), label
        except:
            return 0.0, SentimentLabel.NEUTRAL.value
    
    def _classify_intent(self, text: str) -> Tuple[IntentCategory, float]:
        """
        Classify intent of the commit/issue based on keywords
        
        Returns:
            (IntentCategory, confidence: 0 to 1)
        """
        max_matches = 0
        best_category = IntentCategory.UNKNOWN
        
        # Count keyword matches for each category
        for category, patterns in self.intent_keywords.items():
            matches = sum(
                len(re.findall(pattern, text, re.IGNORECASE))
                for pattern in patterns
            )
            
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        # Confidence based on match count (up to 5 matches = high confidence)
        confidence = min(max_matches / 5.0, 1.0) if max_matches > 0 else 0.0
        
        return best_category, confidence
    
    def _assess_risk(self, text: str, sentiment_score: float) -> Tuple[RiskLevel, float]:
        """
        Assess risk level based on keywords and sentiment
        
        Returns:
            (RiskLevel, risk_score: 0 to 1)
        """
        risk_score = 0.3  # Base risk
        
        # Check for high risk keywords
        high_risk_matches = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in self.high_risk_patterns
        )
        
        if high_risk_matches > 0:
            risk_score += min(high_risk_matches * 0.2, 0.4)
        
        # Negative sentiment increases risk
        if sentiment_score < -0.5:
            risk_score += 0.15
        elif sentiment_score < -0.2:
            risk_score += 0.05
        
        # Clamp to 0-1
        risk_score = min(risk_score, 1.0)
        
        # Determine level
        if risk_score > 0.7:
            level = RiskLevel.CRITICAL
        elif risk_score > 0.5:
            level = RiskLevel.HIGH
        elif risk_score > 0.35:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return level, risk_score
    
    def _extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract important keywords from text
        (removes common stopwords and technical terms)
        """
        try:
            if VADER_AVAILABLE:
                from nltk.corpus import stopwords
                stop_words = set(stopwords.words('english'))
            else:
                # Fallback stopwords
                stop_words = {
                    'a', 'an', 'and', 'the', 'is', 'to', 'in', 'for',
                    'of', 'with', 'from', 'by', 'on', 'at', 'this', 'that'
                }
            
            # Split and clean words
            words = re.findall(r'\b[a-z]+\b', text.lower())
            keywords = [
                w for w in words
                if len(w) > 3 and w not in stop_words
            ]
            
            # Get unique keywords, limiting to top_n
            return list(dict.fromkeys(keywords))[:top_n]
        except:
            return []
    
    def _check_urgency(self, text: str) -> bool:
        """Check if text contains urgent language"""
        matches = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in self.urgency_patterns
        )
        return matches > 0
    
    def _check_bug_related(self, text: str) -> bool:
        """Check if text is bug-related"""
        matches = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in self.bug_keywords
        )
        return matches > 0
    
    def _extract_factors(
        self,
        text: str,
        sentiment_score: float,
        intent_category: IntentCategory,
        risk_level: RiskLevel
    ) -> List[str]:
        """Extract contributing factors for analysis"""
        factors = []
        
        # Sentiment factors
        if sentiment_score < -0.5:
            factors.append("Negative sentiment detected")
        elif sentiment_score > 0.3:
            factors.append("Positive sentiment in message")
        
        # Intent factors
        intent_str = intent_category.value.replace('_', ' ').title()
        factors.append(f"Classification: {intent_str}")
        
        # Risk factors
        factors.append(f"Risk level: {risk_level.value.title()}")
        
        # Content factors
        if len(text.split()) > 50:
            factors.append("Detailed description provided")
        elif len(text.split()) < 5:
            factors.append("Brief message")
        
        # Urgency
        if self._check_urgency(text):
            factors.append("Urgent language detected")
        
        return factors


def analyze_batch(texts: List[str]) -> List[NLPAnalysis]:
    """
    Analyze multiple texts efficiently
    
    Args:
        texts: List of texts to analyze
    
    Returns:
        List of NLPAnalysis objects
    """
    processor = NLPProcessor()
    return [processor.analyze(text) for text in texts]


# Singleton instance for consistency
_processor = None

def get_processor() -> NLPProcessor:
    """Get or create NLP processor singleton"""
    global _processor
    if _processor is None:
        _processor = NLPProcessor()
    return _processor
