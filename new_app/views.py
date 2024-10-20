from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import Rule,ASTNode,combinedRule
from .utils import create_rule,saperate_con,convert_into_single_rule,check_ast_match
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


@require_POST
@csrf_exempt
def createRuleView(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed."}, status=405)
    
    # Handle the POST request
    try:
        body = json.loads(request.body)
        rule_string = body.get('rule_string')
        
        if not rule_string:
            return JsonResponse({"error": "No rule_string provided."}, status=400)

        # Create AST
        ast = create_rule(rule_string)
        ast_dict = ast.to_dict()

        # Fetch the last rule's primary key
        count_of_rules = Rule.objects.filter(Q(rule_string__isnull=False) & Q(rule_string__gt='')).count()
        new_rule_name = f"rule_{int(count_of_rules) + 1}"
        # Save rule to the database
        rule = Rule.objects.create(
            rule_name=new_rule_name,
            rule_string=rule_string
        )
        save_ast(ast_dict,rule)
        return JsonResponse({"ast": ast_dict, "id": rule.rule_id}, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({"error ": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def save_ast(node_data, rule, parent=None):
    # Create a new ASTNode instance
    node_type = node_data['type']
    operator = node_data['value'] if node_type == 'operator' else None
    field_name = None
    value = None

    if node_type == 'operand':
        # Assuming the operand value is of the form "field operator value"
        field_name,operator, value = parse_operand_value(node_data['value'])

    ast_node = ASTNode.objects.create(
        rule=rule,
        node_type=node_type,
        operator=operator,
        field_name=field_name,
        value=value,
        parent_node=parent
    )

    # Recursively save left and right children if they exist
    if 'left' in node_data:
        left_child = save_ast(node_data['left'], rule, ast_node)
        ast_node.left_child = left_child  # Update left_child reference
    if 'right' in node_data:
        right_child = save_ast(node_data['right'], rule, ast_node)
        ast_node.right_child = right_child  # Update right_child reference
    ast_node.save()
    return ast_node
    
def parse_operand_value(value):
    # Logic to parse the operand string into field and value
    # For example, "age > 30" into ("age", "30") or similar parsing
    # This is a simple implementation and might need refinement based on your input format
    parts = saperate_con(value)
    if len(parts) == 3:
        return parts[0], parts[1],parts[2]  # Return field name and value
    return None, None  # Handle cases where parsing fails

@require_POST
@csrf_exempt
def CombineRulesView(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed."}, status=405)
    
    # Handle the POST request
    try:
        body = json.loads(request.body)
        combined_rules = body.get('combined_rules')
        oprator = body.get('oprator')

        if not combined_rules or not oprator:
            return JsonResponse({"error": "No combined_rules or oprator provided."}, status=400)

        rule_string = convert_into_single_rule(combined_rules,oprator)
        
        # Create AST
        ast = create_rule(rule_string)
        ast_dict = ast.to_dict()

        count_of_rules = Rule.objects.filter(Q(rule_string__isnull=True) | Q(rule_string='')).count()
        new_rule_name = f"combine_rule_{int(count_of_rules) + 1}"
        # Save rule to the database
        rule = Rule.objects.create(
            rule_name=new_rule_name,
            combined_type=oprator
        )
        for rule_str in combined_rules:
            combinedRule.objects.create(
                rule=rule,
                rule_string = rule_str
            )
        save_ast(ast_dict,rule)
        return JsonResponse({"ast": ast_dict, "id": rule.rule_id}, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_POST
@csrf_exempt
def evaluate_rule(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed."}, status=405)
    
    # Handle the POST request
    try:
        body = json.loads(request.body)
        ast = body.get('ast')

        if not ast:
            return JsonResponse({"error": "No rule_string or oprator provided."}, status=400)
        
        rules = Rule.objects.all()
        result = check_ast_match(rules,ast)

        return JsonResponse({'result': result},status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def fetch_rules(request):
    if request.method == 'GET':
        try:
            rules = Rule.objects.all().values('rule_id', 'rule_name','rule_string','combined_type')  # Adjust fields as needed
            rules_list = list(rules)
            for r in rules_list:
                if not r['rule_string']:
                    combined_rules=combinedRule.objects.all().values('rule_string')
                    combined_rules_list = list(combined_rules)
                    r['rule_string']=convert_into_single_rule(combined_rules_list,r['combined_type'])

            return JsonResponse(rules_list, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed."}, status=405)

def dashboard_view(request):
    return render(request, 'index.html') 