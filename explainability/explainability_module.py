# AI Explainability Module - Detailed Explanations and Visual Highlighting
# explainability_module.py

import numpy as np
import pandas as pd
import torch
import shap
import lime
from lime.lime_text import LimeTextExplainer
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import json
from transformers import AutoTokenizer, AutoModel
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import cv2
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from sklearn.preprocessing import StandardScaler
import networkx as nx
from captum.attr import (
    IntegratedGradients,
    LayerIntegratedGradients,
    TokenReferenceBase,
    visualization as viz
)
import gradio as gr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= CONFIGURATION =============

@dataclass
class ExplainabilityConfig:
    """Configuration for explainability module"""
    model_name: str = "allenai/scibert_scivocab_uncased"
    shap_samples: int = 100
    lime_samples: int = 5000
    confidence_threshold: float = 0.7
    highlight_top_k: int = 10
    visualization_dpi: int = 150

# ============= TEXT EXPLAINABILITY =============

class TextExplainabilityEngine:
    """Explain text-based predictions with multiple methods"""

    def __init__(self, config: ExplainabilityConfig):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.model = AutoModel.from_pretrained(config.model_name)
        self.lime_explainer = LimeTextExplainer(class_names=['low_risk', 'medium_risk', 'high_risk'])
        self.integrated_gradients = None

    def explain_text_prediction(self, text: str, prediction: float,
                               model_func: callable) -> Dict[str, Any]:
        """Generate comprehensive explanation for text prediction"""

        explanations = {
            "prediction": prediction,
            "confidence": self._calculate_confidence(prediction),
            "methods": {}
        }

        # LIME explanation
        explanations["methods"]["lime"] = self._lime_explanation(text, model_func)

        # SHAP explanation
        explanations["methods"]["shap"] = self._shap_explanation(text, model_func)

        # Attention-based explanation
        explanations["methods"]["attention"] = self._attention_explanation(text)

        # Token importance using integrated gradients
        explanations["methods"]["integrated_gradients"] = self._integrated_gradients_explanation(text)

        # Generate natural language explanation
        explanations["natural_language"] = self._generate_natural_language_explanation(explanations)

        # Create visualization
        explanations["visualization"] = self._create_text_visualization(text, explanations)

        return explanations

    def _lime_explanation(self, text: str, model_func: callable) -> Dict[str, Any]:
        """Generate LIME explanation"""

        try:
            exp = self.lime_explainer.explain_instance(
                text,
                model_func,
                num_features=self.config.highlight_top_k,
                num_samples=self.config.lime_samples
            )

            # Extract feature weights
            features = []
            for feature, weight in exp.as_list():
                features.append({
                    "text": feature,
                    "weight": weight,
                    "importance": abs(weight)
                })

            # Sort by importance
            features.sort(key=lambda x: x["importance"], reverse=True)

            return {
                "features": features[:self.config.highlight_top_k],
                "html": exp.as_html(),
                "score": exp.score
            }
        except Exception as e:
            logger.error(f"LIME explanation failed: {e}")
            return {"error": str(e)}

    def _shap_explanation(self, text: str, model_func: callable) -> Dict[str, Any]:
        """Generate SHAP explanation"""

        try:
            # Tokenize text
            tokens = self.tokenizer.tokenize(text)

            # Create SHAP explainer
            explainer = shap.Explainer(model_func, self.tokenizer)

            # Get SHAP values
            shap_values = explainer([text])

            # Extract token importance
            token_importance = []
            for token, value in zip(tokens, shap_values.values[0]):
                token_importance.append({
                    "token": token,
                    "shap_value": float(value),
                    "importance": abs(float(value))
                })

            # Sort by importance
            token_importance.sort(key=lambda x: x["importance"], reverse=True)

            return {
                "tokens": token_importance[:self.config.highlight_top_k],
                "base_value": float(shap_values.base_values[0]),
                "expected_value": float(explainer.expected_value)
            }
        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            return {"error": str(e)}

    def _attention_explanation(self, text: str) -> Dict[str, Any]:
        """Extract attention weights for explanation"""

        try:
            # Tokenize and encode
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

            # Get model outputs with attention
            with torch.no_grad():
                outputs = self.model(**inputs, output_attentions=True)

            # Average attention across all layers and heads
            attentions = outputs.attentions
            avg_attention = torch.mean(torch.stack(attentions), dim=(0, 1, 2))

            # Get tokens and their attention scores
            tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
            attention_scores = avg_attention.numpy()

            # Create token-attention pairs
            token_attention = []
            for token, score in zip(tokens, attention_scores):
                if token not in ['[CLS]', '[SEP]', '[PAD]']:
                    token_attention.append({
                        "token": token,
                        "attention": float(score),
                        "normalized": float(score / attention_scores.max())
                    })

            # Sort by attention
            token_attention.sort(key=lambda x: x["attention"], reverse=True)

            return {
                "high_attention_tokens": token_attention[:self.config.highlight_top_k],
                "attention_distribution": {
                    "mean": float(attention_scores.mean()),
                    "std": float(attention_scores.std()),
                    "max": float(attention_scores.max()),
                    "min": float(attention_scores.min())
                }
            }
        except Exception as e:
            logger.error(f"Attention explanation failed: {e}")
            return {"error": str(e)}

    def _integrated_gradients_explanation(self, text: str) -> Dict[str, Any]:
        """Use integrated gradients for token importance"""

        try:
            # Tokenize
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            input_ids = inputs['input_ids']

            # Create baseline (all padding tokens)
            baseline_ids = torch.zeros_like(input_ids)

            # Initialize integrated gradients
            if self.integrated_gradients is None:
                self.integrated_gradients = IntegratedGradients(self.model)

            # Calculate attributions
            attributions, delta = self.integrated_gradients.attribute(
                inputs=input_ids,
                baselines=baseline_ids,
                return_convergence_delta=True
            )

            # Get tokens and their attributions
            tokens = self.tokenizer.convert_ids_to_tokens(input_ids[0])
            attr_scores = attributions[0].numpy()

            # Create token-attribution pairs
            token_attributions = []
            for token, score in zip(tokens, attr_scores):
                if token not in ['[CLS]', '[SEP]', '[PAD]']:
                    token_attributions.append({
                        "token": token,
                        "attribution": float(score),
                        "abs_attribution": abs(float(score))
                    })

            # Sort by absolute attribution
            token_attributions.sort(key=lambda x: x["abs_attribution"], reverse=True)

            return {
                "important_tokens": token_attributions[:self.config.highlight_top_k],
                "convergence_delta": float(delta)
            }
        except Exception as e:
            logger.error(f"Integrated gradients failed: {e}")
            return {"error": str(e)}

    def _calculate_confidence(self, prediction: float) -> float:
        """Calculate confidence score for prediction"""

        # Distance from decision boundary (0.5)
        distance_from_boundary = abs(prediction - 0.5)

        # Convert to confidence (0 to 1)
        confidence = min(1.0, distance_from_boundary * 2)

        return confidence

    def _generate_natural_language_explanation(self, explanations: Dict) -> str:
        """Generate human-readable explanation"""

        prediction = explanations["prediction"]
        confidence = explanations["confidence"]

        # Determine risk level
        if prediction >= 0.7:
            risk_level = "high risk"
        elif prediction >= 0.4:
            risk_level = "medium risk"
        else:
            risk_level = "low risk"

        # Build explanation
        explanation = f"The document was classified as {risk_level} with {confidence:.1%} confidence. "

        # Add method-specific insights
        if "lime" in explanations["methods"] and "features" in explanations["methods"]["lime"]:
            top_features = explanations["methods"]["lime"]["features"][:3]
            if top_features:
                explanation += "Key factors include: "
                for feature in top_features:
                    direction = "increases" if feature["weight"] > 0 else "decreases"
                    explanation += f"'{feature['text']}' {direction} risk (weight: {abs(feature['weight']):.2f}), "
                explanation = explanation.rstrip(", ") + ". "

        if "attention" in explanations["methods"]:
            attention_data = explanations["methods"]["attention"]
            if "high_attention_tokens" in attention_data:
                high_attention = attention_data["high_attention_tokens"][:3]
                if high_attention:
                    explanation += "The model focused particularly on: "
                    explanation += ", ".join([f"'{t['token']}'" for t in high_attention]) + ". "

        return explanation

    def _create_text_visualization(self, text: str, explanations: Dict) -> str:
        """Create HTML visualization of text with highlights"""

        html = """
        <div style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
            <h3>Text Analysis Visualization</h3>
            <div style="background: white; padding: 15px; border-radius: 5px; line-height: 1.8;">
        """

        # Get important tokens from different methods
        important_tokens = set()

        if "lime" in explanations["methods"] and "features" in explanations["methods"]["lime"]:
            for feature in explanations["methods"]["lime"]["features"][:5]:
                important_tokens.add(feature["text"].lower())

        if "attention" in explanations["methods"]:
            for token in explanations["methods"]["attention"].get("high_attention_tokens", [])[:5]:
                important_tokens.add(token["token"].lower())

        # Highlight text
        words = text.split()
        highlighted_text = []

        for word in words:
            word_lower = word.lower().strip('.,!?";')
            if word_lower in important_tokens:
                # Determine color based on importance
                color = "#ff6b6b"  # Red for high importance
                highlighted_text.append(
                    f'<span style="background-color: {color}33; padding: 2px 4px; border-radius: 3px; font-weight: bold;">{word}</span>'
                )
            else:
                highlighted_text.append(word)

        html += " ".join(highlighted_text)
        html += """
            </div>
            <div style="margin-top: 15px; font-size: 12px; color: #666;">
                <strong>Legend:</strong>
                <span style="background-color: #ff6b6b33; padding: 2px 6px; border-radius: 3px;">High Impact Terms</span>
            </div>
        </div>
        """

        return html

# ============= IMAGE EXPLAINABILITY =============

class ImageExplainabilityEngine:
    """Explain image-based predictions with visual highlighting"""

    def __init__(self, config: ExplainabilityConfig):
        self.config = config

    def explain_image_prediction(self, image_path: str, prediction: Dict[str, Any],
                                model: Any) -> Dict[str, Any]:
        """Generate explanation for image analysis"""

        # Load image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        explanations = {
            "prediction": prediction,
            "methods": {}
        }

        # Grad-CAM explanation
        explanations["methods"]["gradcam"] = self._gradcam_explanation(image_rgb, model)

        # LIME for images
        explanations["methods"]["lime"] = self._lime_image_explanation(image_rgb, model)

        # Occlusion sensitivity
        explanations["methods"]["occlusion"] = self._occlusion_explanation(image_rgb, model)

        # Generate visualization
        explanations["visualization"] = self._create_image_visualization(
            image_rgb, explanations
        )

        return explanations

    def _gradcam_explanation(self, image: np.ndarray, model: Any) -> Dict[str, Any]:
        """Generate Grad-CAM heatmap"""

        try:
            # Preprocess image for model
            preprocessed = self._preprocess_image(image)

            # Forward pass
            output = model(preprocessed)

            # Get gradients
            model.zero_grad()
            class_idx = output.argmax()
            output[0, class_idx].backward()

            # Get the gradients and activations
            gradients = model.get_gradients()
            activations = model.get_activations()

            # Calculate weights
            weights = torch.mean(gradients, dim=(2, 3))[0]

            # Generate heatmap
            heatmap = torch.zeros(activations.shape[2:])
            for i, weight in enumerate(weights):
                heatmap += weight * activations[0, i]

            heatmap = torch.relu(heatmap)
            heatmap = heatmap / heatmap.max()

            # Resize heatmap to image size
            heatmap = cv2.resize(heatmap.numpy(), (image.shape[1], image.shape[0]))

            return {
                "heatmap": heatmap.tolist(),
                "max_activation": float(heatmap.max()),
                "mean_activation": float(heatmap.mean())
            }
        except Exception as e:
            logger.error(f"Grad-CAM failed: {e}")
            return {"error": str(e)}

    def _lime_image_explanation(self, image: np.ndarray, model: Any) -> Dict[str, Any]:
        """Generate LIME explanation for image"""

        try:
            from lime.lime_image import LimeImageExplainer

            explainer = LimeImageExplainer()

            # Define prediction function
            def predict_fn(images):
                predictions = []
                for img in images:
                    preprocessed = self._preprocess_image(img)
                    pred = model(preprocessed)
                    predictions.append(pred.detach().numpy())
                return np.array(predictions)

            # Generate explanation
            explanation = explainer.explain_instance(
                image,
                predict_fn,
                top_labels=1,
                hide_color=0,
                num_samples=1000
            )

            # Get image mask
            temp, mask = explanation.get_image_and_mask(
                explanation.top_labels[0],
                positive_only=True,
                num_features=5,
                hide_rest=False
            )

            return {
                "mask": mask.tolist(),
                "num_superpixels": len(np.unique(mask)),
                "top_features": explanation.local_exp[explanation.top_labels[0]][:5]
            }
        except Exception as e:
            logger.error(f"LIME image explanation failed: {e}")
            return {"error": str(e)}

    def _occlusion_explanation(self, image: np.ndarray, model: Any) -> Dict[str, Any]:
        """Perform occlusion sensitivity analysis"""

        try:
            occlusion_size = 50
            stride = 25

            height, width = image.shape[:2]
            sensitivity_map = np.zeros((height // stride, width // stride))

            # Original prediction
            original_pred = model(self._preprocess_image(image))
            original_score = float(original_pred.max())

            # Slide occlusion window
            for i in range(0, height - occlusion_size, stride):
                for j in range(0, width - occlusion_size, stride):
                    # Create occluded image
                    occluded = image.copy()
                    occluded[i:i+occlusion_size, j:j+occlusion_size] = 0

                    # Get prediction
                    pred = model(self._preprocess_image(occluded))
                    score = float(pred.max())

                    # Calculate sensitivity
                    sensitivity = original_score - score
                    sensitivity_map[i//stride, j//stride] = sensitivity

            return {
                "sensitivity_map": sensitivity_map.tolist(),
                "max_sensitivity": float(sensitivity_map.max()),
                "mean_sensitivity": float(sensitivity_map.mean()),
                "most_sensitive_region": {
                    "y": int(np.unravel_index(sensitivity_map.argmax(), sensitivity_map.shape)[0] * stride),
                    "x": int(np.unravel_index(sensitivity_map.argmax(), sensitivity_map.shape)[1] * stride)
                }
            }
        except Exception as e:
            logger.error(f"Occlusion analysis failed: {e}")
            return {"error": str(e)}

    def _preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for model input"""

        # Resize to model input size
        image_resized = cv2.resize(image, (224, 224))

        # Normalize
        image_normalized = image_resized / 255.0

        # Convert to tensor
        tensor = torch.from_numpy(image_normalized).float()
        tensor = tensor.permute(2, 0, 1).unsqueeze(0)

        return tensor

    def _create_image_visualization(self, image: np.ndarray,
                                   explanations: Dict) -> Dict[str, Any]:
        """Create visual explanation overlays"""

        visualizations = {}

        # Create Grad-CAM overlay
        if "gradcam" in explanations["methods"] and "heatmap" in explanations["methods"]["gradcam"]:
            heatmap = np.array(explanations["methods"]["gradcam"]["heatmap"])

            # Apply colormap
            heatmap_colored = cv2.applyColorMap(
                (heatmap * 255).astype(np.uint8),
                cv2.COLORMAP_JET
            )

            # Create overlay
            overlay = cv2.addWeighted(image, 0.7, heatmap_colored, 0.3, 0)

            # Convert to base64
            _, buffer = cv2.imencode('.png', overlay)
            visualizations["gradcam_overlay"] = base64.b64encode(buffer).decode('utf-8')

        # Create LIME overlay
        if "lime" in explanations["methods"] and "mask" in explanations["methods"]["lime"]:
            mask = np.array(explanations["methods"]["lime"]["mask"])

            # Highlight important regions
            highlighted = image.copy()
            highlighted[mask == 0] = highlighted[mask == 0] * 0.3  # Dim unimportant areas

            _, buffer = cv2.imencode('.png', highlighted)
            visualizations["lime_overlay"] = base64.b64encode(buffer).decode('utf-8')

        # Create occlusion sensitivity heatmap
        if "occlusion" in explanations["methods"] and "sensitivity_map" in explanations["methods"]["occlusion"]:
            sensitivity = np.array(explanations["methods"]["occlusion"]["sensitivity_map"])

            # Resize to image size
            sensitivity_resized = cv2.resize(
                sensitivity,
                (image.shape[1], image.shape[0]),
                interpolation=cv2.INTER_CUBIC
            )

            # Normalize and apply colormap
            sensitivity_normalized = (sensitivity_resized - sensitivity_resized.min()) / (
                sensitivity_resized.max() - sensitivity_resized.min()
            )
            sensitivity_colored = cv2.applyColorMap(
                (sensitivity_normalized * 255).astype(np.uint8),
                cv2.COLORMAP_HOT
            )

            # Create overlay
            overlay = cv2.addWeighted(image, 0.6, sensitivity_colored, 0.4, 0)

            _, buffer = cv2.imencode('.png', overlay)
            visualizations["occlusion_overlay"] = base64.b64encode(buffer).decode('utf-8')

        return visualizations

# ============= CONFIDENCE SCORE BREAKDOWN =============

class ConfidenceExplainer:
    """Explain and break down confidence scores"""

    def __init__(self):
        self.components = {}

    def explain_confidence(self, predictions: Dict[str, float],
                          features: Dict[str, Any]) -> Dict[str, Any]:
        """Break down confidence score into components"""

        # Calculate component scores
        components = {
            "model_certainty": self._calculate_model_certainty(predictions),
            "feature_quality": self._calculate_feature_quality(features),
            "consistency": self._calculate_consistency(predictions),
            "calibration": self._calculate_calibration(predictions)
        }

        # Calculate overall confidence
        weights = {
            "model_certainty": 0.4,
            "feature_quality": 0.2,
            "consistency": 0.2,
            "calibration": 0.2
        }

        overall_confidence = sum(
            components[key] * weights[key] for key in components
        )

        # Generate explanation
        explanation = self._generate_confidence_explanation(components, overall_confidence)

        # Create visualization
        visualization = self._create_confidence_visualization(components, overall_confidence)

        return {
            "overall_confidence": overall_confidence,
            "components": components,
            "weights": weights,
            "explanation": explanation,
            "visualization": visualization
        }

    def _calculate_model_certainty(self, predictions: Dict[str, float]) -> float:
        """Calculate model certainty based on prediction distribution"""

        if not predictions:
            return 0.5

        # Calculate entropy
        values = list(predictions.values())
        entropy = -sum(p * np.log(p + 1e-10) for p in values if p > 0)
        max_entropy = -np.log(1/len(values))

        # Normalize (lower entropy = higher certainty)
        certainty = 1 - (entropy / max_entropy) if max_entropy > 0 else 0.5

        return certainty

    def _calculate_feature_quality(self, features: Dict[str, Any]) -> float:
        """Assess quality of input features"""

        quality_score = 0.5  # Default

        # Check for missing features
        if "missing_features" in features:
            quality_score -= 0.1 * features["missing_features"]

        # Check for outliers
        if "outlier_count" in features:
            quality_score -= 0.05 * features["outlier_count"]

        # Check for data completeness
        if "completeness" in features:
            quality_score = features["completeness"]

        return max(0, min(1, quality_score))

    def _calculate_consistency(self, predictions: Dict[str, float]) -> float:
        """Calculate consistency across different models"""

        if len(predictions) < 2:
            return 0.5

        values = list(predictions.values())
        std_dev = np.std(values)

        # Lower std dev = higher consistency
        consistency = max(0, 1 - (std_dev * 2))

        return consistency

    def _calculate_calibration(self, predictions: Dict[str, float]) -> float:
        """Calculate calibration score"""

        # This would compare predicted probabilities with actual outcomes
        # For now, return a placeholder
        return 0.75

    def _generate_confidence_explanation(self, components: Dict[str, float],
                                        overall: float) -> str:
        """Generate natural language explanation of confidence"""

        explanation = f"The overall confidence score is {overall:.1%}. "

        # Find strongest and weakest components
        sorted_components = sorted(components.items(), key=lambda x: x[1])
        weakest = sorted_components[0]
        strongest = sorted_components[-1]

        explanation += f"The strongest confidence indicator is {strongest[0].replace('_', ' ')} ({strongest[1]:.1%}), "
        explanation += f"while {weakest[0].replace('_', ' ')} shows lower confidence ({weakest[1]:.1%}). "

        # Add specific insights
        if components["model_certainty"] < 0.5:
            explanation += "The model shows uncertainty in its prediction. "

        if components["feature_quality"] < 0.6:
            explanation += "Some input features may be incomplete or contain anomalies. "

        if components["consistency"] < 0.5:
            explanation += "Different analysis methods show varying results. "

        return explanation

    def _create_confidence_visualization(self, components: Dict[str, float],
                                        overall: float) -> Dict[str, Any]:
        """Create visualization of confidence breakdown"""

        # Create radar chart data
        fig = go.Figure()

        # Add trace for components
        fig.add_trace(go.Scatterpolar(
            r=list(components.values()),
            theta=[k.replace('_', ' ').title() for k in components.keys()],
            fill='toself',
            name='Confidence Components'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title=f"Confidence Score Breakdown (Overall: {overall:.1%})"
        )

        return {
            "plotly_json": fig.to_json(),
            "components_bar_chart": self._create_bar_chart(components)
        }

    def _create_bar_chart(self, components: Dict[str, float]) -> str:
        """Create bar chart of confidence components"""

        fig = go.Figure([go.Bar(
            x=[k.replace('_', ' ').title() for k in components.keys()],
            y=list(components.values()),
            marker_color=['green' if v > 0.7 else 'yellow' if v > 0.4 else 'red'
                         for v in components.values()]
        )])

        fig.update_layout(
            title="Confidence Components",
            yaxis_title="Score",
            yaxis=dict(range=[0, 1]),
            showlegend=False
        )

        return fig.to_json()

# ============= INTERACTIVE EXPLAINABILITY INTERFACE =============

class InteractiveExplainabilityInterface:
    """Gradio-based interactive interface for exploring explanations"""

    def __init__(self, text_engine: TextExplainabilityEngine,
                 image_engine: ImageExplainabilityEngine,
                 confidence_explainer: ConfidenceExplainer):
        self.text_engine = text_engine
        self.image_engine = image_engine
        self.confidence_explainer = confidence_explainer

    def create_interface(self) -> gr.Interface:
        """Create Gradio interface for explainability"""

        with gr.Blocks(title="AI Explainability Dashboard") as interface:
            gr.Markdown("# Academic Integrity AI Explainability Dashboard")

            with gr.Tabs():
                # Text Explainability Tab
                with gr.TabItem("Text Analysis"):
                    with gr.Row():
                        text_input = gr.Textbox(
                            label="Enter text to analyze",
                            lines=10,
                            placeholder="Paste academic text here..."
                        )

                        with gr.Column():
                            text_predict_btn = gr.Button("Analyze Text", variant="primary")
                            text_risk_score = gr.Number(label="Risk Score", precision=3)
                            text_confidence = gr.Number(label="Confidence", precision=3)

                    with gr.Row():
                        text_explanation = gr.HTML(label="Visual Explanation")
                        text_natural = gr.Textbox(label="Natural Language Explanation", lines=5)

                    with gr.Row():
                        lime_plot = gr.Plot(label="LIME Feature Importance")
                        attention_plot = gr.Plot(label="Attention Heatmap")

                # Image Explainability Tab
                with gr.TabItem("Image Analysis"):
                    with gr.Row():
                        image_input = gr.Image(label="Upload image", type="filepath")

                        with gr.Column():
                            image_predict_btn = gr.Button("Analyze Image", variant="primary")
                            image_risk_score = gr.Number(label="Manipulation Score", precision=3)

                    with gr.Row():
                        gradcam_output = gr.Image(label="Grad-CAM Heatmap")
                        lime_output = gr.Image(label="LIME Explanation")
                        occlusion_output = gr.Image(label="Occlusion Sensitivity")

                # Confidence Breakdown Tab
                with gr.TabItem("Confidence Analysis"):
                    with gr.Row():
                        confidence_input = gr.JSON(label="Prediction Data")
                        confidence_analyze_btn = gr.Button("Analyze Confidence", variant="primary")

                    with gr.Row():
                        confidence_score = gr.Number(label="Overall Confidence", precision=3)
                        confidence_explanation = gr.Textbox(label="Explanation", lines=5)

                    confidence_viz = gr.Plot(label="Confidence Breakdown")

                # Model Comparison Tab
                with gr.TabItem("Model Comparison"):
                    gr.Markdown("## Compare Different Model Predictions")

                    with gr.Row():
                        model1_pred = gr.Number(label="Model 1 Prediction", precision=3)
                        model2_pred = gr.Number(label="Model 2 Prediction", precision=3)
                        model3_pred = gr.Number(label="Model 3 Prediction", precision=3)

                    compare_btn = gr.Button("Compare Models", variant="primary")

                    comparison_output = gr.Plot(label="Model Agreement Analysis")
                    disagreement_explanation = gr.Textbox(label="Disagreement Analysis", lines=5)

            # Connect functions to interface
            text_predict_btn.click(
                self._analyze_text,
                inputs=[text_input],
                outputs=[text_risk_score, text_confidence, text_explanation,
                        text_natural, lime_plot, attention_plot]
            )

            image_predict_btn.click(
                self._analyze_image,
                inputs=[image_input],
                outputs=[image_risk_score, gradcam_output, lime_output, occlusion_output]
            )

            confidence_analyze_btn.click(
                self._analyze_confidence,
                inputs=[confidence_input],
                outputs=[confidence_score, confidence_explanation, confidence_viz]
            )

            compare_btn.click(
                self._compare_models,
                inputs=[model1_pred, model2_pred, model3_pred],
                outputs=[comparison_output, disagreement_explanation]
            )

        return interface

    def _analyze_text(self, text: str):
        """Analyze text and return explanations"""

        # Mock prediction function
        def predict_fn(texts):
            return np.array([[0.2, 0.3, 0.5]])  # Mock predictions

        # Get explanations
        explanations = self.text_engine.explain_text_prediction(
            text, 0.5, predict_fn
        )

        # Create LIME plot
        lime_fig = self._create_feature_importance_plot(
            explanations["methods"].get("lime", {}).get("features", [])
        )

        # Create attention plot
        attention_fig = self._create_attention_heatmap(
            explanations["methods"].get("attention", {})
        )

        return (
            explanations["prediction"],
            explanations["confidence"],
            explanations["visualization"],
            explanations["natural_language"],
            lime_fig,
            attention_fig
        )

    def _analyze_image(self, image_path: str):
        """Analyze image and return explanations"""

        # Mock model
        class MockModel:
            def __call__(self, x):
                return torch.tensor([[0.3, 0.7]])

        model = MockModel()

        # Get explanations
        explanations = self.image_engine.explain_image_prediction(
            image_path,
            {"manipulation_score": 0.7},
            model
        )

        # Load visualizations
        visualizations = explanations.get("visualization", {})

        return (
            0.7,  # Mock score
            self._decode_base64_image(visualizations.get("gradcam_overlay", "")),
            self._decode_base64_image(visualizations.get("lime_overlay", "")),
            self._decode_base64_image(visualizations.get("occlusion_overlay", ""))
        )

    def _analyze_confidence(self, prediction_data: Dict):
        """Analyze confidence scores"""

        explanations = self.confidence_explainer.explain_confidence(
            prediction_data.get("predictions", {}),
            prediction_data.get("features", {})
        )

        # Create visualization
        viz = go.Figure(json.loads(explanations["visualization"]["components_bar_chart"]))

        return (
            explanations["overall_confidence"],
            explanations["explanation"],
            viz
        )

    def _compare_models(self, pred1: float, pred2: float, pred3: float):
        """Compare model predictions"""

        predictions = [pred1, pred2, pred3]

        # Create comparison visualization
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=['Model 1', 'Model 2', 'Model 3'],
            y=predictions,
            marker_color=['blue', 'green', 'red']
        ))

        fig.update_layout(
            title="Model Predictions Comparison",
            yaxis_title="Risk Score",
            yaxis=dict(range=[0, 1])
        )

        # Generate disagreement explanation
        std_dev = np.std(predictions)
        if std_dev > 0.2:
            explanation = f"High disagreement between models (std: {std_dev:.3f}). "
            explanation += "This indicates uncertainty in the prediction. "
            explanation += "Manual review is strongly recommended."
        elif std_dev > 0.1:
            explanation = f"Moderate agreement between models (std: {std_dev:.3f}). "
            explanation += "The prediction is fairly consistent across models."
        else:
            explanation = f"Strong agreement between models (std: {std_dev:.3f}). "
            explanation += "All models agree on the risk assessment."

        return fig, explanation

    def _create_feature_importance_plot(self, features: List[Dict]) -> go.Figure:
        """Create feature importance bar plot"""

        if not features:
            return go.Figure()

        fig = go.Figure([go.Bar(
            x=[f["weight"] for f in features],
            y=[f["text"] for f in features],
            orientation='h',
            marker_color=['red' if f["weight"] < 0 else 'green' for f in features]
        )])

        fig.update_layout(
            title="Feature Importance (LIME)",
            xaxis_title="Weight",
            yaxis_title="Feature"
        )

        return fig

    def _create_attention_heatmap(self, attention_data: Dict) -> go.Figure:
        """Create attention heatmap"""

        if not attention_data or "high_attention_tokens" not in attention_data:
            return go.Figure()

        tokens = attention_data["high_attention_tokens"]

        fig = go.Figure([go.Bar(
            x=[t["token"] for t in tokens],
            y=[t["attention"] for t in tokens],
            marker_color='purple'
        )])

        fig.update_layout(
            title="Token Attention Scores",
            xaxis_title="Token",
            yaxis_title="Attention Score"
        )

        return fig

    def _decode_base64_image(self, base64_str: str):
        """Decode base64 image string"""

        if not base64_str:
            return None

        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))

        return image

# ============= MAIN EXECUTION =============

if __name__ == "__main__":
    # Initialize engines
    config = ExplainabilityConfig()
    text_engine = TextExplainabilityEngine(config)
    image_engine = ImageExplainabilityEngine(config)
    confidence_explainer = ConfidenceExplainer()

    # Create interface
    interface_builder = InteractiveExplainabilityInterface(
        text_engine, image_engine, confidence_explainer
    )

    # Launch Gradio interface
    interface = interface_builder.create_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
