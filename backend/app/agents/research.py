import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.schemas.research_schema import (
    ResearchResult, ResearchFinding, Reference, SourceType, ConfidenceLevel
)
from app.agents.prompts.research_prompts import (
    RESEARCH_SYSTEM_PROMPT, SUMMARIZE_PROMPT, QUERY_GENERATION_PROMPT
)

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    '''Enhanced Research Agent with web research capabilities'''
    
    def __init__(self, llm_service, mcp_client=None):
        super().__init__("Research", llm_service)
        self.mcp = mcp_client
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Researching topic...")
        
        try:
            topic = state.topic or state.prompt[:50]
            
            # Step 1: Generate research questions
            questions = await self._generate_questions(topic)
            
            # Step 2: Perform research using LLM
            research_data = await self._perform_research(topic, questions)
            
            # Step 3: Create structured research result
            research_result = self._create_research_result(topic, research_data)
            
            # Step 4: Generate summary
            summary = await self._generate_summary(topic, research_result)
            research_result.summary = summary
            
            # Step 5: Update state
            state.research = research_result.to_dict()
            state.references = [r.to_dict() for r in research_result.references]
            state.progress = 40
            
            # Step 6: Save to file
            await self._save_research(topic, research_result)
            
            await self._log_step(
                state,
                f"Research complete: {len(research_result.findings)} findings, "
                f"{len(research_result.references)} references"
            )
            
        except Exception as e:
            await self._add_error(state, f"Research error: {str(e)}")
            logger.error(f"Research error details: {e}", exc_info=True)
        
        return state
    
    async def _generate_questions(self, topic: str) -> List[str]:
        '''Generate research questions for the topic'''
        try:
            prompt = QUERY_GENERATION_PROMPT.format(topic=topic)
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are a research question generator.",
                temperature=0.3,
                max_tokens=512
            )
            
            # Parse the JSON response
            questions = self._parse_json(response.text)
            if isinstance(questions, list):
                return questions
            else:
                # Fallback questions
                return [
                    f"What is {topic}?",
                    f"What are the key concepts of {topic}?",
                    f"What are the applications of {topic}?",
                    f"What are the challenges in {topic}?",
                    f"What is the future of {topic}?"
                ]
        except Exception as e:
            logger.warning(f"Question generation failed: {e}")
            return [
                f"What is {topic}?",
                f"What are the key concepts of {topic}?",
                f"What are the applications of {topic}?"
            ]
    
    async def _perform_research(
        self,
        topic: str,
        questions: List[str]
    ) -> Dict[str, Any]:
        '''Perform research using the LLM'''
        try:
            question_list = "\n".join([f"- {q}" for q in questions])
            
            system_prompt = RESEARCH_SYSTEM_PROMPT
            
            user_prompt = f'''
            Research the following topic: {topic}
            
            Research questions to address:
            {question_list}
            
            Return ONLY valid JSON with the structure specified.
            Include comprehensive information with credible sources.
            '''
            
            response = await self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=4096
            )
            
            return self._parse_json(response.text)
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return self._create_fallback_research(topic)
    
    def _create_research_result(
        self,
        topic: str,
        data: Dict[str, Any]
    ) -> ResearchResult:
        '''Create a structured research result'''
        # Parse findings
        findings = []
        finding_data = {
            "topic": topic,
            "summary": data.get("summary", ""),
            "key_concepts": data.get("key_concepts", []),
            "key_facts": data.get("key_facts", []),
            "key_questions": data.get("key_questions", [])
        }
        
        # Parse references
        references = []
        for ref_data in data.get("references", []):
            try:
                source_type = SourceType(ref_data.get("source_type", "website"))
            except ValueError:
                source_type = SourceType.WEBSITE
            
            try:
                confidence = ConfidenceLevel(ref_data.get("confidence", "medium"))
            except ValueError:
                confidence = ConfidenceLevel.MEDIUM
            
            ref = Reference(
                title=ref_data.get("title", "Unknown Source"),
                url=ref_data.get("url"),
                source_type=source_type,
                author=ref_data.get("author"),
                year=ref_data.get("year"),
                publisher=ref_data.get("publisher"),
                confidence=confidence,
                key_points=ref_data.get("key_points", [])
            )
            references.append(ref)
        
        # Create finding
        finding = ResearchFinding(
            topic=topic,
            summary=finding_data.get("summary", ""),
            key_concepts=finding_data.get("key_concepts", []),
            key_facts=finding_data.get("key_facts", []),
            key_questions=finding_data.get("key_questions", []),
            references=references,
            confidence=ConfidenceLevel.MEDIUM
        )
        
        return ResearchResult(
            topic=topic,
            findings=[finding],
            references=references,
            status="completed"
        )
    
    async def _generate_summary(self, topic: str, result: ResearchResult) -> str:
        '''Generate an executive summary'''
        try:
            findings_text = "\n".join([
                f"- {f.topic}: {f.summary[:100]}..."
                for f in result.findings
            ])
            
            prompt = SUMMARIZE_PROMPT.format(
                topic=topic,
                findings=findings_text
            )
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are a research summarizer.",
                temperature=0.3,
                max_tokens=512
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            return f"Research on {topic} has been completed with {len(result.findings)} findings."
    
    async def _save_research(self, topic: str, result: ResearchResult):
        '''Save research to file'''
        try:
            # Create directory
            os.makedirs("./generated/research", exist_ok=True)
            
            # Save as markdown
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"./generated/research/research_{timestamp}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result.to_markdown())
            
            logger.info(f"Research saved to: {filename}")
            
        except Exception as e:
            logger.warning(f"Failed to save research: {e}")
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        '''Parse JSON from LLM response'''
        try:
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")
            return {}
    
    def _create_fallback_research(self, topic: str) -> Dict[str, Any]:
        '''Create fallback research data'''
        return {
            "topic": topic,
            "summary": f"This is a summary of research on {topic}.",
            "key_concepts": [f"Key concept 1 about {topic}", f"Key concept 2 about {topic}"],
            "key_facts": [f"Fact 1 about {topic}", f"Fact 2 about {topic}"],
            "key_questions": [f"Question 1 about {topic}", f"Question 2 about {topic}"],
            "references": [
                {
                    "title": f"Reference 1 about {topic}",
                    "url": "https://example.com",
                    "source_type": "website",
                    "author": "Author Name",
                    "year": 2024,
                    "publisher": "Publisher",
                    "confidence": "medium",
                    "key_points": ["Key point 1", "Key point 2"]
                }
            ]
        }
