"""
SkillForge LangChain Adapter (Python version)

For Python-based LangChain applications.
"""

from typing import Any, Dict, List, Optional, Callable
from functools import wraps
import traceback

from skillforge import SkillForge, Failure


class LangChainAdapter:
    """
    Adapter for LangChain Python applications.
    
    Usage:
        from skillforge import SkillForge
        from skillforge.adapters import LangChainAdapter
        
        forge = SkillForge(agent='my-agent')
        adapter = LangChainAdapter(forge)
        
        # Wrap chain
        chain = adapter.wrap_chain(my_chain)
        
        # Wrap agent
        agent = adapter.wrap_agent(my_agent)
    """
    
    def __init__(self, forge: SkillForge):
        self.forge = forge
    
    def wrap_chain(self, chain: Any) -> Any:
        """Wrap a LangChain Chain"""
        # Try different invoke methods based on chain type
        
        if hasattr(chain, 'invoke'):
            # Modern Runnable interface
            original_invoke = chain.invoke
            
            @wraps(original_invoke)
            async def wrapped_invoke(input: Any, config: Optional[Dict] = None):
                try:
                    return await original_invoke(input, config)
                except Exception as error:
                    await self._capture_failure(error, {
                        'input': input,
                        'chain_type': type(chain).__name__,
                        'config': config,
                    })
                    raise
            
            chain.invoke = wrapped_invoke
        
        if hasattr(chain, 'acall'):
            # Legacy async interface
            original_acall = chain.acall
            
            @wraps(original_acall)
            async def wrapped_acall(inputs: Dict[str, Any]):
                try:
                    return await original_acall(inputs)
                except Exception as error:
                    await self._capture_failure(error, {
                        'inputs': inputs,
                        'chain_type': type(chain).__name__,
                    })
                    raise
            
            chain.acall = wrapped_acall
        
        if hasattr(chain, '__call__'):
            # Legacy sync interface
            original_call = chain.__call__
            
            @wraps(original_call)
            def wrapped_call(inputs: Dict[str, Any]):
                try:
                    return original_call(inputs)
                except Exception as error:
                    # Sync version - still capture but don't await
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    loop.run_until_complete(self._capture_failure(error, {
                        'inputs': inputs,
                        'chain_type': type(chain).__name__,
                    }))
                    raise
            
            chain.__call__ = wrapped_call
        
        return chain
    
    def wrap_agent(self, agent: Any) -> Any:
        """Wrap a LangChain Agent"""
        # Wrap agent executor
        if hasattr(agent, 'agent_executor'):
            self.wrap_chain(agent.agent_executor)
        
        # Wrap tools
        if hasattr(agent, 'tools'):
            self.wrap_tools(agent.tools)
        
        return agent
    
    def wrap_tools(self, tools: List[Any]) -> List[Any]:
        """Wrap a list of LangChain tools"""
        for tool in tools:
            if hasattr(tool, '_run'):
                # StructuredTool
                original_run = tool._run
                
                @wraps(original_run)
                def wrapped_run(tool_input: str, original=original_run, tool_name=tool.name):
                    try:
                        return original(tool_input)
                    except Exception as error:
                        import asyncio
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        
                        loop.run_until_complete(self._capture_failure(error, {
                            'tool_name': tool_name,
                            'tool_input': tool_input,
                        }))
                        raise
                
                tool._run = wrapped_run
            
            if hasattr(tool, 'arun'):
                # Async tool
                original_arun = tool.arun
                
                @wraps(original_arun)
                async def wrapped_arun(tool_input: str, original=original_arun, tool_name=tool.name):
                    try:
                        return await original(tool_input)
                    except Exception as error:
                        await self._capture_failure(error, {
                            'tool_name': tool_name,
                            'tool_input': tool_input,
                        })
                        raise
                
                tool.arun = wrapped_arun
        
        return tools
    
    def wrap_llm(self, llm: Any) -> Any:
        """Wrap a LangChain LLM"""
        if hasattr(llm, 'agenerate'):
            original_agenerate = llm.agenerate
            
            @wraps(original_agenerate)
            async def wrapped_agenerate(prompts: List[str], **kwargs):
                try:
                    return await original_agenerate(prompts, **kwargs)
                except Exception as error:
                    await self._capture_failure(error, {
                        'llm_type': type(llm).__name__,
                        'prompt_count': len(prompts),
                        'first_prompt': prompts[0][:100] if prompts else None,
                    })
                    raise
            
            llm.agenerate = wrapped_agenerate
        
        return llm
    
    async def _capture_failure(self, error: Exception, context: Dict[str, Any]) -> Failure:
        """Capture failure with LangChain-specific context"""
        return await self.forge.capture_failure(
            error=error,
            context={
                'task': context.get('input') or context.get('inputs') or 'LangChain execution',
                'context': {
                    'framework': 'langchain',
                    'framework_version': self._get_langchain_version(),
                    'traceback': traceback.format_exc(),
                    **context,
                },
            }
        )
    
    def _get_langchain_version(self) -> str:
        """Get LangChain version"""
        try:
            import langchain
            return langchain.__version__
        except (ImportError, AttributeError):
            return 'unknown'
    
    async def get_suggestions(self, error_type: str) -> List[Dict[str, Any]]:
        """Get skill suggestions for LangChain context"""
        langchain_skill_map = {
            'OutputParserException': ['structured-output-protocol', 'output-fixer'],
            'JSONDecodeError': ['json-sanitizer', 'robust-json-parser'],
            'ToolInputError': ['tool-call-fixer'],
            'TokenLimitError': ['token-optimizer', 'chunking-handler'],
            'RateLimitError': ['rate-limit-handler', 'retry-with-backoff'],
            'ValidationException': ['input-validator', 'schema-enforcer'],
        }
        
        skill_names = langchain_skill_map.get(error_type, [])
        return [{'name': name, 'framework': 'langchain'} for name in skill_names]
    
    def skill_to_tool(self, skill: Any) -> Any:
        """Convert a skill to a LangChain tool"""
        from langchain.tools import BaseTool
        
        class SkillTool(BaseTool):
            name = skill.name
            description = skill.description
            
            def _run(self, tool_input: str) -> str:
                # Execute skill
                # In production, would call skill execution engine
                return f"Applied skill {skill.name}"
            
            async def _arun(self, tool_input: str) -> str:
                return self._run(tool_input)
        
        return SkillTool()


def detect_langchain(obj: Any) -> bool:
    """Detect if object is a LangChain component"""
    return (
        hasattr(obj, 'lc_namespace') or
        hasattr(obj, 'lc_id') or
        type(obj).__module__.startswith('langchain') or
        'Chain' in type(obj).__name__ or
        'Agent' in type(obj).__name__
    )
