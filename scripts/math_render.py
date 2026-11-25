"""Build-time native MathML; no visitor scripts or font CDNs are required."""
import re
from latex2mathml.converter import convert

def protect(text):
    equations=[]
    def replace(match):
        source=match[0]
        display='block' if source.startswith(('$$',r'\[')) else 'inline'
        doubled=source.startswith('\\\\')
        width=3 if doubled else 2
        tex=source[width:-width].strip()
        if doubled:tex=tex.replace('\\\\%','\\%')
        equations.append('<span class="math">'+convert(tex,display=display)+'</span>')
        return 'MYSTARIAMATHPLACEHOLDER'+str(len(equations)-1)+'END'
    # Code samples retain literal TeX and are not typeset as reference equations.
    parts=re.split(r'(?ms)(^```[^\n]*\n.*?^```[^\n]*$|^~~~[^\n]*\n.*?^~~~[^\n]*$|`[^`\n]*`)',text)
    for i in range(0,len(parts),2):parts[i]=re.sub(r'(?s)\$\$.+?\$\$|\\{1,2}\[.+?\\{1,2}\]|\\{1,2}\(.+?\\{1,2}\)',replace,parts[i])
    return ''.join(parts),equations
