"""ReACT validation configuration for quantum training agent."""

from typing import Dict, List, Any
import re

class ReACTValidator:
    """Validates ReACT methodology execution in agent responses."""
    
    REACT_COMPONENTS = [
        "THOUGHT",
        "ACTION",
        "OBSERVATION",
        "REFLECTION"
    ]
    
    REQUIRED_PATTERNS = {
        "THOUGHT": r"\[THOUGHT\].*(?=\[ACTION\]|\Z)",
        "ACTION": r"\[ACTION\].*(?=\[OBSERVATION\]|\Z)",
        "OBSERVATION": r"\[OBSERVATION\].*(?=\[REFLECTION\]|\Z)",
        "REFLECTION": r"\[REFLECTION\].*(?=\[THOUGHT\]|\Z)"
    }
    
    VALIDATION_RULES = {
        "THOUGHT": [
            "Contains clear reasoning process",
            "Considers quantum optimization aspects",
            "Addresses training objectives"
        ],
        "ACTION": [
            "Specifies concrete steps",
            "Includes quantum operations",
            "Defines expected outcomes"
        ],
        "OBSERVATION": [
            "Documents actual results",
            "Includes metrics and measurements",
            "Notes any deviations"
        ],
        "REFLECTION": [
            "Analyzes effectiveness",
            "Suggests improvements",
            "Plans next steps"
        ]
    }
    
    def __init__(self):
        """Initialize the ReACT validator."""
        self.validation_results = {
            component: {"present": False, "valid": False}
            for component in self.REACT_COMPONENTS
        }
    
    def validate_response(self, response: str) -> Dict[str, Any]:
        """Validate a ReACT response.
        
        Args:
            response: The response text to validate
            
        Returns:
            Dictionary containing validation results
        """
        self._reset_validation()
        
        # Check for presence of components
        for component, pattern in self.REQUIRED_PATTERNS.items():
            match = re.search(pattern, response, re.DOTALL)
            if match:
                self.validation_results[component]["present"] = True
                content = match.group(0).strip()
                self.validation_results[component]["valid"] = self._validate_component(
                    component, content
                )
        
        return self._get_validation_summary()
    
    def _reset_validation(self):
        """Reset validation results."""
        for component in self.REACT_COMPONENTS:
            self.validation_results[component] = {
                "present": False,
                "valid": False
            }
    
    def _validate_component(self, component: str, content: str) -> bool:
        """Validate a specific ReACT component.
        
        Args:
            component: The component name
            content: The component content
            
        Returns:
            Boolean indicating if component is valid
        """
        if not content:
            return False
            
        # Check against validation rules
        rules = self.VALIDATION_RULES.get(component, [])
        valid_count = 0
        
        for rule in rules:
            if self._check_rule(content, rule):
                valid_count += 1
                
        # Component is valid if it satisfies at least 2/3 of rules
        return valid_count >= len(rules) * 2 // 3
    
    def _check_rule(self, content: str, rule: str) -> bool:
        """Check if content satisfies a validation rule.
        
        Args:
            content: The content to check
            rule: The rule description
            
        Returns:
            Boolean indicating if rule is satisfied
        """
        # Rule checking logic can be expanded based on specific requirements
        keywords = rule.lower().split()
        content_lower = content.lower()
        
        # Simple keyword matching for now
        return any(keyword in content_lower for keyword in keywords)
    
    def _get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results.
        
        Returns:
            Dictionary containing validation summary
        """
        all_present = all(
            result["present"] 
            for result in self.validation_results.values()
        )
        all_valid = all(
            result["valid"] 
            for result in self.validation_results.values()
        )
        
        return {
            "valid": all_present and all_valid,
            "components": self.validation_results,
            "summary": {
                "components_present": sum(
                    1 for result in self.validation_results.values() 
                    if result["present"]
                ),
                "components_valid": sum(
                    1 for result in self.validation_results.values() 
                    if result["valid"]
                ),
                "total_components": len(self.REACT_COMPONENTS)
            }
        }
    
    def format_validation_results(self, results: Dict[str, Any]) -> str:
        """Format validation results for display.
        
        Args:
            results: Validation results dictionary
            
        Returns:
            Formatted string of validation results
        """
        output = []
        output.append("ReACT Validation Results:")
        output.append("=" * 50)
        
        # Overall status
        status = "✅ PASSED" if results["valid"] else "❌ FAILED"
        output.append(f"Overall Status: {status}")
        output.append("-" * 50)
        
        # Component details
        for component, result in results["components"].items():
            present = "✓" if result["present"] else "✗"
            valid = "✓" if result["valid"] else "✗"
            output.append(f"{component}:")
            output.append(f"  Present: {present}")
            output.append(f"  Valid: {valid}")
        
        # Summary
        output.append("-" * 50)
        summary = results["summary"]
        output.append("Summary:")
        output.append(f"  Components Present: {summary['components_present']}/{summary['total_components']}")
        output.append(f"  Components Valid: {summary['components_valid']}/{summary['total_components']}")
        
        return "\n".join(output)
