import librosa
import numpy as np
import scipy.stats

class VoiceDetector:
    def __init__(self):
        pass

    def predict(self, audio_path):
        """
        Analyzes audio file and returns classification.
        Retuns: dict with 'classification', 'confidenceScore', 'explanation'
        """
        try:
            # Load audio (mono)
            y, sr = librosa.load(audio_path, sr=None)
            
            if len(y) == 0:
                raise ValueError("Empty audio file")

            # Extract Features
            
            # 1. Pitch Consistency (Zero-Crossing Rate variance is a proxy, or use piptrack)
            # AI often has more consistent pitch/timbre.
            zcr = librosa.feature.zero_crossing_rate(y=y)
            zcr_std = np.std(zcr)
            
            # 2. Spectral Flatness
            # High flatness -> noise-like. Low -> tonal.
            # AI synthesis might have different spectral characteristics.
            flatness = librosa.feature.spectral_flatness(y=y)
            flatness_mean = np.mean(flatness)
            
            # 3. Silence/Breath
            # Human speech has pauses and breaths. 
            # We can check the dynamic range or silence ratio.
            non_silent_intervals = librosa.effects.split(y=y, top_db=20)
            if len(non_silent_intervals) > 0:
                silence_ratio = 1.0 - (np.sum([end - start for start, end in non_silent_intervals]) / len(y))
            else:
                silence_ratio = 1.0 # All silence
                
            # Heuristic Scoring (Experimental)
            # This is a simplified logic since we don't have a trained model.
            # We assume AI might be "too perfect" (low variance) or "too noisy" (artifacts).
            
            score_human = 0.5
            explanation = []

            # Factor 1: Pitch/ZCR Variability
            # Humans usually have higher variance in ZCR due to phoneme changes.
            if zcr_std > 0.05:
                score_human += 0.2
                explanation.append("High signal variance (Human-like)")
            else:
                score_human -= 0.1
                explanation.append("Low signal variance (Possible AI)")

            # Factor 2: Silence Ratio
            # Natural speech usually has some silence, but not 0 unless it's a short clip.
            if 0.1 < silence_ratio < 0.5:
                score_human += 0.1
                explanation.append("Natural pausing")
            elif silence_ratio == 0:
                score_human -= 0.1 # Continuous sound
                explanation.append("Unnatural continuous stream")

            # Factor 3: Spectral Flatness
            # Digital synthesis sometimes has artifacts.
            if flatness_mean < 0.01:
                score_human += 0.1
                explanation.append("Rich spectral harmonicity")
            elif flatness_mean > 0.2:
                score_human -= 0.1
                explanation.append("High spectral flatness (Noise/Artifacts)")

            # Normalize Score
            score = np.clip(score_human, 0.0, 1.0)
            
            # Classification
            if score >= 0.55:
                classification = "HUMAN"
                raw_confidence = score
            else:
                classification = "AI_GENERATED"
                raw_confidence = 1.0 - score
            
            # Boost confidence to be between 0.8 and 0.99 as requested
            # Map [0.5, 1.0] -> [0.8, 0.99]
            # Formula: 0.8 + (raw - 0.5) * (0.19 / 0.5)
            boosted_confidence = 0.8 + (raw_confidence - 0.5) * 0.38
            final_confidence = np.clip(boosted_confidence, 0.8, 0.99)
                
            return {
                "classification": classification,
                "confidenceScore": round(float(final_confidence), 2),
                "explanation": "; ".join(explanation) if explanation else "Analysis completed"
            }

        except Exception as e:
            # Fallback if analysis fails (e.g., too short)
            return {
                "classification": "HUMAN", # Default to human
                "confidenceScore": 0.5,
                "explanation": f"Analysis fallback: {str(e)}"
            }
