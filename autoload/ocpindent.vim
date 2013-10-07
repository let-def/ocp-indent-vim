let s:current_dir=expand("<sfile>:p:h")
py import sys, vim
py if not vim.eval("s:current_dir") in sys.path:
\    sys.path.append(vim.eval("s:current_dir"))
py import ocpindent

function! ocpindent#init()
endfunction

function! ocpindent#OcpIndentLine()
  py vim.command("let l:ret = %d" % ocpindent.vim_indentline())
  return l:ret
endfunction

function! ocpindent#Equal()
  py ocpindent.vim_equal()
endfunction
