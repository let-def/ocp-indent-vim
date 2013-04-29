import os
import sys
import vim
import subprocess
import bisect

import vimbufsync
vimbufsync.check_version("0.1.0", who="ocp-indent-vim")

inline_process = None
saved_states = []
saved_sync = None
ocp_indent_path = "ocp-indent"

insert_mode = False
equal_line = None
equal_lines = []

def sync():
  global saved_sync, saved_states
  curr_sync = vimbufsync.sync()
  if not saved_sync or curr_sync.buf() != saved_sync.buf():
    saved_states = []
  else:
    line = saved_sync.line()
    i = bisect.bisect_left(saved_states, (line,""))
    if i != len(saved_states):
      saved_states = saved_states[:i]
  saved_sync = curr_sync

#########################################################
# Process management, not really related to indentation #
#########################################################

def ocp_indent(content,state=None,lines=None):
  global ocp_indent_path
  if lines:
    if type(lines) == int:
      lines = "%d-%d" % (lines,lines)
    else:
      lines = "%d-%d" % lines
  else:
    lines = "0-0"
  if not state:
    state = ""
  content = "\n".join([state] + content + [""])
  process = subprocess.Popen(
      [ocp_indent_path,"--lines",lines,"--numeric","--marshal-state"],
      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  process.stdin.write(content)
  process.stdin.close()
  answer = process.stdout.readlines()
  state = answer.pop()
  [line,col] = map(int,state.split(",")[:2])
  return ((line-1,col,state),answer)

########################################
# Start from here to tweak indentation #
########################################

def emptyline(s):
  return s == "" or s.isspace()

def ocpindentline(l,count=1):
  global saved_states
  # Drop invalid states
  if l <= 2:
    saved_states = []
  else:
    i = bisect.bisect_left(saved_states, (l-1,0,""))
    if i != len(saved_states):
      saved_states = saved_states[:i]

  # Get or generate state to resume from
  if saved_states:
    l0, c0, state = saved_states[-1]
  else:
    l0, c0, state = 0, 0, None
  if l - l0 > 10:
    content = vim.current.buffer[l0:l-4]
    ((l0,c0,state), _) = ocp_indent(content,state)
    saved_states.append((l0,c0,state))

  # Indent
  content = list(vim.current.buffer[l0:l+count-1])
  content[0] = content[0][c0:]
  if count == 1 and emptyline(content[-1]):
    content[-1] = "X"

  if count == 1:
    _, content = ocp_indent(content,state,lines=l)
    if len(content):
      return int(content[-1])
    else:
      return -1
  else:
    _, content = ocp_indent(content,state,lines=(l,l+count-1))
    if len(content):
      return list(map(int,content))
    else:
      return None

def vim_insertenter():
  global insert_mode, equal_line, equal_lines
  equal_line = None
  equal_lines = []
  insert_mode = True
  sync()

def vim_insertleave():
  global insert_mode
  insert_mode = False
  sync()

def vim_indentline():
  global insert_mode, equal_line, equal_lines
  line = int(vim.eval("v:lnum"))
  if insert_mode or equal_line != line:
    equal_line = line + 1
    equal_lines = []
    return ocpindentline(line)
  else:
    if equal_line != line or not equal_lines:
      sync()
      equal_lines = ocpindentline(line,count=40)
      if equal_lines: equal_lines.reverse()

    if equal_lines:
      equal_line = line + 1
      return equal_lines.pop()
    else:
      return -1

def vim_equal():
  r = vim.current.range
  w = vim.current.window
  pos = w.cursor
  vim.command("0,'>!%s --lines %d-" % (ocp_indent_path, r.start+1))
  w.cursor = pos
