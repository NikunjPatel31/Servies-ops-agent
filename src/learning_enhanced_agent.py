#!/usr/bin/env python3
"""
Learning-Enhanced Multi-Endpoint Agent
======================================

This module extends the existing multi-endpoint agent with learning capabilities.
It integrates with the LearningSystem to continuously improve pattern matching.
"""

import json
import re
from typing import Dict, List, Any, Optional
from src.multi_endpoint_agent import MultiEndpointAgent
from src.learning_system import LearningSystem

class LearningEnhancedAgent(MultiEndpointAgent):
    """
    Enhanced multi-endpoint agent with learning capabilities
    """
    
    def __init__(self, learning_db_path: str = "data/learning_database.db"):
        super().__init__()
        
        # Initialize learning system
        self.learning_system = LearningSystem(learning_db_path)
        
        # Enhanced patterns from learning
        self.enhanced_patterns = {}
        self.last_interaction_id = None
        
        # Load learned patterns
        self._load_learned_patterns()
        
        print("🧠 Learning-Enhanced Agent initialized!")
    
    def _load_learned_patterns(self):
        """Load learned patterns and integrate with existing patterns"""
        try:
            # Get current patterns (you may need to adjust this based on your existing structure)
            existing_patterns = {
                'status': [
                    r'status\s+(?:is|equals?)\s+([a-z\s,and]+?)(?:\s+and\s+(?:priority|urgency|category|department|subject)|$)',
                    r'(?:with|having)\s+status\s+(?:is\s+|as\s+)?([a-z\s,and]+?)(?:\s+and\s+(?:priority|urgency|category|department|subject)|$)',
                ],
                'priority': [
                    r'priority\s+(?:is|as|equals?)\s+([a-z\s,and]+?)(?:\s+and\s+(?:status|urgency|category|department|subject)|$)',
                    r'(?:with|having)\s+priority\s+(?:is\s+|as\s+)?([a-z\s,and]+?)(?:\s+and\s+(?:status|urgency|category|department|subject)|$)',
                ],
                'urgency': [
                    r'urgency\s+(?:is|equals?)\s+([a-z\s,and]+?)(?:\s+and\s+(?:status|priority|category|department|subject)|$)',
                    r'(?:with|having)\s+urgency\s+(?:is\s+|as\s+)?([a-z\s,and]+?)(?:\s+and\s+(?:status|priority|category|department|subject)|$)',
                ],
                'subject': [
                    r'subject\s+contains\s+([a-z\s]+)',
                    r'(?:with|having)\s+subject\s+(?:contains\s+)?([a-z\s]+)',
                ]
            }
            
            # Integrate with learned patterns
            self.enhanced_patterns = self.learning_system.integrate_with_existing_patterns(existing_patterns)
            
            print(f"✅ Loaded and integrated learned patterns for {len(self.enhanced_patterns)} field types")
            
        except Exception as e:
            print(f"⚠️ Failed to load learned patterns: {e}")
            self.enhanced_patterns = {}
    
    def execute_query(self, user_prompt: str) -> Dict[str, Any]:
        """
        Execute query with learning enhancement
        
        Args:
            user_prompt: User's natural language prompt
            
        Returns:
            Enhanced query result with learning integration
        """
        print(f"🧠 Learning-Enhanced Agent processing: '{user_prompt}'")
        
        # Get pattern suggestions from learning system
        pattern_suggestions = self.learning_system.get_pattern_suggestions_for_prompt(user_prompt)
        
        if pattern_suggestions:
            print(f"💡 Found {len(pattern_suggestions)} learned pattern suggestions")
            for field_type, suggestions in pattern_suggestions.items():
                print(f"   📋 {field_type}: {len(suggestions)} suggestions")
        
        # Execute the original query
        result = super().execute_query(user_prompt)
        
        # Record the interaction for learning if successful
        if result.get('success', False) and 'qualification' in result:
            try:
                self._record_successful_interaction(user_prompt, result)
            except Exception as e:
                print(f"⚠️ Failed to record interaction for learning: {e}")
        
        # Add learning metadata to result
        result['learning_metadata'] = {
            'pattern_suggestions_used': len(pattern_suggestions),
            'learning_enabled': True,
            'interaction_recorded': self.last_interaction_id is not None
        }
        
        return result
    
    def _record_successful_interaction(self, user_prompt: str, result: Dict[str, Any]):
        """Record successful interaction for learning"""
        try:
            endpoint = result.get('endpoint', 'unknown')
            qualification = result.get('qualification', {})
            
            # Extract filters from qualification
            filters = []
            qual_details = qualification.get('qualDetails', {})
            quals = qual_details.get('quals', [])
            
            for qual in quals:
                filters.append({
                    'leftOperand': qual.get('leftOperand', {}),
                    'operator': qual.get('operator', ''),
                    'rightOperand': qual.get('rightOperand', {}),
                    'type': qual.get('type', '')
                })
            
            # Determine if API call was successful
            api_success = 'error' not in result.get('response', {})
            result_count = 0
            
            if api_success and 'response' in result:
                response = result['response']
                if isinstance(response, dict):
                    result_count = response.get('totalCount', len(response.get('objectList', [])))
                elif isinstance(response, list):
                    result_count = len(response)
            
            # Record the interaction
            self.last_interaction_id = self.learning_system.record_successful_interaction(
                user_prompt=user_prompt,
                endpoint=endpoint,
                filters=filters,
                api_success=api_success,
                result_count=result_count
            )
            
            print(f"📝 Recorded interaction {self.last_interaction_id} for learning")
            
        except Exception as e:
            print(f"⚠️ Failed to record interaction: {e}")
            self.last_interaction_id = None
    
    def get_enhanced_patterns_for_field(self, field_type: str) -> List[str]:
        """Get enhanced patterns for a specific field type"""
        return self.enhanced_patterns.get(field_type, [])
    
    def resolve_status_references_enhanced(self, user_prompt: str) -> Dict[str, Any]:
        """Enhanced status resolution using learned patterns"""
        # Try learned patterns first
        learned_patterns = self.learning_system.get_learned_patterns('status', min_confidence=0.8)
        
        for pattern_info in learned_patterns:
            try:
                pattern = pattern_info['pattern_regex']
                matches = re.findall(pattern, user_prompt.lower(), re.IGNORECASE)
                
                if matches:
                    print(f"🎯 Using learned pattern for status: {pattern_info['description']}")
                    # Process matches using the learned pattern
                    # (You would implement the specific logic here based on your needs)
                    break
                    
            except re.error:
                continue
        
        # Fall back to original method
        return super().resolve_status_references(user_prompt)
    
    def resolve_priority_references_enhanced(self, user_prompt: str) -> Dict[str, Any]:
        """Enhanced priority resolution using learned patterns"""
        # Try learned patterns first
        learned_patterns = self.learning_system.get_learned_patterns('priority', min_confidence=0.8)
        
        for pattern_info in learned_patterns:
            try:
                pattern = pattern_info['pattern_regex']
                matches = re.findall(pattern, user_prompt.lower(), re.IGNORECASE)
                
                if matches:
                    print(f"🎯 Using learned pattern for priority: {pattern_info['description']}")
                    # Process matches using the learned pattern
                    break
                    
            except re.error:
                continue
        
        # Fall back to original method
        return super().resolve_priority_references(user_prompt)
    
    def provide_user_feedback(self, feedback_type: str, comment: str = None) -> bool:
        """
        Allow users to provide feedback on the last interaction
        
        Args:
            feedback_type: 'correct', 'incorrect', 'partial'
            comment: Optional user comment
            
        Returns:
            True if feedback was recorded successfully
        """
        if self.last_interaction_id is None:
            print("❌ No recent interaction to provide feedback on")
            return False
        
        try:
            self.learning_system.record_user_feedback(
                interaction_id=self.last_interaction_id,
                feedback_type=feedback_type,
                comment=comment
            )
            print(f"✅ Feedback recorded: {feedback_type}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to record feedback: {e}")
            return False
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        return self.learning_system.get_learning_statistics()
    
    def export_learned_knowledge(self, output_file: str = None) -> Dict[str, Any]:
        """Export all learned knowledge"""
        stats = self.get_learning_statistics()
        patterns = self.learning_system.export_learned_patterns(output_file)
        performance = self.learning_system.analyze_pattern_performance()
        
        return {
            'statistics': stats,
            'learned_patterns': patterns,
            'pattern_performance': performance,
            'export_timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def refresh_learned_patterns(self):
        """Refresh learned patterns from the database"""
        print("🔄 Refreshing learned patterns...")
        self._load_learned_patterns()
        print("✅ Learned patterns refreshed")
    
    def cleanup_learning_data(self, days_to_keep: int = 90):
        """Clean up old learning data"""
        self.learning_system.cleanup_old_data(days_to_keep)
        self.refresh_learned_patterns()
    
    def suggest_pattern_improvements(self, user_prompt: str) -> Dict[str, List[str]]:
        """Get pattern improvement suggestions for a specific prompt"""
        current_patterns = self.enhanced_patterns
        return self.learning_system.suggest_improved_patterns(user_prompt, current_patterns)
