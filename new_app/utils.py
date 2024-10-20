import re

class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type  # "operator" or "operand"
        self.left = left  # Left child Node
        self.right = right  # Right child Node
        self.value = value  # Value for operand nodes (e.g., number)

    def to_dict(self):
        # Convert the Node to a dictionary for JSON serialization
        node_dict = {
            'type': self.type,
            'value': self.value,
        }
        if self.left:
            node_dict['left'] = self.left.to_dict()
        if self.right:
            node_dict['right'] = self.right.to_dict()
        return node_dict


def create_rule(rule_string):
    part = separate_conditions(rule_string)
    if len(part) > 1:
        # Create nodes for left and right conditions
        left = create_rule(part[0])
        right = create_rule(part[2])
        return Node("operator", left=left, right=right, value=part[1])
    else:
        # Create leaf node for a single condition
        return Node("operand", value=part[0].strip())

def saperate_con(condition):
    return re.findall(r'[a-zA-Z_]\w*|[<>=]=?|!=|\d+', condition)

def separate_conditions(condition):
    # Define the logical operators
    logical_operators = ['AND', 'OR']
    
    # Split the condition into parts based on the operators
    parts = []
    current_part = ''
    in_parentheses = 0
    
    for char in condition:
        if char == '(':
            in_parentheses += 1
        elif char == ')':
            in_parentheses -= 1

        current_part += char

        # Check if we reached the end of a part (considering parentheses)
        if in_parentheses == 0 and any(op in current_part for op in logical_operators):
            if any(current_part.strip().endswith(op) for op in logical_operators):
                parts.extend(current_part.strip().rsplit(' ',1))
            else:    
                parts.append(current_part.strip())
            current_part = ''
            
    # Add the last part if there's any remaining
    if current_part:
        parts.append(current_part.strip())

    if len(parts) == 1 and parts[0] == condition and any(ops in condition for ops in logical_operators):
        return separate_conditions(condition[1:-1])
    return parts

def convert_into_single_rule(rules,oprator):
    if not rules:
        return ""

    # Start with the first rule
    convert_into_single_rule = rules[0]

    # Iterate through the remaining rules and combine them
    for rule in rules[1:]:
        convert_into_single_rule = f"({convert_into_single_rule}) {oprator} ({rule})"

    return convert_into_single_rule

def build_ast(node):
    ast = {
        "type": node.node_type,  # This will be "operator" or "operand"
        "value": node.value if node.node_type == "operand" else node.operator
    }
    if node.node_type == "operand":
        if isinstance(node.value, str) and not node.value.isnumeric():
            # If it's a string, wrap it with quotes
            ast["value"] = f"{node.field_name} {node.operator} '{node.value}'"  # Example: "age < '25'"
        else:
            # If it's a number, do not wrap it
            ast["value"] = f"{node.field_name} {node.operator} {node.value}"  # Example: "age < 25"

    if node.left_child:
        ast["left"] = build_ast(node.left_child)
    if node.right_child:
        ast["right"] = build_ast(node.right_child)

    return ast

def compare_asts(ast1, ast2):
    if ast1.get("type") != ast2.get("type"):
        return False
    if ast1.get("type") == "operand":
        # Compare both field name and value for operands
        if ast1.get("value") != ast2.get("value"):
            return False
    else:
        # For operators, just compare the operator value
        if ast1.get("value") != ast2.get("value"):
            return False
    
    left1, left2 = ast1.get("left"), ast2.get("left")
    right1, right2 = ast1.get("right"), ast2.get("right")

    return (compare_asts(left1, left2) if left1 and left2 else left1 == left2) and \
           (compare_asts(right1, right2) if right1 and right2 else right1 == right2)

def check_ast_match(rules,provided_ast):
    for rule in rules:
        ast_nodes = rule.ast_nodes.all()
        root_nodes = ast_nodes.filter(parent_node=None)  # Get root nodes
        constructed_asts = [build_ast(node) for node in root_nodes]

        # Check each constructed AST
        for ast in constructed_asts:
            if compare_asts(ast, provided_ast):
                return True  # Match found

    return False  # No matches found