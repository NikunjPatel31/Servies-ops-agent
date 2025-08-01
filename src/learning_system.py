#!/usr/bin/env python3
"""
Learning System for API Filter Generation
=========================================

This module implements a comprehensive learning system that:
1. Stores successful prompt→filter mappings
2. Learns new patterns from successful interactions
3. Improves pattern matching over time
4. Provides feedback-based learning
"""

import sqlite3
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from pathlib import Path
import logging

class LearningSystem:
    """
    Comprehensive learning system for API filter generation
    """
    
    def __init__(self, db_path: str = "data/learning_database.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Learning configuration
        self.min_pattern_confidence = 0.7
        self.min_pattern_frequency = 3
        self.learning_window_days = 30
        
        print(f"🧠 Learning System initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize the learning database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table for successful interactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS successful_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_hash TEXT NOT NULL,
                    user_prompt TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    filters_json TEXT NOT NULL,
                    api_success BOOLEAN NOT NULL,
                    result_count INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL DEFAULT 1.0
                )
            ''')
            
            # Table for learned patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_type TEXT NOT NULL,
                    pattern_regex TEXT NOT NULL,
                    pattern_description TEXT,
                    success_count INTEGER DEFAULT 1,
                    total_attempts INTEGER DEFAULT 1,
                    confidence_score REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Table for field mappings learned from successful queries
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learned_field_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_name TEXT NOT NULL,
                    field_value TEXT NOT NULL,
                    mapped_id INTEGER NOT NULL,
                    endpoint TEXT NOT NULL,
                    success_count INTEGER DEFAULT 1,
                    confidence_score REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table for user feedback
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interaction_id INTEGER,
                    feedback_type TEXT NOT NULL, -- 'correct', 'incorrect', 'partial'
                    user_comment TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (interaction_id) REFERENCES successful_interactions (id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_prompt_hash ON successful_interactions(prompt_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_field_type ON learned_patterns(field_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_field_mapping ON learned_field_mappings(field_name, field_value)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON successful_interactions(timestamp)')
            
            conn.commit()
            print("✅ Learning database initialized successfully")
    
    def record_successful_interaction(self, user_prompt: str, endpoint: str, 
                                    filters: List[Dict], api_success: bool, 
                                    result_count: int = 0) -> int:
        """
        Record a successful interaction for learning
        
        Args:
            user_prompt: The original user prompt
            endpoint: The API endpoint used
            filters: The generated filters that worked
            api_success: Whether the API call was successful
            result_count: Number of results returned
            
        Returns:
            interaction_id: ID of the recorded interaction
        """
        prompt_hash = hashlib.md5(user_prompt.lower().encode()).hexdigest()
        filters_json = json.dumps(filters, sort_keys=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO successful_interactions 
                (prompt_hash, user_prompt, endpoint, filters_json, api_success, result_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (prompt_hash, user_prompt, endpoint, filters_json, api_success, result_count))
            
            interaction_id = cursor.lastrowid
            conn.commit()
        
        print(f"📝 Recorded successful interaction: ID {interaction_id}")
        
        # Trigger pattern learning from this interaction
        self._learn_patterns_from_interaction(user_prompt, endpoint, filters)
        
        return interaction_id
    
    def _learn_patterns_from_interaction(self, user_prompt: str, endpoint: str, filters: List[Dict]):
        """Learn new patterns from a successful interaction"""
        prompt_lower = user_prompt.lower()
        
        for filter_obj in filters:
            try:
                # Extract filter information
                left_operand = filter_obj.get('leftOperand', {})
                operator = filter_obj.get('operator', '')
                right_operand = filter_obj.get('rightOperand', {})
                
                # Determine field type
                field_key = left_operand.get('key', left_operand.get('value', ''))
                field_type = self._extract_field_type(field_key)
                
                if not field_type:
                    continue
                
                # Learn patterns based on field type
                if field_type in ['status', 'priority', 'urgency', 'category', 'department']:
                    self._learn_field_value_patterns(prompt_lower, field_type, right_operand)
                elif field_type == 'subject':
                    self._learn_text_search_patterns(prompt_lower, right_operand)
                elif 'date' in field_type.lower() or 'time' in field_type.lower():
                    self._learn_date_patterns(prompt_lower, right_operand)
                    
            except Exception as e:
                self.logger.warning(f"Failed to learn from filter: {e}")
    
    def _extract_field_type(self, field_key: str) -> str:
        """Extract field type from field key"""
        if 'status' in field_key.lower():
            return 'status'
        elif 'priority' in field_key.lower():
            return 'priority'
        elif 'urgency' in field_key.lower():
            return 'urgency'
        elif 'category' in field_key.lower():
            return 'category'
        elif 'department' in field_key.lower():
            return 'department'
        elif 'subject' in field_key.lower():
            return 'subject'
        elif 'created' in field_key.lower() or 'updated' in field_key.lower():
            return 'date'
        elif 'technician' in field_key.lower() or 'requester' in field_key.lower():
            return 'user'
        else:
            return 'unknown'
    
    def _learn_field_value_patterns(self, prompt: str, field_type: str, right_operand: Dict):
        """Learn patterns for field value matching"""
        try:
            value_obj = right_operand.get('value', {})
            
            if value_obj.get('type') == 'ListLongValueRest':
                # Multiple values - learn conjunction patterns
                values = value_obj.get('value', [])
                if len(values) > 1:
                    # Look for "and" patterns
                    if ' and ' in prompt:
                        pattern = f'{field_type}\\s+(?:is|as|equals?)\\s+([a-z\\s,and]+?)(?:\\s+and\\s+(?:status|priority|urgency|category|department|subject)|$)'
                        self._store_learned_pattern(field_type, pattern, f"Multiple {field_type} with 'and' conjunction")
            
            elif value_obj.get('type') == 'StringValueRest':
                # Text search patterns
                search_text = value_obj.get('value', '')
                if 'contains' in prompt:
                    pattern = f'{field_type}\\s+contains\\s+([a-z\\s]+)'
                    self._store_learned_pattern(field_type, pattern, f"{field_type} contains pattern")
                    
        except Exception as e:
            self.logger.warning(f"Failed to learn field value pattern: {e}")
    
    def _learn_text_search_patterns(self, prompt: str, right_operand: Dict):
        """Learn patterns for text search"""
        try:
            value_obj = right_operand.get('value', {})
            search_text = value_obj.get('value', '')
            
            if 'contains' in prompt:
                # Find the context around 'contains'
                contains_match = re.search(r'(\w+)\s+contains\s+(\w+)', prompt)
                if contains_match:
                    field, value = contains_match.groups()
                    pattern = f'{field}\\s+contains\\s+([a-z\\s]+)'
                    self._store_learned_pattern('subject', pattern, f"Text contains pattern for {field}")
                    
        except Exception as e:
            self.logger.warning(f"Failed to learn text search pattern: {e}")
    
    def _learn_date_patterns(self, prompt: str, right_operand: Dict):
        """Learn patterns for date filtering"""
        try:
            # Look for date-related keywords
            date_keywords = ['today', 'yesterday', 'last week', 'this month', 'within', 'before', 'after']
            
            for keyword in date_keywords:
                if keyword in prompt:
                    if keyword == 'today':
                        pattern = r'(?:created|updated).*?today'
                        self._store_learned_pattern('date', pattern, f"Date filter for 'today'")
                    elif 'within' in prompt:
                        pattern = r'within\s+(?:last\s+)?(\d+)\s+(day|week|month)s?'
                        self._store_learned_pattern('date', pattern, f"Date filter for 'within' duration")
                        
        except Exception as e:
            self.logger.warning(f"Failed to learn date pattern: {e}")
    
    def _store_learned_pattern(self, field_type: str, pattern_regex: str, description: str):
        """Store a learned pattern in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if pattern already exists
            cursor.execute('''
                SELECT id, success_count, total_attempts FROM learned_patterns 
                WHERE field_type = ? AND pattern_regex = ?
            ''', (field_type, pattern_regex))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                pattern_id, success_count, total_attempts = existing
                cursor.execute('''
                    UPDATE learned_patterns 
                    SET success_count = success_count + 1,
                        total_attempts = total_attempts + 1,
                        confidence_score = CAST(success_count + 1 AS REAL) / (total_attempts + 1),
                        last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (pattern_id,))
                print(f"📈 Updated learned pattern: {description}")
            else:
                # Insert new pattern
                cursor.execute('''
                    INSERT INTO learned_patterns 
                    (field_type, pattern_regex, pattern_description, confidence_score)
                    VALUES (?, ?, ?, ?)
                ''', (field_type, pattern_regex, description, 1.0))
                print(f"🆕 Learned new pattern: {description}")
            
            conn.commit()

    def get_learned_patterns(self, field_type: str = None, min_confidence: float = None) -> List[Dict]:
        """
        Get learned patterns, optionally filtered by field type and confidence

        Args:
            field_type: Filter by specific field type
            min_confidence: Minimum confidence score

        Returns:
            List of learned patterns
        """
        if min_confidence is None:
            min_confidence = self.min_pattern_confidence

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = '''
                SELECT field_type, pattern_regex, pattern_description,
                       success_count, total_attempts, confidence_score,
                       created_at, last_used
                FROM learned_patterns
                WHERE is_active = 1 AND confidence_score >= ?
            '''
            params = [min_confidence]

            if field_type:
                query += ' AND field_type = ?'
                params.append(field_type)

            query += ' ORDER BY confidence_score DESC, success_count DESC'

            cursor.execute(query, params)
            results = cursor.fetchall()

            patterns = []
            for row in results:
                patterns.append({
                    'field_type': row[0],
                    'pattern_regex': row[1],
                    'description': row[2],
                    'success_count': row[3],
                    'total_attempts': row[4],
                    'confidence_score': row[5],
                    'created_at': row[6],
                    'last_used': row[7]
                })

            return patterns

    def suggest_improved_patterns(self, user_prompt: str, current_patterns: Dict) -> Dict[str, List[str]]:
        """
        Suggest improved patterns based on learned data

        Args:
            user_prompt: The current user prompt
            current_patterns: Current patterns being used

        Returns:
            Dictionary of suggested improved patterns by field type
        """
        suggestions = defaultdict(list)
        prompt_lower = user_prompt.lower()

        # Get recent successful interactions with similar prompts
        similar_interactions = self._find_similar_interactions(user_prompt)

        for interaction in similar_interactions:
            try:
                filters = json.loads(interaction['filters_json'])

                # Analyze what patterns worked for similar prompts
                for filter_obj in filters:
                    field_type = self._extract_field_type(
                        filter_obj.get('leftOperand', {}).get('key', '')
                    )

                    if field_type and field_type in current_patterns:
                        # Check if learned patterns might work better
                        learned_patterns = self.get_learned_patterns(field_type)

                        for pattern in learned_patterns:
                            if pattern['confidence_score'] > 0.8:
                                suggestions[field_type].append(pattern['pattern_regex'])

            except Exception as e:
                self.logger.warning(f"Failed to analyze interaction: {e}")

        return dict(suggestions)

    def _find_similar_interactions(self, user_prompt: str, limit: int = 10) -> List[Dict]:
        """Find similar successful interactions"""
        prompt_words = set(user_prompt.lower().split())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get recent successful interactions
            cursor.execute('''
                SELECT user_prompt, filters_json, result_count, confidence_score
                FROM successful_interactions
                WHERE api_success = 1
                AND timestamp > datetime('now', '-30 days')
                ORDER BY timestamp DESC
                LIMIT 50
            ''')

            interactions = cursor.fetchall()

            # Calculate similarity scores
            similar_interactions = []
            for row in interactions:
                stored_prompt, filters_json, result_count, confidence = row
                stored_words = set(stored_prompt.lower().split())

                # Simple Jaccard similarity
                intersection = len(prompt_words & stored_words)
                union = len(prompt_words | stored_words)
                similarity = intersection / union if union > 0 else 0

                if similarity > 0.3:  # Threshold for similarity
                    similar_interactions.append({
                        'prompt': stored_prompt,
                        'filters_json': filters_json,
                        'result_count': result_count,
                        'confidence': confidence,
                        'similarity': similarity
                    })

            # Sort by similarity and return top results
            similar_interactions.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_interactions[:limit]

    def record_user_feedback(self, interaction_id: int, feedback_type: str, comment: str = None):
        """
        Record user feedback on a specific interaction

        Args:
            interaction_id: ID of the interaction
            feedback_type: 'correct', 'incorrect', 'partial'
            comment: Optional user comment
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_feedback (interaction_id, feedback_type, user_comment)
                VALUES (?, ?, ?)
            ''', (interaction_id, feedback_type, comment))
            conn.commit()

        # Update confidence scores based on feedback
        self._update_confidence_from_feedback(interaction_id, feedback_type)

        print(f"📝 Recorded user feedback: {feedback_type} for interaction {interaction_id}")

    def _update_confidence_from_feedback(self, interaction_id: int, feedback_type: str):
        """Update confidence scores based on user feedback"""
        confidence_adjustment = {
            'correct': 0.1,      # Boost confidence
            'partial': 0.0,      # No change
            'incorrect': -0.2    # Reduce confidence
        }

        adjustment = confidence_adjustment.get(feedback_type, 0)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Update interaction confidence
            cursor.execute('''
                UPDATE successful_interactions
                SET confidence_score = MAX(0.1, MIN(1.0, confidence_score + ?))
                WHERE id = ?
            ''', (adjustment, interaction_id))

            # Get the prompt to update related patterns
            cursor.execute('''
                SELECT user_prompt, filters_json FROM successful_interactions WHERE id = ?
            ''', (interaction_id,))

            result = cursor.fetchone()
            if result:
                user_prompt, filters_json = result
                self._update_pattern_confidence_from_feedback(user_prompt, filters_json, adjustment)

            conn.commit()

    def _update_pattern_confidence_from_feedback(self, user_prompt: str, filters_json: str, adjustment: float):
        """Update pattern confidence based on feedback"""
        try:
            filters = json.loads(filters_json)
            prompt_lower = user_prompt.lower()

            # Find patterns that might have been used
            learned_patterns = self.get_learned_patterns(min_confidence=0.1)

            for pattern in learned_patterns:
                if re.search(pattern['pattern_regex'], prompt_lower):
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE learned_patterns
                            SET confidence_score = MAX(0.1, MIN(1.0, confidence_score + ?))
                            WHERE field_type = ? AND pattern_regex = ?
                        ''', (adjustment, pattern['field_type'], pattern['pattern_regex']))
                        conn.commit()

        except Exception as e:
            self.logger.warning(f"Failed to update pattern confidence: {e}")

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total interactions
            cursor.execute('SELECT COUNT(*) FROM successful_interactions')
            total_interactions = cursor.fetchone()[0]

            # Successful API calls
            cursor.execute('SELECT COUNT(*) FROM successful_interactions WHERE api_success = 1')
            successful_calls = cursor.fetchone()[0]

            # Learned patterns by field type
            cursor.execute('''
                SELECT field_type, COUNT(*), AVG(confidence_score)
                FROM learned_patterns
                WHERE is_active = 1
                GROUP BY field_type
            ''')
            patterns_by_type = {row[0]: {'count': row[1], 'avg_confidence': row[2]}
                              for row in cursor.fetchall()}

            # Recent learning activity (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) FROM successful_interactions
                WHERE timestamp > datetime('now', '-7 days')
            ''')
            recent_interactions = cursor.fetchone()[0]

            # User feedback summary
            cursor.execute('''
                SELECT feedback_type, COUNT(*) FROM user_feedback
                GROUP BY feedback_type
            ''')
            feedback_summary = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                'total_interactions': total_interactions,
                'successful_api_calls': successful_calls,
                'success_rate': successful_calls / total_interactions if total_interactions > 0 else 0,
                'patterns_by_type': patterns_by_type,
                'recent_interactions_7d': recent_interactions,
                'user_feedback': feedback_summary,
                'database_path': self.db_path
            }

    def export_learned_patterns(self, output_file: str = None) -> Dict[str, List[str]]:
        """
        Export learned patterns for integration with existing pattern matching

        Args:
            output_file: Optional file to save patterns to

        Returns:
            Dictionary of patterns organized by field type
        """
        patterns_by_type = defaultdict(list)
        learned_patterns = self.get_learned_patterns(min_confidence=self.min_pattern_confidence)

        for pattern in learned_patterns:
            patterns_by_type[pattern['field_type']].append({
                'regex': pattern['pattern_regex'],
                'description': pattern['description'],
                'confidence': pattern['confidence_score'],
                'usage_count': pattern['success_count']
            })

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(dict(patterns_by_type), f, indent=2)
            print(f"📁 Exported learned patterns to: {output_file}")

        return dict(patterns_by_type)

    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old learning data to maintain performance"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Remove old interactions
            cursor.execute('''
                DELETE FROM successful_interactions
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days_to_keep))

            # Remove patterns with very low confidence that haven't been used recently
            cursor.execute('''
                UPDATE learned_patterns
                SET is_active = 0
                WHERE confidence_score < 0.3
                AND last_used < datetime('now', '-30 days')
            ''')

            # Remove orphaned feedback
            cursor.execute('''
                DELETE FROM user_feedback
                WHERE interaction_id NOT IN (SELECT id FROM successful_interactions)
            ''')

            conn.commit()
            print(f"🧹 Cleaned up learning data older than {days_to_keep} days")

    def get_pattern_suggestions_for_prompt(self, user_prompt: str) -> Dict[str, List[str]]:
        """
        Get specific pattern suggestions for a given prompt

        Args:
            user_prompt: The user prompt to analyze

        Returns:
            Dictionary of suggested patterns by field type
        """
        suggestions = defaultdict(list)
        prompt_lower = user_prompt.lower()

        # Get all high-confidence learned patterns
        learned_patterns = self.get_learned_patterns(min_confidence=0.8)

        for pattern in learned_patterns:
            try:
                # Test if the pattern might match this prompt
                if re.search(pattern['pattern_regex'], prompt_lower, re.IGNORECASE):
                    suggestions[pattern['field_type']].append({
                        'pattern': pattern['pattern_regex'],
                        'description': pattern['description'],
                        'confidence': pattern['confidence_score'],
                        'usage_count': pattern['success_count']
                    })
            except re.error:
                # Skip invalid regex patterns
                continue

        return dict(suggestions)

    def integrate_with_existing_patterns(self, existing_patterns: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Integrate learned patterns with existing hardcoded patterns

        Args:
            existing_patterns: Current hardcoded patterns

        Returns:
            Enhanced patterns combining existing and learned patterns
        """
        enhanced_patterns = existing_patterns.copy()
        learned_patterns = self.export_learned_patterns()

        for field_type, patterns in learned_patterns.items():
            if field_type not in enhanced_patterns:
                enhanced_patterns[field_type] = []

            # Add high-confidence learned patterns
            for pattern_info in patterns:
                if pattern_info['confidence'] >= self.min_pattern_confidence:
                    pattern_regex = pattern_info['regex']

                    # Avoid duplicates
                    if pattern_regex not in enhanced_patterns[field_type]:
                        enhanced_patterns[field_type].append(pattern_regex)
                        print(f"🔗 Integrated learned pattern for {field_type}: {pattern_info['description']}")

        return enhanced_patterns

    def analyze_pattern_performance(self) -> Dict[str, Any]:
        """Analyze the performance of learned patterns"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get pattern performance metrics
            cursor.execute('''
                SELECT
                    field_type,
                    pattern_regex,
                    pattern_description,
                    success_count,
                    total_attempts,
                    confidence_score,
                    (julianday('now') - julianday(last_used)) as days_since_used
                FROM learned_patterns
                WHERE is_active = 1
                ORDER BY confidence_score DESC, success_count DESC
            ''')

            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    'field_type': row[0],
                    'pattern_regex': row[1],
                    'description': row[2],
                    'success_count': row[3],
                    'total_attempts': row[4],
                    'confidence_score': row[5],
                    'days_since_used': row[6],
                    'success_rate': row[3] / row[4] if row[4] > 0 else 0
                })

            # Calculate overall statistics
            total_patterns = len(patterns)
            high_confidence_patterns = len([p for p in patterns if p['confidence_score'] >= 0.8])
            recently_used_patterns = len([p for p in patterns if p['days_since_used'] <= 7])

            return {
                'total_patterns': total_patterns,
                'high_confidence_patterns': high_confidence_patterns,
                'recently_used_patterns': recently_used_patterns,
                'pattern_details': patterns,
                'avg_confidence': sum(p['confidence_score'] for p in patterns) / total_patterns if total_patterns > 0 else 0
            }
