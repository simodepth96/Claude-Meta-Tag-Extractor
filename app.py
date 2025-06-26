import streamlit as st
import pandas as pd
import json
from io import BytesIO
import traceback

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

def extract_claude_metadata(data):
    """Extract metadata from Claude JSON export"""
    try:
        # First, try the direct path method
        web_results = data['chat_messages'][3]['content'][2]
        
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
            
            if rows:
                return pd.DataFrame(rows), "direct_path"
        
    except (KeyError, IndexError, TypeError):
        pass
    
    # If direct path fails, search the entire structure
    all_results = find_web_results(data)
    
    if all_results:
        return pd.DataFrame(all_results), "recursive_search"
    
    return pd.DataFrame(), "no_results"

def convert_df_to_excel(df):
    """Convert DataFrame to Excel bytes for download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def main():
    st.set_page_config(
        page_title="Claude Metadata Extractor",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Claude Export Metadata Extractor")
    st.markdown("Upload a Claude conversation JSON export file to extract web search metadata.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a JSON file", 
        type="json",
        help="Upload the JSON export from your Claude conversation"
    )
    
    if uploaded_file is not None:
        try:
            # Load JSON data
            json_data = json.load(uploaded_file)
            
            st.success("✅ JSON file loaded successfully!")
            
            # Show basic file info
            with st.expander("📄 File Information"):
                try:
                    chat_messages_count = len(json_data.get('chat_messages', []))
                    st.write(f"**Chat Messages:** {chat_messages_count}")
                    st.write(f"**File size:** {len(str(json_data))} characters")
                    
                    # Try to get conversation title or ID
                    if 'uuid' in json_data:
                        st.write(f"**Conversation ID:** {json_data['uuid']}")
                    if 'name' in json_data:
                        st.write(f"**Conversation Name:** {json_data['name']}")
                        
                except Exception as e:
                    st.write("Basic file information extracted")
            
            # Extract metadata
            st.subheader("🔍 Web Search Metadata")
            
            metadata_df, extraction_method = extract_claude_metadata(json_data)
            
            if not metadata_df.empty:
                # Show success message with method used
                if extraction_method == "direct_path":
                    st.success(f"✅ Found {len(metadata_df)} web results using direct path extraction")
                elif extraction_method == "recursive_search":
                    st.success(f"✅ Found {len(metadata_df)} web results using recursive search")
                
                # Display the metadata table
                st.dataframe(metadata_df, use_container_width=True)
                
                # Download button
                excel_data = convert_df_to_excel(metadata_df)
                st.download_button(
                    label="📥 Download Metadata (Excel)",
                    data=excel_data,
                    file_name="claude_web_metadata.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Show statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    unique_domains = metadata_df['site_name'].nunique()
                    st.metric("Unique Domains", unique_domains)
                with col2:
                    total_urls = len(metadata_df)
                    st.metric("Total URLs", total_urls)
                with col3:
                    urls_with_titles = len(metadata_df[metadata_df['title'] != 'N/A'])
                    st.metric("URLs with Titles", urls_with_titles)
                
            else:
                st.warning("❌ No web search metadata found in the uploaded file.")
                
                # Show debug information
                with st.expander("🔍 Debug Information"):
                    st.write("**File Structure Analysis:**")
                    
                    if 'chat_messages' in json_data:
                        st.write(f"- Found {len(json_data['chat_messages'])} chat messages")
                        
                        # Analyze the structure of chat messages
                        for i, msg in enumerate(json_data['chat_messages'][:5]):  # Show first 5
                            if isinstance(msg, dict) and 'content' in msg:
                                content_types = []
                                if isinstance(msg['content'], list):
                                    content_types = [item.get('type', 'unknown') if isinstance(item, dict) else type(item).__name__ for item in msg['content']]
                                st.write(f"  - Message {i}: {len(msg['content'])} content items, types: {content_types}")
                    else:
                        st.write("- No 'chat_messages' key found")
                        st.write(f"- Available keys: {list(json_data.keys())}")
        
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file. Please upload a valid JSON file from Claude.")
        except Exception as e:
            st.error(f"❌ An error occurred while processing the file: {str(e)}")
            with st.expander("Debug Information"):
                st.code(traceback.format_exc())
    
    else:
        # Instructions when no file is uploaded
        st.info("👆 Please upload a Claude conversation JSON export file to begin extraction.")
        
        with st.expander("ℹ️ How to use this app"):
            st.markdown("""
            1. **Export your conversation** from Claude as a JSON file
            2. **Upload the file** using the file uploader above
            3. **View the results** in the metadata table showing:
               - **Title**: Page title from web search results
               - **URL**: Source URL
               - **Site Name**: Domain/site name
               - **Favicon URL**: Website icon URL
               - **Found At**: Location in JSON (for recursive search)
            4. **Download** the results as an Excel file for further analysis
            
            **Expected JSON Structure:**
            The app looks for web search results in Claude's tool_result structures:
            ```
            {
              "chat_messages": [
                {
                  "content": [
                    {
                      "type": "tool_result",
                      "content": [
                        {
                          "type": "knowledge",
                          "title": "...",
                          "url": "...",
                          "metadata": {...}
                        }
                      ]
                    }
                  ]
                }
              ]
            }
            ```
            
            **Extraction Methods:**
            - **Direct Path**: Tries to access `chat_messages[3].content[2]` first
            - **Recursive Search**: Searches the entire JSON structure if direct path fails
            """)

if __name__ == "__main__":
    main()
