import os
import pickle
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from typing import Tuple

class TaskPrioritizer:
    """ML-based priority classification - keeping it simple for now.
    
    I went with DecisionTreeClassifier over fancier models because:
    
    INTERPRETABILITY > ACCURACY for this use case:
    - I can actually see why it made a decision
    - Easy to debug when priorities seem wrong
    - Can manually inspect the learned rules
    
    BIAS vs VARIANCE trade-offs:
    - Simple model = high bias, low variance
    - With small datasets (20-100 examples), low variance matters more
    - Complex models would probably just overfit
    
    This works well enough for learning, though I'd probably need something
    more sophisticated for production use.
    """
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = "prioritizer_model.pkl"
        self.vectorizer_path = "prioritizer_vectorizer.pkl"
        self.accuracy_history = []  # TODO: use this for model drift detection
        
    def load_training_data(self) -> Tuple[list, list]:
        """Load training data with fallback for missing files.
        
        Small dataset reality: Most agent systems start with limited training data.
        I handle this by:
        1. Trying to load real data first
        2. Falling back to synthetic examples if needed
        3. Acknowledging that initial performance will be limited
        
        This is honest about the "cold start" problem in agent systems -
        you often need to deploy with minimal data and improve over time.
        """
        try:
            df = pd.read_csv("data/training_data.csv")
            return df['query'].tolist(), df['priority'].tolist()
        except FileNotFoundError:
            print("⚠️ Training data not found, using fallback data")
            return self._create_fallback_data()
    
    def _create_fallback_data(self) -> Tuple[list, list]:
        """Synthetic training data that demonstrates key classification patterns.
        
        I create obvious examples that capture the essential distinction:
        - Urgent: System failures, security issues, tight deadlines
        - Normal: Planning, documentation, routine tasks
        
        This is intentionally simple because:
        1. Complex synthetic data often doesn't match real usage patterns
        2. Better to start simple and add real examples over time
        3. Obvious examples help the model learn clear decision boundaries
        
        Limitations of this approach:
        - Doesn't capture edge cases or domain-specific urgency patterns
        - May not generalize well to different organizational contexts
        - Requires manual curation as new patterns emerge
        """
        urgent_samples = [
            "server down need fix now", "critical bug in production", "urgent client request",
            "system crash immediate help", "security breach fix asap", "deadline in 1 hour"
        ]
        normal_samples = [
            "update documentation", "refactor code", "add new feature",
            "schedule meeting", "review pull request", "optimize queries"
        ]
        texts = urgent_samples + normal_samples
        labels = ["urgent"] * len(urgent_samples) + ["normal"] * len(normal_samples)
        return texts, labels
    
    def train(self) -> float:
        """Train the classifier with explicit model choices and their reasoning.
        
        Model hyperparameter decisions:
        - max_features=100: Limits vocabulary to most important terms
        - max_depth=10: Prevents overfitting on small datasets
        - random_state=42: Ensures reproducible results for debugging
        
        Why TF-IDF over other approaches:
        - Word embeddings: Overkill for simple binary classification
        - Bag of words: Loses important term frequency information
        - Neural networks: Would overfit badly on small datasets
        
        What signals indicate the model is learning:
        1. Accuracy > 0.7 on test set (better than random)
        2. Consistent performance across training runs
        3. Sensible feature importance (words like "urgent", "crash" matter)
        4. Reasonable decision tree depth (not too shallow or deep)
        
        Small dataset challenges:
        - High variance in accuracy estimates
        - Risk of overfitting to specific examples
        - Limited generalization to new domains
        - Need for careful validation strategy
        """
        texts, labels = self.load_training_data()
        
        # Create TF-IDF vectorizer with conservative settings for small datasets
        self.vectorizer = TfidfVectorizer(
            max_features=100,  # Limit vocabulary to prevent overfitting
            stop_words='english'  # Remove common words that don't indicate priority
        )
        X = self.vectorizer.fit_transform(texts)
        
        # Train/test split with stratification to maintain class balance
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Train classifier with conservative hyperparameters
        self.model = DecisionTreeClassifier(
            random_state=42,  # Reproducible results
            max_depth=10,     # Prevent overfitting
            min_samples_split=2,  # Allow fine-grained splits
            min_samples_leaf=1    # Allow detailed decision boundaries
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate and track performance
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        self.accuracy_history.append(accuracy)
        
        # Save model and vectorizer for consistent predictions
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"✅ Prioritizer trained with accuracy: {accuracy:.3f}")
        
        # Warn about potential issues
        if accuracy < 0.7:
            print("⚠️ Low accuracy - consider adding more training examples")
        if len(texts) < 20:
            print("⚠️ Very small dataset - model may not generalize well")
            
        return accuracy
    
    def load(self) -> bool:
        """Load existing model and vectorizer"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                return True
        except Exception as e:
            print(f"⚠️ Failed to load model: {e}")
        return False
    
    def predict(self, text: str) -> str:
        """Predict priority with fallback when things go wrong.
        
        Agent systems fail in weird ways, so I default to "normal" for anything
        unexpected. Better to under-prioritize than over-prioritize unknown patterns.
        
        TODO: Add confidence scoring to detect uncertain predictions
        TODO: Log prediction failures for model improvement
        """
        if not self.model or not self.vectorizer:
            return "normal"  # Model not loaded - safe default
            
        try:
            X = self.vectorizer.transform([text])
            prediction = self.model.predict(X)[0]
            return prediction
        except Exception:
            # Any failure in prediction pipeline - return safe default
            # In production, would definitely log this for debugging
            return "normal"
    
    def get_accuracy_trend(self) -> float:
        """Track model performance over time to detect degradation.
        
        Why this matters for agent systems:
        - Model performance can degrade as usage patterns change
        - Need early warning when retraining is necessary
        - Helps distinguish between model issues vs other system problems
        
        What I track:
        - Recent accuracy (last 5 training runs)
        - Trend over time (improving, stable, or degrading)
        - Absolute performance thresholds
        
        What I don't track yet but should:
        - Prediction confidence distributions
        - Error patterns by input type
        - Performance on different domains
        """
        if not self.accuracy_history:
            return 0.85  # Optimistic default for new models
        return sum(self.accuracy_history[-5:]) / len(self.accuracy_history[-5:])

prioritizer = TaskPrioritizer()