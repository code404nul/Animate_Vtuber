from detoxify import Detoxify
from typing import Dict, List, Union
import pandas as pd


class MultilingualToxicityEvaluator:
    """
    multiple models with different toxicity categories:
    - original: toxicity, severe_toxicity, obscene, threat, insult, identity_attack
    - unbiased: same categories, trained to reduce bias
    - multilingual: supports 7 languages (English, French, Spanish, Italian, Portuguese, Turkish, Russian)
    """
    
    def __init__(self, model_type: str = "multilingual"):
        """
        Initialize the toxicity evaluator.
        
        Args:
            model_type: Type of model to use. Options:
                - "multilingual" (default) - supports 7 languages
                - "original" - original English model
                - "unbiased" - debiased English model
                - "original-small" - smaller/faster English model
                - "unbiased-small" - smaller/faster debiased model
        """
        self.model_type = model_type
        print(f"Loading Detoxify model: {model_type}")
        
        self.model = Detoxify(model_type)
        
        print("Model loaded successfully!")
        
        if model_type == "multilingual":
            self.categories = ["toxicity", "severe_toxicity", "obscene", 
                             "threat", "insult", "identity_attack", "sexual_explicit"]
        else:
            self.categories = ["toxicity", "severe_toxicity", "obscene", 
                             "threat", "insult", "identity_attack"]
    
    def evaluate(self, text: Union[str, List[str]], threshold: float = 0.5) -> Union[Dict, List[Dict]]:
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        
        predictions = self.model.predict(texts)
        
        results = []
        for i, txt in enumerate(texts):
            result = {
                "text": txt,
                "scores": {}
            }
            
            for category in self.categories:
                if isinstance(predictions[category], list):
                    score = float(predictions[category][i])
                else:
                    score = float(predictions[category])
                result["scores"][category] = round(score, 4)
            
            result["is_toxic"] = result["scores"]["toxicity"] >= threshold
            result["toxicity_score"] = result["scores"]["toxicity"]
            result["max_category"] = max(result["scores"].items(), key=lambda x: x[1])
            
            results.append(result)
        
        return results[0] if is_single else results
    
    def batch_evaluate(self, texts: List[str], threshold: float = 0.5) -> List[Dict]:
        return self.evaluate(texts, threshold)
    
    def get_detailed_report(self, text: str, threshold: float = 0.5) -> Dict:
        result = self.evaluate(text, threshold)
        
        flagged_categories = [cat for cat, score in result["scores"].items() 
                            if score >= threshold]
        
        report = {
            "text": text,
            "overall_toxic": result["is_toxic"],
            "toxicity_score": result["toxicity_score"],
            "all_scores": result["scores"],
            "flagged_categories": flagged_categories,
            "highest_score": {
                "category": result["max_category"][0],
                "score": result["max_category"][1]
            },
            "severity_level": self._get_severity_level(result["toxicity_score"])
        }
        
        return report
    
    def _get_severity_level(self, score: float) -> str:
        if score < 0.3:
            return "Low"
        elif score < 0.6:
            return "Medium"
        elif score < 0.8:
            return "High"
        else:
            return "Very High"
    
    def compare_texts(self, texts: List[str]) -> pd.DataFrame:
        results = self.batch_evaluate(texts)
        
        data = []
        for r in results:
            row = {
                "text": r["text"][:50] + "..." if len(r["text"]) > 50 else r["text"],
                "is_toxic": r["is_toxic"],
                **r["scores"]
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def filter_toxic_content(self, texts, threshold: float = 0.5) -> Dict[str, List[str]]:
        if type(texts) == str:
            texts = [texts]
        results = self.batch_evaluate(texts, threshold)
        
        filtered = {
            "toxic": [],
            "non_toxic": []
        }
        
        for r in results:
            if r["is_toxic"]:
                filtered["toxic"].append(r["text"])
            else:
                filtered["non_toxic"].append(r["text"])
        
        return filtered


if __name__ == "__main__":
    evaluator = MultilingualToxicityEvaluator(model_type="multilingual")
    
    test_texts = [
        "I love this product! It's amazing!",  # English - non-toxic
        "You are stupid and worthless, idiot!",  # English - toxic
        "Je déteste ce produit, mais le service était bon.",  # French
        "Va te faire foutre, espèce d'imbécile!",  # French - toxic
        "Eres un idiota y te odio.",  # Spanish - toxic
        "Questo è un ottimo ristorante!",  # Italian - non-toxic
        "Você é incrível!",  # Portuguese - non-toxic
        "This is complete garbage and you should be ashamed.",  # English - toxic
    ]
    
    filtered = evaluator.filter_toxic_content(test_texts) #can be str
    print(filtered)
    for txt in filtered['toxic']:
        print(f"  - {txt[:60]}...")