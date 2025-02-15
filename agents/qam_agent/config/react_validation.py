"""ReACT validation rules and utilities for QAM Agent."""

import re
from typing import Dict, List, Optional

class ReACTValidator:
    """Validates ReACT methodology compliance in agent responses."""
    
    def __init__(self):
        self.validation_rules = {
            'thought': {
                'required': True,
                'min_words': 10,
                'max_words': 200,
                'pattern': r'\[THOUGHT\].*?(?=\[ACTION\]|\[OBSERVATION\]|\[REFLECTION\]|\[RECOMMENDATION\]|\[VALIDATION\]|$)',
                'required_elements': ['analysis', 'reasoning', 'consideration']
            },
            'action': {
                'required': True,
                'min_words': 15,
                'max_words': 300,
                'pattern': r'\[ACTION\].*?(?=\[OBSERVATION\]|\[REFLECTION\]|\[RECOMMENDATION\]|\[VALIDATION\]|$)',
                'required_elements': ['specific steps', 'clear objectives']
            },
            'observation': {
                'required': True,
                'min_words': 15,
                'max_words': 150,
                'pattern': r'\[OBSERVATION\].*?(?=\[REFLECTION\]|\[RECOMMENDATION\]|\[VALIDATION\]|$)',
                'required_elements': ['findings', 'results', 'outcomes']
            },
            'reflection': {
                'required': True,
                'min_words': 20,
                'max_words': 200,
                'pattern': r'\[REFLECTION\].*?(?=\[RECOMMENDATION\]|\[VALIDATION\]|$)',
                'required_elements': ['analysis']
            }
        }
        
    def validate_response(self, response: str) -> Dict[str, bool]:
        """
        Validate a ReACT response against defined rules.
        
        Args:
            response: The agent's ReACT-formatted response
            
        Returns:
            Dict[str, bool]: Validation results for each component
        """
        results = {}
        for component, rules in self.validation_rules.items():
            # Extract component content using regex pattern
            pattern = rules['pattern']
            match = re.search(pattern, response, re.DOTALL)
            
            if not match and rules['required']:
                results[component] = False  # Require all components
                continue
                
            if not match:
                results[component] = True  # Optional component not present
                continue
                
            content = match.group(0)
            content = content.split(']', 1)[1].strip() if len(content.split(']')) > 1 else content.strip()
            
            # Validate content
            word_count = len(content.split())
            has_required_elements = all(
                element.lower() in content.lower() 
                for element in rules['required_elements']
            )
            
            # More lenient validation
            word_count_valid = (
                word_count >= rules['min_words'] * 0.5 and  # Allow 50% less
                word_count <= rules['max_words'] * 1.5      # Allow 50% more
            )
            results[component] = word_count_valid or has_required_elements  # Pass if either condition is met
            
        return results
        
    def get_validation_summary(self, results: Dict[str, bool]) -> str:
        """
        Generate a human-readable validation summary.
        
        Args:
            results: Validation results from validate_response()
            
        Returns:
            str: Formatted validation summary
        """
        summary = []
        for component, passed in results.items():
            status = "✅" if passed else "❌"
            summary.append(f"{status} {component.title()}: {'Passed' if passed else 'Failed'}")
            
            if not passed:
                rules = self.validation_rules[component]
                summary.append(f"   Required elements: {', '.join(rules['required_elements'])}")
                summary.append(f"   Word count range: {rules['min_words']}-{rules['max_words']}")
                
        return "\n".join(summary)
        
    def validate_tool_selection(self, thought_content: str, selected_tools: List[str]) -> bool:
        """
        Validate tool selection based on reasoning in thought component.
        
        Args:
            thought_content: Content of the THOUGHT section
            selected_tools: List of tools selected for use
            
        Returns:
            bool: Whether tool selection is justified by reasoning
        """
        # Extract tool justification from thought content
        tool_mentions = []
        for tool in selected_tools:
            # Look for explicit reasoning about tool selection
            if tool.lower() in thought_content.lower():
                surrounding_context = re.findall(
                    f".{{50}}{tool}.{{50}}", 
                    thought_content, 
                    re.IGNORECASE
                )
                if surrounding_context:
                    tool_mentions.append({
                        'tool': tool,
                        'context': surrounding_context[0]
                    })
                    
        # More lenient validation - require justification for at least half of tools
        justified_tools = sum(
            'because' in mention['context'].lower() or
            'reason' in mention['context'].lower() or
            'need' in mention['context'].lower() or
            'use' in mention['context'].lower() or
            'using' in mention['context'].lower()
            for mention in tool_mentions
        )
        return justified_tools >= len(selected_tools) / 2
        
    def validate_optimization_reasoning(self, thought_content: str) -> bool:
        """
        Validate quantum optimization reasoning in thought component.
        
        Args:
            thought_content: Content of the THOUGHT section
            
        Returns:
            bool: Whether optimization approach is properly reasoned
        """
        required_concepts = [
            'qubo',
            'qaoa',
            'optimization',
            'quantum',
            'parameter'
        ]
        
        # Check for presence of key concepts
        concept_mentions = {
            concept: concept.lower() in thought_content.lower()
            for concept in required_concepts
        }
        
        # More lenient validation - require only 2 out of 5 concepts
        concepts_present = sum(concept_mentions.values())
        has_sufficient_concepts = concepts_present >= 2
        
        # Validate relationships between concepts
        has_optimization_flow = (
            'convert' in thought_content.lower() or
            'transform' in thought_content.lower() or
            'formulate' in thought_content.lower() or
            'optimize' in thought_content.lower() or
            'schedule' in thought_content.lower()
        )
        
        has_parameter_reasoning = (
            'parameter' in thought_content.lower() or
            'configuration' in thought_content.lower() or
            'setting' in thought_content.lower()
        )
        
        return has_sufficient_concepts or (has_optimization_flow and has_parameter_reasoning)
