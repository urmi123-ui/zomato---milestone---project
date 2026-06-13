# Project Context: AI-Powered Restaurant Recommendation System

## Overview

Build an AI-powered restaurant recommendation service inspired by **Zomato**. The system combines structured restaurant data with a **Large Language Model (LLM)** to deliver personalized, human-like restaurant suggestions based on user preferences.

---

## Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and more)
2. Uses a real-world restaurant dataset
3. Leverages an LLM to generate personalized, human-like recommendations
4. Displays clear and useful results to the user

---

## Data Source

| Field | Value |
|-------|-------|
| **Dataset** | Zomato Restaurant Recommendation |
| **Provider** | Hugging Face |
| **URL** | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |

### Relevant Fields to Extract

- Restaurant name
- Location
- Cuisine
- Cost
- Rating
- Other applicable metadata from the dataset

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- Extract relevant fields (name, location, cuisine, cost, rating, etc.)
- Prepare data for filtering and LLM consumption

### 2. User Input

Collect the following preferences from the user:

| Preference | Examples |
|------------|----------|
| **Location** | Delhi, Bangalore |
| **Budget** | Low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | Numeric threshold |
| **Additional preferences** | Family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter restaurant data based on user input
- Prepare structured results for the LLM
- Design a prompt that enables the LLM to reason over and rank options

### 4. Recommendation Engine

Use the LLM to:

- **Rank** restaurants by relevance to user preferences
- **Explain** why each recommendation fits the user
- **Optionally summarize** the overall set of choices

### 5. Output Display

Present top recommendations in a user-friendly format:

| Field | Description |
|-------|-------------|
| Restaurant Name | Name of the recommended restaurant |
| Cuisine | Type of cuisine offered |
| Rating | Restaurant rating |
| Estimated Cost | Cost estimate for the user |
| AI-generated explanation | Why this restaurant was recommended |

---

## Architecture Summary

```
User Preferences
       ↓
  Data Filtering (structured dataset)
       ↓
  LLM Prompt (filtered results + user context)
       ↓
  Recommendation Engine (rank, explain, summarize)
       ↓
  User-facing Output
```

---

## Key Technical Components

1. **Dataset pipeline** — Load, clean, and index Zomato data from Hugging Face
2. **Preference collection** — UI or CLI for capturing user inputs
3. **Filter layer** — Narrow candidates by location, budget, cuisine, rating, and extras
4. **LLM integration** — Prompt design, API calls, response parsing
5. **Presentation layer** — Render ranked recommendations with explanations

---

## Success Criteria

- Recommendations reflect user-stated preferences (location, budget, cuisine, rating)
- LLM provides meaningful, personalized explanations—not generic boilerplate
- Output is readable and actionable for end users
- System uses the specified Hugging Face Zomato dataset as its data foundation
