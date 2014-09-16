Use with ocp-indent >= 1.2.0.

Just add this directory to your runtime path.

    set rtp+=</path/to/ocp-indent-vim>

BEWARE: By default, ocp-indent only works with spaces, not tabs. So be sure to `:set expandtab` either globally or for your ocaml files, for example by putting a line au FileType ocaml setlocal expandtab in your `.vimrc`

Released under MIT License.

### Passing custom arguments to ocp-indent

You can set the variables ```g:ocp_indent_args``` (global settings) or ```b:ocp_indent_args``` (buffer local settings) to pass arguments to ocp-indent.

Set variable to a string or a list of strings.

This may work for enabling tab-based indenting if required -- see the ocp-indent documentation.
