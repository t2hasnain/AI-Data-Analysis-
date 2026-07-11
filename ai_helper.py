"""
ai_helper.py — Multi-Agent AI Module (Azure OpenAI)
=====================================================
Implements a multi-agent architecture with three specialized agents:
  1. Data Analyst Agent   — answers dataset questions
  2. Chart Explainer Agent — explains generated charts
  3. Insight Generator Agent — proactively finds key insights

Uses the OpenAI Python SDK pointed at the user's Azure AI endpoint
(project-scoped, OpenAI-compatible).
"""

import os
import json
from openai import OpenAI
import streamlit as st
import time
import hashlib
import re

# ---------------------------------------------------------------------------
# Security — Rate Limiting, Input Sanitization & Deduplication
# ---------------------------------------------------------------------------

MAX_REQUESTS_PER_MINUTE = 15

def _sanitize_input(text: str) -> str:
    """Sanitize user input before sending to AI — strip HTML, limit length, block injection."""
    if not isinstance(text, str):
        return ""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove potential prompt injection markers
    text = re.sub(r'(ignore previous|system:|assistant:|you are now)', '', text, flags=re.IGNORECASE)
    # Limit length to 500 characters
    text = text.strip()[:500]
    return text


def _check_rate_limit() -> bool:
    """Returns True if the request is within rate limits, False if throttled."""
    now = time.time()
    if "_api_call_times" not in st.session_state:
        st.session_state._api_call_times = []
    # Purge entries older than 60 seconds
    st.session_state._api_call_times = [
        t for t in st.session_state._api_call_times if now - t < 60
    ]
    if len(st.session_state._api_call_times) >= MAX_REQUESTS_PER_MINUTE:
        return False
    st.session_state._api_call_times.append(now)
    return True


def _dedup_key(*args) -> str:
    """Create a hash key for deduplication of identical requests."""
    raw = "|".join(str(a) for a in args)
    return hashlib.md5(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Client & Routing Logic
# ---------------------------------------------------------------------------

def _get_azure_client():
    api_key = os.environ.get("AZURE_API_KEY", "")
    endpoint = os.environ.get("AZURE_ENDPOINT", "")
    model = os.environ.get("AZURE_OPENAI_MODEL", "gpt-4o-mini")

    base_url = endpoint.rstrip("/")
    if base_url.endswith("/responses"):
        base_url = base_url[: -len("/responses")]
    if not base_url.endswith("/v1"):
        if "/v1" not in base_url:
            base_url = base_url.rstrip("/") + "/v1"

    client = OpenAI(api_key=api_key, base_url=base_url)
    return client, model


def extract_text(content):
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)

def call_llm(selected_model, system_prompt, user_prompt, temperature=0.7, max_tokens=300):
    """
    Routes the request to the appropriate AI provider based on the selected_model dropdown.
    Includes rate limiting and deduplication.
    """
    # Rate limit check
    if not _check_rate_limit():
        return "⚠️ Rate limit reached (max 15 requests/minute). Please wait a moment and try again."

    # Deduplication — check session_state cache
    cache_key = _dedup_key(selected_model, system_prompt[:100], user_prompt)
    if "_llm_cache" not in st.session_state:
        st.session_state._llm_cache = {}
    if cache_key in st.session_state._llm_cache:
        return st.session_state._llm_cache[cache_key]

    if "Grok" in selected_model:
        client = OpenAI(
            api_key=os.environ.get("GROK_API_KEY", ""),
            base_url="https://api.x.ai/v1"
        )
        try:
            response = client.chat.completions.create(
                model="grok-2-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            result = response.choices[0].message.content
            st.session_state._llm_cache[cache_key] = result
            return result
        except Exception as e:
            return f"⚠️ Grok API Error: {str(e)}"

    elif selected_model.startswith("Groq"):
        client = OpenAI(
            api_key=os.environ.get("GROQ_API_KEY", ""),
            base_url="https://api.groq.com/openai/v1"
        )
        
        if "Llama" in selected_model and "70B" in selected_model:
            model_name = "llama-3.3-70b-versatile"
        elif "Llama" in selected_model and "8B" in selected_model:
            model_name = "llama-3.1-8b-instant"
        else:
            model_name = "llama-3.1-8b-instant"
            
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=["\nQ:", "\nQuestion:", "\nUser:", "\n\nQ:"]
            )
            result = response.choices[0].message.content
            st.session_state._llm_cache[cache_key] = result
            return result
        except Exception as groq_err:
            print(f"Groq API Error: {groq_err}. Falling back to Azure OpenAI...")
            try:
                az_client, az_model = _get_azure_client()
                az_response = az_client.chat.completions.create(
                    model=az_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                result = az_response.choices[0].message.content
                st.session_state._llm_cache[cache_key] = result
                return result
            except Exception as az_err:
                return f"⚠️ API Error (Groq failed, and Azure fallback also failed): {str(az_err)}"

    elif selected_model.startswith("Gemini"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage
        
        if "High" in selected_model:
            model_name = "gemini-3.1-pro-preview"
            fallback = "gemini-1.5-pro-latest"
        elif "Medium" in selected_model:
            model_name = "gemini-3.5-flash"
            fallback = "gemini-1.5-flash-latest"
        else:
            model_name = "gemini-3.1-flash-lite"
            fallback = "gemini-1.5-flash-8b"
            
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
        try:
            llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=temperature, max_tokens=max_tokens)
            res = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            result = extract_text(res.content)
            st.session_state._llm_cache[cache_key] = result
            return result
        except Exception as e:
            # Fallback if the experimental 3.x models aren't active in their region/tier yet
            print(f"Failed calling {model_name}, falling back to {fallback}. Error: {e}")
            llm = ChatGoogleGenerativeAI(model=fallback, google_api_key=api_key, temperature=temperature, max_tokens=max_tokens)
            res = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            result = extract_text(res.content)
            st.session_state._llm_cache[cache_key] = result
            return result

    else:
        # Default Azure
        client, model = _get_azure_client()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        result = response.choices[0].message.content
        st.session_state._llm_cache[cache_key] = result
        return result


# ---------------------------------------------------------------------------
# Agent 1 — Data Analyst
# ---------------------------------------------------------------------------

DATA_ANALYST_SYSTEM_PROMPT = """\
You are DataBot, an expert AI Data Analyst.
Analyze the dataset context provided and answer the user's question accurately.
If the context does not contain enough information to answer definitively, explain what is missing based on the provided summary.
Be concise and professional. Do not write excessively long explanations.
IMPORTANT: Provide your answer exactly ONCE. Do NOT repeat the user's question, and do NOT repeat your own answer.
"""

@st.cache_data(show_spinner=False, ttl=3600)
def answer_data_question(schema, summary, user_question,
                         column_hints=None, selected_model="Azure ChatGPT-4o-mini", sample_data=None, corr_matrix=None):
    try:
        context = (
            f"Dataset Schema:\n{json.dumps(schema, indent=2)}\n\n"
            f"Statistical Summary:\n{json.dumps(summary, indent=2)}"
        )
        if corr_matrix is not None and not corr_matrix.empty:
            context += f"\n\nCorrelation Matrix (Relationships between numbers):\n{corr_matrix.to_json(orient='index')}"
        if column_hints:
            context += f"\n\nColumn Hints:\n{json.dumps(column_hints, indent=2)}"
        if sample_data:
            context += f"\n\nSample Data (Top Rows):\n{sample_data}"

        clean_question = _sanitize_input(user_question)
        if not clean_question:
            return "⚠️ Please enter a valid question."
        return call_llm(selected_model, DATA_ANALYST_SYSTEM_PROMPT, f"Context:\n{context}\n\nQuestion: {clean_question}", temperature=0.2)
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# ---------------------------------------------------------------------------
# Agent 2 — Chart Explainer
# ---------------------------------------------------------------------------

CHART_EXPLAINER_SYSTEM_PROMPT = """\
You are ChartBot, an expert data visualization explainer.
Given the metadata of a chart (columns used, type of chart, aggregations), explain
to a non-technical user what this chart tells them and why it might be useful.
Keep it under 3 sentences.
"""

@st.cache_data(show_spinner=False, ttl=3600)
def explain_chart(chart_metadata, selected_model="Azure ChatGPT-4o-mini"):
    """
    Explains the significance of a generated chart based on its metadata.
    """
    try:
        user_prompt = f"Chart Metadata:\n{json.dumps(chart_metadata, indent=2)}"
        return call_llm(selected_model, CHART_EXPLAINER_SYSTEM_PROMPT, user_prompt, temperature=0.7)
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# ---------------------------------------------------------------------------
# Agent 3 — Insight Generator
# ---------------------------------------------------------------------------

INSIGHT_SYSTEM_PROMPT = """\
You are InsightBot, an AI agent that proactively discovers insights.
Given a dataset schema and summary, identify the top 3 most interesting
findings a business analyst would care about.

Format each insight as:
🔍 **Insight N:** <one sentence>

Be specific — cite column names and numbers. Keep the total response
under 150 words.
"""

@st.cache_data(show_spinner=False, ttl=3600)
def generate_insights(schema, summary, column_hints=None, selected_model="Azure ChatGPT-4o-mini"):
    """
    Proactively generates 3-4 bullet points of high-value insights.
    """
    try:
        context = (
            f"Dataset Schema:\n{json.dumps(schema, indent=2)}\n\n"
            f"Statistical Summary:\n{json.dumps(summary, indent=2)}"
        )
        if column_hints:
            context += f"\n\nColumn Hints:\n{json.dumps(column_hints, indent=2)}"

        return call_llm(selected_model, INSIGHT_SYSTEM_PROMPT, context, temperature=0.5, max_tokens=400)
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# ---------------------------------------------------------------------------
# Agent 4 — Question Generator
# ---------------------------------------------------------------------------

QUESTIONS_SYSTEM_PROMPT = """\
You are an AI assistant that generates exactly 3 insightful questions about a dataset.
Given the schema and summary, write 3 questions that a business user would want to ask.
Return the result strictly as a JSON array of strings, e.g.:
["What is the average sales?", "Which category is most frequent?", "What is the correlation between X and Y?"]
Do not return any other text.
"""

@st.cache_data(show_spinner=False, ttl=3600)
def generate_suggested_questions(schema, summary, selected_model="Azure ChatGPT-4o-mini", sample_data=None):
    """
    Generates 3 contextual questions based on the dataset schema and summary.
    Always uses Azure ChatGPT to ensure stable JSON output.
    """
    selected_model = "Azure ChatGPT-4o-mini"
    
    try:
        context = (
            f"Dataset Schema:\n{json.dumps(schema, indent=2)}\n\n"
            f"Statistical Summary:\n{json.dumps(summary, indent=2)}"
        )
        if sample_data:
            context += f"\n\nSample Data:\n{sample_data}"

        content = call_llm(selected_model, QUESTIONS_SYSTEM_PROMPT, context, temperature=0.7, max_tokens=200).strip()
        
        # Clean up in case the AI wraps it in markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        questions = json.loads(content.strip())
        if isinstance(questions, list) and len(questions) >= 3:
            return questions[:3]
        return ["What is the total number of records?", "What is the most frequent category?", "Are there any missing values?"]
    except Exception as e:
        print("Error generating questions:", e)
        return ["What is the total number of records?", "What is the most frequent category?", "Are there any missing values?"]
