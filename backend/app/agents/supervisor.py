import json
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.agents.state import AgentState

class SupervisorAgent(BaseAgent):
    '''Supervisor agent that orchestrates the workflow'''
    
    def __init__(self, llm_service):
        super().__init__("Supervisor", llm_service)
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Analyzing prompt and planning workflow...")
        
        try:
            system_prompt = """You are a presentation supervisor. Analyze the user's request and determine:
            1. The main topic
            2. How many slides are needed (8-15)
            3. The target audience (general, expert, beginner, executive)
            4. The tone of the presentation (professional, casual, educational, persuasive)
            
            Return ONLY valid JSON with this structure:
            {
                "topic": "Main topic",
                "slide_count": 10,
                "audience": "general",
                "tone": "professional"
            }"""
            
            response = await self.llm.generate(
                prompt=f"Analyze this request and plan the presentation: {state.prompt}",
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # Parse the response
            plan = self._parse_json(response.text)
            
            state.topic = plan.get("topic", state.prompt[:50])
            state.slide_count = plan.get("slide_count", 10)
            state.progress = 10
            
            await self._log_step(state, f"Topic: {state.topic}, Slides: {state.slide_count}")
            
        except Exception as e:
            await self._add_error(state, f"Supervisor error: {str(e)}")
        
        return state
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        '''Parse JSON from LLM response'''
        try:
            import re
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"topic": "Presentation", "slide_count": 10, "audience": "general", "tone": "professional"}
        except:
            return {"topic": "Presentation", "slide_count": 10, "audience": "general", "tone": "professional"}
