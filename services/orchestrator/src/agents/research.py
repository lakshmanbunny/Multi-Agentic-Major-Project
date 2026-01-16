"""
Research Agent - Dataset Discovery & Literature Review

This agent uses Tavily search and Arxiv to find relevant datasets and research papers
based on the user's machine learning goal.
"""

import os
import sys
from typing import Dict, List

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import ArxivAPIWrapper
from langchain_core.messages import SystemMessage, HumanMessage
import requests
import json

from libs.core.state import AgentState
from libs.core.logger import setup_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logger("research_agent", level="INFO")


def search_serper(query: str, num_results: int = 5) -> dict:
    """
    Search using Serper.dev Google Search API.
    
    Args:
        query: Search query string
        num_results: Number of results to return
    
    Returns:
        dict: Search results with 'organic' results list
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        logger.warning("SERPER_API_KEY not found, falling back to Tavily")
        return None
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": num_results})
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Serper API error: {e}")
        return None


def research_node(state: AgentState) -> AgentState:
    """
    Research Agent node that finds datasets and research papers.
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with research findings
    """
    user_goal = state.get("user_goal", "")
    existing_url = state["dataset_info"].get("url", "")

    # --- LOGIC FIX: Check if User Provided a URL ---
    if existing_url and len(existing_url.strip()) > 5:
        logger.info(f"✅ User provided dataset: {existing_url}")
        logger.info("Skipping web search to respect user input.")

        # We still generate a plan, but we assume the dataset is found
        state["research_plan"] = [
            f"1. Use user-provided dataset: {existing_url}",
            "2. Load data using Pandas and inspect schema",
            "3. Perform Exploratory Data Analysis (EDA)",
            "4. specific preprocessing and model training for this goal"
        ]
        
        state["messages"].append({
            "role": "assistant",
            "content": f"Research: Using user-provided dataset at {existing_url}"
        })
        
        # Move directly to Data Engineer
        state["next_step"] = "data_engineering_agent"
        return state
    # -----------------------------------------------

    logger.info(f"🔍 Research Agent started for goal: {user_goal}")
    
    # Initialize research_data structure
    research_data = {
        "queries": [],
        "dataset_name": "",
        "dataset_url": "",
        "source_type": "",
        "papers": []
    }
    
    try:
        # Initialize LLM
        # Using 1.5-flash-001 as it is the current stable version
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Step 1: Generate search queries using LLM - PRIORITIZE KAGGLE
        logger.info("Generating Kaggle-focused search queries...")
        
        # Get rejected URLs to exclude
        rejected_urls = state.get("rejected_urls", [])
        rejection_context = ""
        if rejected_urls:
            rejection_context = f"\n\nIMPORTANT: Avoid these previously rejected URLs:\n" + "\n".join([f"- {url}" for url in rejected_urls])
            logger.info(f"Excluding {len(rejected_urls)} previously rejected URL(s)")
        
        query_prompt = f"""Given this machine learning goal: "{user_goal}"
{rejection_context}

Generate TWO specific search queries that PRIORITIZE KAGGLE DATASETS:
1. A query to find Kaggle datasets (add 'site:kaggle.com/datasets' to ensure Kaggle results)
2. A query to find ML algorithms/papers

Format your response as:
DATASET_QUERY: kaggle dataset <relevant keywords here> site:kaggle.com/datasets
ALGORITHM_QUERY: <your algorithm query>"""
        
        query_response = llm.invoke(query_prompt)
        query_text = query_response.content
        
        # Parse queries
        dataset_query = ""
        algorithm_query = ""
        
        for line in query_text.split('\n'):
            if line.startswith("DATASET_QUERY:"):
                dataset_query = line.replace("DATASET_QUERY:", "").strip()
            elif line.startswith("ALGORITHM_QUERY:"):
                algorithm_query = line.replace("ALGORITHM_QUERY:", "").strip()
        
        # Capture queries
        if dataset_query:
            research_data["queries"].append(dataset_query)
        if algorithm_query:
            research_data["queries"].append(algorithm_query)
        
        logger.info(f"Dataset query: {dataset_query}")
        logger.info(f"Algorithm query: {algorithm_query}")
        
        # Step 2: Search for datasets - TRY SERPER FIRST, then Tavily fallback
        dataset_url = ""
        dataset_sources = []
        
        # Try Serper API first
        serper_available = os.getenv("SERPER_API_KEY") is not None
        if serper_available and dataset_query:
            logger.info("Using Serper API for dataset search...")
            dataset_search_query = f"{user_goal} dataset site:kaggle.com OR site:huggingface.co OR site:paperswithcode.com"
            serper_results = search_serper(dataset_search_query, num_results=5)
            
            if serper_results and 'organic' in serper_results:
                for result in serper_results['organic']:
                    url = result.get('link', '')
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    
                    # Filter valid dataset sources
                    if any(domain in url for domain in ['kaggle.com', 'huggingface.co', 'paperswithcode.com']):
                        if url not in rejected_urls:
                            dataset_sources.append({
                                'url': url,
                                'title': title,
                                'snippet': snippet
                            })
                
                if dataset_sources:
                    dataset_url = dataset_sources[0]['url']
                    logger.info(f"✅ Found dataset URL via Serper: {dataset_url}")
                    logger.info(f"   Total alternatives available: {len(dataset_sources)}")
        
        # Fallback to Tavily if Serper didn't work
        
        try:
            tavily_search = TavilySearchResults(
                max_results=5,  # Get more results to have options after filtering
                api_key=os.getenv("TAVILY_API_KEY")
            )
            
            if dataset_query:
                logger.info("Searching for Kaggle datasets with Tavily...")
                search_results = tavily_search.invoke(dataset_query)
                
                if search_results:
                    # Extract URLs and filter out rejected ones
                    for result in search_results:
                        if isinstance(result, dict):
                            url = result.get('url', '')
                            content = result.get('content', '')
                            
                            # Skip if URL was previously rejected
                            if url and url not in rejected_urls:
                                dataset_sources.append({
                                    'url': url,
                                    'snippet': content[:200]
                                })
                    
                    # Prioritize Kaggle URLs first
                    kaggle_sources = [s for s in dataset_sources if 'kaggle.com' in s['url'].lower()]
                    non_kaggle_sources = [s for s in dataset_sources if 'kaggle.com' not in s['url'].lower()]
                    dataset_sources = kaggle_sources + non_kaggle_sources
                    
                    # Use the first NON-REJECTED result
                    if dataset_sources:
                        dataset_url = dataset_sources[0]['url']
                        
                        # Capture dataset info
                        research_data["dataset_url"] = dataset_url
                        if 'kaggle.com' in dataset_url:
                            research_data["source_type"] = "kaggle"
                            # Extract Kaggle handle (e.g., username/dataset-name)
                            parts = dataset_url.split('/')[-2:]
                            if len(parts) == 2:
                                research_data["dataset_name"] = f"{parts[0]}/{parts[1]}"
                            else:
                                research_data["dataset_name"] = dataset_url.split('/')[-1]
                        else:
                            research_data["source_type"] = "direct"
                            research_data["dataset_name"] = dataset_url.split('/')[-1] or "Unknown Dataset"
                        
                        logger.info(f"✅ Found dataset URL: {dataset_url}")
                        logger.info(f"   Total alternatives available: {len(dataset_sources) - 1}")
                    else:
                        logger.warning("⚠️ All search results were previously rejected!")
        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            dataset_sources = []
        
        # Step 3: Find research papers - USE SERPER FOR BETTER RESULTS
        papers_text = "No relevant papers found."
        
        if serper_available:
            logger.info("Using Serper API for research papers...")
            papers_search_query = f"{user_goal} research paper pdf"
            papers_serper_results = search_serper(papers_search_query, num_results=5)
            
            if papers_serper_results and 'organic' in papers_serper_results:
                logger.info(f"✅ Found {len(papers_serper_results['organic'])} paper result(s)")
                
                for result in papers_serper_results['organic']:
                    paper_url = result.get('link', '')
                    paper_title = result.get('title', '')
                    paper_snippet = result.get('snippet', '')
                    
                    # Detect source type
                    source = 'web'
                    if 'arxiv.org' in paper_url:
                        source = 'arxiv'
                    elif '.pdf' in paper_url.lower():
                        source = 'pdf'
                    
                    # Only add papers with valid URLs (not generic homepages)
                    if paper_url and paper_url != 'https://arxiv.org' and len(paper_url) > 20:
                        research_data["papers"].append({
                            "title": paper_title or f"Research on {user_goal}",
                            "url": paper_url,
                            "summary": paper_snippet or "No summary available",
                            "source": source
                        })
        
        # Fallback to Arxiv if Serper didn't find papers or wasn't available
        if not research_data["papers"]: # Only use Arxiv if Serper didn't yield results
            try:
                arxiv = ArxivAPIWrapper(top_k_results=1)
                logger.info("Searching Arxiv for research papers...")
                
                # Use algorithm query or user goal
                query = algorithm_query if algorithm_query else user_goal
                arxiv_results = arxiv.run(query)
                
                if arxiv_results:
                    papers_text = arxiv_results[:500]  # Truncate for display
                    research_data["papers"].append({
                        "title": f"Research papers on {user_goal}",
                        "url": "https://arxiv.org",
                        "summary": papers_text,
                        "source": "arxiv"
                    })
                    logger.info(f"✅ Found 1 research paper(s) via Arxiv fallback")
                else:
                    logger.info("No research papers found via Arxiv fallback.")
        
            except Exception as e:
                logger.error(f"Arxiv search failed: {str(e)}")
        
        # --- CRITICAL FIX: Define 'papers' variable for downstream code ---
        papers = research_data["papers"]
        # -----------------------------------------------------------------
        
        # Step 4: Generate research plan using LLM
        logger.info("Generating research plan...")
        
        plan_prompt = f"""Based on the user goal: "{user_goal}"

Dataset sources found:
{chr(10).join([f"- {s['url']}: {s['snippet']}" for s in dataset_sources[:2]]) if dataset_sources else "No datasets found"}

Research papers:
{papers[0]['summary'][:300] if papers else "No papers found"}

Create a concise 4-step research plan for this ML project. Each step should be ONE sentence."""
        
        plan_response = llm.invoke(plan_prompt)
        research_steps = [
            line.strip() 
            for line in plan_response.content.split('\n') 
            if line.strip() and not line.strip().startswith('#')
        ][:4]
        
        # Step 5: Update state
        logger.info("Updating state with research findings...")
        
        # Update dataset info
        state["dataset_info"]["url"] = dataset_url
        state["dataset_info"]["description"] = f"Dataset for {user_goal}"
        state["dataset_info"]["is_public"] = True
        
        # Update research plan
        state["research_plan"] = research_steps
        
        # Save research_data to state
        state["research_data"] = research_data
        logger.info(f"📊 Captured research data: {len(research_data['queries'])} queries, {len(research_data['papers'])} papers")
        
        # Add message to conversation
        research_summary = f"""✅ Research Complete

**Datasets Found:** {len(dataset_sources)}
{f"- Primary: {dataset_url}" if dataset_url else "- No public datasets found"}

**Research Papers:** {len(papers)} paper(s) reviewed

**Research Plan:**
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(research_steps)])}
"""
        
        state["messages"].append({
            "role": "assistant",
            "content": research_summary
        })
        
        # Set next step
        state["next_step"] = "data_engineering_agent"
        
        logger.info("✅ Research Agent completed successfully")
        
        return state
    
    except Exception as e:
        logger.error(f"❌ Research Agent failed: {str(e)}", exc_info=True)
        
        # Fallback: create a minimal research plan
        state["research_plan"] = [
            f"Find dataset for {user_goal}",
            "Perform exploratory data analysis",
            "Select appropriate ML algorithm",
            "Train and evaluate model"
        ]
        
        state["messages"].append({
            "role": "assistant",
            "content": f"⚠️ Research completed with limited results. Created basic plan for: {user_goal}"
        })
        
        state["next_step"] = "data_engineering_agent"
        
        return state