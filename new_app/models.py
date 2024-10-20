from django.db import models

class Rule(models.Model):
    rule_id = models.AutoField(primary_key=True)
    rule_name = models.CharField(max_length=255, blank=True, null=True)  # Name of the rule
    rule_string = models.TextField()  # Original rule string
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Update timestamp
    combined_type = models.CharField(max_length=50,blank=True, null=True)

class ASTNode(models.Model):
    node_id = models.AutoField(primary_key=True)
    rule = models.ForeignKey(Rule, related_name='ast_nodes', on_delete=models.CASCADE)  # Link to the rule
    node_type = models.CharField(max_length=50)  # "operator" or "operand"
    operator = models.CharField(max_length=10, blank=True, null=True)  # Operator value
    field_name = models.CharField(max_length=50, blank=True, null=True)  # Field being compared
    value = models.CharField(max_length=255, blank=True, null=True)  # Value to compare against
    parent_node = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True, blank=True)  # Parent node
    left_child = models.ForeignKey('self', related_name='left', on_delete=models.CASCADE, null=True, blank=True)  # Left child
    right_child = models.ForeignKey('self', related_name='right', on_delete=models.CASCADE, null=True, blank=True)  # Right child


class combinedRule(models.Model):
    combined_rule_id = models.AutoField(primary_key=True)
    rule = models.ForeignKey(Rule,related_name='combined_rules',on_delete=models.CASCADE)
    rule_string = models.TextField()