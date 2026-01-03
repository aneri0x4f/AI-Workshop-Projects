
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import httpx
import json
from io import StringIO
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "<ADD HERE>"
BASE_URL = "<ADD HERE>"

def clean_data_for_json(data):
    """Convert pandas data to JSON-safe format by handling NaN, Inf, and other problematic values"""
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, (np.integer, np.int64, np.int32)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64, np.float32)):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    elif isinstance(data, np.bool_):
        return bool(data)
    elif pd.isna(data):
        return None
    elif isinstance(data, str):
        return data if data.strip() else None
    return data


@app.post("/api/analyze-interactive")
async def analyze_with_interactive_graphs(file: UploadFile = File(...)):
    try:
        # Read CSV
        contents = await file.read()
        
        # Read with string dtype to prevent automatic type inference issues
        df = pd.read_csv(StringIO(contents.decode('utf-8')), keep_default_na=True)
        
        # Replace empty strings with None for cleaner data
        df = df.replace('', None)
        df = df.replace(r'^\s*$', None, regex=True)
        
        # Get basic info
        columns = df.columns.tolist()
        shape = list(df.shape)
        
        # Get dtypes safely
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Get sample data - clean it for JSON
        sample_data = df.head(10).to_dict('records')
        sample_data_clean = clean_data_for_json(sample_data)
        
        # Get statistics only for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            stats = df[numeric_cols].describe().to_dict()
            stats_clean = clean_data_for_json(stats)
        else:
            stats_clean = {}
        
        # Get missing values count
        missing_values = df.isnull().sum().to_dict()
        missing_values_clean = clean_data_for_json(missing_values)
        
        data_summary = {
            "columns": columns,
            "shape": shape,
            "dtypes": dtypes,
            "sample": sample_data_clean,
            "statistics": stats_clean,
            "missing_values": missing_values_clean,
            "numeric_columns": numeric_cols
        }
        
        # Create a simplified summary for the prompt
        prompt_summary = {
            "columns": columns,
            "shape": shape,
            "numeric_columns": numeric_cols,
            "sample_rows": sample_data_clean[:5]  # Only first 5 rows
        }
        
        # Ask LLM to generate interactive visualization code
        prompt = f"""You are a data visualization expert. Analyze this CSV data and generate interactive Plotly graphs.

Data Summary:
- Columns: {prompt_summary['columns']}
- Shape: {prompt_summary['shape'][0]} rows × {prompt_summary['shape'][1]} columns
- Numeric columns available for visualization: {prompt_summary['numeric_columns']}

Sample data (first 5 rows):
{json.dumps(prompt_summary['sample_rows'], indent=2)}

Generate:
1. A brief analysis of the data (key insights, trends, patterns)
2. 3 interactive Plotly graphs as standalone HTML (using plotly.js CDN version 2.27.0)
3. Focus on the numeric columns for visualizations

Return your response as JSON with this structure:
{{
  "analysis": "your detailed analysis text including insights about the data patterns",
  "graphs": [
    {{
      "title": "Graph 1 Title",
      "description": "What this graph shows",
      "html": "<div id='graph0'></div><script src='https://cdn.plot.ly/plotly-2.27.0.min.js'></script><script>var data=[{{x:['1-Oct','2-Oct','3-Oct'],y:[13,16,11],type:'bar',marker:{{color:'rgb(102,126,234)'}}}}];var layout={{title:'Daily Calls',xaxis:{{title:'Date'}},yaxis:{{title:'Calls'}}}};Plotly.newPlot('graph0',data,layout,{{responsive:true}});</script>"
    }},
    {{
      "title": "Graph 2 Title",
      "description": "What this shows",
      "html": "<div id='graph1'></div><script>var data=[{{...}}];var layout={{...}};Plotly.newPlot('graph1',data,layout,{{responsive:true}});</script>"
    }},
    {{
      "title": "Graph 3 Title",
      "description": "What this shows",
      "html": "<div id='graph2'></div><script>var data=[{{...}}];var layout={{...}};Plotly.newPlot('graph2',data,layout,{{responsive:true}});</script>"
    }}
  ]
}}

Important: 
- Use plotly.js CDN: https://cdn.plot.ly/plotly-2.27.0.min.js (include only in first graph)
- Use unique div IDs: graph0, graph1, graph2
- Create complete, executable HTML for each graph
- Use actual data from the sample
- Make graphs interactive with responsive:true
- Choose appropriate graph types (bar charts, line charts, pie charts)
"""

        payload = {
            "model": "claude-sonnet-4-5-20250929",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert data analyst specializing in interactive visualizations with Plotly. Always return valid JSON with properly escaped strings."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                BASE_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                error_detail = f"LLM API error: {response.status_code} - {response.text[:200]}"
                print(error_detail)
                raise HTTPException(status_code=response.status_code, detail=error_detail)
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response
            try:
                # Clean up markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                analysis_result = json.loads(content.strip())
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Content received: {content[:500]}")
                analysis_result = {
                    "analysis": "Analysis completed. See graphs below.",
                    "graphs": []
                }
        
        # Return response with cleaned data
        return {
            "filename": file.filename,
            "data_summary": data_summary,
            "analysis": analysis_result.get("analysis", ""),
            "interactive_graphs": analysis_result.get("graphs", [])
        }
        
    except pd.errors.ParserError as e:
        print(f"CSV parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except Exception as e:
        print(f"Error in analyze_with_interactive_graphs: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/")
async def root():
    return {"message": "AI Clone Backend is running! 🚀"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)