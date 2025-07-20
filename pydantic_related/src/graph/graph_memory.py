from __future__ import annotations as _annotations
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

from pydantic_graph.persistence.file import FileStatePersistence


from dataclasses import dataclass
from pydantic_graph import Graph, BaseNode, End, GraphRunContext


@dataclass
class CountDownState:
    counter: int


@dataclass
class CountDown(BaseNode[CountDownState, None, int]):
    async def run(self, ctx: GraphRunContext[CountDownState]) -> CountDown | End[int]:
        if ctx.state.counter <= 0:
            return End(ctx.state.counter)
        ctx.state.counter -= 1
        return CountDown()


count_down_graph = Graph(nodes=[CountDown])


async def run_node(run_id: str) -> bool:  
    persistence = FileStatePersistence(Path(f'count_down_{run_id}.json'))
    async with count_down_graph.iter_from_persistence(persistence) as run:  
        node_or_end = await run.next()  

    print('Node:', node_or_end)
    #> Node: CountDown()
    #> Node: CountDown()
    #> Node: CountDown()
    #> Node: CountDown()
    #> Node: CountDown()
    #> Node: End(data=0)
    return isinstance(node_or_end, End)


async def main():
    run_id = 'run_abc123'
    persistence = FileStatePersistence(Path(f'count_down_{run_id}.json'))  
    state = CountDownState(counter=5)
    await count_down_graph.initialize(  
        CountDown(), state=state, persistence=persistence
    )

    count_down_graph.mermaid_save('count_down_graph.mmd') # 머메이드로 저장
    done = False
    while not done:
        done = await run_node(run_id)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    
    