from fastmcp import FastMCP
import random 
import json
import logging
logging.basicConfig(level=logging.DEBUG)


# create the FastMCP server instance

mcp = FastMCP("simple calculator server")

# tool: add two numbers
@mcp.tool
def add(a:int, b:int)->int:
    '''Add two numbers together
    
    Args:
        a: First number
        b: Second number

    returns:
            The sum of a and b
    
    '''

    
    return a+b

# Tool: Generate a random number
@mcp.tool
def random_number(min_val: int=1, max_val: int = 100)->int:
    '''
    Generate a random number within a range

    Ags:
        min_val: Minimum value(default: 1)
        max_val: Maximum value(default: 100)

    Returns:
        A random integer between min_value and max_value
    '''

    return random.randint(min_val, max_val)

# Resource: Server information
@mcp.resource("info://server")
def server_info()->str:
    '''Get information about this server'''
    info={
        "name": "simple calculator server",
        "version":"1.0.0",
        "description":"A basic mcp server with math tools",
        "tools":["add", "random_number"],
        "author":"Chandra Pal Keshari"
    }
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)
