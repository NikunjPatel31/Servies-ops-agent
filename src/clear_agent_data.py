#!/usr/bin/env python3
"""
Clear Agent Data
================

This script clears all learned data from the knowledge agents,
allowing you to start fresh and teach only specific APIs.
"""

import os
import sqlite3
import glob
from pathlib import Path

def find_database_files():
    """Find all database files created by the agents"""
    db_files = []
    
    # Common database file patterns
    patterns = [
        "*.db",
        "*knowledge*.db", 
        "*agent*.db",
        "*api*.db"
    ]
    
    for pattern in patterns:
        db_files.extend(glob.glob(pattern))
    
    # Remove duplicates
    return list(set(db_files))

def clear_database(db_path):
    """Clear all data from a database file"""
    try:
        if not os.path.exists(db_path):
            return f"❌ Database not found: {db_path}"
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            conn.close()
            return f"✅ {db_path} - No tables found (already empty)"
        
        # Clear all tables
        cleared_tables = []
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name}")
            cleared_tables.append(table_name)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        return f"✅ {db_path} - Cleared tables: {', '.join(cleared_tables)}"
        
    except Exception as e:
        return f"❌ Error clearing {db_path}: {str(e)}"

def delete_database(db_path):
    """Completely delete a database file"""
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            return f"🗑️  Deleted: {db_path}"
        else:
            return f"❌ File not found: {db_path}"
    except Exception as e:
        return f"❌ Error deleting {db_path}: {str(e)}"

def clear_all_agent_data(delete_files=False):
    """Clear all agent data"""
    print("🧹 CLEARING ALL AGENT DATA")
    print("=" * 40)
    
    # Find all database files
    db_files = find_database_files()
    
    if not db_files:
        print("✅ No database files found - agents are already clean!")
        return
    
    print(f"📁 Found {len(db_files)} database files:")
    for db_file in db_files:
        print(f"   - {db_file}")
    
    print(f"\n🧹 Clearing data...")
    
    results = []
    for db_file in db_files:
        if delete_files:
            result = delete_database(db_file)
        else:
            result = clear_database(db_file)
        results.append(result)
        print(f"   {result}")
    
    print(f"\n✅ Data clearing complete!")
    
    # Show summary
    success_count = sum(1 for r in results if r.startswith("✅") or r.startswith("🗑️"))
    print(f"📊 Summary: {success_count}/{len(results)} operations successful")
    
    return results

def interactive_clear():
    """Interactive data clearing"""
    print("🧹 INTERACTIVE AGENT DATA CLEANER")
    print("=" * 40)
    
    # Find database files
    db_files = find_database_files()
    
    if not db_files:
        print("✅ No database files found - agents are already clean!")
        return
    
    print(f"📁 Found {len(db_files)} database files:")
    for i, db_file in enumerate(db_files, 1):
        # Get file size
        try:
            size = os.path.getsize(db_file)
            size_str = f"{size:,} bytes"
        except:
            size_str = "unknown size"
        
        print(f"   {i}. {db_file} ({size_str})")
    
    print(f"\nOptions:")
    print(f"1. Clear data (keep files)")
    print(f"2. Delete files completely")
    print(f"3. Show database contents")
    print(f"4. Cancel")
    
    choice = input(f"\nChoose option (1-4): ").strip()
    
    if choice == "1":
        print(f"\n🧹 Clearing data from all databases...")
        clear_all_agent_data(delete_files=False)
    
    elif choice == "2":
        confirm = input(f"\n⚠️  This will permanently delete all database files. Continue? (yes/no): ").strip().lower()
        if confirm == "yes":
            print(f"\n🗑️  Deleting all database files...")
            clear_all_agent_data(delete_files=True)
        else:
            print("❌ Operation cancelled")
    
    elif choice == "3":
        show_database_contents(db_files)
    
    elif choice == "4":
        print("❌ Operation cancelled")
    
    else:
        print("❌ Invalid choice")

def show_database_contents(db_files):
    """Show contents of database files"""
    print(f"\n📊 DATABASE CONTENTS:")
    print("=" * 30)
    
    for db_file in db_files:
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            print(f"\n📁 {db_file}:")
            
            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print("   No tables found")
                continue
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   - {table_name}: {count} records")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error reading {db_file}: {e}")

def create_fresh_agent():
    """Create a fresh agent after clearing data"""
    print(f"\n🆕 CREATING FRESH AGENT")
    print("=" * 30)
    
    try:
        from curl_api_trainer import CurlAPITrainer
        
        # Create new agent
        agent = CurlAPITrainer("FreshAPIAgent")
        
        stats = agent.get_stats()
        print(f"✅ Fresh agent created!")
        print(f"   📚 Documents: {stats['total_documents']}")
        print(f"   🎯 APIs: {stats['learned_apis']}")
        
        return agent
        
    except Exception as e:
        print(f"❌ Error creating fresh agent: {e}")
        return None

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clear":
            clear_all_agent_data(delete_files=False)
        elif command == "delete":
            clear_all_agent_data(delete_files=True)
        elif command == "show":
            db_files = find_database_files()
            show_database_contents(db_files)
        elif command == "fresh":
            clear_all_agent_data(delete_files=False)
            create_fresh_agent()
        else:
            print(f"❌ Unknown command: {command}")
            print(f"Usage: python3 clear_agent_data.py [clear|delete|show|fresh]")
    else:
        interactive_clear()

if __name__ == "__main__":
    main()
