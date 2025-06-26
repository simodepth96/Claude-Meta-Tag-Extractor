# Claude Meta Data Extractor
In this repository, you will find the raw Python code I used to transform structured JSON data into readable text-based content in the form of an Excel table.

- 🔗 [GitHub: Claude Raw Python Code](https://github.com/simodepth96/Claude-Meta-Tag-Extractor/blob/main/raw.py)

A Streamlit app is also available as a shortcut. Just load your JSON export straight into the app and it'll extract insights in a table-based format.
- 🔗 [Claude Meta Data Extractor (Streamlit)](https://claude-meta-tag-extractor.streamlit.app/)


## ⚠️ Requirements

- **JavaScript Bookmarklet:**
After Claude returned an output in response to your prompt, use the following JavScript bookmarklet to export the raw structured data from the conversation.


### Claude Grounded Query Extractor

```javascript
javascript:(async()=>{try{const c=location.pathname.match(/\/chat\/([^/]+)/)?.[1];if(!c){alert('Open%20a%20Claude%20chat%20first');return;}const t=Date.now();const o=(await(await fetch(`/api/organizations?_t=${t}`,{credentials:'include',cache:'no-cache'})).json())[0].uuid;const j=await(await fetch(`/api/organizations/${o}/chat_conversations/${c}?tree=true&rendering_mode=messages&render_all_tools=true&_t=${t}`,{credentials:'include',cache:'no-cache'})).json();const u=URL.createObjectURL(new Blob([JSON.stringify(j,null,2)],{type:'application/json'}));Object.assign(document.createElement('a'),{href:u,download:`claude-${c}-rich.json`}).click();setTimeout(()=>URL.revokeObjectURL(u),2000);}catch(e){alert('Could%20not%20fetch%20rich%20conversation%20JSON');console.error(e);}})();
```

