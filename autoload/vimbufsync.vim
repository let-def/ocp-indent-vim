let s:current_dir=expand("<sfile>:p:h")
py import vim
py if not vim.eval("s:current_dir") in sys.path: sys.path.append(vim.eval("s:current_dir"))

function! vimbufsync#init()
endfunction
