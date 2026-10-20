"""Verify reported final checks against actual reviewer command events."""
import json, shlex

def verify_review_checks(review,log,require_success=True):
 """Every claimed final acceptance check must match an actual successful command."""
 observed=[]
 for line in log.read_text().splitlines():
  try:event=json.loads(line)
  except json.JSONDecodeError:continue
  item=event.get('item',{})
  if event.get('type')!='item.completed' or item.get('type')!='command_execution':continue
  command=item.get('command','');variants={command.strip()}
  try:
   args=shlex.split(command)
   if len(args)>=3 and args[1] in ('-lc','-c'):variants.add(args[2].strip())
  except ValueError:pass
  observed.append((variants,item.get('exit_code')))
 checks=review.get('checks',[])
 if not checks:raise ValueError('No final acceptance checks')
 for check in checks:
  claim=check.get('command','').strip()
  if (require_success and check.get('exit_code')!=0) or not any(claim in commands and code==check.get('exit_code') for commands,code in observed):
   raise ValueError('Final check not backed by successful reviewer execution: '+claim[:160])
 return True

