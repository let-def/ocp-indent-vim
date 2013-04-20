import os
import sys
import vim
import subprocess
import bisect

import vimbufsync
vimbufsync.check_version([0,1,0], who="merlindent")

inline_process = None
saved_states = []
saved_sync = None
ocp_indent_path = "ocp-indent"

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
      [ocp_indent_path,"--lines",lines,"--numeric","--rest"],
      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  process.stdin.write(content)
  process.stdin.close()
  answer = process.stdout.readlines()
  state = answer.pop()
  return (state,answer)

########################################
# Start from here to tweak indentation #
########################################

def emptyline(s):
  return s == "" or s.isspace()

def ocpindentline(l):
  global saved_states

  # Drop invalid states
  if l <= 2:
    saved_states = []
  else:
    i = bisect.bisect_left(saved_states, (l,""))
    if i != len(saved_states):
      saved_states = saved_states[:i]

  # Get or generate state to resume from
  if saved_states:
    l0, state = saved_states[-1]
  else:
    l0, state = 0, ""
  if l - l0 > 10:
    content = vim.current.buffer[l0:l-4]
    (state, _) = ocp_indent(content,state)
    l0 = l-4
    saved_states.append((l0,state))

  # Indent
  content = list(vim.current.buffer[l0:l])
  if emptyline(content[-1]):
    content[-1] = "X"

  _, content = ocp_indent(content,state,lines=l)
  if len(content):
    return int(content[-1])
  else:
    return -1

def vim_sync():
  sync()

def vim_indentline():
  return ocpindentline(int(vim.eval("v:lnum")))

