import json
from typing import Dict, Any, List
from core.llm_provider import LLMProvider
from agents.base import BaseAgent

class CoordinatorAgent:
    """The brain of the platform. Plans tasks and routes them to sub-agents."""
    
    def __init__(self):
        self.llm = LLMProvider()
        self.agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    async def analyze_intent_and_plan(self, user_query: str) -> List[Dict[str, str]]:
        """Uses LLM to determine which agents need to be called and in what order."""
        available_agents = "\n".join([f"- {name}: {agent.description}" for name, agent in self.agents.items()])
        
        system_prompt = f"""
You are the Coordinator for a Scientific Research Agent Platform.
Your job is to analyze the user's query and output a JSON array of tasks.
Each task must have an 'agent' (the name of the agent to route to) and a 'query' (the specific query for that agent).

Available Agents:
{available_agents}

Return ONLY a valid JSON array. For example:
[
  {{"agent": "LiteratureAgent", "query": "TP53 lung cancer"}}
]
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        response_text = await self.llm.chat(messages)
        
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        try:
            plan = json.loads(clean_text)
            return plan
        except json.JSONDecodeError as e:
            print(f"Failed to parse plan: {clean_text}")
            return []

    async def synthesize_final_answer(self, user_query: str, evidence: List[Dict[str, Any]]) -> str:
        """Synthesize the collected evidence into a final cited answer."""
        evidence_text = json.dumps(evidence, indent=2, ensure_ascii=False)
        
        system_prompt = """
You are an expert Bioinformatics Scientist. 
Use the provided Evidence to answer the User's Query. 
Always include citations to the evidence (e.g. PubMed IDs, Titles, or Authors) if applicable.
Do not hallucinate information not present in the evidence.

CRITICAL INSTRUCTION: You MUST explicitly support English and Traditional Chinese. You MUST reply in the exact same language as the User Query. Ensure professional biomedical terminology is correctly translated and aligned.
"""
        
        user_prompt = f"""
User Query: {user_query}

Evidence Collected:
{evidence_text}

Please provide a comprehensive answer.
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self.llm.chat(messages)

    async def execute_workflow(self, user_query: str) -> Dict[str, Any]:
        """Main entry point for handling a user query."""
        print("-> [Coordinator] Analyzing intent and planning tasks...")
        plan = await self.analyze_intent_and_plan(user_query)
        
        evidence = []
        for task in plan:
            agent_name = task.get("agent")
            task_query = task.get("query")
            
            if agent_name in self.agents:
                print(f"-> [Coordinator] Delegating to {agent_name}: '{task_query}'")
                result = await self.agents[agent_name].process_task(task_query)
                evidence.append({"agent": agent_name, "task": task_query, "result": result})
            else:
                print(f"-> [Coordinator] Warning: Agent {agent_name} not found.")
                
        print("-> [Coordinator] Synthesizing final answer based on collected evidence...")
        final_answer = await self.synthesize_final_answer(user_query, evidence)
        
        return {
            "plan": plan,
            "evidence": evidence,
            "evidence_collected": len(evidence),
            "final_answer": final_answer
        }
