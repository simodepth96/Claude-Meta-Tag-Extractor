import pandas as pd
import json

# Load JSON from file
with open('/content/claude-1477a78a-704b-4df0-9e36-3f7a24bf32a5-rich.json', encoding='utf-8') as f:
    data = json.load(f)

# Extract web results
web_results = data['chat_messages'][3]['content'][2]

# Extract the relevant data
try:
    # Check if it's a tool_result structure
    if isinstance(web_results, dict) and web_results.get('type') == 'tool_result':
        content = web_results.get('content', [])
        
        rows = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'knowledge':
                # Extract the required fields
                row = {
                    'title': item.get('title', 'N/A'),
                    'url': item.get('url', 'N/A'),
                    'site_name': item.get('metadata', {}).get('site_name', 'N/A'),
                    'favicon_url': item.get('metadata', {}).get('favicon_url', 'N/A')
                }
                rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Display results
        print(f"✅ Extracted {len(rows)} web results:")
        print("\n" + df.to_string(index=False))
        
        # Save to Excel
        df.to_excel("web_results_extracted.xlsx", index=False)
        print(f"\n💾 Saved to web_results_extracted.xlsx")
        
    else:
        print("❌ Unexpected structure. Let's explore what we have:")
        
        # If it's a list, check the first few items
        if isinstance(web_results, list):
            print(f"It's a list with {len(web_results)} items")
            for i, item in enumerate(web_results[:3]):
                print(f"Item {i}: {type(item)} - {str(item)[:100]}...")
        
        # If it's a dict, show its keys
        elif isinstance(web_results, dict):
            print(f"It's a dict with keys: {list(web_results.keys())}")
            
except Exception as e:
    print(f"❌ Error processing web results: {e}")
    
    def find_web_results(obj, path=""):
        """Recursively search for web_search results"""
        results = []
        
        if isinstance(obj, dict):
            # Check if this is a web_search tool result
            if obj.get('name') == 'web_search' and 'content' in obj:
                content = obj['content']
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'knowledge':
                            results.append({
                                'title': item.get('title', 'N/A'),
                                'url': item.get('url', 'N/A'),
                                'site_name': item.get('metadata', {}).get('site_name', 'N/A'),
                                'favicon_url': item.get('metadata', {}).get('favicon_url', 'N/A'),
                                'found_at': path
                            })
            
            # Continue searching in nested objects
            for key, value in obj.items():
                results.extend(find_web_results(value, f"{path}.{key}" if path else key))
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                results.extend(find_web_results(item, f"{path}[{i}]"))
        
        return results
    
    # Search the entire data structure
    all_results = find_web_results(data)
    
    if all_results:
        df = pd.DataFrame(all_results)
        print(f"\n✅ Found {len(all_results)} web results:")
        print(df.to_string(index=False))
        
        # Save results
        df.to_excel("web_results_found.xlsx", index=False)
        print("\n💾 Saved to web_results_found.xlsx")
    else:
        print("❌ No web search results found in the entire JSON file")
