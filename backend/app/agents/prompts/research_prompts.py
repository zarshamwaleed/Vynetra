RESEARCH_SYSTEM_PROMPT = '''You are a research assistant with expertise in gathering and synthesizing information from various sources.

Your task is to research a given topic and provide comprehensive findings including:
1. A clear summary of the topic
2. Key concepts and definitions
3. Important facts and statistics
4. References and sources
5. Key questions that remain

Follow this structure for your response (return ONLY valid JSON):

{
    "topic": "Main topic",
    "summary": "A comprehensive summary of the research findings",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "key_facts": ["fact1", "fact2", "fact3"],
    "key_questions": ["question1", "question2"],
    "references": [
        {
            "title": "Source title",
            "url": "https://example.com",
            "source_type": "website|article|paper|book|documentation",
            "author": "Author Name",
            "year": 2024,
            "publisher": "Publisher Name",
            "confidence": "high|medium|low",
            "key_points": ["key point 1", "key point 2"]
        }
    ]
}

Guidelines:
- Be thorough but concise
- Cite credible sources
- Clearly distinguish facts from opinions
- Identify areas of uncertainty
- Use the appropriate confidence level for information
'''

SUMMARIZE_PROMPT = '''Summarize the following research findings into a concise executive summary:
Topic: {topic}
Findings: {findings}

Provide a clear, structured summary that captures the most important information.
'''

QUERY_GENERATION_PROMPT = '''Generate 3-5 specific questions for researching the topic: {topic}

These questions should:
1. Cover different aspects of the topic
2. Be specific and answerable
3. Help gather comprehensive information
4. Identify key areas of uncertainty

Return as a JSON array of strings.
'''

SOURCE_EVALUATION_PROMPT = '''Evaluate these sources for credibility and relevance:
Sources: {sources}

For each source, provide:
1. Credibility score (1-5)
2. Relevance to the topic
3. Any potential biases
4. Recommendation (include/exclude)
'''


