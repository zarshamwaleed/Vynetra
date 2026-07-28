CONTENT_SYSTEM_PROMPT = '''You are an expert content creator for presentations. You transform outlines and research into engaging, well-structured slide content.

Your task is to create comprehensive slide content that includes:
1. Clear, compelling titles
2. Well-organized bullet points
3. Detailed explanations
4. Relevant examples
5. Speaker notes
6. Key takeaways

Follow this structure for your response (return ONLY valid JSON):

{
    "slides": [
        {
            "number": 1,
            "title": "Compelling slide title",
            "subtitle": "Optional subtitle",
            "content": "Main content paragraph",
            "bullet_points": ["Key point 1", "Key point 2", "Key point 3"],
            "explanation": "Detailed explanation of the concept",
            "examples": ["Example 1", "Example 2"],
            "speaker_notes": "What the presenter should say",
            "key_takeaways": ["Takeaway 1", "Takeaway 2"],
            "references": ["Reference 1", "Reference 2"]
        }
    ]
}

Guidelines:
- Each slide should have a clear purpose
- Bullet points should be concise and impactful
- Examples should illustrate key concepts
- Speaker notes should be conversational and engaging
- Content should match the audience level (beginner, intermediate, expert)
'''

SLIDE_TITLE_PROMPT = '''Generate a compelling title for a slide about:
Topic: {topic}
Context: {context}
Audience: {audience}

The title should be:
1. Clear and descriptive
2. Engaging and interesting
3. Appropriate for the audience
4. Under 10 words

Return ONLY the title text.'''

BULLET_POINTS_PROMPT = '''Generate 3-5 bullet points for a slide about:
Topic: {topic}
Content: {content}
Audience: {audience}

Bullet points should be:
1. Concise and scannable
2. Key takeaways
3. Actionable insights
4. Appropriate for the audience

Return as a JSON array of strings.'''

EXPLANATION_PROMPT = '''Generate a detailed explanation for:
Topic: {topic}
Concept: {concept}
Audience: {audience}

The explanation should:
1. Be clear and easy to understand
2. Include key details
3. Use appropriate language for the audience
4. Be 3-5 sentences long

Return ONLY the explanation text.'''

EXAMPLES_PROMPT = '''Generate 2-3 examples for:
Topic: {topic}
Concept: {concept}
Audience: {audience}

Examples should:
1. Be relevant and relatable
2. Illustrate the concept clearly
3. Be appropriate for the audience
4. Include real-world scenarios

Return as a JSON array of strings.'''

SPEAKER_NOTES_PROMPT = '''Generate speaker notes for a slide about:
Topic: {topic}
Title: {title}
Content: {content}
Audience: {audience}

Speaker notes should:
1. Be conversational and natural
2. Include key talking points
3. Provide context and transitions
4. Be 3-5 sentences long

Return ONLY the speaker notes text.'''

CONTENT_QUALITY_PROMPT = '''Evaluate the quality of this slide content:
Title: {title}
Content: {content}
Bullet Points: {bullet_points}
Explanation: {explanation}
Examples: {examples}

Provide a quality score from 0-1 and brief feedback:
1. Clarity (0-1)
2. Relevance (0-1)
3. Engagement (0-1)
4. Completeness (0-1)

Return as JSON with 'score' and 'feedback' fields.
'''
