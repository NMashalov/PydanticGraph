from .scan import Operator
from pydantic import BaseModel
import typing as tp
from types import ModuleType
import inspect

class OperatorMart:
    def __init__(self):
        self.operators: dict[str,Operator] = {}
        

    def register(self,inputs: list[tuple] = [], outputs: list[tuple] = [], module_name: str = ''):
        """
        Register any object
        INPUTS and OUTPUTS defined explicitly in decorator params
        Widgets yield from function signature
        """

        def decorator(func_to_node: tp.Callable):
            node = Operator.from_callable(func=func_to_node, inputs=inputs, outputs=outputs)

            self.operators[node.id] = node
            return func_to_node

        return decorator
    
    def load_nodes_from_module(self,module: ModuleType, module_name: str):

        def _check_defined_pydantic(x):
            return (
                inspect.isclass(x)
                and issubclass(x, BaseModel)
                and x.__module__ == module_name
            )

        new_nodes = []
        for cls in inspect.getmembers(module, _check_defined_pydantic):
            new_node = Operator(*cls)
            new_nodes.append(new_node)
            self.operators[new_node.hash] = cls[1]
        return {"nodes": new_nodes, "module_name": module_name}

    def validate_graph(self, g):
        if g.nodes:
            for node in g.nodes:
                props = node.properties
                hash_key = props.pop("hash")
                if props:
                    _NODE_MODELS[hash_key](**props)  # type: ignore

    def from_configs():
        pass


    def from_text(self,text: str, name: str):
        # creates new module
        module = ModuleType(name)
        # populate the module with code
        exec(contents, module.__dict__)
        return self.load_nodes_from_module(module, name)