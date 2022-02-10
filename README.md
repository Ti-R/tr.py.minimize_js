# Script to help to minimize js files

## Why
I just wanted to minimize tr.markdown-fs.js and minimize most of my variables, but not everyhing.
I didn't find a tool easy to use to fill my need (or some couldn't parse my JS with all the regex...), so why not to make it quickly on sunday afternoon instead of looking for yet another tool...
Just to have some fun :)

## Result
I use "yuicompressor" since years with good results.

|        | yuicompressor | tr.py.minimize_js + yuicompressor |
| min.js | 21.82 Kio     | 12.19 Kio (45% smaller)           |
| gzip   | 5.27 Kio      | 4.45 Kio (16% smaller)            |

## Example
cmd file I use to minimize tr.markdown-fs

~~~cmd
REM 1) Rename all vars to small variable and excluded some VarName from renaming
"tr.py.minimize_js.py" --js "tr.markdown-fs.js" --excludeVarName TR MarkdownFS Debug MarkdownFSGlobal toHtml

REM 2) Call a "yuicompressor" for example
CALL "compress.bat" "tr.markdown-fs.min.js"

REM 3) Remove intermediate file
del tr.markdown-fs.min.js

REM 4) Rename min.min.js to .min.js
rename tr.markdown-fs.min.min.js tr.markdown-fs.min.js

REM 5) Use the same script to copy back the first line for the license.
"tr.py.minimize_js.py" --js "tr.markdown-fs.js" --restoreFirstLine

PAUSE
~~~

## What do you get inside
- Simple parser for JS, for comments, regex and strings
- Renaming the vars by some letters (the javascript keywords are exclude from renaming)
- Sort the renaming by the occurance of the varible, the most use variable will be "a", the seconde most used, will be 'b' and so on...