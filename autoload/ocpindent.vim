let s:current_dir=expand("<sfile>:p:h")
if has("python")
py <<EOF
import sys, vim
if not vim.eval("s:current_dir") in sys.path:
  sys.path.append(vim.eval("s:current_dir"))
import ocpindent
EOF
else
py3 <<EOF
import sys, vim
if not vim.eval("s:current_dir") in sys.path:
  sys.path.append(vim.eval("s:current_dir"))
import ocpindent
EOF
endif

function! ocpindent#init()
endfunction

function! ocpindent#OcpIndentLine()
  if has("python")
    py  vim.command("let l:ret = %d" % ocpindent.vim_indentline())
  else
    py3 vim.command("let l:ret = %d" % ocpindent.vim_indentline())
  endif
  return l:ret
endfunction

function! ocpindent#Equal()
  if has("python")
    py  ocpindent.vim_equal()
  else
    py3 ocpindent.vim_equal()
  endif
endfunction
