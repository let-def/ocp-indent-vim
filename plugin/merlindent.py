import os
import sys
import vim
import subprocess
import bisect

import vimbufsync

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

nullfd = open(os.devnull, 'w')

def fastpath(lines,state=None):
  global inline_process
  if not state: state=""
  lines = [line.replace('\\','\\\\') for line in lines]
  lines.insert(0,state)
  inline_process.stdin.write("\\n".join(lines))
  inline_process.stdin.write("\n")
  inline_process.stdin.flush()
  lines = inline_process.stdout.readline().decode('string_escape')
  if lines:
    lines = lines.rstrip().split("\n")
    state = lines.pop()
    return (state,lines)
  else:
    return False

def indentlines(lines,state=None):
  global inline_process, ocp_indent_path
  if not inline_process:
    inline_process = subprocess.Popen([ocp_indent_path,"--numeric","--inline","--rest"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=nullfd)
  return fastpath(lines,state)

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

  # Get best state to resume from
  if saved_states:
    l0, state = saved_states[-1]
  else:
    l0, state = 0, ""
  lines = list(vim.current.buffer[l0:l])
  if emptyline(lines[-1]):
    lines[-1] = "X"

  state, lines = indentlines(lines,state)
  saved_states.append((l,state))
  if len(lines):
    return int(lines[-1])
  else:
    return -1

def vim_sync():
  sync()

def vim_indentline():
  return ocpindentline(int(vim.eval("v:lnum")))

