#!/usr/bin/env python3
"""
Local Intelligence Agent
Provides intelligent filter generation without external LLM APIs
Uses advanced pattern matching and semantic understanding
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class LocalIntelligenceAgent:
    def __init__(self):
        # Dynamic mappings
        self.field_mappings = {
            'priority': {},
            'status': {},
            'urgency': {},
            'users': {},
            'locations': {},
            'categories': {}
        }
        
        # Semantic understanding patterns
        self.priority_synonyms = {
            'high': ['high', 'urgent', 'important', 'critical', 'p1', 'p2'],
            'medium': ['medium', 'normal', 'standard', 'p3'],
            'low': ['low', 'minor', 'p4'],
            'critical': ['critical', 'urgent', 'emergency', 'p1', 'severe']
        }
        
        self.status_synonyms = {
            'open': ['open', 'new', 'active', 'unresolved'],
            'in progress': ['in progress', 'working', 'active', 'processing'],
            'pending': ['pending', 'waiting', 'on hold', 'paused'],
            'resolved': ['resolved', 'fixed', 'completed', 'done'],
            'closed': ['closed', 'finished', 'archived']
        }
        
        # Note: today/yesterday patterns moved to enhanced date detection in _detect_time_filters
        self.time_patterns = {
            r'\blast\s+week\b': ('within_last', 7, 'days'),
            r'\blast\s+month\b': ('within_last', 30, 'days'),
            r'\blast\s+(\d+)\s+days?\b': ('within_last', None, 'days'),
            r'\bpast\s+(\d+)\s+days?\b': ('within_last', None, 'days'),
            r'\bin\s+the\s+last\s+(\d+)\s+days?\b': ('within_last', None, 'days'),
        }
        
        self.negation_patterns = [
            r'\bnot\s+',
            r'\bnon[-\s]',
            r'\bexcept\s+',
            r'\bexclude\s+',
            r'\bwithout\s+',
            r'\bisn\'?t\s+',
            r'\baren\'?t\s+'
        ]

    def update_field_mappings(self, mappings: Dict[str, Dict[str, int]]):
        """Update field mappings from live API data"""
        self.field_mappings.update(mappings)
        print(f"🧠 Local Intelligence updated mappings: {list(mappings.keys())}")

    def generate_filter_payload(self, user_prompt: str) -> Dict[str, Any]:
        """Generate filter payload using local intelligence"""
        try:
            print(f"🧠 Local Intelligence processing: '{user_prompt}'")
            
            # Normalize prompt
            prompt_lower = user_prompt.lower().strip()
            
            # Detect all filter components
            quals = []
            
            # 1. Priority detection
            priority_quals = self._detect_priority_filters(prompt_lower)
            quals.extend(priority_quals)
            
            # 2. Status detection
            status_quals = self._detect_status_filters(prompt_lower)
            quals.extend(status_quals)
            
            # 3. Time detection
            time_quals = self._detect_time_filters(prompt_lower)
            quals.extend(time_quals)
            
            # 4. Text search detection
            text_quals = self._detect_text_filters(prompt_lower)
            quals.extend(text_quals)
            
            # 5. User/assignee detection
            user_quals = self._detect_user_filters(prompt_lower)
            quals.extend(user_quals)
            
            # 6. Location detection
            location_quals = self._detect_location_filters(prompt_lower)
            quals.extend(location_quals)
            
            # 7. Category detection
            category_quals = self._detect_category_filters(prompt_lower)
            quals.extend(category_quals)
            
            payload = {
                "qualDetails": {
                    "quals": quals,
                    "type": "FlatQualificationRest"
                }
            }
            
            print(f"🎯 Generated {len(quals)} filter conditions")
            return payload
            
        except Exception as e:
            print(f"❌ Local Intelligence error: {e}")
            return {"qualDetails": {"quals": [], "type": "FlatQualificationRest"}}

    def _detect_priority_filters(self, prompt: str) -> List[Dict]:
        """Detect priority-related filters with semantic understanding"""
        quals = []
        
        # Check for negation
        is_negated = any(re.search(pattern, prompt) for pattern in self.negation_patterns)
        
        # Priority detection patterns
        priority_patterns = [
            r'\bpriority\s+(?:is|are|equals?)\s+([a-z\s,]+?)(?:\s+(?:and|or)\s+(?!priority)|$)',
            r'\b(high|medium|low|critical|urgent)\s+priority\b',
            r'\bp([1-4])\s+(?:tickets?|issues?|requests?)\b',
            r'\b(critical|urgent|important|high|medium|low)\s+(?:tickets?|issues?|requests?)\b'
        ]
        
        found_priorities = set()
        
        for pattern in priority_patterns:
            matches = re.finditer(pattern, prompt)
            for match in matches:
                if match.group(1):
                    # Extract priority values
                    priority_text = match.group(1).strip()
                    priorities = self._parse_priority_values(priority_text)
                    found_priorities.update(priorities)
        
        if found_priorities:
            priority_ids = []
            for priority in found_priorities:
                if priority in self.field_mappings.get('priority', {}):
                    priority_ids.append(self.field_mappings['priority'][priority])
            
            if priority_ids:
                operator = "not_in" if is_negated else "in"
                quals.append({
                    "leftOperand": {"key": "request.priorityId", "type": "PropertyOperandRest"},
                    "operator": operator,
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "ListLongValueRest", "value": priority_ids}
                    }
                })
                print(f"🎯 Priority filter: {operator} {priority_ids} ({list(found_priorities)})")
        
        return quals

    def _detect_status_filters(self, prompt: str) -> List[Dict]:
        """Detect status-related filters with semantic understanding"""
        quals = []
        
        # Check for negation
        is_negated = any(re.search(pattern, prompt) for pattern in self.negation_patterns)
        
        # Status detection patterns
        status_patterns = [
            r'\bstatus\s+(?:is|are|equals?)\s+([a-z\s,]+?)(?:\s+(?:and|or)\s+(?!status)|$)',
            r'\b(?:tickets?|requests?|issues?)\s+(?:that\s+are\s+)?([a-z\s]+?)(?:\s+(?:and|or)|$)',
            r'\b(open|closed|pending|resolved|in\s+progress)\s+(?:tickets?|requests?|issues?)\b',
            r'\bshow\s+([a-z\s]+?)\s+(?:tickets?|requests?|issues?)\b'
        ]
        
        found_statuses = set()
        
        for pattern in status_patterns:
            matches = re.finditer(pattern, prompt)
            for match in matches:
                if match.group(1):
                    status_text = match.group(1).strip()
                    statuses = self._parse_status_values(status_text)
                    found_statuses.update(statuses)
        
        if found_statuses:
            status_ids = []
            for status in found_statuses:
                if status in self.field_mappings.get('status', {}):
                    status_ids.append(self.field_mappings['status'][status])
            
            if status_ids:
                operator = "not_in" if is_negated else "in"
                quals.append({
                    "leftOperand": {"key": "request.statusId", "type": "PropertyOperandRest"},
                    "operator": operator,
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "ListLongValueRest", "value": status_ids}
                    }
                })
                print(f"🎯 Status filter: {operator} {status_ids} ({list(found_statuses)})")
        
        return quals

    def _detect_time_filters(self, prompt: str) -> List[Dict]:
        """Detect time-related filters with enhanced date handling"""
        quals = []

        # Enhanced date patterns for today/yesterday (use request.createdTime)
        enhanced_date_patterns = {
            r'\btoday\b': ('equal', 'today'),
            r'\byesterday\b': ('equal', 'yesterday'),
            r'\bcreated\s+today\b': ('equal', 'today'),
            r'\bcreated\s+yesterday\b': ('equal', 'yesterday'),
            r'\bmade\s+today\b': ('equal', 'today'),
            r'\bmade\s+yesterday\b': ('equal', 'yesterday')
        }

        # Check for enhanced date patterns first (today/yesterday)
        for pattern, (operator, value) in enhanced_date_patterns.items():
            if re.search(pattern, prompt):
                field_key = "request.createdTime"
                operand_type = "PropertyOperandRest"

                # Create appropriate filter based on operator
                if operator == "equal" and value in ["today", "yesterday"]:
                    # Use PropertyOperandRest with VariableOperandRest for today/yesterday
                    quals.append({
                        "type": "RelationalQualificationRest",
                        "leftOperand": {"key": field_key, "type": operand_type},
                        "operator": operator,
                        "rightOperand": {
                            "type": "VariableOperandRest",
                            "value": value
                        }
                    })
                    print(f"🎯 Date filter: {field_key} {operator} {value}")
                    return quals  # Return immediately for today/yesterday

        # Fallback to relative time patterns (last week, last month, etc.)
        relative_time_patterns = {
            r'\blast\s+week\b': ('within_last', 7, 'days'),
            r'\blast\s+month\b': ('within_last', 30, 'days'),
            r'\blast\s+(\d+)\s+days?\b': ('within_last', None, 'days'),
            r'\bpast\s+(\d+)\s+days?\b': ('within_last', None, 'days'),
            r'\bin\s+the\s+last\s+(\d+)\s+days?\b': ('within_last', None, 'days'),
            r'\bwithin\s+(\d+)\s+days?\b': ('within_last', None, 'days')
        }

        for pattern, (operator, value, unit) in relative_time_patterns.items():
            match = re.search(pattern, prompt)
            if match:
                if value is None and match.groups():
                    value = int(match.group(1))

                quals.append({
                    "type": "RelationalQualificationRest",
                    "leftOperand": {"key": "created_date", "type": "VariableOperandRest"},
                    "operator": operator,
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "DurationValueRest", "value": value, "unit": unit}
                    }
                })
                print(f"🎯 Time filter: {operator} {value} {unit}")
                break

        return quals

    def _detect_text_filters(self, prompt: str) -> List[Dict]:
        """Detect text search filters"""
        quals = []
        
        text_patterns = [
            r'\bsubject\s+containing\s+([a-z0-9]+)\b',
            r'\bwith\s+([a-z0-9]+)\s+in\s+(?:subject|title)\b',
            r'\babout\s+([a-z0-9]+)\b',
            r'\bmentioning\s+([a-z0-9]+)\b',
            r'\btickets?\s+(?:with|containing)\s+([a-z0-9]+)\b'
        ]
        
        for pattern in text_patterns:
            match = re.search(pattern, prompt)
            if match:
                keyword = match.group(1)
                quals.append({
                    "leftOperand": {"key": "request.subject", "type": "PropertyOperandRest"},
                    "operator": "contains",
                    "rightOperand": {
                        "type": "ValueOperandRest",
                        "value": {"type": "StringValueRest", "value": keyword}
                    }
                })
                print(f"🎯 Text filter: contains '{keyword}'")
                break
        
        return quals

    def _detect_user_filters(self, prompt: str) -> List[Dict]:
        """Detect user/assignee filters"""
        quals = []
        
        # Check for unassigned
        if re.search(r'\b(?:unassigned|no\s+assignee|not\s+assigned)\b', prompt):
            quals.append({
                "leftOperand": {"key": "request.technicianId", "type": "PropertyOperandRest"},
                "operator": "is_blank",
                "rightOperand": None
            })
            print("🎯 User filter: unassigned")
            return quals
        
        # Check for specific users
        user_patterns = [
            r'\bassigned\s+to\s+([a-z]+)\b',
            r'\b([a-z]+)\'?s?\s+(?:tickets?|requests?)\b',
            r'\bby\s+([a-z]+)\b'
        ]
        
        for pattern in user_patterns:
            match = re.search(pattern, prompt)
            if match:
                username = match.group(1).lower()
                if username in self.field_mappings.get('users', {}):
                    user_id = self.field_mappings['users'][username]
                    quals.append({
                        "leftOperand": {"key": "request.technicianId", "type": "PropertyOperandRest"},
                        "operator": "in",
                        "rightOperand": {
                            "type": "ValueOperandRest",
                            "value": {"type": "ListLongValueRest", "value": [user_id]}
                        }
                    })
                    print(f"🎯 User filter: assigned to {username} (ID: {user_id})")
                break
        
        return quals

    def _detect_location_filters(self, prompt: str) -> List[Dict]:
        """Detect location filters"""
        quals = []
        
        location_patterns = [
            r'\bfrom\s+([a-z\s]+?)(?:\s+office|\s+location|$)',
            r'\b([a-z\s]+?)\s+(?:office|location)\b'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, prompt)
            if match:
                location_name = match.group(1).strip().lower()
                if location_name in self.field_mappings.get('locations', {}):
                    location_id = self.field_mappings['locations'][location_name]
                    quals.append({
                        "leftOperand": {"key": "request.locationId", "type": "PropertyOperandRest"},
                        "operator": "in",
                        "rightOperand": {
                            "type": "ValueOperandRest",
                            "value": {"type": "ListLongValueRest", "value": [location_id]}
                        }
                    })
                    print(f"🎯 Location filter: {location_name} (ID: {location_id})")
                break
        
        return quals

    def _detect_category_filters(self, prompt: str) -> List[Dict]:
        """Detect category filters"""
        quals = []
        
        category_patterns = [
            r'\b(it|hr|facilities|finance|security|legal)\s+(?:tickets?|requests?|issues?)\b',
            r'\bfrom\s+(it|hr|facilities|finance|security|legal)\s+department\b'
        ]
        
        for pattern in category_patterns:
            match = re.search(pattern, prompt)
            if match:
                category_name = match.group(1).lower()
                if category_name in self.field_mappings.get('categories', {}):
                    category_id = self.field_mappings['categories'][category_name]
                    quals.append({
                        "leftOperand": {"key": "request.categoryId", "type": "PropertyOperandRest"},
                        "operator": "in",
                        "rightOperand": {
                            "type": "ValueOperandRest",
                            "value": {"type": "ListLongValueRest", "value": [category_id]}
                        }
                    })
                    print(f"🎯 Category filter: {category_name} (ID: {category_id})")
                break
        
        return quals

    def _parse_priority_values(self, priority_text: str) -> List[str]:
        """Parse priority values from text with semantic understanding"""
        priorities = set()
        
        # Split by common separators
        parts = re.split(r'[,\s]+(?:and|or|\&|\+)?\s*', priority_text.strip())
        
        for part in parts:
            part = part.strip().lower()
            if not part:
                continue
            
            # Direct mapping
            if part in self.field_mappings.get('priority', {}):
                priorities.add(part)
                continue
            
            # Semantic mapping
            for canonical, synonyms in self.priority_synonyms.items():
                if part in synonyms:
                    if canonical in self.field_mappings.get('priority', {}):
                        priorities.add(canonical)
                    break
            
            # P-notation (P1, P2, etc.)
            p_match = re.match(r'p(\d)', part)
            if p_match:
                p_num = int(p_match.group(1))
                priority_map = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low'}
                if p_num in priority_map:
                    canonical = priority_map[p_num]
                    if canonical in self.field_mappings.get('priority', {}):
                        priorities.add(canonical)
        
        return list(priorities)

    def _parse_status_values(self, status_text: str) -> List[str]:
        """Parse status values from text with semantic understanding"""
        statuses = set()
        
        # Split by common separators
        parts = re.split(r'[,\s]+(?:and|or|\&|\+)?\s*', status_text.strip())
        
        for part in parts:
            part = part.strip().lower()
            if not part:
                continue
            
            # Direct mapping
            if part in self.field_mappings.get('status', {}):
                statuses.add(part)
                continue
            
            # Semantic mapping
            for canonical, synonyms in self.status_synonyms.items():
                if part in synonyms:
                    if canonical in self.field_mappings.get('status', {}):
                        statuses.add(canonical)
                    break
        
        return list(statuses)

# Example usage and testing
if __name__ == "__main__":
    # Initialize agent
    agent = LocalIntelligenceAgent()
    
    # Update with sample mappings
    sample_mappings = {
        'priority': {'low': 1, 'medium': 2, 'high': 3, 'critical': 4},
        'status': {'open': 9, 'in progress': 10, 'pending': 11, 'resolved': 12, 'closed': 13},
        'users': {'john': 45, 'jane': 78, 'bob': 23},
        'locations': {'new york': 10, 'london': 15, 'tokyo': 20}
    }
    agent.update_field_mappings(sample_mappings)
    
    # Test prompts
    test_prompts = [
        "Show high priority open tickets",
        "Find tickets created last week",
        "Get critical issues assigned to John",
        "Display tickets from New York with medium priority",
        "Show tickets not closed",
        "Find tickets with subject containing login",
        "Show unassigned tickets",
        "Get P1 tickets from yesterday"
    ]
    
    print("🧪 Testing Local Intelligence Agent:")
    print("=" * 50)
    
    for prompt in test_prompts:
        try:
            payload = agent.generate_filter_payload(prompt)
            print(f"✅ Prompt: {prompt}")
            print(f"📋 Filters: {len(payload['qualDetails']['quals'])}")
            print("-" * 30)
        except Exception as e:
            print(f"❌ Error for '{prompt}': {e}")
            print("-" * 30)
